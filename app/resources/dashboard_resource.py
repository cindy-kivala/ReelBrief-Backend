"""
Dashboard Resource - Unified Data Overview
Owner: Caleb
Description: Provides summary data for freelancers, clients, and admins.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.extensions import db
from app.models.escrow_transaction import EscrowTransaction
from app.models.notification import Notification
from app.models.project import Project
from app.models.user import User

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def get_dashboard():
    """Return role-specific dashboard statistics."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role == "freelancer":
        projects_in_progress = Project.query.filter_by(
            freelancer_id=user_id, status="in_progress"
        ).count()
        earnings = (
            db.session.query(db.func.sum(EscrowTransaction.amount))
            .filter_by(freelancer_id=user_id, status="released")
            .scalar()
            or 0
        )
        pending_feedback = Project.query.filter_by(
            freelancer_id=user_id, status="pending_review"
        ).count()

        data = {
            "role": "freelancer",
            "projects_in_progress": projects_in_progress,
            "earnings_summary": earnings,
            "pending_feedback": pending_feedback,
        }

    elif role == "client":
        active_projects = Project.query.filter_by(client_id=user_id, status="in_progress").count()
        pending_payments = EscrowTransaction.query.filter_by(
            client_id=user_id, status="in_escrow"
        ).count()
        feedback_requests = Project.query.filter_by(
            client_id=user_id, status="pending_review"
        ).count()

        data = {
            "role": "client",
            "active_projects": active_projects,
            "pending_payments": pending_payments,
            "feedback_requests": feedback_requests,
        }

    elif role == "admin":
        total_users = User.query.count()
        total_projects = Project.query.count()
        escrow_overview = {
            "total_escrows": EscrowTransaction.query.count(),
            "released": EscrowTransaction.query.filter_by(status="released").count(),
            "in_escrow": EscrowTransaction.query.filter_by(status="in_escrow").count(),
            "refunded": EscrowTransaction.query.filter_by(status="refunded").count(),
        }

        data = {
            "role": "admin",
            "total_users": total_users,
            "total_projects": total_projects,
            "escrow_overview": escrow_overview,
        }

    else:
        return jsonify({"error": "Invalid role"}), 400

    return jsonify({"dashboard": data}), 200


@dashboard_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    """Return unread notifications for current user."""
    user_id = get_jwt_identity()
    unread_notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    return jsonify({"notifications": [n.to_dict() for n in unread_notifications]}), 200


@dashboard_bp.route("/activity", methods=["GET"])
@jwt_required()
def get_activity():
    """Return recent user activity (placeholder for now)."""
    # This would normally query an ActivityLog model
    activity_logs = [
        {"action": "Logged in", "timestamp": "2025-10-23T09:00:00Z"},
        {"action": "Viewed dashboard", "timestamp": "2025-10-23T09:02:00Z"},
        {"action": "Checked projects", "timestamp": "2025-10-23T09:05:00Z"},
    ]
    return jsonify({"recent_activity": activity_logs[:10]}), 200


from sqlalchemy import extract


@dashboard_bp.route("/revenue", methods=["GET"])
@jwt_required()
def get_revenue_data():
    """Return monthly revenue statistics for admin chart display."""
    claims = get_jwt()
    role = claims.get("role")

    if role != "admin":
        return jsonify({"error": "Unauthorized access"}), 403

    # Query total released escrow amount per month (current year)
    current_year = db.func.extract("year", db.func.current_date())
    monthly_revenue = (
        db.session.query(
            extract("month", EscrowTransaction.released_at).label("month"),
            db.func.sum(EscrowTransaction.amount).label("total_revenue"),
        )
        .filter(
            EscrowTransaction.status == "released",
            extract("year", EscrowTransaction.released_at) == current_year,
        )
        .group_by(extract("month", EscrowTransaction.released_at))
        .order_by("month")
        .all()
    )

    # Map month numbers to short month names (1=Jan, 2=Feb, etc.)
    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    revenue_data = []
    for i in range(1, 13):
        month_total = next(
            (float(row.total_revenue) for row in monthly_revenue if int(row.month) == i),
            0.0,
        )
        revenue_data.append({"month": month_names[i - 1], "revenue": month_total})

    return jsonify({"revenue": revenue_data}), 200
