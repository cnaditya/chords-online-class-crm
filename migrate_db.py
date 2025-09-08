#!/usr/bin/env python3
"""
Migrate existing database to new schema
"""

import sqlite3
import os

def migrate_database():
    """Add country_code column to existing students table"""
    db_path = "data/chords_crm.db"
    
    if not os.path.exists(db_path):
        print("Database doesn't exist, will be created fresh")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if country_code column exists
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'country_code' not in columns:
            print("Adding country_code column...")
            cursor.execute("ALTER TABLE students ADD COLUMN country_code VARCHAR(5) DEFAULT '+91'")
            
            # Update existing records - extract country code from phone if it starts with +
            cursor.execute("SELECT id, phone FROM students")
            students = cursor.fetchall()
            
            for student_id, phone in students:
                if phone.startswith('+91'):
                    new_phone = phone[3:]
                    cursor.execute("UPDATE students SET country_code = '+91', phone = ? WHERE id = ?", (new_phone, student_id))
                elif phone.startswith('+1'):
                    new_phone = phone[2:]
                    cursor.execute("UPDATE students SET country_code = '+1', phone = ? WHERE id = ?", (new_phone, student_id))
                elif phone.startswith('+64'):
                    new_phone = phone[3:]
                    cursor.execute("UPDATE students SET country_code = '+64', phone = ? WHERE id = ?", (new_phone, student_id))
                else:
                    # Default to +91 for existing records
                    cursor.execute("UPDATE students SET country_code = '+91' WHERE id = ?", (student_id,))
            
            conn.commit()
            print("Migration completed successfully!")
        else:
            print("Database already migrated")
            
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()