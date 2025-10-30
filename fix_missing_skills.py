#!/usr/bin/env python3
import re

print("🔧 Restoring missing skills relationship and fixing overlaps...")

# 1. Fix FreelancerProfile - restore skills relationship and add overlaps
with open('app/models/freelancer_profile.py', 'r') as f:
    content = f.read()

# Check if skills relationship exists
if 'skills = db.relationship' not in content:
    print("Restoring skills relationship...")
    
    # Find where to insert it (after skill_associations)
    skill_assoc_pattern = r'(skill_associations\s*=\s*db\.relationship\([^)]+\))'
    replacement = r'''\\1

    # Many-to-many relationship with Skill (through freelancer_skills)
    skills = db.relationship(
        "Skill", 
        secondary="freelancer_skills", 
        back_populates="freelancer_profiles",
        overlaps="skill_associations,freelancer_skills"
    )'''
    
    content = re.sub(skill_assoc_pattern, replacement, content, flags=re.DOTALL)

with open('app/models/freelancer_profile.py', 'w') as f:
    f.write(content)
print("✅ Restored skills relationship in FreelancerProfile")

# 2. Fix Skill model - add overlaps to resolve warnings
with open('app/models/skill.py', 'r') as f:
    content = f.read()

# Fix freelancer_skills relationship with overlaps
content = re.sub(
    r'freelancer_skills = db\.relationship\(\s*\'FreelancerSkill\',\s*back_populates=\'skill\',\s*cascade=\'all, delete-orphan\'',
    'freelancer_skills = db.relationship(\\n        \\\'FreelancerSkill\\\',\\n        back_populates=\\\'skill\\\',\\n        cascade=\\\'all, delete-orphan\\\',\\n        overlaps="freelancer_profiles"',
    content
)

# Fix freelancer_profiles relationship with overlaps
content = re.sub(
    r'freelancer_profiles = db\.relationship\(\s*"FreelancerProfile",\s*secondary="freelancer_skills",\s*back_populates="skills_m2m"',
    'freelancer_profiles = db.relationship(\\n        "FreelancerProfile",\\n        secondary="freelancer_skills", \\n        back_populates="skills",\\n        overlaps="freelancer_skills"',
    content
)

with open('app/models/skill.py', 'w') as f:
    f.write(content)
print("✅ Fixed Skill model overlaps")

# 3. Fix FreelancerSkill overlaps (in the same file)
content = re.sub(
    r'skill = db\.relationship\(\s*"Skill", \s*back_populates="freelancer_skills"',
    'skill = db.relationship(\\n        "Skill", \\n        back_populates="freelancer_skills",\\n        overlaps="freelancer_profiles"',
    content
)

content = re.sub(
    r'freelancer_profile = db\.relationship\(\'FreelancerProfile\', back_populates="skill_associations"',
    'freelancer_profile = db.relationship(\\\'FreelancerProfile\\\', back_populates="skill_associations", overlaps="freelancer_profiles,skills"',
    content
)

with open('app/models/skill.py', 'w') as f:
    f.write(content)
print("✅ Fixed FreelancerSkill overlaps")

print("🎉 All relationship overlaps fixed!")
