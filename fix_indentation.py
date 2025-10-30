with open('app/models/skill.py', 'r') as f:
    lines = f.readlines()

# Find and fix the indentation issue
fixed_lines = []
for i, line in enumerate(lines):
    # Check if this is the problematic __repr__ method
    if 'def __repr__(self):' in line and not line.startswith('    '):
        print(f"Found indentation issue at line {i+1}")
        # Fix the indentation
        fixed_lines.append('    ' + line)
    else:
        fixed_lines.append(line)

# Write the fixed file
with open('app/models/skill.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed indentation issues")
