"""
seed.py
Owner: Monica
Description:
Populates the database with initial test data:
 - Skills
 - Users (clients & freelancers)
 - FreelancerProfiles (with CVs, portfolio, and vetting status)
 - FreelancerSkills
 - Projects
 - ProjectSkills
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


#Helper for safe DB commits
def safe_commit():
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Commit failed:", e)
        raise


#  Seed skills
def seed_skills():
    if Skill is None:
        print(" Skill model not found — skipping skills seed.")
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

    for s in skills_data:
        existing = Skill.query.filter_by(name=s["name"]).first()
        if not existing:
            skill = Skill(name=s["name"], category=s["category"])
            db.session.add(skill)
            print(f"✅ Added skill: {s['name']}")
    safe_commit()

    return Skill.query.all()


# Seed users & freelancers
def seed_users_and_freelancers(skills):
    if not User or not FreelancerProfile:
        print("User or FreelancerProfile model not found — skipping.")
        return [], []

    # Create users 
    sample_users = [
        {"email": "cindy@gmail.com", "name": "Cindy Kate", "role": "client"},
        {"email": "alice@gmail.com", "name": "Alice Doe", "role": "freelancer"},
        {"email": "bob@gmail.com", "name": "Bob Smith", "role": "freelancer"},
        {"email": "carol@gmail.com", "name": "Carol Lee", "role": "freelancer"},
    ]

    created_users = []
    for u in sample_users:
        existing = User.query.filter_by(email=u["email"]).first()
        if existing:
            created_users.append(existing)
            continue

        from werkzeug.security import generate_password_hash
        user = User(
            email=u["email"],
            name=u["name"],
            role=u["role"],
            password_hash=generate_password_hash("password123"),
        )
        db.session.add(user)
        created_users.append(user)

    safe_commit()

    # Create freelancer profiles 
    freelancer_users = [u for u in created_users if u.role == "freelancer"]
    created_profiles = []

    statuses = ["pending", "approved", "rejected"]

    sample_profiles = [
        {
            "name": "Alice Doe",
            "email": "alice@gmail.com",
            "bio": "Frontend developer specializing in React and UI/UX.",
            "portfolio_url": "https://dribbble.com/alicedoe",
            "years_experience": 3,
            "hourly_rate": 30,
        },
        {
            "name": "Bob Smith",
            "email": "bob@gmail.com",
            "bio": "Backend engineer with Flask, Node.js, and REST APIs.",
            "portfolio_url": "https://github.com/bobsmith",
            "years_experience": 5,
            "hourly_rate": 45,
        },
        {
            "name": "Carol Lee",
            "email": "carol@gmail.com",
            "bio": "Creative UI/UX designer passionate about branding.",
            "portfolio_url": "https://behance.net/carollee",
            "years_experience": 4,
            "hourly_rate": 35,
        },
    ]

    for i, p in enumerate(sample_profiles):
        existing = FreelancerProfile.query.filter_by(email=p["email"]).first()
        if existing:
            created_profiles.append(existing)
            continue

        match_user = next((u for u in freelancer_users if u.email == p["email"]), None)
        user_id = match_user.id if match_user else None

        profile = FreelancerProfile(
            user_id=user_id,
            name=p["name"],
            email=p["email"],
            bio=p["bio"],
            portfolio_url=p["portfolio_url"],
            years_experience=p["years_experience"],
            hourly_rate=p["hourly_rate"],
            cv_url=f"https://res.cloudinary.com/demo/{p['name'].lower().replace(' ', '_')}_cv.pdf",
            cv_filename=f"{p['name'].replace(' ', '_')}_cv.pdf",
            cv_uploaded_at=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            application_status=random.choice(statuses),
            open_to_work=True,
            created_at=datetime.utcnow(),
        )
        db.session.add(profile)
        created_profiles.append(profile)

    safe_commit()

    #  Assign skills 
    if FreelancerSkill and skills:
        for prof in created_profiles:
            chosen = random.sample(skills, min(3, len(skills)))
            for sk in chosen:
                exists = FreelancerSkill.query.filter_by(
                    freelancer_id=prof.id, skill_id=sk.id
                ).first()
                if not exists:
                    link = FreelancerSkill(
                        freelancer_id=prof.id,
                        skill_id=sk.id,
                        proficiency=random.choice(
                            ["beginner", "intermediate", "expert"]
                        ),
                    )
                    db.session.add(link)
        safe_commit()

    return created_users, created_profiles


#  Seed projects
def seed_projects(skills, freelancers, client_user=None):
    if Project is None:
        print("Project model not found — skipping.")
        return []

    sample_projects = [
        {
            "title": "Landing Page for New App",
            "description": "Build a modern landing page for our app.",
            "budget": 500.0,
            "deadline_days": 14,
            "project_type": "web",
            "priority": "normal",
        },
        {
            "title": "Brand UI Kit",
            "description": "Design a complete UI kit and components.",
            "budget": 800.0,
            "deadline_days": 21,
            "project_type": "design",
            "priority": "high",
        },
        {
            "title": "Data Analysis Report",
            "description": "Analyze quarterly data and visualize insights.",
            "budget": 600.0,
            "deadline_days": 10,
            "project_type": "data",
            "priority": "normal",
        },
    ]

    created_projects = []
    for p in sample_projects:
        exists = Project.query.filter_by(title=p["title"]).first()
        if exists:
            created_projects.append(exists)
            continue

        project = Project(
            title=p["title"],
            description=p["description"],
            client_id=client_user.id if client_user else None,
            budget=p["budget"],
            deadline=datetime.utcnow() + timedelta(days=p["deadline_days"]),
            project_type=p["project_type"],
            priority=p["priority"],
            status="submitted",
            created_at=datetime.utcnow(),
        )
        db.session.add(project)
        created_projects.append(project)

    safe_commit()

    # Attach random skills
    if ProjectSkill and skills:
        for proj in created_projects:
            chosen = random.sample(skills, min(3, len(skills)))
            for sk in chosen:
                exists = ProjectSkill.query.filter_by(
                    project_id=proj.id, skill_id=sk.id
                ).first()
                if not exists:
                    ps = ProjectSkill(
                        project_id=proj.id,
                        skill_id=sk.id,
                        required_proficiency=random.choice(
                            ["intermediate", "expert"]
                        ),
                    )
                    db.session.add(ps)
        safe_commit()

    # Assign freelancers (demo matching)
    if freelancers and created_projects:
        for i, proj in enumerate(created_projects):
            prof = freelancers[i % len(freelancers)]
            if hasattr(proj, "freelancer_id"):
                proj.freelancer_id = prof.user_id
                proj.status = "matched"
                proj.matched_at = datetime.utcnow()
                db.session.add(proj)
        safe_commit()

    return created_projects


# Running everything
def main():
    app = create_app()
    with app.app_context():
        print("\n🔹 Seeding database...")

        skills = seed_skills()
        users, freelancers = seed_users_and_freelancers(skills)

        client_user = next(
            (u for u in users if getattr(u, "role", "") == "client"), users[0]
        )

        projects = seed_projects(skills, freelancers, client_user)

        print("\n Seeding complete!")
        print(f"Skills: {len(skills)}")
        print(f"Users: {len(users)}")
        print(f"Freelancer Profiles: {len(freelancers)}")
        print(f"Projects: {len(projects)}\n")


if __name__ == "__main__":
    main()
