"""
activity_resource.py
Owner: Caleb
Description: Provides API endpoints for viewing and managing Activity Logs (audit trail).
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import ActivityLog, User

activity_bp = Blueprint("activity", __name__, url_prefix="/api/activity")


@activity_bp.route("/", methods=["GET"])
def get_all_activities():
    try:
        limit = int(request.args.get("limit", 20))
        user_id = request.args.get("user_id")
        role = request.args.get("role")
        action_filter = request.args.get("action")

        query = ActivityLog.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        if role:
            query = query.join(User).filter(User.role_as == int(role))
        if action_filter:
            query = query.filter(ActivityLog.action.ilike(f"%{action_filter}%"))

        logs = query.order_by(ActivityLog.created_at.desc()).limit(limit).all()

        return jsonify([log.to_dict() for log in logs]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activity_bp.route("/<int:activity_id>", methods=["GET"])
def get_activity(activity_id):
    log = ActivityLog.query.get(activity_id)
    if not log:
        return jsonify({"message": "Activity not found"}), 404
    return jsonify(log.to_dict()), 200


@activity_bp.route("/", methods=["POST"])
def create_activity():
    try:
        data = request.get_json()
        new_log = ActivityLog(
            user_id=data.get("user_id"),
            action=data.get("action"),
            details=data.get("details"),
            ip_address=request.remote_addr,
            created_at=datetime.utcnow(),
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Activity log created", "log": new_log.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@activity_bp.route("/<int:activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    try:
        log = ActivityLog.query.get(activity_id)
        if not log:
            return jsonify({"message": "Activity not found"}), 404

        db.session.delete(log)
        db.session.commit()
        return jsonify({"message": f"Activity ID {activity_id} deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@activity_bp.route("/clear", methods=["DELETE"])
def clear_all_activities():
    try:
        db.session.query(ActivityLog).delete()
        db.session.commit()
        return jsonify({"message": "All activity logs cleared"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
