"""
Payment Service
Owner: Caleb
Description: Handles escrow payments, releases, and refunds logic.
"""

from datetime import datetime

from models import Escrow, Transaction, db
from services.email_service import send_payment_notification


def create_escrow(project_id, client_id, freelancer_id, amount):
    """
    Create a new escrow transaction.

    Args:
        project_id (int): Associated project ID.
        client_id (int): ID of the client funding the escrow.
        freelancer_id (int): ID of the freelancer assigned to the project.
        amount (float): Amount to be held in escrow.
    """
    escrow = Escrow(
        project_id=project_id,
        client_id=client_id,
        freelancer_id=freelancer_id,
        amount=amount,
        status="PENDING",
        created_at=datetime.utcnow(),
    )

    db.session.add(escrow)
    db.session.commit()

    print(f"Escrow created for Project ID {project_id} - Amount: ${amount}")
    return escrow


def release_payment(escrow_id):
    """
    Release payment from escrow to freelancer.
    Updates escrow status and records a completed transaction.
    """
    escrow = Escrow.query.get(escrow_id)
    if not escrow:
        raise ValueError("Escrow not found")

    if escrow.status != "PENDING":
        raise ValueError("Escrow cannot be released. Invalid status.")

    escrow.status = "RELEASED"
    escrow.released_at = datetime.utcnow()

    transaction = Transaction(
        user_id=escrow.freelancer_id,
        amount=escrow.amount,
        transaction_type="RELEASE",
        description=f"Payment released for Project ID {escrow.project_id}",
        created_at=datetime.utcnow(),
    )

    db.session.add(transaction)
    db.session.commit()

    # Notify freelancer of payment release
    try:
        send_payment_notification(transaction)
    except Exception as e:
        print(f"Failed to send payment notification: {e}")

    print(f"Payment released for Escrow ID {escrow_id} - Amount: ${escrow.amount}")
    return transaction


def refund_payment(escrow_id, reason):
    """
    Refund client and mark escrow as refunded.

    Args:
        escrow_id (int): Escrow transaction ID.
        reason (str): Reason for refund.
    """
    escrow = Escrow.query.get(escrow_id)
    if not escrow:
        raise ValueError("Escrow not found")

    if escrow.status not in ["PENDING", "HELD"]:
        raise ValueError("Only pending or held escrows can be refunded.")

    escrow.status = "REFUNDED"
    escrow.refund_reason = reason
    escrow.refunded_at = datetime.utcnow()

    transaction = Transaction(
        user_id=escrow.client_id,
        amount=escrow.amount,
        transaction_type="REFUND",
        description=f"Refund for Project ID {escrow.project_id}. Reason: {reason}",
        created_at=datetime.utcnow(),
    )

    db.session.add(transaction)
    db.session.commit()

    # Notify client of refund
    try:
        send_payment_notification(transaction)
    except Exception as e:
        print(f"Failed to send refund notification: {e}")

    print(f"Escrow ID {escrow_id} refunded. Reason: {reason}")
    return transaction


def calculate_freelancer_earnings(freelancer_id):
    """
    Aggregate released and pending earnings for a freelancer.
    """
    released = (
        db.session.query(db.func.sum(Escrow.amount))
        .filter_by(freelancer_id=freelancer_id, status="RELEASED")
        .scalar()
        or 0
    )

    pending = (
        db.session.query(db.func.sum(Escrow.amount))
        .filter_by(freelancer_id=freelancer_id, status="PENDING")
        .scalar()
        or 0
    )

    earnings = {"released": float(released), "pending": float(pending)}
    print(f"Earnings for Freelancer {freelancer_id}: {earnings}")
    return earnings
