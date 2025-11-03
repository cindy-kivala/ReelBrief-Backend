"""
Project Approval Workflow - Admin-Mediated Approval & Assignment
Owner: Cindy
Description: Handles project approval workflow, freelancer shortlisting, and assignment with notifications
"""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import and_
from app.extensions import db
from app.models.project import Project, ProjectSkill
from app.models.freelancer_profile import FreelancerProfile
from app.models.skill import Skill, FreelancerSkill
from app.models.user import User
from app.models.notification import Notification
from app.services.email_service import send_email


class ProjectApprovalService:
    """Handles project approval and freelancer matching workflow"""

    @staticmethod
    def check_project_feasibility(project_id: int) -> Dict:
        """
        Check if project is feasible based on available freelancers
        Returns: {
            'is_feasible': bool,
            'matching_freelancers': list,
            'reasons': list
        }
        """
        project = Project.query.get_or_404(project_id)
        
        # Get required skills
        required_skill_ids = [ps.skill_id for ps in project.required_skills]
        
        if not required_skill_ids:
            return {
                'is_feasible': False,
                'matching_freelancers': [],
                'reasons': ['No required skills specified for project']
            }
        
        # Find freelancers with matching skills
        matching_freelancers = (
            FreelancerProfile.query
            .filter(
                FreelancerProfile.application_status == 'approved',
                FreelancerProfile.open_to_work == True
            )
            .join(FreelancerSkill)
            .filter(FreelancerSkill.skill_id.in_(required_skill_ids))
            .distinct()
            .all()
        )
        
        # Calculate match scores
        freelancer_scores = []
        for freelancer in matching_freelancers:
            freelancer_skill_ids = [fs.skill_id for fs in freelancer.freelancer_skills]
            matching_skills = set(required_skill_ids) & set(freelancer_skill_ids)
            match_score = len(matching_skills) / len(required_skill_ids)
            
            # Check proficiency levels
            has_sufficient_proficiency = True
            for ps in project.required_skills:
                fs = next((x for x in freelancer.freelancer_skills if x.skill_id == ps.skill_id), None)
                if fs:
                    proficiency_levels = ['beginner', 'intermediate', 'expert']
                    required_level = proficiency_levels.index(ps.required_proficiency)
                    freelancer_level = proficiency_levels.index(fs.proficiency)
                    if freelancer_level < required_level:
                        has_sufficient_proficiency = False
                        break
            
            if has_sufficient_proficiency and match_score >= 0.7:  # At least 70% skill match
                freelancer_scores.append({
                    'freelancer': freelancer,
                    'match_score': match_score,
                    'matching_skills': len(matching_skills),
                    'total_required': len(required_skill_ids)
                })
        
        # Sort by match score
        freelancer_scores.sort(key=lambda x: x['match_score'], reverse=True)
        
        is_feasible = len(freelancer_scores) > 0
        reasons = []
        
        if not is_feasible:
            if not matching_freelancers:
                reasons.append('No approved freelancers available with required skills')
            else:
                reasons.append('Available freelancers do not meet minimum proficiency requirements')
        
        return {
            'is_feasible': is_feasible,
            'matching_freelancers': freelancer_scores,
            'reasons': reasons
        }

    @staticmethod
    def approve_project(project_id: int, admin_id: int) -> Dict:
        """
        Admin approves project as feasible
        - Updates project status to 'approved'
        - Generates shortlist of qualified freelancers
        - Notifies client with shortlist
        """
        project = Project.query.get_or_404(project_id)
        admin = User.query.get_or_404(admin_id)
        client = User.query.get_or_404(project.client_id)
        
        # Check feasibility
        feasibility = ProjectApprovalService.check_project_feasibility(project_id)
        
        if not feasibility['is_feasible']:
            raise ValueError("Project cannot be approved - " + "; ".join(feasibility['reasons']))
        
        # Update project status
        project.status = 'approved'
        project.approved_at = datetime.utcnow()
        project.approved_by = admin_id
        
        # Create shortlist notification for client
        shortlisted_freelancers = feasibility['matching_freelancers'][:5]  # Top 5 matches
        
        notification = Notification(
            user_id=client.id,
            type='project_approved',
            title=f'Project Approved: {project.title}',
            message=f'Your project has been approved! {len(shortlisted_freelancers)} qualified freelancers have been shortlisted for your review.',
            related_project_id=project.id
        )
        db.session.add(notification)
        
        # Send email to client with shortlist
        freelancer_list_html = ""
        for item in shortlisted_freelancers:
            fl = item['freelancer']
            user = User.query.get(fl.user_id)
            freelancer_list_html += f"""
            <div style="border: 1px solid #e0e0e0; padding: 15px; margin: 10px 0; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0; color: #1E3A8A;">{fl.name}</h4>
                <p style="margin: 5px 0;"><strong>Match Score:</strong> {int(item['match_score'] * 100)}%</p>
                <p style="margin: 5px 0;"><strong>Skills:</strong> {', '.join([s.skill.name for s in fl.freelancer_skills])}</p>
                <p style="margin: 5px 0;"><strong>Experience:</strong> {fl.years_experience} years</p>
                <p style="margin: 5px 0;"><strong>Hourly Rate:</strong> ${fl.hourly_rate}/hr</p>
                {f'<p style="margin: 5px 0;"><strong>Bio:</strong> {fl.bio}</p>' if fl.bio else ''}
            </div>
            """
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        email_sent = send_email(
            recipient=client.email,
            subject=f"Project Approved: {project.title}",
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #10B981;">Project Approved!</h2>
                <p>Hello {client.first_name},</p>
                <p>Great news! Your project <strong>"{project.title}"</strong> has been reviewed and approved by our admin team.</p>
                
                <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1F2937;">Shortlisted Freelancers</h3>
                    <p>We've identified {len(shortlisted_freelancers)} qualified freelancers who match your project requirements:</p>
                    {freelancer_list_html}
                </div>
                
                <p style="margin: 20px 0;">
                    <a href="{frontend_url}/projects/{project.id}" 
                       style="display: inline-block; background-color: #1E3A8A; color: white; 
                              padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        Review Freelancers & Assign
                    </a>
                </p>
                
                <p style="color: #6B7280; font-size: 14px;">
                    You can review these freelancers and either:
                    <br/>• Select and assign a freelancer yourself
                    <br/>• Request admin to assign the best match for you
                </p>
            </div>
            """
        )
        
        db.session.commit()
        
        return {
            'success': True,
            'project': project.to_dict(),
            'shortlisted_freelancers': [
                {
                    'freelancer': item['freelancer'].to_dict(),
                    'match_score': item['match_score'],
                    'matching_skills': item['matching_skills']
                }
                for item in shortlisted_freelancers
            ],
            'email_sent': email_sent
        }

    @staticmethod
    def reject_project_feasibility(project_id: int, admin_id: int, reason: str) -> Dict:
        """
        Admin rejects project as not feasible
        - Notifies client with reasons
        - Provides suggestions for improvement
        """
        project = Project.query.get_or_404(project_id)
        admin = User.query.get_or_404(admin_id)
        client = User.query.get_or_404(project.client_id)
        
        # Update project status
        project.status = 'not_feasible'
        project.rejection_reason = reason
        
        # Create notification
        notification = Notification(
            user_id=client.id,
            type='project_not_feasible',
            title=f'Project Review: {project.title}',
            message=f'Your project has been reviewed. Unfortunately, we cannot proceed at this time. Reason: {reason}',
            related_project_id=project.id
        )
        db.session.add(notification)
        
        # Check what skills are missing
        feasibility = ProjectApprovalService.check_project_feasibility(project_id)
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        email_sent = send_email(
            recipient=client.email,
            subject=f"Project Review Update: {project.title}",
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #F59E0B;">Project Review Update</h2>
                <p>Hello {client.first_name},</p>
                <p>Thank you for submitting your project <strong>"{project.title}"</strong>.</p>
                
                <div style="background-color: #FEF3C7; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #F59E0B;">
                    <h3 style="margin: 0 0 10px 0; color: #92400E;">Current Status</h3>
                    <p style="margin: 0;">Unfortunately, we cannot proceed with this project at this time.</p>
                </div>
                
                <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1F2937;">Reason</h3>
                    <p style="margin: 0;">{reason}</p>
                    {'<p style="margin: 10px 0 0 0;"><strong>Details:</strong> ' + ', '.join(feasibility['reasons']) + '</p>' if feasibility['reasons'] else ''}
                </div>
                
                <div style="background-color: #DBEAFE; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1E40AF;">What You Can Do</h3>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        <li>Modify your project requirements</li>
                        <li>Adjust skill requirements or proficiency levels</li>
                        <li>Consider expanding your timeline</li>
                        <li>Contact us for alternative solutions</li>
                    </ul>
                </div>
                
                <p style="margin: 20px 0;">
                    <a href="{frontend_url}/projects/{project.id}" 
                       style="display: inline-block; background-color: #1E3A8A; color: white; 
                              padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                        Review & Modify Project
                    </a>
                </p>
            </div>
            """
        )
        
        db.session.commit()
        
        return {
            'success': True,
            'project': project.to_dict(),
            'email_sent': email_sent
        }

    @staticmethod
    def assign_freelancer_to_project(project_id: int, freelancer_user_id: int, assigned_by: int) -> Dict:
        """
        Assign a freelancer to an approved project
        - Can be done by client or admin
        - Notifies all parties (client, freelancer, admin)
        """
        project = Project.query.get_or_404(project_id)
        freelancer_user = User.query.get(freelancer_user_id)
        if not freelancer_user:
            raise ValueError(f"Freelancer with ID {freelancer_user_id} not found")
        freelancer_profile = FreelancerProfile.query.filter_by(user_id=freelancer_user_id).first_or_404()
        assigner = User.query.get_or_404(assigned_by)
        client = User.query.get_or_404(project.client_id)
        
        if project.status not in ['approved', 'submitted']:
            raise ValueError(f"Project must be approved before assignment (current status: {project.status})")
        
        if not freelancer_profile.open_to_work:
            raise ValueError("Freelancer is not currently available")
        
        # Assign freelancer
        project.freelancer_id = freelancer_user.id
        project.status = 'assigned'
        project.assigned_at = datetime.utcnow()
        freelancer_profile.open_to_work = False
        
        # Notify freelancer
        freelancer_notification = Notification(
            user_id=freelancer_user.id,
            type='project_assigned',
            title=f'New Project Assignment: {project.title}',
            message=f'You have been assigned to project "{project.title}". Budget: ${project.budget}',
            related_project_id=project.id
        )
        db.session.add(freelancer_notification)
        
        # Notify client (if assigned by admin)
        if assigner.role == 'admin' and assigner.id != client.id:
            client_notification = Notification(
                user_id=client.id,
                type='freelancer_assigned',
                title=f'Freelancer Assigned: {project.title}',
                message=f'{freelancer_profile.name} has been assigned to your project.',
                related_project_id=project.id
            )
            db.session.add(client_notification)
        
        # Notify admin (if assigned by client)
        if assigner.role == 'client':
            admin_users = User.query.filter_by(role='admin').all()
            for admin in admin_users:
                admin_notification = Notification(
                    user_id=admin.id,
                    type='project_assigned',
                    title=f'Project Assignment: {project.title}',
                    message=f'Client has assigned {freelancer_profile.name} to project "{project.title}".',
                    related_project_id=project.id
                )
                db.session.add(admin_notification)
        
        # Send emails
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        
        # Email to freelancer
        send_email(
            recipient=freelancer_user.email,
            subject=f"New Project Assignment: {project.title}",
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #10B981;">Congratulations! New Project Assignment</h2>
                <p>Hello {freelancer_user.first_name},</p>
                <p>You have been assigned to a new project!</p>
                
                <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1F2937;">{project.title}</h3>
                    <p style="margin: 5px 0;"><strong>Client:</strong> {client.first_name} {client.last_name}</p>
                    <p style="margin: 5px 0;"><strong>Budget:</strong> ${project.budget}</p>
                    <p style="margin: 5px 0;"><strong>Deadline:</strong> {project.deadline.strftime('%B %d, %Y') if project.deadline else 'Not specified'}</p>
                    <p style="margin: 10px 0 0 0;">{project.description}</p>
                </div>
                
                <p style="margin: 20px 0;">
                    <a href="{frontend_url}/projects/{project.id}" 
                       style="display: inline-block; background-color: #10B981; color: white; 
                              padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                        View Project Details
                    </a>
                </p>
                
                <p style="color: #6B7280; font-size: 14px;">
                    Please review the project details and start working on the deliverables.
                </p>
            </div>
            """
        )
        
        # Email to client (if assigned by admin)
        if assigner.role == 'admin':
            send_email(
                recipient=client.email,
                subject=f"Freelancer Assigned: {project.title}",
                html_content=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1E3A8A;">Freelancer Assigned to Your Project</h2>
                    <p>Hello {client.first_name},</p>
                    <p>A freelancer has been assigned to your project <strong>"{project.title}"</strong>.</p>
                    
                    <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #1F2937;">Assigned Freelancer</h3>
                        <p style="margin: 5px 0;"><strong>Name:</strong> {freelancer_profile.name}</p>
                        <p style="margin: 5px 0;"><strong>Experience:</strong> {freelancer_profile.years_experience} years</p>
                        <p style="margin: 5px 0;"><strong>Rate:</strong> ${freelancer_profile.hourly_rate}/hr</p>
                    </div>
                    
                    <p style="margin: 20px 0;">
                        <a href="{frontend_url}/projects/{project.id}" 
                           style="display: inline-block; background-color: #1E3A8A; color: white; 
                                  padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                            View Project
                        </a>
                    </p>
                </div>
                """
            )
        
        db.session.commit()
        
        return {
            'success': True,
            'project': project.to_dict(),
            'freelancer': freelancer_profile.to_dict(),
            'assigned_by': assigner.role
        }

    @staticmethod
    def get_project_shortlist(project_id: int) -> List[Dict]:
        """Get the shortlist of freelancers for a project"""
        feasibility = ProjectApprovalService.check_project_feasibility(project_id)
        
        if not feasibility['is_feasible']:
            return []
        
        return [
            {
                'freelancer': item['freelancer'].to_dict(),
                'match_score': item['match_score'],
                'matching_skills': item['matching_skills'],
                'total_required': item['total_required']
            }
            for item in feasibility['matching_freelancers'][:10]  # Top 10
        ]


import os