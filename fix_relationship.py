import re

# Fix FreelancerSkill model
with open('app/models/skill.py', 'r') as f:
    content = f.read()

# Find FreelancerSkill class and fix the back_populates
# It should match the relationship name in FreelancerProfile
content = re.sub(
    r"(class FreelancerSkill.*?back_populates=)'freelancer_profile'",
    r"\1'profile'",  # or whatever the correct name is in FreelancerProfile
    content,
    flags=re.DOTALL
)

with open('app/models/skill.py', 'w') as f:
    f.write(content)

print("✅ Fixed FreelancerSkill back_populates")
