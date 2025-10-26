"""
seed.py
Owner: Monica
Description: Populates the database with initial test data:
 - skills
 - users
 - freelancer_profiles
 - freelancer_skills
 - projects
 - project_skills
"""

from datetime import datetime, timedelta
import random

from app import create_app
from app.extensions import db

# Models
try:
    from app.models.user import User
except Exception:
    User = None

try:
    from app.models.skill import Skill, FreelancerSkill
except Exception:
    Skill = None
    FreelancerSkill = None

try:
    from app.models.freelancer_profile import FreelancerProfile
except Exception:
    FreelancerProfile = None

try:
    from app.models.project import Project, ProjectSkill
except Exception:
    Project = None
    ProjectSkill = None


def safe_commit():
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Commit failed:", e)
        raise


def seed_skills():
    if Skill is None:
        print("Skill model not found — skipping skills seed.")
        return []

    skills_data = [
        {"name": "Web Development", "category": "Programming"},
        {"name": "React", "category": "Frontend"},
        {"name": "Node.js", "category": "Backend"},
        {"name": "UI/UX Design", "category": "Design"},
        {"name": "Copywriting", "category": "Writing"},
        {"name": "Data Analysis", "category": "Analytics"},
        {"name": "Video Editing", "category": "Media"},
        {"name": "Python", "category": "Programming"},
    ]

    created = []
    for s in skills_data:
        found = Skill.query.filter_by(name=s["name"]).first()
        if not found:
            found = Skill(name=s["name"], category=s.get("category"))
            db.session.add(found)
            print(f"Adding skill: {s['name']}")
        else:
            print(f"Skill exists: {s['name']}")
        created.append(found)

    safe_commit()
    return Skill.query.all()


def seed_users_and_freelancers(skills):
    created_users = []
    created_profiles = []

    if User:
        sample_users = [
            {"email": "client1@example.com", "name": "Client One", "role": "client"},
            {"email": "freelancer1@example.com", "name": "Alice Doe", "role": "freelancer"},
            {"email": "freelancer2@example.com", "name": "Bob Smith", "role": "freelancer"},
            {"email": "freelancer3@example.com", "name": "Carol Lee", "role": "freelancer"},
        ]

        for u in sample_users:
            existing = User.query.filter_by(email=u["email"]).first()
            if existing:
                created_users.append(existing)
                continue

            user_kwargs = {"email": u["email"], "name": u.get("name"), "role": u.get("role")}
            if hasattr(User, "password_hash"):
                from werkzeug.security import generate_password_hash
                user_kwargs["password_hash"] = generate_password_hash("password123")
            elif hasattr(User, "password"):
                user_kwargs["password"] = "password123"

            new_user = User(**{k: v for k, v in user_kwargs.items() if v is not None})
            db.session.add(new_user)
            created_users.append(new_user)

        safe_commit()

    if FreelancerProfile:
        freelancer_users = [u for u in created_users if getattr(u, "role", "") == "freelancer"]

        samples = [
            {"name": "Alice Doe", "email": "freelancer1@example.com", "bio": "Frontend developer, React specialist."},
            {"name": "Bob Smith", "email": "freelancer2@example.com", "bio": "Backend engineer, Python & Flask."},
            {"name": "Carol Lee", "email": "freelancer3@example.com", "bio": "UI/UX designer and prototyper."},
        ]

        for s in samples:
            existing = FreelancerProfile.query.filter_by(email=s["email"]).first()
            if existing:
                created_profiles.append(existing)
                continue

            user_id = None
            if freelancer_users:
                match = next((u for u in freelancer_users if getattr(u, "email", "") == s["email"]), None)
                user_id = match.id if match else freelancer_users[0].id

            profile_kwargs = {
                "user_id": user_id,
                "name": s["name"],
                "email": s["email"],
                "bio": s.get("bio") or "No bio provided.",
                "cv_url": None,
                "is_available": True,
                "approved": True,
                "created_at": datetime.utcnow(),
            }

            new_profile = FreelancerProfile(**profile_kwargs)
            db.session.add(new_profile)
            created_profiles.append(new_profile)

        safe_commit()

        if FreelancerSkill and skills:
            for prof in created_profiles:
                chosen = random.sample(skills, min(3, len(skills)))
                for sk in chosen:
                    exists = FreelancerSkill.query.filter_by(freelancer_id=prof.id, skill_id=sk.id).first()
                    if exists:
                        continue
                    link = FreelancerSkill(
                        freelancer_id=prof.id,
                        skill_id=sk.id,
                        proficiency=random.choice(["beginner", "intermediate", "expert"])
                    )
                    db.session.add(link)
            safe_commit()

    return created_users, created_profiles


def seed_projects(skills, freelancer_profiles, client_user=None):
    if Project is None:
        print("Project model not found — skipping projects seed.")
        return []

    sample_projects = [
        {"title": "Landing Page for New App", "description": "Create a responsive landing page for our mobile app.", "budget": 500.0, "deadline_days": 14, "project_type": "web", "is_sensitive": False, "priority": "normal"},
        {"title": "Brand UI Kit", "description": "Design UI kit and reusable components for the brand.", "budget": 800.0, "deadline_days": 21, "project_type": "design", "is_sensitive": False, "priority": "high"},
        {"title": "Data Analysis Report", "description": "Analyze sales data and prepare recommendations.", "budget": 600.0, "deadline_days": 10, "project_type": "data", "is_sensitive": True, "priority": "normal"},
    ]

    created_projects = []
    for p in sample_projects:
        exists = Project.query.filter_by(title=p["title"]).first()
        if exists:
            created_projects.append(exists)
            continue

        project_kwargs = {
            "title": p.get("title") or "Untitled Project",
            "description": p.get("description") or "No description provided.",
            "client_id": client_user.id if client_user else None,
            "budget": p.get("budget") or 0.0,
            "deadline": datetime.utcnow() + timedelta(days=p.get("deadline_days", 7)),
            "project_type": p.get("project_type") or "general",
            "is_sensitive": p.get("is_sensitive", False),
            "priority": p.get("priority") or "normal",
            "status": "submitted",
            "created_at": datetime.utcnow(),
        }

        new_proj = Project(**project_kwargs)
        db.session.add(new_proj)
        created_projects.append(new_proj)

    safe_commit()

    # attach skills
    if ProjectSkill and skills:
        for proj in created_projects:
            chosen = random.sample(skills, min(3, len(skills)))
            for sk in chosen:
                exists = ProjectSkill.query.filter_by(project_id=proj.id, skill_id=sk.id).first()
                if exists:
                    continue
                ps = ProjectSkill(
                    project_id=proj.id,
                    skill_id=sk.id,
                    required_proficiency=random.choice(["intermediate", "expert"])
                )
                db.session.add(ps)
        safe_commit()

    # assign freelancers safely
    if freelancer_profiles and created_projects:
        for i, proj in enumerate(created_projects):
            prof = freelancer_profiles[i % len(freelancer_profiles)]
            if hasattr(proj, "freelancer_id"):
                proj.freelancer_id = getattr(prof, "user_id", None) or getattr(prof, "id", None)
                proj.status = "matched"
                proj.matched_at = datetime.utcnow()
                db.session.add(proj)
        safe_commit()

    return created_projects


def main():
    app = create_app()
    with app.app_context():
        print("Seeding database...")

        skills = seed_skills()
        users, freelancers = seed_users_and_freelancers(skills)

        client_user = None
        if users:
            client_user = next((u for u in users if getattr(u, "role", "") == "client"), users[0])

        projects = seed_projects(skills, freelancers, client_user)

        print("Seeding complete.")
        print(f"Skills: {len(skills)}")
        print(f"Users created or found: {len(users)}")
        print(f"Freelancer profiles created or found: {len(freelancers)}")
        print(f"Projects created or found: {len(projects)}")


if __name__ == "__main__":
    main()
