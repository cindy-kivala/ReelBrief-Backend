#!/usr/bin/env python3
from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"📊 Found {len(users)} users in database:")
    for user in users:
        print(f"  👤 {user.email} ({user.role}) - {user.first_name} {user.last_name}")
