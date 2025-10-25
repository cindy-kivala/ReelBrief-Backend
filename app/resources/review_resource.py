"""
Review Resource - Freelancer Reviews & Ratings
Owner: Caleb
Description: Submit and view reviews for completed projects.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.notification import Notification
from app.models.project import Project
from app.models.review import Review
from app.models.user import User

review_bp = Blueprint("reviews", __name__)


@review_bp.route("/", methods=["POST"])
@jwt_required()
def create_review():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = [
        "project_id",
        "rating",
        "communication_rating",
        "quality_rating",
        "timeliness_rating",
        "review_text",
        "is_public",
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    project = Project.query.get(data["project_id"])
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if project.client_id != current_user_id:
        return jsonify({"error": "Unauthorized: You are not the client of this project"}), 403

    if project.status.lower() != "completed":
        return jsonify({"error": "Cannot review an incomplete project"}), 400

    existing_review = Review.query.filter_by(project_id=project.id).first()
    if existing_review:
        return jsonify({"error": "Review already submitted for this project"}), 400

    review = Review(
        project_id=project.id,
        client_id=current_user_id,
        freelancer_id=project.freelancer_id,
        rating=data["rating"],
        communication_rating=data["communication_rating"],
        quality_rating=data["quality_rating"],
        timeliness_rating=data["timeliness_rating"],
        review_text=data["review_text"],
        is_public=data["is_public"],
    )

    db.session.add(review)
    db.session.commit()

    # Create notification for freelancer
    freelancer = User.query.get(project.freelancer_id)
    if freelancer:
        notification = Notification(
            user_id=freelancer.id,
            message=f"You received a new review from {freelancer.first_name or 'a client'}.",
            is_read=False,
        )
        db.session.add(notification)
        db.session.commit()

    return jsonify({"message": "Review created successfully", "review": review.to_dict()}), 201


@review_bp.route("/users/<int:user_id>/reviews", methods=["GET"])
@jwt_required(optional=True)
def get_user_reviews(user_id):
    current_user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Review.query.filter_by(freelancer_id=user_id)

    # Show only public reviews unless user owns the profile
    if current_user_id != user_id:
        query = query.filter_by(is_public=True)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    reviews = [review.to_dict() for review in pagination.items]

    return (
        jsonify(
            {
                "reviews": reviews,
                "total": pagination.total,
                "page": page,
                "pages": pagination.pages,
            }
        ),
        200,
    )


@review_bp.route("/projects/<int:project_id>/reviews", methods=["GET"])
@jwt_required()
def get_project_review(project_id):
    review = Review.query.filter_by(project_id=project_id).first()
    if not review:
        return jsonify({"error": "No review found for this project"}), 404

    return jsonify({"review": review.to_dict()}), 200


@review_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_review(id):
    current_user_id = get_jwt_identity()
    review = Review.query.get(id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    if review.client_id != current_user_id:
        return jsonify({"error": "Unauthorized: You can only edit your own reviews"}), 403

    data = request.get_json()
    editable_fields = [
        "rating",
        "communication_rating",
        "quality_rating",
        "timeliness_rating",
        "review_text",
        "is_public",
    ]

    for field in editable_fields:
        if field in data:
            setattr(review, field, data[field])

    db.session.commit()
    return jsonify({"message": "Review updated successfully", "review": review.to_dict()}), 200


@review_bp.route("/freelancers/<int:freelancer_id>/rating-summary", methods=["GET"])
def get_freelancer_rating_summary(freelancer_id):
    reviews = Review.query.filter_by(freelancer_id=freelancer_id, is_public=True).all()
    if not reviews:
        return jsonify({"message": "No reviews found", "average_rating": 0}), 200

    total_reviews = len(reviews)
    avg_rating = sum([r.rating for r in reviews]) / total_reviews
    avg_comm = sum([r.communication_rating for r in reviews]) / total_reviews
    avg_quality = sum([r.quality_rating for r in reviews]) / total_reviews
    avg_timeliness = sum([r.timeliness_rating for r in reviews]) / total_reviews

    return (
        jsonify(
            {
                "freelancer_id": freelancer_id,
                "total_reviews": total_reviews,
                "average_rating": round(avg_rating, 2),
                "communication_rating": round(avg_comm, 2),
                "quality_rating": round(avg_quality, 2),
                "timeliness_rating": round(avg_timeliness, 2),
            }
        ),
        200,
    )
