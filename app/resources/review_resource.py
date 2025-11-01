"""
Review Resource
Owner: Caleb  
Description: Handles project reviews and ratings between clients and freelancers
"""

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.review import Review
from app.models.project import Project
from app.models.user import User

review_bp = Blueprint('reviews', __name__)

@review_bp.route('/', methods=['POST'])
@jwt_required()
def create_review():
    """
    Create a new review for a completed project
    ---
    tags:
      - Reviews
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - project_id
            - rating
          properties:
            project_id:
              type: integer
              description: ID of the project being reviewed
            rating:
              type: integer
              minimum: 1
              maximum: 5
              description: Overall rating (1-5 stars)
            communication_rating:
              type: integer
              minimum: 1
              maximum: 5
              description: Communication rating (optional)
            quality_rating:
              type: integer
              minimum: 1
              maximum: 5
              description: Quality of work rating (optional)
            timeliness_rating:
              type: integer
              minimum: 1
              maximum: 5
              description: Timeliness rating (optional)
            review_text:
              type: string
              description: Detailed review comments
            is_public:
              type: boolean
              description: Whether the review is publicly visible
    responses:
      201:
        description: Review created successfully
      400:
        description: Missing required fields or invalid data
      403:
        description: User not authorized to review this project
      404:
        description: Project not found
      409:
        description: Review already exists for this project
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        print(f"Creating review - User ID: {current_user_id}, Data: {data}")
        
        # Validate required fields
        if not data:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'No data provided'
            }), 400
        
        required_fields = ['project_id', 'rating']
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'message': f'Missing fields: {", ".join(missing_fields)}',
                'missing_fields': missing_fields
            }), 400
        
        # Validate rating (1-5)
        rating = data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({
                'error': 'Invalid rating',
                'message': 'Rating must be an integer between 1 and 5'
            }), 400
        
        # Validate optional ratings if provided
        optional_ratings = ['communication_rating', 'quality_rating', 'timeliness_rating']
        for rating_field in optional_ratings:
            if rating_field in data and data[rating_field] is not None:
                if not isinstance(data[rating_field], int) or data[rating_field] < 1 or data[rating_field] > 5:
                    return jsonify({
                        'error': 'Invalid rating',
                        'message': f'{rating_field} must be an integer between 1 and 5'
                    }), 400
        
        # Check if project exists
        project = Project.query.get(data['project_id'])
        if not project:
            return jsonify({
                'error': 'Project not found',
                'message': f'Project with ID {data["project_id"]} does not exist'
            }), 404
        
        # Check if user is the client for this project
        if current_user_id != project.client_id:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Only the project client can submit reviews'
            }), 403
        
        # Check if project is completed
        if project.status != 'completed':
            return jsonify({
                'error': 'Project not completed',
                'message': 'Reviews can only be submitted for completed projects'
            }), 400
        
        # Check if review already exists for this project
        existing_review = Review.query.filter_by(project_id=data['project_id']).first()
        if existing_review:
            return jsonify({
                'error': 'Review already exists',
                'message': 'A review already exists for this project'
            }), 409
        
        # Create review
        review = Review(
            project_id=data['project_id'],
            client_id=current_user_id,
            freelancer_id=project.freelancer_id,
            rating=data['rating'],
            communication_rating=data.get('communication_rating'),
            quality_rating=data.get('quality_rating'),
            timeliness_rating=data.get('timeliness_rating'),
            review_text=data.get('review_text', ''),
            is_public=data.get('is_public', True)
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Review submitted successfully',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating review: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to create review',
            'message': str(e)
        }), 500

@review_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_review(project_id):
    """
    Get review for a specific project
    ---
    tags:
      - Reviews
    parameters:
      - in: path
        name: project_id
        required: true
        type: integer
        description: ID of the project
    responses:
      200:
        description: Review retrieved successfully
      404:
        description: Project or review not found
    """
    try:
        # Check if project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({
                'error': 'Project not found',
                'message': f'Project with ID {project_id} does not exist'
            }), 404
        
        review = Review.query.filter_by(project_id=project_id).first()
        
        if not review:
            return jsonify({
                'success': True,
                'review': None,
                'message': 'No review found for this project'
            }), 200
        
        return jsonify({
            'success': True,
            'review': review.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch review',
            'message': str(e)
        }), 500

@review_bp.route('/freelancer/<int:freelancer_id>', methods=['GET'])
def get_freelancer_reviews(freelancer_id):
    """
    Get all public reviews for a freelancer
    ---
    tags:
      - Reviews
    parameters:
      - in: path
        name: freelancer_id
        required: true
        type: integer
        description: ID of the freelancer
    responses:
      200:
        description: Reviews retrieved successfully
      404:
        description: Freelancer not found
    """
    try:
        # Check if freelancer exists
        freelancer = User.query.get(freelancer_id)
        if not freelancer or freelancer.role != 'freelancer':
            return jsonify({
                'error': 'Freelancer not found',
                'message': f'Freelancer with ID {freelancer_id} does not exist'
            }), 404
        
        # Get public reviews for freelancer
        reviews = Review.query.filter_by(freelancer_id=freelancer_id, is_public=True).all()
        
        # Calculate statistics
        total_reviews = len(reviews)
        if total_reviews > 0:
            avg_rating = sum(review.average_rating() for review in reviews) / total_reviews
            avg_rating = round(avg_rating, 2)
        else:
            avg_rating = 0
        
        return jsonify({
            'success': True,
            'freelancer_id': freelancer_id,
            'freelancer_name': f"{freelancer.first_name} {freelancer.last_name}",
            'reviews': [review.to_dict() for review in reviews],
            'statistics': {
                'total_reviews': total_reviews,
                'average_rating': avg_rating,
                'average_communication': calculate_average_subrating(reviews, 'communication_rating'),
                'average_quality': calculate_average_subrating(reviews, 'quality_rating'),
                'average_timeliness': calculate_average_subrating(reviews, 'timeliness_rating')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch reviews',
            'message': str(e)
        }), 500

@review_bp.route('/user/my-reviews', methods=['GET'])
@jwt_required()
def get_my_reviews():
    """
    Get all reviews for the current user (both as client and freelancer)
    ---
    tags:
      - Reviews
    responses:
      200:
        description: User reviews retrieved successfully
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get reviews where user is either client or freelancer
        reviews_as_client = Review.query.filter_by(client_id=current_user_id).all()
        reviews_as_freelancer = Review.query.filter_by(freelancer_id=current_user_id).all()
        
        # Calculate statistics for freelancer reviews
        public_freelancer_reviews = [r for r in reviews_as_freelancer if r.is_public]
        total_public_reviews = len(public_freelancer_reviews)
        
        if total_public_reviews > 0:
            avg_freelancer_rating = sum(review.average_rating() for review in public_freelancer_reviews) / total_public_reviews
            avg_freelancer_rating = round(avg_freelancer_rating, 2)
        else:
            avg_freelancer_rating = 0
        
        return jsonify({
            'success': True,
            'reviews_as_client': [review.to_dict() for review in reviews_as_client],
            'reviews_as_freelancer': [review.to_dict() for review in reviews_as_freelancer],
            'statistics': {
                'total_reviews_given': len(reviews_as_client),
                'total_reviews_received': len(reviews_as_freelancer),
                'average_rating_received': avg_freelancer_rating,
                'public_reviews_count': total_public_reviews
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_my_reviews: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to fetch user reviews',
            'message': str(e)
        }), 500

@review_bp.route('/<int:review_id>', methods=['GET'])
@jwt_required()
def get_review(review_id):
    """
    Get a specific review by ID
    ---
    tags:
      - Reviews
    parameters:
      - in: path
        name: review_id
        required: true
        type: integer
        description: ID of the review
    responses:
      200:
        description: Review retrieved successfully
      404:
        description: Review not found
    """
    try:
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({
                'error': 'Review not found',
                'message': f'Review with ID {review_id} does not exist'
            }), 404
        
        return jsonify({
            'success': True,
            'review': review.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch review',
            'message': str(e)
        }), 500

@review_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """
    Update a review (only by the original author)
    ---
    tags:
      - Reviews
    parameters:
      - in: path
        name: review_id
        required: true
        type: integer
        description: ID of the review to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            rating:
              type: integer
              minimum: 1
              maximum: 5
            communication_rating:
              type: integer
              minimum: 1
              maximum: 5
            quality_rating:
              type: integer
              minimum: 1
              maximum: 5
            timeliness_rating:
              type: integer
              minimum: 1
              maximum: 5
            review_text:
              type: string
            is_public:
              type: boolean
    responses:
      200:
        description: Review updated successfully
      403:
        description: User not authorized to update this review
      404:
        description: Review not found
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        review = Review.query.get(review_id)
        if not review:
            return jsonify({
                'error': 'Review not found',
                'message': f'Review with ID {review_id} does not exist'
            }), 404
        
        # Check if user is the author of the review
        if review.client_id != current_user_id:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Only the review author can update this review'
            }), 403
        
        # Update fields if provided
        updatable_fields = [
            'rating', 'communication_rating', 'quality_rating', 
            'timeliness_rating', 'review_text', 'is_public'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(review, field, data[field])
        
        # Validate ratings if updated
        rating_fields = ['rating', 'communication_rating', 'quality_rating', 'timeliness_rating']
        for field in rating_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], int) or data[field] < 1 or data[field] > 5:
                    return jsonify({
                        'error': 'Invalid rating',
                        'message': f'{field} must be an integer between 1 and 5'
                    }), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Review updated successfully',
            'review': review.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update review',
            'message': str(e)
        }), 500

@review_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """
    Delete a review (only by the original author or admin)
    ---
    tags:
      - Reviews
    parameters:
      - in: path
        name: review_id
        required: true
        type: integer
        description: ID of the review to delete
    responses:
      200:
        description: Review deleted successfully
      403:
        description: User not authorized to delete this review
      404:
        description: Review not found
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is admin (you might need to import and check user role)
        from app.models.user import User
        current_user = User.query.get(current_user_id)
        
        review = Review.query.get(review_id)
        if not review:
            return jsonify({
                'error': 'Review not found',
                'message': f'Review with ID {review_id} does not exist'
            }), 404
        
        # Check if user is the author or an admin
        if review.client_id != current_user_id and (not current_user or current_user.role != 'admin'):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Only the review author or admin can delete this review'
            }), 403
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Review deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete review',
            'message': str(e)
        }), 500

@review_bp.route('/stats/freelancer/<int:freelancer_id>', methods=['GET'])
def get_freelancer_review_stats(freelancer_id):
    """
    Get review statistics for a freelancer
    ---
    tags:
      - Reviews
    parameters:
      - in: path
        name: freelancer_id
        required: true
        type: integer
        description: ID of the freelancer
    responses:
      200:
        description: Statistics retrieved successfully
      404:
        description: Freelancer not found
    """
    try:
        # Check if freelancer exists
        freelancer = User.query.get(freelancer_id)
        if not freelancer or freelancer.role != 'freelancer':
            return jsonify({
                'error': 'Freelancer not found',
                'message': f'Freelancer with ID {freelancer_id} does not exist'
            }), 404
        
        # Get all public reviews for freelancer
        reviews = Review.query.filter_by(freelancer_id=freelancer_id, is_public=True).all()
        
        # Calculate detailed statistics
        total_reviews = len(reviews)
        
        if total_reviews == 0:
            return jsonify({
                'success': True,
                'freelancer_id': freelancer_id,
                'freelancer_name': f"{freelancer.first_name} {freelancer.last_name}",
                'statistics': {
                    'total_reviews': 0,
                    'average_rating': 0,
                    'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                    'average_communication': 0,
                    'average_quality': 0,
                    'average_timeliness': 0
                }
            }), 200
        
        # Calculate averages
        avg_rating = sum(review.average_rating() for review in reviews) / total_reviews
        avg_rating = round(avg_rating, 2)
        
        # Calculate rating distribution
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating = round(review.average_rating())
            if 1 <= rating <= 5:
                rating_distribution[rating] += 1
        
        return jsonify({
            'success': True,
            'freelancer_id': freelancer_id,
            'freelancer_name': f"{freelancer.first_name} {freelancer.last_name}",
            'statistics': {
                'total_reviews': total_reviews,
                'average_rating': avg_rating,
                'rating_distribution': rating_distribution,
                'average_communication': calculate_average_subrating(reviews, 'communication_rating'),
                'average_quality': calculate_average_subrating(reviews, 'quality_rating'),
                'average_timeliness': calculate_average_subrating(reviews, 'timeliness_rating')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch review statistics',
            'message': str(e)
        }), 500

def calculate_average_subrating(reviews, rating_field):
    """Calculate average for a specific sub-rating"""
    ratings = [getattr(review, rating_field) for review in reviews if getattr(review, rating_field) is not None]
    if not ratings:
        return 0
    return round(sum(ratings) / len(ratings), 2)