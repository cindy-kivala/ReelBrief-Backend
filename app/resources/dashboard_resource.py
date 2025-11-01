# app/resources/dashboard_bp.py
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import extract, func

from app.extensions import db
from app.models.activity_log import ActivityLog
from app.models.escrow_transaction import EscrowTransaction
from app.models.project import Project
from app.models.user import User

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/api/dashboard")

def get_user_info():
    """Helper function to get user ID and role from JWT token"""
    current_user = get_jwt_identity()
    
    if isinstance(current_user, dict):
        user_id = current_user.get('id')
        role = current_user.get('role')
    else:
        # If it's just an ID, get the user from database
        user_id = current_user
        user = User.query.get(user_id)
        role = user.role if user else None
    
    return user_id, role

@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    user_id, role = get_user_info()
    
    if not role:
        return jsonify({"error": "Could not determine user role"}), 400

    if role == "admin":
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
    
    elif role == "client":
        # Client-specific stats
        total_projects = Project.query.filter_by(client_id=user_id).count()
        active_projects = Project.query.filter_by(client_id=user_id, status='active').count()
        completed_projects = Project.query.filter_by(client_id=user_id, status='completed').count()
        pending_approval = Project.query.filter_by(client_id=user_id, status='pending_approval').count()
        
        # Calculate total spent from escrow transactions
        total_spent_result = EscrowTransaction.query.filter_by(
            client_id=user_id, 
            status='released'
        ).with_entities(func.sum(EscrowTransaction.amount)).scalar()
        total_spent = float(total_spent_result) if total_spent_result else 0
        
        stats = {
            "active_projects": active_projects,
            "pending_approval": pending_approval,
            "completed_projects": completed_projects,
            "total_spent": total_spent
        }
        return jsonify(stats), 200
    
    elif role == "freelancer":
        # Freelancer-specific stats
        total_projects = Project.query.filter_by(freelancer_id=user_id).count()
        active_projects = Project.query.filter_by(freelancer_id=user_id, status='active').count()
        completed_projects = Project.query.filter_by(freelancer_id=user_id, status='completed').count()
        pending_reviews = Project.query.filter_by(freelancer_id=user_id, status='pending_review').count()
        
        # Calculate total earned from escrow transactions
        total_earned_result = EscrowTransaction.query.filter_by(
            freelancer_id=user_id,
            status='released'
        ).with_entities(func.sum(EscrowTransaction.amount)).scalar()
        total_earned = float(total_earned_result) if total_earned_result else 0
        
        stats = {
            "active_projects": active_projects,
            "pending_reviews": pending_reviews,
            "completed_projects": completed_projects,
            "total_earned": total_earned
        }
        return jsonify(stats), 200
    
    else:
        return jsonify({"error": "Unauthorized"}), 403

@dashboard_bp.route("/recent-projects", methods=["GET"])
@jwt_required()
def recent_projects():
    user_id, role = get_user_info()
    
    if not role:
        return jsonify({"error": "Could not determine user role"}), 400

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

    # Convert projects to dictionaries with consistent field names
    projects_data = []
    for project in projects:
        project_dict = project.to_dict()
        
        # Ensure consistent field names for frontend
        if 'client' in project_dict and 'name' in project_dict['client']:
            project_dict['client_name'] = project_dict['client']['name']
        if 'freelancer' in project_dict and 'name' in project_dict['freelancer']:
            project_dict['freelancer_name'] = project_dict['freelancer']['name']
        
        projects_data.append(project_dict)

    return jsonify(projects_data), 200

@dashboard_bp.route("/transactions", methods=["GET"])
@jwt_required()
def recent_transactions():
    user_id, role = get_user_info()
    
    if not role:
        return jsonify({"error": "Could not determine user role"}), 400

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
    user_id, role = get_user_info()
    
    if not role:
        return jsonify({"error": "Could not determine user role"}), 400

    if role == "admin":
        activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    else:
        activities = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    return jsonify([activity.to_dict() for activity in activities]), 200

@dashboard_bp.route("/revenue", methods=["GET"])
@jwt_required()
def get_revenue_data():
    user_id, role = get_user_info()
    
    if not role:
        return jsonify({"error": "Could not determine user role"}), 400
        
    if role != "admin":
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
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    revenue_data = [{"month": month_names[i], "revenue": 0.0} for i in range(12)]
    for row in monthly_revenue:
        revenue_data[int(row.month) - 1]["revenue"] = float(row.total)

    return jsonify({"revenue": revenue_data}), 200