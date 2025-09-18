#!/usr/bin/env python3

# Script to remove duplicate endpoint functions from app.py

# Read the file
with open('/Users/anji/Desktop/IntelliAttend/backend/app.py', 'r') as f:
    lines = f.readlines()

# Find the line numbers of the duplicate routes
duplicate_lines = []
for i, line in enumerate(lines):
    if "@app.route('/api/admin/students/<int:student_id>/delete', methods=['DELETE'])" in line:
        duplicate_lines.append(i)

print(f"Found duplicate routes at lines: {duplicate_lines}")

# Remove the first two occurrences, keeping only the last one
# We'll remove from the end to avoid changing line numbers
if len(duplicate_lines) > 1:
    # Find the start and end of each function
    functions_to_remove = []
    
    for line_num in duplicate_lines[:-1]:  # All except the last one
        # Find the start of the function (the @app.route decorator)
        start_line = line_num
        
        # Find the end of the function (next @app.route or end of file)
        end_line = len(lines) - 1
        for i in range(start_line + 1, len(lines)):
            if "@app.route(" in lines[i] or i == len(lines) - 1:
                end_line = i - 1
                break
        
        functions_to_remove.append((start_line, end_line))
    
    # Remove functions from the end to avoid changing line numbers
    for start_line, end_line in reversed(functions_to_remove):
        print(f"Removing function from line {start_line} to {end_line}")
        del lines[start_line:end_line+1]
    
    # Write the file back
    with open('/Users/anji/Desktop/IntelliAttend/backend/app.py', 'w') as f:
        f.writelines(lines)
    
    print("Duplicate functions removed successfully!")
else:
    print("No duplicates found or only one route exists.")