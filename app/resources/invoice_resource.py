"""
Invoice Resource - Invoice Management Endpoints
Owner: Caleb
Description: Handles creation, retrieval, and payment of invoices.
"""

from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.escrow_transaction import EscrowTransaction
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.wallet import Wallet
from app.models.user import User
from app.models.wallet_transaction import WalletTransaction
from app.services.email_service import send_invoice_email, send_payment_received_email

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

    return (
        jsonify(
            {
                "invoices": invoices,
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
            }
        ),
        200,
    )


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

    return (
        jsonify({"message": "Invoice created successfully", "invoice": new_invoice.to_dict()}),
        201,
    )


# -------------------- POST /api/invoices/<id>/pay --------------------
@invoice_bp.route('/<int:invoice_id>/pay', methods=['POST'])
@jwt_required()
def pay_invoice(invoice_id):
    """Pay an invoice"""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        user_id = get_jwt_identity()
        
        # Verify authorization
        if invoice.client_id != user_id:
            return jsonify({"error": "Not authorized"}), 403
        
        # Get wallet
        client_wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not client_wallet:
            return jsonify({"error": "Wallet not found"}), 404
        
        # Check balance
        if client_wallet.balance < invoice.amount:
            return jsonify({"error": "Insufficient balance"}), 400
        
        # Process payment
        client_wallet.debit(invoice.amount)
        
        # Create wallet transaction - THIS NEEDS THE IMPORT
        wallet_tx = WalletTransaction(
            wallet_id=client_wallet.id,
            amount=invoice.amount,
            transaction_type="payment", 
            description=f"Invoice {invoice.invoice_number}",
            reference_id=invoice.id
        )
        db.session.add(wallet_tx)
        
        # Update invoice
        invoice.status = "paid"
        invoice.paid_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "Invoice paid",
            "invoice": invoice.to_dict(),
            "new_balance": float(client_wallet.balance)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------------------- PATCH /api/invoices/<id> --------------------
@invoice_bp.patch("/<int:invoice_id>")
@jwt_required()
def update_invoice(invoice_id):
    """Update an existing invoice (admin or freelancer who created it)."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    invoice = Invoice.query.get_or_404(invoice_id)

    # Only admin or the freelancer who owns it can update
    if role != "admin" and user_id != invoice.freelancer_id:
        return jsonify({"error": "Unauthorized to update this invoice"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    allowed_fields = ["amount", "due_date", "notes", "status"]
    for field in allowed_fields:
        if field in data:
            if field == "due_date" and data[field]:
                invoice.due_date = datetime.strptime(data[field], "%Y-%m-%d")
            else:
                setattr(invoice, field, data[field])

    db.session.commit()
    return jsonify({"message": "Invoice updated successfully", "invoice": invoice.to_dict()}), 200


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
