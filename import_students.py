#!/usr/bin/env python3
"""
Import students from CSV file
"""

import pandas as pd
from datetime import datetime
from models.base import SessionLocal
from models.student import Student

def import_students():
    """Import students from CSV file"""
    db = SessionLocal()
    
    try:
        # Read CSV file
        df = pd.read_csv('student_bulk_data.csv')
        
        imported_count = 0
        
        for index, row in df.iterrows():
            try:
                student = Student(
                    name=row['name'],
                    email=row['email'] if pd.notna(row['email']) and row['email'] else None,
                    phone=str(row['phone']),
                    whatsapp_number=str(row['whatsapp_number']),
                    date_of_birth=None,
                    address=row['address'] if pd.notna(row['address']) and row['address'] else None,
                    emergency_contact=row['emergency_contact'] if pd.notna(row['emergency_contact']) and row['emergency_contact'] else None,
                    emergency_phone=str(row['emergency_phone']) if pd.notna(row['emergency_phone']) and row['emergency_phone'] else None,
                    instructor=row['instructor'],
                    preferred_instrument=row['preferred_instrument'],
                    skill_level=row['skill_level'],
                    timezone=row['timezone'],
                    notes=row['notes'] if pd.notna(row['notes']) and row['notes'] else None
                )
                
                db.add(student)
                imported_count += 1
                print(f"Added: {row['name']}")
                
            except Exception as e:
                print(f"Error adding {row['name']}: {str(e)}")
        
        db.commit()
        print(f"\nSuccessfully imported {imported_count} students!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_students()