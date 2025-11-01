"""
Feedback Resource - Structured Revision Requests
Owner: Cindy
Description: Submit and manage feedback on deliverables
"""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import Schema, fields, validate, ValidationError

from app.extensions import db
from app.models.deliverable import Deliverable
from app.models.user import User

# FIXED: Changed url_prefix - removed trailing space
feedback_bp = Blueprint("feedback", __name__, url_prefix='/api/feedback')

# Schemas for validation
class FeedbackSchema(Schema):
    deliverable_id = fields.Int(required=True)
    feedback_type = fields.Str(
        required=True, 
        validate=validate.OneOf(['comment', 'revision', 'approval'])
    )
    content = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']), missing='medium')
    parent_feedback_id = fields.Int(allow_none=True)

class FeedbackUpdateSchema(Schema):
    content = fields.Str(validate=validate.Length(min=1, max=5000))
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']))

# Helper functions
def handle_validation_error(error):
    """Handle marshmallow validation errors consistently"""
    return jsonify({
        'success': False,
        'error': 'Validation failed',
        'details': error.messages
    }), 400

def handle_db_error(error):
    """Handle database errors consistently"""
    db.session.rollback()
    current_app.logger.error(f"Database error: {str(error)}")
    return jsonify({'success': False, 'error': str(error)}), 500

def check_feedback_ownership(feedback, user_id):
    """Check if user owns the feedback"""
    return feedback.user_id == user_id

# ROUTES
@feedback_bp.route('/test', methods=['GET'])
def test_feedback():
    return jsonify({'success': True, 'message': 'Feedback endpoint works!'}), 200
# FIXED: GET /api/feedback/deliverable/<id> with better error handling
@feedback_bp.route('/deliverable/<int:deliverable_id>', methods=['GET'])
@jwt_required()
def get_deliverable_feedback(deliverable_id):
    """Get all feedback for a deliverable"""
    try:
        # Check if deliverable exists
        deliverable = Deliverable.query.get(deliverable_id)
        if not deliverable:
            return jsonify({
                'success': False,
                'error': f'Deliverable {deliverable_id} not found'
            }), 404
        
        # Get feedback with proper error handling
        try:
            include_resolved = request.args.get('include_resolved', 'true').lower() == 'true'
            
            # FIXED: Safe query with error handling
            query = Feedback.query.filter_by(deliverable_id=deliverable_id)
            
            if not include_resolved:
                query = query.filter_by(is_resolved=False)
            
            feedback_items = query.all()
            
            # Build response with author info
            feedback_list = []
            for f in feedback_items:
                feedback_dict = f.to_dict() if hasattr(f, 'to_dict') else {
                    'id': f.id,
                    'content': f.content,
                    'feedback_type': f.feedback_type,
                    'priority': f.priority,
                    'is_resolved': f.is_resolved,
                    'created_at': f.created_at.isoformat() if f.created_at else None
                }
                
                # Add author info
                if f.user_id:
                    author = User.query.get(f.user_id)
                    if author:
                        feedback_dict['author'] = {
                            'id': author.id,
                            'first_name': author.first_name,
                            'last_name': author.last_name,
                            'email': author.email
                        }
                
                feedback_list.append(feedback_dict)
            
            unresolved_count = sum(1 for f in feedback_items if not f.is_resolved)
            
            return jsonify({
                'success': True,
                'feedback': feedback_list,
                'total_count': len(feedback_items),
                'unresolved_count': unresolved_count
            }), 200
            
        except Exception as query_error:
            current_app.logger.error(f"Query error: {str(query_error)}")
            return jsonify({
                'success': False,
                'error': f'Database query failed: {str(query_error)}'
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Error fetching feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch feedback: {str(e)}'
        }), 500


# FIXED: POST /api/feedback - Submit new feedback
@feedback_bp.route('', methods=['POST'])
@jwt_required()
def create_feedback():
    """Submit feedback on a deliverable"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        current_app.logger.info(f"Creating feedback: {data}")
        
        # Validate input
        schema = FeedbackSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return handle_validation_error(err)
        
        # Verify deliverable exists
        deliverable = Deliverable.query.get(validated_data['deliverable_id'])
        if not deliverable:
            return jsonify({
                'success': False,
                'error': f"Deliverable {validated_data['deliverable_id']} not found"
            }), 404
        
        # Validate parent feedback if provided
        if validated_data.get('parent_feedback_id'):
            parent = Feedback.query.get(validated_data['parent_feedback_id'])
            if not parent or parent.deliverable_id != validated_data['deliverable_id']:
                return jsonify({
                    'success': False,
                    'error': 'Invalid parent feedback'
                }), 400
        
        # Create feedback entry
        feedback = Feedback(
            deliverable_id=validated_data['deliverable_id'],
            user_id=current_user_id,
            feedback_type=validated_data['feedback_type'],
            content=validated_data['content'].strip(),
            priority=validated_data.get('priority', 'medium'),
            parent_feedback_id=validated_data.get('parent_feedback_id')
        )

        db.session.add(feedback)
        db.session.commit()
        
        # Build response with author info
        author = User.query.get(current_user_id)
        feedback_dict = feedback.to_dict() if hasattr(feedback, 'to_dict') else {
            'id': feedback.id,
            'content': feedback.content,
            'feedback_type': feedback.feedback_type,
            'priority': feedback.priority,
            'is_resolved': feedback.is_resolved,
            'created_at': feedback.created_at.isoformat() if feedback.created_at else None
        }
        
        if author:
            feedback_dict['author'] = {
                'id': author.id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'email': author.email
            }
        
        current_app.logger.info(f"Feedback created successfully: {feedback.id}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback': feedback_dict
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"Error creating feedback: {str(e)}")
        return handle_db_error(e)



@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
@jwt_required()
def get_feedback(feedback_id):
    """Get specific feedback with replies"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        return jsonify({
            'success': True,
            'feedback': feedback.to_dict(include_replies=True) if hasattr(feedback, 'to_dict') else {
                'id': feedback.id,
                'content': feedback.content
            }
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching feedback: {str(e)}")
        return jsonify({"success": False, "error": "Feedback not found"}), 404


@feedback_bp.route('/<int:feedback_id>', methods=['PATCH'])
@jwt_required()
def update_feedback(feedback_id):
    """Update feedback content"""
    try:
        current_user_id = get_jwt_identity()

        feedback = Feedback.query.get_or_404(feedback_id)
        
        # Authorization check
        if not check_feedback_ownership(feedback, current_user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Validate input
        schema = FeedbackUpdateSchema()
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return handle_validation_error(err)
        
        # Update fields
        if 'content' in data:
            feedback.content = data['content'].strip()
        
        if 'priority' in data:
            feedback.priority = data['priority']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback updated successfully',
            'feedback': feedback.to_dict() if hasattr(feedback, 'to_dict') else {
                'id': feedback.id,
                'content': feedback.content
            }
        }), 200
    
    except Exception as e:
        return handle_db_error(e)


@feedback_bp.route('/<int:feedback_id>/resolve', methods=['PATCH'])
@jwt_required()
def resolve_feedback(feedback_id):
    """Mark feedback as resolved"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        if hasattr(feedback, 'resolve'):
            feedback.resolve()
        else:
            feedback.is_resolved = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback marked as resolved',
            'feedback': feedback.to_dict() if hasattr(feedback, 'to_dict') else {
                'id': feedback.id,
                'is_resolved': feedback.is_resolved
            }
        }), 200
    
    except Exception as e:
        return handle_db_error(e)


@feedback_bp.route("/<int:feedback_id>/unresolve", methods=["PATCH"])
@jwt_required()
def unresolve_feedback(feedback_id):
    """Mark feedback as unresolved"""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        
        if hasattr(feedback, 'unresolve'):
            feedback.unresolve()
        else:
            feedback.is_resolved = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback marked as unresolved',
            'feedback': feedback.to_dict() if hasattr(feedback, 'to_dict') else {
                'id': feedback.id,
                'is_resolved': feedback.is_resolved
            }
        }), 200
    
    except Exception as e:
        return handle_db_error(e)


@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
@jwt_required()
def delete_feedback(feedback_id):
    """Delete feedback"""
    try:
        current_user_id = get_jwt_identity()
        feedback = Feedback.query.get_or_404(feedback_id)
        
        # Authorization check
        if not check_feedback_ownership(feedback, current_user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Prevent deletion of feedback with replies
        if hasattr(feedback, 'replies') and feedback.replies and len(feedback.replies) > 0:
            return jsonify({
                'success': False,
                'error': 'Cannot delete feedback with replies'
            }), 400
        
        db.session.delete(feedback)
        db.session.commit()

        return jsonify({"success": True, "message": "Feedback deleted successfully"}), 200

    except Exception as e:
        return handle_db_error(e)


@feedback_bp.route("/stats/<int:deliverable_id>", methods=["GET"])
@jwt_required()
def get_feedback_stats(deliverable_id):
    """Get feedback statistics for a deliverable"""
    try:
        deliverable = Deliverable.query.get(deliverable_id)
        if not deliverable:
            return jsonify({'success': False, 'error': 'Deliverable not found'}), 404
        
        feedback_items = Feedback.query.filter_by(deliverable_id=deliverable_id).all()
        
        total = len(feedback_items)
        unresolved = sum(1 for f in feedback_items if not f.is_resolved)
        resolved = total - unresolved
        
        stats = {
            'total_feedback': total,
            'unresolved_count': unresolved,
            'resolved_count': resolved,
            'resolution_rate': round((resolved / total * 100), 2) if total else 0,
            'by_type': {},
            'by_priority': {}
        }
        
        # Count by type and priority
        for item in feedback_items:
            stats['by_type'][item.feedback_type] = stats['by_type'].get(item.feedback_type, 0) + 1
            stats['by_priority'][item.priority] = stats['by_priority'].get(item.priority, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching feedback stats: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch stats'}), 500
