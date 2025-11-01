"""
Project Service
Owner: Monica
Description: Manages project creation, updates, assignments, and matching freelancers.
"""

from datetime import datetime
from ..extensions import db
from ..models.project import Project
from ..models.freelancer_profile import FreelancerProfile
from ..models.skill import Skill


class ProjectService:
    """Handles all project-related operations."""

    #  Create new project
    @staticmethod
    def create_project(data, client_id=None):
        """Create a new project."""
        try:
            project = Project(
                title=data.get("title"),
                description=data.get("description"),
                budget=data.get("budget"),
                deadline=datetime.strptime(data.get("deadline"), "%Y-%m-%d"),
                is_sensitive=data.get("is_sensitive", False)
            )

            # attach skills if provided
            skill_ids = data.get("skill_ids", [])
            if skill_ids:
                skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
                project.skills = skills

            db.session.add(project)
            db.session.commit()
            return project
        except Exception as e:
            db.session.rollback()
            raise e

    # Update project details
    @staticmethod
    def update_project(project_id, data):
        """Update project details."""
        project = Project.query.get_or_404(project_id)

        for key, value in data.items():
            if key == "skill_ids":
                skills = Skill.query.filter(Skill.id.in_(value)).all()
                project.skills = skills
            elif hasattr(project, key):
                setattr(project, key, value)

        db.session.commit()
        return project

    # Assign freelancer to a project
    @staticmethod
    def assign_freelancer(project_id, freelancer_id):
        """Assign freelancer to a project."""
        project = Project.query.get_or_404(project_id)
        freelancer = FreelancerProfile.query.get_or_404(freelancer_id)

        if not freelancer.approved:
            raise ValueError("Freelancer not approved")
        if not freelancer.is_available:
            raise ValueError("Freelancer not available")

        project.freelancer_id = freelancer.id
        project.status = "assigned"
        freelancer.is_available = False

        db.session.commit()
        return project

    # Fetch project details with freelancer info
    @staticmethod
    def get_project_details(project_id):
        """Fetch project details with freelancer info."""
        project = Project.query.get_or_404(project_id)
        freelancer = None
        if project.assigned_freelancer_id:
            freelancer = FreelancerProfile.query.get(project.assigned_freelancer_id)

        data = project.to_dict()
        data["freelancer"] = freelancer.to_dict() if freelancer else None
        return data

    # Match freelancers to a project (by shared skills)
    @staticmethod
    def match_freelancers_to_project(project):
        """Return a list of suggested freelancers."""
        required_skill_ids = [s.id for s in project.skills]

        if not required_skill_ids:
            return []

        matched_freelancers = (
            FreelancerProfile.query
            .filter(FreelancerProfile.approved == True)
            .filter(FreelancerProfile.is_available == True)
            .join(FreelancerProfile.skills)
            .filter(Skill.id.in_(required_skill_ids))
            .distinct()
            .all()
        )

        # rank by number of matching skills
        suggestions = []
        for f in matched_freelancers:
            overlap = len([s for s in f.skills if s.id in required_skill_ids])
            suggestions.append({
                "freelancer": f.to_dict(),
                "match_score": overlap / len(required_skill_ids)
            })

        suggestions.sort(key=lambda x: x["match_score"], reverse=True)
        return suggestions
