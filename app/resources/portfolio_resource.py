"""
Portfolio API Routes
Owner: Caleb (Portfolio display and management)
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.portfolio_service import PortfolioService
from app.models.portfolio_item import PortfolioItem
from app.extensions import db

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')


@portfolio_bp.route('/freelancer/<int:freelancer_id>', methods=['GET'])
def get_public_portfolio(freelancer_id):
    """
    Public endpoint - Get freelancer's portfolio with profile (only visible items)
    No authentication required - public portfolio view
    """
    try:
        data = PortfolioService.get_freelancer_portfolio_with_profile(
            freelancer_id,
            include_hidden=False
        )
        
        if not data:
            return jsonify({"error": "Freelancer portfolio not found"}), 404
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_portfolio():
    """
    Private endpoint - Get current user's portfolio (includes hidden items)
    For freelancers to manage their own portfolio
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user if isinstance(current_user, int) else current_user.get('id')
        
        data = PortfolioService.get_freelancer_portfolio_with_profile(
            user_id,
            include_hidden=True
        )
        
        if not data:
            return jsonify({"error": "Portfolio not found"}), 404
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route('/item/<int:item_id>', methods=['PATCH'])
@jwt_required()
def update_portfolio_item(item_id):
    """
    Update portfolio item (visibility, featured, display_order, title, description, tags)
    Only the owner freelancer can update their portfolio items
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user if isinstance(current_user, int) else current_user.get('id')
        
        portfolio_item = PortfolioItem.query.get(item_id)
        
        if not portfolio_item:
            return jsonify({"error": "Portfolio item not found"}), 404
        
        # Verify ownership
        if portfolio_item.freelancer_id != user_id:
            return jsonify({"error": "Unauthorized - you can only edit your own portfolio items"}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'is_visible' in data:
            portfolio_item.is_visible = bool(data['is_visible'])
        
        if 'is_featured' in data:
            portfolio_item.is_featured = bool(data['is_featured'])
        
        if 'display_order' in data:
            portfolio_item.display_order = int(data['display_order'])
        
        if 'title' in data:
            portfolio_item.title = data['title']
        
        if 'description' in data:
            portfolio_item.description = data['description']
        
        if 'tags' in data:
            portfolio_item.tags = data['tags']
        
        db.session.commit()
        
        return jsonify({
            "message": "Portfolio item updated successfully",
            "item": portfolio_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route('/item/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio_item(item_id):
    """
    Delete a portfolio item
    Only the owner freelancer can delete their portfolio items
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user if isinstance(current_user, int) else current_user.get('id')
        
        portfolio_item = PortfolioItem.query.get(item_id)
        
        if not portfolio_item:
            return jsonify({"error": "Portfolio item not found"}), 404
        
        # Verify ownership
        if portfolio_item.freelancer_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        db.session.delete(portfolio_item)
        db.session.commit()
        
        return jsonify({"message": "Portfolio item deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route('/reorder', methods=['POST'])
@jwt_required()
def reorder_portfolio_items():
    """
    Reorder portfolio items
    Expects: {"items": [{"id": 1, "display_order": 0}, {"id": 2, "display_order": 1}, ...]}
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user if isinstance(current_user, int) else current_user.get('id')
        
        data = request.get_json()
        
        if 'items' not in data:
            return jsonify({"error": "Missing 'items' field"}), 400
        
        updated_count = 0
        
        for item_data in data['items']:
            item_id = item_data.get('id')
            new_order = item_data.get('display_order')
            
            if item_id is None or new_order is None:
                continue
            
            portfolio_item = PortfolioItem.query.get(item_id)
            
            # Skip if not found or not owned by user
            if not portfolio_item or portfolio_item.freelancer_id != user_id:
                continue
            
            portfolio_item.display_order = new_order
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": "Portfolio items reordered successfully",
            "updated_count": updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@portfolio_bp.route('/project/<int:project_id>/create', methods=['POST'])
@jwt_required()
def manually_create_portfolio(project_id):
    """
    Manually create portfolio item for a project
    Useful for freelancers who want to add a project manually
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user if isinstance(current_user, int) else current_user.get('id')
        
        from app.models.project import Project
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({"error": "Project not found"}), 404
        
        # Check if user is the freelancer
        if project.freelancer_id != user_id:
            return jsonify({"error": "Unauthorized - you can only create portfolio items for your own projects"}), 403
        
        portfolio_item = PortfolioService.create_portfolio_from_project(
            project_id=project.id,
            freelancer_id=project.freelancer_id
        )
        
        if not portfolio_item:
            return jsonify({"error": "Failed to create portfolio item"}), 500
        
        return jsonify({
            "message": "Portfolio item created successfully",
            "portfolio_item": portfolio_item.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500