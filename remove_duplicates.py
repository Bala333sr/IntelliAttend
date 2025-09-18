#!/usr/bin/env python3

# Script to remove duplicate endpoint functions from app.py

import re

# Read the file
with open('/Users/anji/Desktop/IntelliAttend/backend/app.py', 'r') as f:
    content = f.read()

# Define the pattern to match the duplicate function
pattern = r'@app\.route\(/api/admin/students/<int:student_id>/delete.*, methods=\[.*DELETE.*\]\)\s*@jwt_required\(\)\s*def admin_delete_student\(student_id\):(.*?)(?=@app\.route|@jwt_required\(\)\s*def|\Z)'

# Remove the first occurrence of the duplicate function
# This will keep the second (more complete) version
new_content = re.sub(pattern, '', content, count=1, flags=re.DOTALL)

# Write the file back
with open('/Users/anji/Desktop/IntelliAttend/backend/app.py', 'w') as f:
    f.write(new_content)

print("Duplicate function removed successfully!")