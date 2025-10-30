#!/usr/bin/env python3
import re

print("�� Fixing remaining overlap warnings...")

# 1. Fix FreelancerProfile skill_associations overlaps
with open('app/models/freelancer_profile.py', 'r') as f:
    content = f.read()

# Fix skill_associations relationship
content = re.sub(
    r'skill_associations = db\.relationship\(\s*"FreelancerSkill", \s*back_populates="freelancer_profile",',
    'skill_associations = db.relationship(\n    "FreelancerSkill", \n    back_populates="freelancer_profile",\n    overlaps="freelancer_profiles",',
    content
)

# Fix skills relationship overlaps
content = re.sub(
    r'overlaps="skill_associations,freelancer_skills"',
    'overlaps="skill_associations,freelancer_skills,skill"',
    content
)

with open('app/models/freelancer_profile.py', 'w') as f:
    f.write(content)
print("✅ Fixed FreelancerProfile overlaps")

# 2. Fix FreelancerSkill overlaps in skill.py
with open('app/models/skill.py', 'r') as f:
    content = f.read()

# Fix FreelancerSkill.skill overlaps
content = re.sub(
    r'skill = db\.relationship\(\s*"Skill",\s*back_populates="freelancer_skills",\s*overlaps="freelancer_profiles"',
    'skill = db.relationship(\n        "Skill",\n        back_populates="freelancer_skills",\n        overlaps="freelancer_profiles,skills"',
    content
)

with open('app/models/skill.py', 'w') as f:
    f.write(content)
print("✅ Fixed FreelancerSkill overlaps")

print("🎉 All overlap warnings should be resolved!")
