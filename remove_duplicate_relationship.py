with open('app/models/skill.py', 'r') as f:
    lines = f.readlines()

# Find and remove the duplicate relationship (the one with backref)
in_relationship = False
relationship_start = -1
fixed_lines = []

for i, line in enumerate(lines):
    if 'freelancer_profile = db.relationship(' in line and 'backref=db.backref' in ' '.join(lines[i:i+5]):
        print(f"Found duplicate relationship at line {i+1}:")
        print(''.join(lines[i:i+5]))
        # Skip this relationship block
        in_relationship = True
        relationship_start = i
        continue
    
    if in_relationship and line.strip() == ')':
        in_relationship = False
        print("Removed duplicate relationship")
        continue
        
    if not in_relationship:
        fixed_lines.append(line)

# Write the fixed file
with open('app/models/skill.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Removed duplicate relationship!")
