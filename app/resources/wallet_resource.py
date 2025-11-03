"""
Wallet Resource - Handles user wallet operations
Owner: Caleb
Description:
Allows users to view balance, view transactions, deposit funds,
and perform transfers. Admins can view all wallets and credit users.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction

wallet_bp = Blueprint("wallet_bp", __name__, url_prefix="/api/wallet")


# -------------------- Helper --------------------
def get_or_create_wallet(user_id):
    """Ensure wallet exists for a user."""
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.00)
        db.session.add(wallet)
        db.session.commit()
    return wallet


# -------------------- GET /api/wallet --------------------
@wallet_bp.get("/")
@jwt_required()
def get_wallet():
    """Get wallet info for the current user (or all if admin)."""
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    if role == "admin":
        wallets = Wallet.query.all()
        return jsonify({"wallets": [w.to_dict() for w in wallets]}), 200

    wallet = get_or_create_wallet(user_id)
    return jsonify({"wallet": wallet.to_dict()}), 200


# -------------------- GET /api/wallet/transactions --------------------
@wallet_bp.get("/transactions")
@jwt_required()
def get_wallet_transactions():
    """Get wallet transaction history for current user (admin can filter by user)."""
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()

    # Admins can query any user's wallet
    if role == "admin" and request.args.get("user_id"):
        target_user_id = int(request.args.get("user_id"))
    else:
        target_user_id = user_id

    wallet = get_or_create_wallet(target_user_id)
    transactions = wallet.transactions.order_by(WalletTransaction.created_at.desc()).all()

    return jsonify({"transactions": [t.to_dict() for t in transactions]}), 200


# -------------------- POST /api/wallet/deposit --------------------
@wallet_bp.post("/deposit")
@jwt_required()
def deposit_funds():
    """Deposit funds to current user's wallet."""
    user_id = get_jwt_identity()
    data = request.get_json()

    amount = data.get("amount")
    description = data.get("description", "Wallet deposit")

    if not amount or amount <= 0:
        return jsonify({"error": "Invalid deposit amount"}), 400

    wallet = get_or_create_wallet(user_id)

    try:
        wallet.credit(amount)
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type="deposit",
            description=description,
        )
        db.session.add(transaction)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to deposit"}), 500

    return (
        jsonify(
            {
                "message": "Deposit successful",
                "wallet": wallet.to_dict(),
                "transaction": transaction.to_dict(),
            }
        ),
        201,
    )


# -------------------- POST /api/wallet/debit --------------------
@wallet_bp.post("/debit")
@jwt_required()
def debit_wallet():
    """Deduct funds from wallet (used when paying an invoice or moving to escrow)."""
    user_id = get_jwt_identity()
    data = request.get_json()

    amount = data.get("amount")
    description = data.get("description", "Wallet debit")

    if not amount or amount <= 0:
        return jsonify({"error": "Invalid debit amount"}), 400

    wallet = get_or_create_wallet(user_id)

    try:
        wallet.debit(amount)
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type="payment",
            description=description,
        )
        db.session.add(transaction)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to debit"}), 500

    return (
        jsonify(
            {
                "message": "Wallet debited successfully",
                "wallet": wallet.to_dict(),
                "transaction": transaction.to_dict(),
            }
        ),
        200,
    )


# -------------------- GET /api/wallet/balance --------------------
@wallet_bp.get("/balance")
@jwt_required()
def get_wallet_balance():
    """Return current user's wallet balance only."""
    user_id = get_jwt_identity()
    wallet = get_or_create_wallet(user_id)
    return jsonify(wallet.to_dict()), 200


# -------------------- POST /api/wallet/transfer --------------------
@wallet_bp.post("/transfer")
@jwt_required()
def transfer_funds():
    """Transfer funds from current user to another user."""
    user_id = get_jwt_identity()
    data = request.get_json()

    target_email = data.get("email")
    amount = data.get("amount")

    if not target_email or not amount or amount <= 0:
        return jsonify({"error": "Email and amount are required"}), 400

    sender_wallet = get_or_create_wallet(user_id)
    recipient_user = User.query.filter_by(email=target_email).first()

    if not recipient_user:
        return jsonify({"error": "Recipient not found"}), 404

    recipient_wallet = get_or_create_wallet(recipient_user.id)

    if sender_wallet.balance < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    try:
        # Perform transfer
        sender_wallet.debit(amount)
        recipient_wallet.credit(amount)

        sender_tx = WalletTransaction(
            wallet_id=sender_wallet.id,
            amount=amount,
            transaction_type="transfer_out",
            description=f"Transfer to {target_email}",
        )
        recipient_tx = WalletTransaction(
            wallet_id=recipient_wallet.id,
            amount=amount,
            transaction_type="transfer_in",
            description=f"Received from user {user_id}",
        )

        db.session.add_all([sender_tx, recipient_tx])
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Transferred {amount} to {target_email}",
                    "sender_wallet": sender_wallet.to_dict(),
                    "recipient_wallet": recipient_wallet.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------------------- ADMIN: POST /api/wallet/credit-user/<user_id> --------------------
@wallet_bp.post("/credit-user/<int:user_id>")
@jwt_required()
def admin_credit_user(user_id):
    """Admin can credit (add funds) to any user wallet manually."""
    claims = get_jwt()
    role = claims.get("role")
    if role != "admin":
        return jsonify({"error": "Only admins can credit wallets"}), 403

    data = request.get_json()
    amount = data.get("amount")
    description = data.get("description", "Admin credit")

    if not amount or amount <= 0:
        return jsonify({"error": "Invalid credit amount"}), 400

    wallet = get_or_create_wallet(user_id)

    wallet.credit(amount)
    transaction = WalletTransaction(
        wallet_id=wallet.id,
        amount=amount,
        transaction_type="credit",
        description=description,
    )
    db.session.add(transaction)
    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Wallet credited for user {user_id}",
                "wallet": wallet.to_dict(),
                "transaction": transaction.to_dict(),
            }
        ),
        200,
    )


# -------------------- ADMIN: GET /api/wallet/admin/overview --------------------
@wallet_bp.get("/admin/overview")
@jwt_required()
def admin_overview():
    """Admin route to get summary of all wallets and transactions."""
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    total_balance = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    total_transactions = WalletTransaction.query.count()
    total_deposits = (
        db.session.query(db.func.sum(WalletTransaction.amount))
        .filter(WalletTransaction.transaction_type == "deposit")
        .scalar()
        or 0
    )

    return (
        jsonify(
            {
                "total_balance": total_balance,
                "total_transactions": total_transactions,
                "total_deposits": total_deposits,
            }
        ),
        200,
    )


# -------------------- DEV: GET /api/wallet/seed --------------------
@wallet_bp.get("/seed")
def seed_wallets():
    """Development-only route to create wallets for all users."""
    users = User.query.all()
    count = 0
    for user in users:
        if not Wallet.query.filter_by(user_id=user.id).first():
            wallet = Wallet(user_id=user.id, balance=100.00)
            db.session.add(wallet)
            count += 1
    db.session.commit()
    return jsonify({"message": f"Seeded {count} wallets"}), 201
