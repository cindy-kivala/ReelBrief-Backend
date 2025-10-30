"""
seed_projects.py
Owner: Ryan
Description: Seeds ReelBrief with sample projects, deliverables, and feedback
Usage:
    python seed_projects.py
"""

from app import create_app, db
from app.models import User, Project, Deliverable, Feedback
from datetime import datetime, timedelta


def seed_projects():
    print("🚀 Seeding projects, deliverables, and feedback...")

    # -------------------- Get existing users --------------------
    client = User.query.filter_by(role="client").first()
    freelancer = User.query.filter_by(role="freelancer").first()

    if not client or not freelancer:
        print("⚠️ Please run seed.py first to create client and freelancer users.")
        return

    # -------------------- Projects --------------------
    project1 = Project(
        title="Product Promo Video",
        description="A short promotional video for a new product launch.",
        status="in_progress",
        budget=1200.00,
        deadline=datetime.utcnow() + timedelta(days=10),
        client_id=client.id,
        freelancer_id=freelancer.id,
        payment_status="in_escrow",
        priority="high",
    )

    project2 = Project(
        title="Brand Awareness Campaign",
        description="A brand campaign to increase online presence through video marketing.",
        status="completed",
        budget=2500.00,
        deadline=datetime.utcnow() - timedelta(days=5),
        client_id=client.id,
        freelancer_id=freelancer.id,
        payment_status="released",
        completed_at=datetime.utcnow() - timedelta(days=3),
    )

    db.session.add_all([project1, project2])
    db.session.commit()

    # -------------------- Deliverables --------------------
    deliverable1 = Deliverable(
        project_id=project1.id,
        uploaded_by=freelancer.id,
        title="Storyboard Draft",
        description="Initial storyboard for client approval.",
        file_url="https://res.cloudinary.com/demo/video/upload/v1234567890/storyboard.mp4",
        file_type="video",
        file_size=1048576,
        status="pending",
        uploaded_at=datetime.utcnow(),
    )

    deliverable2 = Deliverable(
        project_id=project2.id,
        uploaded_by=freelancer.id,
        reviewed_by=client.id,
        title="Final Video Upload",
        description="Completed and delivered product promo video.",
        file_url="https://res.cloudinary.com/demo/video/upload/v1234567890/final_video.mp4",
        file_type="video",
        file_size=2048576,
        status="approved",
        uploaded_at=datetime.utcnow() - timedelta(days=6),
        reviewed_at=datetime.utcnow() - timedelta(days=5),
    )

    db.session.add_all([deliverable1, deliverable2])
    db.session.commit()

    # -------------------- Feedback --------------------
    feedback1 = Feedback(
        deliverable_id=deliverable2.id,
        user_id=client.id,
        feedback_type="approval",
        content="Amazing work! Exactly what we needed for our product launch.",
        priority="high",
        is_resolved=True,
        created_at=datetime.utcnow(),
    )

    feedback2 = Feedback(
        deliverable_id=deliverable1.id,
        user_id=client.id,
        feedback_type="revision",
        content="Please adjust the pacing in scene 2 and brighten the lighting.",
        priority="medium",
        is_resolved=False,
        created_at=datetime.utcnow(),
    )

    db.session.add_all([feedback1, feedback2])
    db.session.commit()

    print("✅ Projects, deliverables, and feedback seeded successfully!")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_projects()
