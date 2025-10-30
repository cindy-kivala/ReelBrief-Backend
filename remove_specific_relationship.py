with open('app/models/skill.py', 'r') as f:
    lines = f.readlines()

# Find and remove the specific freelancer_profile relationship in Skill class
in_skill_class = False
in_relationship = False
relationship_start = -1
fixed_lines = []

for i, line in enumerate(lines):
    # Track when we're in the Skill class
    if 'class Skill(db.Model):' in line:
        in_skill_class = True
        fixed_lines.append(line)
        continue
    
    # Track when we find the problematic relationship in Skill class
    if in_skill_class and 'freelancer_profile = db.relationship(' in line:
        print(f"Found problematic relationship at line {i+1}")
        in_relationship = True
        relationship_start = i
        continue
    
    # Skip lines until the relationship block ends
    if in_relationship:
        if line.strip() == ')':
            in_relationship = False
            print("Removed problematic freelancer_profile relationship from Skill class")
        continue
    
    # Keep all other lines
    fixed_lines.append(line)

# Write the fixed file
with open('app/models/skill.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Successfully removed problematic relationship")
