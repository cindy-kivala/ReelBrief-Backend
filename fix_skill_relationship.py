with open('app/models/skill.py', 'r') as f:
    content = f.read()

# Find and fix the freelancer_profiles relationship in Skill class
import re

# Pattern to find the freelancer_profiles relationship
pattern = r'freelancer_profiles\s*=\s*db\.relationship\(\s*[\'"]FreelancerProfile[\'"]\s*,\s*secondary=[\'"]freelancer_skills[\'"]\s*,\s*back_populates=[\'"]skills[\'"]\s*,\s*overlaps=[\'"]freelancer_skills[\'"]\s*\)'

# Replace with a simpler, correct version
replacement = 'freelancer_profiles = db.relationship("FreelancerProfile", secondary="freelancer_skills", back_populates="skills", viewonly=True)'

if re.search(pattern, content):
    content = re.sub(pattern, replacement, content)
    with open('app/models/skill.py', 'w') as f:
        f.write(content)
    print("✅ Fixed freelancer_profiles relationship in Skill model")
else:
    print("Could not find the exact pattern to replace")
    # Show what's there
    match = re.search(r'freelancer_profiles\s*=\s*db\.relationship.*', content)
    if match:
        print("Current relationship:", match.group())
