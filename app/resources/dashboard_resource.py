# app/routes/dashboard_bp.py
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import extract, func

from app.extensions import db
from app.models.activity_log import ActivityLog
from app.models.escrow_transaction import EscrowTransaction
from app.models.project import Project
from app.models.user import User

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    role = get_jwt_identity()["role"] if isinstance(get_jwt_identity(), dict) else None
    if role != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    total_projects = Project.query.count()
    total_users = User.query.count()
    escrow_released = EscrowTransaction.query.filter_by(status="released").count()
    escrow_in_escrow = EscrowTransaction.query.filter_by(status="in_escrow").count()

    stats = [
        {"label": "Total Users", "value": total_users, "color": "blue"},
        {"label": "Total Projects", "value": total_projects, "color": "green"},
        {"label": "Released Payments", "value": escrow_released, "color": "yellow"},
        {"label": "In Escrow", "value": escrow_in_escrow, "color": "purple"},
    ]
    return jsonify(stats), 200


@dashboard_bp.route("/recent-projects", methods=["GET"])
@jwt_required()
def recent_projects():
    user_id = get_jwt_identity()
    role = get_jwt_identity()["role"]

    if role == "admin":
        projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    elif role == "client":
        projects = (
            Project.query.filter_by(client_id=user_id)
            .order_by(Project.created_at.desc())
            .limit(5)
            .all()
        )
    elif role == "freelancer":
        projects = (
            Project.query.filter_by(freelancer_id=user_id)
            .order_by(Project.created_at.desc())
            .limit(5)
            .all()
        )
    else:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify([p.to_dict() for p in projects]), 200


@dashboard_bp.route("/transactions", methods=["GET"])
@jwt_required()
def recent_transactions():
    user_id = get_jwt_identity()
    role = get_jwt_identity()["role"]

    if role == "admin":
        txs = EscrowTransaction.query.order_by(EscrowTransaction.held_at.desc()).limit(5).all()
    elif role == "client":
        txs = (
            EscrowTransaction.query.filter_by(client_id=user_id)
            .order_by(EscrowTransaction.held_at.desc())
            .limit(5)
            .all()
        )
    elif role == "freelancer":
        txs = (
            EscrowTransaction.query.filter_by(freelancer_id=user_id)
            .order_by(EscrowTransaction.held_at.desc())
            .limit(5)
            .all()
        )
    else:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify([t.to_dict() for t in txs]), 200


@dashboard_bp.route("/activity", methods=["GET"])
@jwt_required()
def get_activity():
    user_id = get_jwt_identity()
    role = get_jwt_identity()["role"]

    if role == "admin":
        activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    else:
        activities = (
            ActivityLog.query.filter_by(user_id=user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(10)
            .all()
        )

    return jsonify({"recent_activity": [a.to_dict() for a in activities]}), 200


@dashboard_bp.route("/revenue", methods=["GET"])
@jwt_required()
def get_revenue_data():
    if get_jwt_identity()["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    current_year = extract("year", func.current_date())
    monthly_revenue = (
        db.session.query(
            extract("month", EscrowTransaction.released_at).label("month"),
            func.coalesce(func.sum(EscrowTransaction.amount), 0).label("total"),
        )
        .filter(EscrowTransaction.status == "released")
        .group_by("month")
        .order_by("month")
        .all()
    )

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
    revenue_data = [{"month": month_names[i], "revenue": 0.0} for i in range(12)]
    for row in monthly_revenue:
        revenue_data[int(row.month) - 1]["revenue"] = float(row.total)

    return jsonify({"revenue": revenue_data}), 200
