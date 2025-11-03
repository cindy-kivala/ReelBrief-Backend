"""
Escrow Resource
Owner: Caleb
Description:
Handles escrow transactions for projects — creation, release, refund, and retrieval.
Integrated with JWT authentication and role-based access control.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.extensions import db
from app.models.escrow_transaction import EscrowTransaction
from app.models.project import Project
from app.models.wallet import Wallet

escrow_bp = Blueprint("escrow_bp", __name__, url_prefix="/api/escrow")


@escrow_bp.post("/create")
@jwt_required()
def create_escrow():
    """Create (fund) an escrow transaction for a project."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role not in ["client", "admin"]:
        return jsonify({"error": "Unauthorized to create escrow"}), 403

    data = request.get_json()
    project_id = data.get("project_id")
    amount = data.get("amount")

    if not project_id or not amount:
        return jsonify({"error": "Missing project_id or amount"}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    existing_escrow = EscrowTransaction.query.filter_by(project_id=project_id).first()
    if existing_escrow:
        return jsonify({"error": "Escrow already exists for this project"}), 409

    # ✅ Check client wallet
    client_wallet = Wallet.query.filter_by(user_id=user_id).first()

    if not client_wallet or client_wallet.balance < float(amount):
        return jsonify({"error": "Insufficient balance to fund escrow"}), 400

    # ✅ Deduct funds from client wallet
    client_wallet.balance -= float(amount)

    # ✅ Create escrow transaction
    escrow = EscrowTransaction(
        project_id=project_id,
        sender_id=user_id,  # client who funds the escrow
        receiver_id=getattr(project, "freelancer_id", None),  # freelancer
        amount=amount,
        status="held",  # held in escrow
        created_at=datetime.utcnow(),
    )

    db.session.add(escrow)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Escrow created and funded successfully",
                "escrow": escrow.to_dict(),
                "client_wallet": float(client_wallet.balance),
            }
        ),
        201,
    )



@escrow_bp.post("/<int:escrow_id>/release")
@jwt_required()
def release_escrow(escrow_id):
    """Release escrow funds to freelancer."""
    claims = get_jwt()
    role = claims.get("role")

    if role not in ["admin"]:
        return jsonify({"error": "Only admin can release funds"}), 403

    escrow = EscrowTransaction.query.get(escrow_id)
    if not escrow:
        return jsonify({"error": "Escrow not found"}), 404

    if escrow.status != "held":
        return jsonify({
            "error": f"Cannot release escrow with status '{escrow.status}'. Only 'held' escrows can be released."
        }), 400

    # ✅ Mark escrow as released
    escrow.status = "released"
    escrow.released_at = datetime.utcnow()

    # ✅ Fetch or create freelancer wallet
    freelancer_wallet = Wallet.query.filter_by(user_id=escrow.receiver_id).first()
    if not freelancer_wallet:
        freelancer_wallet = Wallet(user_id=escrow.receiver_id, balance=0.0)
        db.session.add(freelancer_wallet)

    # ✅ Transfer funds to freelancer (funds already deducted from client in create_escrow)
    freelancer_wallet.balance += escrow.amount

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Funds released successfully",
                "escrow": escrow.to_dict(),
                "freelancer_wallet": float(freelancer_wallet.balance),
            }
        ),
        200,
    )


@escrow_bp.post("/<int:escrow_id>/cancel")
@jwt_required()
def cancel_escrow(escrow_id):
    """Cancel/refund escrow to client (sender) if project is cancelled or disputed."""
    claims = get_jwt()
    role = claims.get("role")

    if role not in ["client", "admin"]:
        return jsonify({"error": "Unauthorized to refund funds"}), 403

    escrow = EscrowTransaction.query.get(escrow_id)
    if not escrow:
        return jsonify({"error": "Escrow not found"}), 404

    if escrow.status != "held":
        return jsonify({
            "error": f"Cannot refund escrow with status '{escrow.status}'. Only 'held' escrows can be refunded."
        }), 400

    # ✅ Mark as refunded
    escrow.status = "refunded"
    escrow.refunded_at = datetime.utcnow()

    # ✅ Return funds to client (sender)
    client_wallet = Wallet.query.filter_by(user_id=escrow.sender_id).first()
    if not client_wallet:
        client_wallet = Wallet(user_id=escrow.sender_id, balance=0.0)
        db.session.add(client_wallet)

    client_wallet.balance += escrow.amount

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Funds refunded successfully",
                "escrow": escrow.to_dict(),
                "wallet_balance": float(client_wallet.balance),
            }
        ),
        200,
    )


@escrow_bp.post("/refund")
@jwt_required()
def refund_escrow():
    """Legacy refund endpoint - redirects to cancel"""
    data = request.get_json()
    escrow_id = data.get("escrow_id")

    if not escrow_id:
        return jsonify({"error": "Missing escrow_id"}), 400

    # Call the cancel endpoint logic
    return cancel_escrow(escrow_id)


@escrow_bp.get("/<int:project_id>")
@jwt_required()
def get_escrow(project_id):
    """Fetch escrow details for a project."""
    escrow = EscrowTransaction.query.filter_by(project_id=project_id).first()

    if not escrow:
        return jsonify({"error": "No escrow found for this project"}), 404

    return jsonify({"escrow": escrow.to_dict()}), 200


@escrow_bp.get("/")
@jwt_required()
def list_user_escrows():
    """List escrows belonging to the authenticated user."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role == "admin":
        # Admin sees all escrows
        escrows = EscrowTransaction.query.all()
    elif role == "client":
        # Client sees escrows where they are the sender
        escrows = EscrowTransaction.query.filter_by(sender_id=user_id).all()
    elif role == "freelancer":
        # Freelancer sees escrows where they are the receiver
        escrows = EscrowTransaction.query.filter_by(receiver_id=user_id).all()
    else:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify({"escrows": [e.to_dict() for e in escrows]}), 200