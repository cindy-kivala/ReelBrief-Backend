"""
Feedback Resource - Structured Revision Requests
Owner: Cindy
Description: Submit and manage feedback on deliverables
"""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.deliverable import Deliverable
from app.models.feedback import Feedback

feedback_bp = Blueprint("feedback", __name__, url_prefix="/api/feedback")


# TODO: Cindy - Implement feedback endpoints
#
# Required endpoints:
#
# GET /api/deliverables/:deliverable_id/feedback
# - Requires: JWT auth
# - Return: all feedback for this deliverable
# - Include nested replies (threaded comments)
@feedback_bp.route("/deliverables/<int:deliverable_id>", methods=["GET"])
@jwt_required()
def get_deliverable_feedback(deliverable_id):
    """
    Get all feedback for a deliverable

    Query params:
        - include_resolved: Include resolved feedback (default: true)
        - include_replies: Include threaded replies (default: true)
    """
    try:
        # Verify deliverable exists
        deliverable = Deliverable.query.get_or_404(deliverable_id)

        include_resolved = request.args.get("include_resolved", "true").lower() == "true"

        # Get feedback (only top-level, not replies)
        feedback_items = Feedback.get_feedback_for_deliverable(
            deliverable_id, include_resolved=include_resolved
        )

        return (
            jsonify(
                {
                    "success": True,
                    "feedback": [f.to_dict(include_replies=True) for f in feedback_items],
                    "total_count": len(feedback_items),
                    "unresolved_count": Feedback.get_unresolved_count(deliverable_id),
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error fetching feedback: {str(e)}")
        return jsonify({"success": False, "error": "Failed to fetch feedback"}), 500


#
# POST /api/feedback
# - Requires: JWT auth
# - Accept: deliverable_id, feedback_type, content, priority, parent_feedback_id
# - Create feedback record
# - Send notification if it's a new revision request
# - Return: created feedbackv
@feedback_bp.route("/", methods=["POST"])
@jwt_required()
def create_feedback():
    """
    Submit feedback on a deliverable

    JSON body:
        - deliverable_id: ID of deliverable (required)
        - feedback_type: 'comment', 'revision', 'approval' (required)
        - content: Feedback text (required)
        - priority: 'low', 'medium', 'high' (optional)
        - parent_feedback_id: ID of parent for threaded reply (optional)
    """
    try:
        current_user_id = get_jwt_identity()

        data = request.get_json()

        # Validate required fields
        required_fields = ["deliverable_id", "feedback_type", "content"]
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"{field} is required"}), 400

        # Verify deliverable exists
        deliverable = Deliverable.query.get_or_404(data["deliverable_id"])

        # Validate feedback_type
        valid_types = ["comment", "revision", "approval"]
        if data["feedback_type"] not in valid_types:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'feedback_type must be one of: {", ".join(valid_types)}',
                    }
                ),
                400,
            )

        # Create feedback
        feedback = Feedback(
            deliverable_id=data["deliverable_id"],
            user_id=current_user_id,
            feedback_type=data["feedback_type"],
            content=data["content"],
            priority=data.get("priority", "medium"),
            parent_feedback_id=data.get("parent_feedback_id"),
        )

        db.session.add(feedback)
        db.session.commit()

        # TODO: Send notification if revision request (notification service)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Feedback submitted successfully",
                    "feedback": feedback.to_dict(include_replies=False),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating feedback: {str(e)}")
        return jsonify({"success": False, "error": "Failed to create feedback"}), 500


@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
@jwt_required()
def get_feedback(feedback_id):
    """Get specific feedback with replies"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)

        return jsonify({"success": True, "feedback": feedback.to_dict(include_replies=True)}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching feedback: {str(e)}")
        return jsonify({"success": False, "error": "Feedback not found"}), 404


# PATCH
@feedback_bp.route("/<int:feedback_id>", methods=["PATCH"])
@jwt_required()
def update_feedback(feedback_id):
    """
    Update feedback content

    JSON body:
        - content: Updated feedback text
        - priority: Updated priority level
    """
    try:
        current_user_id = get_jwt_identity()

        feedback = Feedback.query.get_or_404(feedback_id)

        # Check ownership
        if feedback.user_id != current_user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        data = request.get_json()

        if "content" in data:
            feedback.content = data["content"]

        if "priority" in data:
            feedback.priority = data["priority"]

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Feedback updated successfully",
                    "feedback": feedback.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating feedback: {str(e)}")
        return jsonify({"success": False, "error": "Failed to update feedback"}), 500


# PATCH /api/feedback/:id/resolve
# - Requires: JWT auth
# - Update is_resolved to True
# - Set resolved_at timestamp
# - Return: updated feedback
@feedback_bp.route("/<int:feedback_id>/resolve", methods=["PATCH"])
@jwt_required()
def resolve_feedback(feedback_id):
    """Mark feedback as resolved"""
    try:
        current_user_id = get_jwt_identity()

        feedback = Feedback.query.get_or_404(feedback_id)

        # Only feedback author or freelancer can resolve
        # TODO: Add role check when Ryan creates decorator

        feedback.resolve()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Feedback marked as resolved",
                    "feedback": feedback.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error resolving feedback: {str(e)}")
        return jsonify({"success": False, "error": "Failed to resolve feedback"}), 500


@feedback_bp.route("/<int:feedback_id>/unresolve", methods=["PATCH"])
@jwt_required()
def unresolve_feedback(feedback_id):
    """Mark feedback as unresolved"""
    try:
        current_user_id = get_jwt_identity()

        feedback = Feedback.query.get_or_404(feedback_id)

        feedback.unresolve()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Feedback marked as unresolved",
                    "feedback": feedback.to_dict(),
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error unresolving feedback: {str(e)}")
        return jsonify({"success": False, "error": "Failed to unresolve feedback"}), 500


#
# DELETE /api/feedback/:id
# - Requires: JWT auth (feedback author or admin)
# - Delete feedback (or soft delete)
# - Return: success message
@feedback_bp.route("/<int:feedback_id>", methods=["DELETE"])
@jwt_required()
def delete_feedback(feedback_id):
    """Delete feedback (author or admin only)"""
    try:
        current_user_id = get_jwt_identity()

        feedback = Feedback.query.get_or_404(feedback_id)

        # Check ownership
        if feedback.user_id != current_user_id:
            # TODO: Add admin check when Ryan creates decorator
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        db.session.delete(feedback)
        db.session.commit()

        return jsonify({"success": True, "message": "Feedback deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting feedback: {str(e)}")
        return jsonify({"success": False, "error": "Failed to delete feedback"}), 500


@feedback_bp.route("/stats/<int:deliverable_id>", methods=["GET"])
@jwt_required()
def get_feedback_stats(deliverable_id):
    """Get feedback statistics for a deliverable"""
    try:
        deliverable = Deliverable.query.get_or_404(deliverable_id)

        all_feedback = Feedback.query.filter_by(deliverable_id=deliverable_id).all()

        stats = {
            "total_feedback": len(all_feedback),
            "unresolved_count": sum(1 for f in all_feedback if not f.is_resolved),
            "resolved_count": sum(1 for f in all_feedback if f.is_resolved),
            "by_type": {
                "comment": sum(1 for f in all_feedback if f.feedback_type == "comment"),
                "revision": sum(1 for f in all_feedback if f.feedback_type == "revision"),
                "approval": sum(1 for f in all_feedback if f.feedback_type == "approval"),
            },
            "by_priority": {
                "low": sum(1 for f in all_feedback if f.priority == "low"),
                "medium": sum(1 for f in all_feedback if f.priority == "medium"),
                "high": sum(1 for f in all_feedback if f.priority == "high"),
            },
        }

        return jsonify({"success": True, "stats": stats}), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching feedback stats: {str(e)}")
        return jsonify({"success": False, "error": "Failed to fetch stats"}), 500
