#!/usr/bin/env python3

# Script to remove duplicate endpoint functions from app.py

# Read the file
with open('/Users/anji/Desktop/IntelliAttend/backend/app.py', 'r') as f:
    lines = f.readlines()

# Function to remove duplicates for a specific route pattern
def remove_duplicates(route_pattern, function_name):
    # Find the line numbers of the duplicate routes
    duplicate_lines = []
    for i, line in enumerate(lines):
        if route_pattern in line:
            duplicate_lines.append(i)

    print(f"Found {len(duplicate_lines)} occurrences of {function_name} at lines: {duplicate_lines}")

    # Remove all except the first occurrence
    # We'll remove from the end to avoid changing line numbers
    if len(duplicate_lines) > 1:
        # Find the start and end of each function
        functions_to_remove = []
        
        for line_num in duplicate_lines[1:]:  # All except the first one
            # Find the start of the function (the @app.route decorator)
            start_line = line_num
            
            # Find the end of the function (next @app.route or end of file)
            end_line = len(lines) - 1
            for i in range(start_line + 1, len(lines)):
                if "@app.route(" in lines[i] and "/update" not in lines[i] and "/delete" not in lines[i]:
                    end_line = i - 1
                    break
            
            functions_to_remove.append((start_line, end_line))
        
        # Remove functions from the end to avoid changing line numbers
        for start_line, end_line in reversed(functions_to_remove):
            print(f"Removing {function_name} function from line {start_line} to {end_line}")
            del lines[start_line:end_line+1]
        
        return True
    return False

# Remove duplicates for admin_delete_student
removed_delete = remove_duplicates("@app.route('/api/admin/students/<int:student_id>/delete', methods=['DELETE'])", "admin_delete_student")

# Remove duplicates for admin_update_student
removed_update = remove_duplicates("@app.route('/api/admin/students/<int:student_id>/update', methods=['PUT'])", "admin_update_student")

if removed_delete or removed_update:
    # Write the file back
    with open('/Users/anji/Desktop/IntelliAttend/backend/app.py', 'w') as f:
        f.writelines(lines)
    
    print("Duplicate functions removed successfully!")
else:
    print("No duplicates found.")

# Also check for any remaining duplicate function definitions
function_patterns = ["def admin_delete_student(", "def admin_update_student("]
for pattern in function_patterns:
    count = 0
    for line in lines:
        if pattern in line:
            count += 1
    if count > 1:
        print(f"Warning: Still found {count} definitions of {pattern}")