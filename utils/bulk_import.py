import pandas as pd
from datetime import datetime
from models.student import Student
from models.base import SessionLocal

def create_student_template():
    """Create Excel template for bulk student import"""
    template_data = {
        'name': ['John Doe', 'Jane Smith'],
        'email': ['john@example.com', 'jane@example.com'],
        'country_code': ['+91', '+1'],
        'phone': ['9876543210', '2016168147'],
        'parent1_country_code': ['+91', '+1'],
        'parent1_phone': ['9876543200', '9178619761'],
        'parent2_country_code': ['', '+1'],
        'parent2_phone': ['', '4042718365'],
        'instructor': ['Aditya', 'Brahmani'],
        'preferred_instrument': ['Piano', 'Guitar'],
        'skill_level': ['Beginner', 'Intermediate'],
        'timezone': ['Asia/Kolkata', 'America/New_York'],
        'notes': ['Interested in classical', 'Prefers evening classes']
    }
    
    df = pd.DataFrame(template_data)
    return df

def import_students_from_excel(file_content, instructor_filter=None):
    """Import students from Excel file"""
    try:
        df = pd.read_excel(file_content)
        
        # Validate required columns
        required_cols = ['name', 'country_code', 'phone', 'instructor']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return False, f"Missing required columns: {', '.join(missing_cols)}"
        
        db = SessionLocal()
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Skip if instructor filter doesn't match
                if instructor_filter and row['instructor'] != instructor_filter:
                    continue
                
                # Parse date of birth
                dob = None
                if pd.notna(row.get('date_of_birth')):
                    if isinstance(row['date_of_birth'], str):
                        dob = datetime.strptime(row['date_of_birth'], '%Y-%m-%d')
                    else:
                        dob = row['date_of_birth']
                
                student = Student(
                    name=row['name'],
                    email=row.get('email') if pd.notna(row.get('email')) else None,
                    country_code=row['country_code'],
                    phone=str(row['phone']),
                    parent1_country_code=row.get('parent1_country_code') if pd.notna(row.get('parent1_country_code')) else None,
                    parent1_phone=str(row.get('parent1_phone')) if pd.notna(row.get('parent1_phone')) else None,
                    parent2_country_code=row.get('parent2_country_code') if pd.notna(row.get('parent2_country_code')) else None,
                    parent2_phone=str(row.get('parent2_phone')) if pd.notna(row.get('parent2_phone')) else None,
                    date_of_birth=dob,
                    address=row.get('address') if pd.notna(row.get('address')) else None,
                    instructor=row['instructor'],
                    preferred_instrument=row.get('preferred_instrument') if pd.notna(row.get('preferred_instrument')) else None,
                    skill_level=row.get('skill_level', 'Beginner'),
                    timezone=row.get('timezone', 'Asia/Kolkata'),
                    notes=row.get('notes') if pd.notna(row.get('notes')) else None
                )
                
                db.add(student)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.commit()
        db.close()
        
        if errors:
            return True, f"Imported {imported_count} students with {len(errors)} errors: {'; '.join(errors[:3])}"
        else:
            return True, f"Successfully imported {imported_count} students"
            
    except Exception as e:
        return False, f"Error processing file: {str(e)}"