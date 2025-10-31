from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.feedback import Feedback
from app.models.deliverable import Deliverable

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/', methods=['POST'])
@jwt_required()
def submit_feedback():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        print("Received feedback data:", data)
        
        # Validate required fields based on your Feedback model
        required_fields = ['deliverable_id', 'feedback_type', 'content']
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'error': 'Validation failed',
                'message': f'Missing required fields: {", ".join(missing_fields)}',
                'details': {'missing_fields': missing_fields},
                'success': False
            }), 400
        
        # Validate feedback_type (matches your model)
        valid_feedback_types = ['comment', 'revision', 'approval']
        if data['feedback_type'] not in valid_feedback_types:
            return jsonify({
                'error': 'Validation failed',
                'message': f'Invalid feedback_type. Must be one of: {", ".join(valid_feedback_types)}',
                'success': False
            }), 400
        
        # Validate priority if provided (matches your model)
        if 'priority' in data and data['priority']:
            valid_priorities = ['low', 'medium', 'high']
            if data['priority'] not in valid_priorities:
                return jsonify({
                    'error': 'Validation failed',
                    'message': f'Invalid priority. Must be one of: {", ".join(valid_priorities)}',
                    'success': False
                }), 400
        
        # Check if deliverable exists
        deliverable = Deliverable.query.get(data['deliverable_id'])
        if not deliverable:
            return jsonify({
                'error': 'Deliverable not found',
                'message': f'Deliverable with ID {data["deliverable_id"]} does not exist',
                'success': False
            }), 404
        
        # Check if parent feedback exists if provided
        parent_feedback_id = data.get('parent_feedback_id')
        if parent_feedback_id:
            parent_feedback = Feedback.query.get(parent_feedback_id)
            if not parent_feedback:
                return jsonify({
                    'error': 'Parent feedback not found',
                    'message': f'Parent feedback with ID {parent_feedback_id} does not exist',
                    'success': False
                }), 404
        
        # Create feedback (matches your model structure)
        feedback = Feedback(
            deliverable_id=data['deliverable_id'],
            user_id=current_user['id'],
            parent_feedback_id=parent_feedback_id,
            feedback_type=data['feedback_type'],
            content=data['content'],
            priority=data.get('priority'),
            is_resolved=False
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback': feedback.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting feedback: {str(e)}")
        return jsonify({
            'error': 'Failed to submit feedback',
            'message': str(e),
            'success': False
        }), 500

@feedback_bp.route('/deliverable/<int:deliverable_id>', methods=['GET'])
@jwt_required()
def get_deliverable_feedback(deliverable_id):
    try:
        # Check if deliverable exists
        deliverable = Deliverable.query.get(deliverable_id)
        if not deliverable:
            return jsonify({
                'error': 'Deliverable not found',
                'success': False
            }), 404
        
        # Get feedback for this deliverable using your model's static method
        feedback_list = Feedback.get_feedback_for_deliverable(deliverable_id)
        
        return jsonify({
            'success': True,
            'deliverable_id': deliverable_id,
            'feedback': [feedback.to_dict() for feedback in feedback_list],
            'unresolved_count': Feedback.get_unresolved_count(deliverable_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch feedback',
            'message': str(e),
            'success': False
        }), 500

@feedback_bp.route('/<int:feedback_id>/resolve', methods=['PUT'])
@jwt_required()
def resolve_feedback(feedback_id):
    try:
        current_user = get_jwt_identity()
        feedback = Feedback.query.get(feedback_id)
        
        if not feedback:
            return jsonify({
                'error': 'Feedback not found',
                'success': False
            }), 404
        
        # Use your model's resolve method
        feedback.resolve()
        
        return jsonify({
            'success': True,
            'message': 'Feedback marked as resolved',
            'feedback': feedback.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to resolve feedback',
            'message': str(e),
            'success': False
        }), 500

@feedback_bp.route('/<int:feedback_id>/unresolve', methods=['PUT'])
@jwt_required()
def unresolve_feedback(feedback_id):
    try:
        feedback = Feedback.query.get(feedback_id)
        
        if not feedback:
            return jsonify({
                'error': 'Feedback not found',
                'success': False
            }), 404
        
        # Use your model's unresolve method
        feedback.unresolve()
        
        return jsonify({
            'success': True,
            'message': 'Feedback marked as unresolved',
            'feedback': feedback.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to unresolve feedback',
            'message': str(e),
            'success': False
        }), 500