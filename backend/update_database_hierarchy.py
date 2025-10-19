#!/usr/bin/env python3
"""
Script to update the database structure to implement the hierarchical schema
College > Department > Branch > Timetable > Class > Faculty > Schedule > Students > Attendance
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text

def update_database_hierarchy():
    """Update database to implement hierarchical structure"""
    
    with app.app_context():
        try:
            print("Starting database hierarchy update...")
            
            # 1. Create colleges table
            print("1. Creating colleges table...")
            create_colleges_sql = """
            CREATE TABLE IF NOT EXISTS colleges (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(50) UNIQUE NOT NULL,
                address TEXT,
                contact_info VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """
            db.session.execute(text(create_colleges_sql))
            
            # 2. Create departments table
            print("2. Creating departments table...")
            create_departments_sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                college_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(50) UNIQUE NOT NULL,
                head VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE,
                INDEX idx_college_id (college_id)
            );
            """
            db.session.execute(text(create_departments_sql))
            
            # 3. Create branches table
            print("3. Creating branches table...")
            create_branches_sql = """
            CREATE TABLE IF NOT EXISTS branches (
                id INT AUTO_INCREMENT PRIMARY KEY,
                department_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(50) UNIQUE NOT NULL,
                degree_type ENUM('B.Tech', 'M.Tech', 'MBA', 'Other') DEFAULT 'B.Tech',
                duration INT DEFAULT 4,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
                INDEX idx_department_id (department_id)
            );
            """
            db.session.execute(text(create_branches_sql))
            
            # 4. Create timetables table
            print("4. Creating timetables table...")
            create_timetables_sql = """
            CREATE TABLE IF NOT EXISTS timetables (
                id INT AUTO_INCREMENT PRIMARY KEY,
                branch_id INT NOT NULL,
                academic_year VARCHAR(9) NOT NULL,
                semester VARCHAR(20) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
                INDEX idx_branch_id (branch_id),
                INDEX idx_academic_year (academic_year),
                INDEX idx_semester (semester)
            );
            """
            db.session.execute(text(create_timetables_sql))
            
            # 5. Add branch_id to students table if not exists
            print("5. Updating students table...")
            try:
                add_branch_to_students_sql = """
                ALTER TABLE students ADD COLUMN branch_id INT AFTER student_id,
                ADD FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
                ADD INDEX idx_branch_id (branch_id);
                """
                db.session.execute(text(add_branch_to_students_sql))
            except Exception as e:
                print(f"   Note: branch_id column may already exist in students table: {e}")
            
            # 6. Add department_id to faculty table if not exists
            print("6. Updating faculty table...")
            try:
                add_department_to_faculty_sql = """
                ALTER TABLE faculty ADD COLUMN department_id INT AFTER faculty_id,
                ADD FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
                ADD INDEX idx_department_id (department_id);
                """
                db.session.execute(text(add_department_to_faculty_sql))
            except Exception as e:
                print(f"   Note: department_id column may already exist in faculty table: {e}")
            
            # 7. Add timetable_id to classes table if not exists
            print("7. Updating classes table...")
            try:
                add_timetable_to_classes_sql = """
                ALTER TABLE classes ADD COLUMN timetable_id INT AFTER class_id,
                ADD FOREIGN KEY (timetable_id) REFERENCES timetables(id) ON DELETE SET NULL,
                ADD INDEX idx_timetable_id (timetable_id);
                """
                db.session.execute(text(add_timetable_to_classes_sql))
            except Exception as e:
                print(f"   Note: timetable_id column may already exist in classes table: {e}")
            
            # 8. Create schedules table (using class_id as foreign key)
            print("8. Creating schedules table...")
            create_schedules_sql = """
            CREATE TABLE IF NOT EXISTS schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                class_id INT NOT NULL,
                day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
                start_time TIME,
                end_time TIME,
                schedule_type ENUM('regular', 'lab', 'break', 'lunch') DEFAULT 'regular',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
                INDEX idx_class_id (class_id),
                INDEX idx_day_of_week (day_of_week)
            );
            """
            db.session.execute(text(create_schedules_sql))
            
            # 9. Insert default college, department, and branch data
            print("9. Inserting default data...")
            
            # Check if default college exists
            check_college_sql = "SELECT id FROM colleges WHERE code = 'MRCET' LIMIT 1"
            result = db.session.execute(text(check_college_sql)).fetchone()
            
            if not result:
                # Insert default college
                insert_college_sql = """
                INSERT INTO colleges (name, code, address, contact_info) 
                VALUES ('Malla Reddy College of Engineering & Technology', 'MRCET', 
                        'Maisammaguda, Dhulapally Post, Via Hakimpet, Secunderabad–500100', 
                        'contact@mrcet.edu.in')
                """
                db.session.execute(text(insert_college_sql))
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                college_id = result[0] if result else 1
            else:
                college_id = result[0]
            
            # Check if default department exists
            check_department_sql = "SELECT id FROM departments WHERE code = 'CSE' AND college_id = :college_id LIMIT 1"
            result = db.session.execute(text(check_department_sql), {'college_id': college_id}).fetchone()
            
            if not result:
                # Insert default department
                insert_department_sql = """
                INSERT INTO departments (college_id, name, code, head) 
                VALUES (:college_id, 'Computer Science and Engineering', 'CSE', 'Dr. Kanniaah')
                """
                db.session.execute(text(insert_department_sql), {'college_id': college_id})
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                department_id = result[0] if result else 1
            else:
                department_id = result[0]
            
            # Check if default branch exists
            check_branch_sql = "SELECT id FROM branches WHERE code = 'B.Tech-CSE' AND department_id = :department_id LIMIT 1"
            result = db.session.execute(text(check_branch_sql), {'department_id': department_id}).fetchone()
            
            if not result:
                # Insert default branch
                insert_branch_sql = """
                INSERT INTO branches (department_id, name, code, degree_type, duration) 
                VALUES (:department_id, 'B.Tech Computer Science and Engineering', 'B.Tech-CSE', 'B.Tech', 4)
                """
                db.session.execute(text(insert_branch_sql), {'department_id': department_id})
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                branch_id = result[0] if result else 1
            else:
                branch_id = result[0]
            
            # 10. Update existing students with branch_id if not set
            print("10. Updating existing students with branch_id...")
            update_students_sql = """
            UPDATE students SET branch_id = :branch_id WHERE branch_id IS NULL
            """
            db.session.execute(text(update_students_sql), {'branch_id': branch_id})
            
            # 11. Update existing faculty with department_id if not set
            print("11. Updating existing faculty with department_id...")
            update_faculty_sql = """
            UPDATE faculty SET department_id = :department_id WHERE department_id IS NULL
            """
            db.session.execute(text(update_faculty_sql), {'department_id': department_id})
            
            # 12. Create default timetable if not exists
            print("12. Creating default timetable...")
            check_timetable_sql = """
            SELECT id FROM timetables WHERE branch_id = :branch_id AND academic_year = '2025-26' AND semester = 'Fall' LIMIT 1
            """
            result = db.session.execute(text(check_timetable_sql), {'branch_id': branch_id}).fetchone()
            
            if not result:
                insert_timetable_sql = """
                INSERT INTO timetables (branch_id, academic_year, semester) 
                VALUES (:branch_id, '2025-26', 'Fall')
                """
                db.session.execute(text(insert_timetable_sql), {'branch_id': branch_id})
                result = db.session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()
                timetable_id = result[0] if result else 1
            else:
                timetable_id = result[0]
            
            # 13. Update existing classes with timetable_id if not set
            print("13. Updating existing classes with timetable_id...")
            update_classes_sql = """
            UPDATE classes SET timetable_id = :timetable_id WHERE timetable_id IS NULL
            """
            db.session.execute(text(update_classes_sql), {'timetable_id': timetable_id})
            
            # 14. Migrate timetable data to schedules
            print("14. Migrating timetable data to schedules...")
            migrate_timetable_sql = """
            INSERT INTO schedules (class_id, day_of_week, start_time, end_time, schedule_type)
            SELECT c.class_id, t.day_of_week, t.start_time, t.end_time, 
                   CASE WHEN t.slot_type IS NOT NULL THEN t.slot_type ELSE 'regular' END
            FROM timetable t
            JOIN sections s ON t.section_id = s.id
            LEFT JOIN classes c ON c.class_code = t.subject_code
            WHERE t.slot_type != 'break' AND t.slot_type != 'lunch' AND c.class_id IS NOT NULL
            ON DUPLICATE KEY UPDATE 
                day_of_week = VALUES(day_of_week),
                start_time = VALUES(start_time),
                end_time = VALUES(end_time),
                schedule_type = VALUES(schedule_type)
            """
            try:
                db.session.execute(text(migrate_timetable_sql))
            except Exception as e:
                print(f"   Note: Could not migrate timetable data to schedules: {e}")
            
            db.session.commit()
            print("✅ Database hierarchy update completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating database hierarchy: {e}")
            raise e

if __name__ == '__main__':
    update_database_hierarchy()