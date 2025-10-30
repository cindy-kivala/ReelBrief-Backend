with open('app/models/skill.py', 'r') as f:
    content = f.read()

# Remove the problematic freelancer_profiles relationship entirely
# and use only the association object approach
import re

# Remove the freelancer_profiles relationship (we'll use only freelancer_skills)
pattern = r'freelancer_profiles\s*=\s*db\.relationship\([^)]+\)'
content = re.sub(pattern, '', content)

# Also make sure the freelancer_skills relationship is correct
freelancer_skills_pattern = r'freelancer_skills\s*=\s*db\.relationship\([^)]+\)'
if not re.search(freelancer_skills_pattern, content):
    # Add it back if it was removed
    skill_class_start = content.find("class Skill")
    if skill_class_start != -1:
        # Find where to insert (after the table definition)
        insert_point = content.find(")", skill_class_start) + 1
        new_relationship = '''
    # Relationship to FreelancerSkill association objects
    freelancer_skills = db.relationship(
        "FreelancerSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )'''
        content = content[:insert_point] + new_relationship + content[insert_point:]

with open('app/models/skill.py', 'w') as f:
    f.write(new_content)

print("✅ Simplified relationships in Skill model")
