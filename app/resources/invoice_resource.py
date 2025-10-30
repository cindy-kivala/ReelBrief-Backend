"""
Invoice Resource - Invoice Management Endpoints
Owner: Caleb
Description: Handles creation, retrieval, and payment of invoices.
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.escrow_transaction import EscrowTransaction
from app.models.invoice import Invoice
from app.models.project import Project

invoice_bp = Blueprint("invoice_bp", __name__, url_prefix="/api/invoices")


# -------------------- GET /api/invoices --------------------
@invoice_bp.get("/")
@jwt_required()
def list_invoices():
    """Return paginated list of invoices for the current user."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    page = int(request.args.get("page", 1))
    per_page = 10

    query = Invoice.query

    if role == "client":
        query = query.filter_by(client_id=user_id)
    elif role == "freelancer":
        query = query.filter_by(freelancer_id=user_id)
    elif role != "admin":
        return jsonify({"error": "Unauthorized role"}), 403

    pagination = query.order_by(Invoice.issue_date.desc()).paginate(page=page, per_page=per_page)
    invoices = [inv.to_dict() for inv in pagination.items]

    return jsonify({
        "invoices": invoices,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    }), 200


# -------------------- GET /api/invoices/<id> --------------------
@invoice_bp.get("/<int:invoice_id>")
@jwt_required()
def get_invoice(invoice_id):
    """Return details of a specific invoice."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    invoice = Invoice.query.get_or_404(invoice_id)

    if role != "admin" and user_id not in [invoice.client_id, invoice.freelancer_id]:
        return jsonify({"error": "Access denied"}), 403

    return jsonify({"invoice": invoice.to_dict()}), 200


# -------------------- POST /api/invoices --------------------
@invoice_bp.post("/")
@jwt_required()
def create_invoice():
    """Create a new invoice for a project (freelancer or admin only)."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role not in ["freelancer", "admin"]:
        return jsonify({"error": "Only freelancers or admins can create invoices"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    project_id = data.get("project_id")
    amount = data.get("amount")
    due_date = data.get("due_date")
    notes = data.get("notes")

    if not project_id or not amount:
        return jsonify({"error": "Missing required fields"}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if role == "freelancer" and project.freelancer_id != user_id:
        return jsonify({"error": "You cannot invoice this project"}), 403

    invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    new_invoice = Invoice(
        project_id=project_id,
        client_id=project.client_id,
        freelancer_id=project.freelancer_id,
        invoice_number=invoice_number,
        amount=amount,
        due_date=datetime.strptime(due_date, "%Y-%m-%d") if due_date else None,
        notes=notes,
    )

    db.session.add(new_invoice)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Duplicate invoice number"}), 409

    return jsonify({
        "message": "Invoice created successfully",
        "invoice": new_invoice.to_dict()
    }), 201


# -------------------- PATCH /api/invoices/<id>/pay --------------------
@invoice_bp.patch("/<int:invoice_id>/pay")
@jwt_required()
def pay_invoice(invoice_id):
    """Mark an invoice as paid (client only)."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    invoice = Invoice.query.get_or_404(invoice_id)

    if role != "client" or user_id != invoice.client_id:
        return jsonify({"error": "Only the client who owns this invoice can pay it"}), 403

    if invoice.status == "paid":
        return jsonify({"message": "Invoice already paid"}), 200

    invoice.status = "paid"
    invoice.paid_at = datetime.utcnow()

    # Optional: update escrow
    if invoice.escrow_id:
        escrow = EscrowTransaction.query.get(invoice.escrow_id)
        if escrow:
            escrow.status = "released"
            escrow.released_at = datetime.utcnow()

    db.session.commit()
    return jsonify({"message": "Invoice marked as paid", "invoice": invoice.to_dict()}), 200


# -------------------- DELETE /api/invoices/<id> --------------------
@invoice_bp.delete("/<int:invoice_id>")
@jwt_required()
def delete_invoice(invoice_id):
    """Delete an invoice (admin only)."""
    claims = get_jwt()
    role = claims.get("role")

    if role != "admin":
        return jsonify({"error": "Only admins can delete invoices"}), 403

    invoice = Invoice.query.get_or_404(invoice_id)
    db.session.delete(invoice)
    db.session.commit()
    return jsonify({"message": "Invoice deleted successfully"}), 200
