"""
Portfolio Service - Handles automatic portfolio creation from completed projects
Owner: Caleb (Portfolio automation)
Integrated with: Monica's Project model, Ryan's User model, Cindy's Deliverable model
"""
from app.extensions import db
from app.models.portfolio_item import PortfolioItem
from app.models.project import Project
from app.models.user import User
from app.models.freelancer_profile import FreelancerProfile
from datetime import datetime


class PortfolioService:
    """Service for managing portfolio automation"""
    
    @staticmethod
    def create_portfolio_from_project(project_id, freelancer_id):
        """
        Automatically creates a portfolio item from a completed project.
        
        Args:
            project_id: ID of the completed project
            freelancer_id: ID of the freelancer (User ID)
            
        Returns:
            PortfolioItem instance or None if creation fails
        """
        try:
            # Check if portfolio item already exists
            existing_item = PortfolioItem.query.filter_by(
                project_id=project_id
            ).first()
            
            if existing_item:
                print(f"Portfolio item already exists for project {project_id}")
                return existing_item
            
            # Get project details
            project = Project.query.get(project_id)
            if not project:
                print(f"Project {project_id} not found")
                return None
            
            # Verify the freelancer owns this project
            if project.freelancer_id != freelancer_id:
                print(f"Freelancer {freelancer_id} does not own project {project_id}")
                return None
            
            # Skip sensitive projects
            if project.is_sensitive:
                print(f"Skipping sensitive project {project_id}")
                return None
            
            # Extract tags from project
            tags = PortfolioService._extract_tags_from_project(project)
            
            # Get cover image from deliverables
            cover_image = PortfolioService._get_project_image(project)
            
            # Get the highest display_order for this freelancer
            max_order = db.session.query(
                db.func.max(PortfolioItem.display_order)
            ).filter_by(freelancer_id=freelancer_id).scalar() or 0
            
            # Create portfolio item
            portfolio_item = PortfolioItem(
                freelancer_id=freelancer_id,
                project_id=project_id,
                title=project.title,
                description=project.description,
                cover_image_url=cover_image,
                project_url=f"/projects/{project_id}",
                tags=tags,
                display_order=max_order + 1,
                is_featured=False,
                is_visible=True,  # Auto-visible, freelancer can change later
                created_at=datetime.utcnow()
            )
            
            db.session.add(portfolio_item)
            db.session.commit()
            
            print(f"✅ Portfolio item created successfully for project: {project.title}")
            return portfolio_item
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating portfolio item: {str(e)}")
            return None
    
    @staticmethod
    def _extract_tags_from_project(project):
        """
        Extracts relevant tags from project based on required_skills relationship.
        """
        tags = []
        
        # Extract from project_type
        if project.project_type:
            tags.append(project.project_type)
        
        # Extract from required_skills relationship (via ProjectSkill)
        if project.required_skills:
            for project_skill in project.required_skills:
                if project_skill.skill and hasattr(project_skill.skill, 'name'):
                    tags.append(project_skill.skill.name)
        
        # Remove duplicates and limit to 8 tags
        tags = list(set(tags))[:8]
        
        return tags if tags else None
    
    @staticmethod
    def _get_project_image(project):
        """
        Gets the cover image from approved deliverables.
        Prioritizes image and video file types.
        """
        if not project.deliverables:
            return None
        
        # First, try to find an approved image deliverable
        for deliverable in project.deliverables:
            if deliverable.status == 'approved' and deliverable.file_type == 'image':
                return deliverable.thumbnail_url or deliverable.file_url
        
        # Second, try to find an approved video with thumbnail
        for deliverable in project.deliverables:
            if deliverable.status == 'approved' and deliverable.file_type == 'video':
                if deliverable.thumbnail_url:
                    return deliverable.thumbnail_url
        
        # Third, any approved deliverable with thumbnail
        for deliverable in project.deliverables:
            if deliverable.status == 'approved' and deliverable.thumbnail_url:
                return deliverable.thumbnail_url
        
        # Last resort: first approved deliverable file_url
        for deliverable in project.deliverables:
            if deliverable.status == 'approved':
                return deliverable.file_url
        
        return None
    
    @staticmethod
    def update_portfolio_from_project(project_id):
        """
        Updates an existing portfolio item when project details change.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Updated PortfolioItem or None
        """
        try:
            portfolio_item = PortfolioItem.query.filter_by(
                project_id=project_id
            ).first()
            
            if not portfolio_item:
                print(f"No portfolio item found for project {project_id}")
                return None
            
            project = Project.query.get(project_id)
            if not project:
                return None
            
            # Update fields
            portfolio_item.title = project.title
            portfolio_item.description = project.description
            portfolio_item.cover_image_url = PortfolioService._get_project_image(project)
            portfolio_item.tags = PortfolioService._extract_tags_from_project(project)
            
            db.session.commit()
            
            print(f"✅ Portfolio item updated for project {project_id}")
            return portfolio_item
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating portfolio item: {str(e)}")
            return None
    
    @staticmethod
    def get_freelancer_portfolio_with_profile(freelancer_id, include_hidden=False):
        """
        Gets complete portfolio with freelancer profile details.
        
        Args:
            freelancer_id: ID of the freelancer (User ID)
            include_hidden: Whether to include hidden items (for owner view)
            
        Returns:
            Dictionary with freelancer profile and portfolio items
        """
        try:
            # Get user
            user = User.query.get(freelancer_id)
            if not user or user.role != 'freelancer':
                return None
            
            # Get freelancer profile
            freelancer_profile = FreelancerProfile.query.filter_by(
                user_id=freelancer_id
            ).first()
            
            if not freelancer_profile:
                return None
            
            # Get portfolio items
            query = PortfolioItem.query.filter_by(freelancer_id=freelancer_id)
            
            if not include_hidden:
                query = query.filter_by(is_visible=True)
            
            portfolio_items = query.order_by(
                PortfolioItem.is_featured.desc(),
                PortfolioItem.display_order.asc(),
                PortfolioItem.created_at.desc()
            ).all()
            
            # Calculate stats
            total_projects = Project.query.filter_by(
                freelancer_id=freelancer_id,
                status='completed'
            ).count()
            
            # Get average rating from reviews
            from app.models.review import Review
            avg_rating = db.session.query(
                db.func.avg(Review.rating)
            ).filter_by(freelancer_id=freelancer_id).scalar()
            
            avg_rating = round(float(avg_rating), 1) if avg_rating else 0.0
            
            # Get total reviews count
            total_reviews = Review.query.filter_by(
                freelancer_id=freelancer_id
            ).count()
            
            return {
                "freelancer": {
                    "id": user.id,
                    "name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "avatar_url": user.avatar_url,
                    "bio": user.bio or freelancer_profile.bio,
                    "professional_title": "Freelancer",  # Can be customized
                    "location": "Remote",  # Add to User model if needed
                    "skills": [skill.name for skill in freelancer_profile.skills],
                    "hourly_rate": freelancer_profile.hourly_rate,
                    "years_experience": freelancer_profile.years_experience,
                    "rating": avg_rating,
                    "total_projects": total_projects,
                    "total_reviews": total_reviews,
                    "portfolio_url": freelancer_profile.portfolio_url,
                    "member_since": user.created_at.isoformat() if user.created_at else None,
                    "availability": "available" if freelancer_profile.open_to_work else "busy",
                },
                "portfolio_items": [item.to_dict() for item in portfolio_items],
                "stats": {
                    "total_portfolio_items": len(portfolio_items),
                    "featured_items": sum(1 for item in portfolio_items if item.is_featured),
                    "visible_items": sum(1 for item in portfolio_items if item.is_visible),
                }
            }
            
        except Exception as e:
            print(f"❌ Error fetching portfolio with profile: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def bulk_create_portfolios_for_completed_projects():
        """
        One-time migration: Creates portfolio items for all existing completed projects.
        Run this once to populate portfolios from historical data.
        """
        try:
            # Get all completed, non-sensitive projects that don't have portfolio items
            completed_projects = db.session.query(Project).filter(
                Project.status == 'completed',
                Project.is_sensitive == False,
                Project.freelancer_id.isnot(None),
                ~Project.id.in_(
                    db.session.query(PortfolioItem.project_id)
                )
            ).all()
            
            created_count = 0
            skipped_count = 0
            
            for project in completed_projects:
                result = PortfolioService.create_portfolio_from_project(
                    project.id,
                    project.freelancer_id
                )
                if result:
                    created_count += 1
                else:
                    skipped_count += 1
            
            print(f"✅ Bulk creation complete: {created_count} portfolio items created, {skipped_count} skipped")
            return created_count
            
        except Exception as e:
            print(f"❌ Error in bulk portfolio creation: {str(e)}")
            return 0