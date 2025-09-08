import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from models.base import engine, Base
from models import User, Student, Enrollment, Payment, Attendance, ClassSchedule, Material, NotificationLog
from utils.auth import hash_password, verify_password
from services.notifications import Fast2SMSService
from config import Config
import os
import io

# Initialize database
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Page config
st.set_page_config(
    page_title="Chords Online Class CRM",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

def init_default_users():
    """Initialize default admin and instructor users"""
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@chordsmusic.com",
                hashed_password=hash_password("admin123"),
                full_name="Administrator",
                role="admin"
            )
            db.add(admin_user)
        
        # Check if instructors exist
        for instructor in Config.INSTRUCTORS:
            user = db.query(User).filter(User.instructor_name == instructor).first()
            if not user:
                instructor_user = User(
                    username=instructor.lower(),
                    email=f"{instructor.lower()}@chordsmusic.com",
                    hashed_password=hash_password("instructor123"),
                    full_name=instructor,
                    role="instructor",
                    instructor_name=instructor
                )
                db.add(instructor_user)
        
        db.commit()
    except Exception as e:
        st.error(f"Error initializing users: {str(e)}")
        db.rollback()
    finally:
        db.close()

def login_page():
    """Login page"""
    st.title("🎵 Chords Online Class CRM")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.username == username, User.is_active == True).first()
                        if user and verify_password(password, user.hashed_password):
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                'id': user.id,
                                'username': user.username,
                                'full_name': user.full_name,
                                'role': user.role,
                                'instructor_name': user.instructor_name
                            }
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    finally:
                        db.close()
                else:
                    st.error("Please enter both username and password")
        
        st.info("Default credentials:\n- Admin: admin/admin123\n- Aditya: aditya/instructor123\n- Brahmani: brahmani/instructor123")

def main_app():
    """Main application after login"""
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.title("🎵 Chords Online Class CRM")
        st.write(f"Welcome, {user['full_name']}")
        st.write(f"Role: {user['role'].title()}")
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
        
        st.markdown("---")
        
        # Navigation based on role
        if user['role'] == 'admin':
            page = st.selectbox("Navigate", [
                "Dashboard", "Students", "Enrollments", "Payments", 
                "Attendance", "Schedule", "Materials", "Reports", 
                "Notifications", "Settings"
            ])
        elif user['role'] == 'instructor':
            page = st.selectbox("Navigate", [
                "Dashboard", "My Students", "My Schedule", "Attendance", 
                "Materials", "Payments"
            ])
        else:
            page = st.selectbox("Navigate", ["My Classes", "My Materials", "My Payments"])
    
    # Main content
    if page == "Dashboard":
        dashboard_page()
    elif page == "Students" or page == "My Students":
        students_page()
    elif page == "Enrollments":
        enrollments_page()
    elif page == "Payments" or page == "My Payments":
        payments_page()
    elif page == "Attendance":
        attendance_page()
    elif page == "Schedule" or page == "My Schedule":
        schedule_page()
    elif page == "Materials" or page == "My Materials":
        materials_page()
    elif page == "Reports":
        reports_page()
    elif page == "Notifications":
        notifications_page()
    elif page == "Settings":
        settings_page()

def dashboard_page():
    """Dashboard with key metrics"""
    st.title("📊 Dashboard")
    
    user = st.session_state.user
    db = SessionLocal()
    
    try:
        # Filter by instructor if not admin
        instructor_filter = user['instructor_name'] if user['role'] != 'admin' else None
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if instructor_filter:
                total_students = db.query(Student).filter(Student.instructor == instructor_filter, Student.is_active == True).count()
            else:
                total_students = db.query(Student).filter(Student.is_active == True).count()
            st.metric("Active Students", total_students)
        
        with col2:
            if instructor_filter:
                active_enrollments = db.query(Enrollment).join(Student).filter(
                    Student.instructor == instructor_filter, 
                    Enrollment.status == 'active'
                ).count()
            else:
                active_enrollments = db.query(Enrollment).filter(Enrollment.status == 'active').count()
            st.metric("Active Enrollments", active_enrollments)
        
        with col3:
            today = datetime.now().date()
            if instructor_filter:
                today_classes = db.query(ClassSchedule).join(Student).filter(
                    Student.instructor == instructor_filter,
                    ClassSchedule.class_date.cast(db.query(ClassSchedule.class_date).subquery().c.class_date.type) == today,
                    ClassSchedule.status == 'scheduled'
                ).count()
            else:
                today_classes = db.query(ClassSchedule).filter(
                    ClassSchedule.class_date.cast(db.query(ClassSchedule.class_date).subquery().c.class_date.type) == today,
                    ClassSchedule.status == 'scheduled'
                ).count()
            st.metric("Today's Classes", today_classes)
        
        with col4:
            # Expiring packages (next 7 days)
            next_week = datetime.now() + timedelta(days=7)
            if instructor_filter:
                expiring_packages = db.query(Enrollment).join(Student).filter(
                    Student.instructor == instructor_filter,
                    Enrollment.end_date <= next_week,
                    Enrollment.status == 'active'
                ).count()
            else:
                expiring_packages = db.query(Enrollment).filter(
                    Enrollment.end_date <= next_week,
                    Enrollment.status == 'active'
                ).count()
            st.metric("Expiring Packages (7 days)", expiring_packages, delta_color="inverse")
        
        st.markdown("---")
        
        # Recent activities
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Enrollments")
            if instructor_filter:
                recent_enrollments = db.query(Enrollment).join(Student).filter(
                    Student.instructor == instructor_filter
                ).order_by(Enrollment.created_at.desc()).limit(5).all()
            else:
                recent_enrollments = db.query(Enrollment).order_by(Enrollment.created_at.desc()).limit(5).all()
            
            if recent_enrollments:
                for enrollment in recent_enrollments:
                    st.write(f"• {enrollment.student.name} - {enrollment.package_name}")
            else:
                st.write("No recent enrollments")
        
        with col2:
            st.subheader("Recent Payments")
            if instructor_filter:
                recent_payments = db.query(Payment).join(Student).filter(
                    Student.instructor == instructor_filter
                ).order_by(Payment.created_at.desc()).limit(5).all()
            else:
                recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(5).all()
            
            if recent_payments:
                for payment in recent_payments:
                    st.write(f"• {payment.student.name} - ₹{payment.amount}")
            else:
                st.write("No recent payments")
    
    finally:
        db.close()

def students_page():
    """Students management page"""
    st.title("👥 Students")
    
    user = st.session_state.user
    db = SessionLocal()
    
    try:
        # Bulk Import Section
        st.subheader("📊 Bulk Import")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download Template"):
                from utils.bulk_import import create_student_template
                template_df = create_student_template()
                csv = template_df.to_csv(index=False)
                st.download_button(
                    label="Download Student Template",
                    data=csv,
                    file_name="student_template.csv",
                    mime="text/csv"
                )
        
        with col2:
            uploaded_file = st.file_uploader(
                "📤 Upload Students Excel/CSV",
                type=['xlsx', 'xls', 'csv'],
                help="Upload Excel or CSV file with student data"
            )
            
            if uploaded_file is not None:
                if st.button("Import Students"):
                    from utils.bulk_import import import_students_from_excel
                    
                    instructor_filter = None if user['role'] == 'admin' else user['instructor_name']
                    
                    success, message = import_students_from_excel(uploaded_file, instructor_filter)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown("---")
        
        # Add new student
        with st.expander("➕ Add New Student"):
            with st.form("add_student"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Name*")
                    email = st.text_input("Email")
                    
                    from utils.countries import get_country_options, extract_country_code
                    country_options = get_country_options()
                    default_index = next((i for i, option in enumerate(country_options) if "India" in option), 0)
                    
                    selected_country = st.selectbox(
                        "Country*", 
                        country_options,
                        index=default_index,
                        help="Type to search countries"
                    )
                    country_code = extract_country_code(selected_country)
                    
                    phone = st.text_input("Phone Number*", help=f"Without country code ({country_code})")
                    dob = st.date_input("Date of Birth", value=None)
                
                with col2:
                    if user['role'] == 'admin':
                        instructor = st.selectbox("Instructor*", Config.INSTRUCTORS)
                    else:
                        instructor = user['instructor_name']
                        st.write(f"Instructor: {instructor}")
                    
                    instrument = st.selectbox("Preferred Instrument", Config.INSTRUMENTS)
                    skill_level = st.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"])
                
                address = st.text_area("Address")
                notes = st.text_area("Notes")
                
                if st.form_submit_button("Add Student"):
                    if name and phone:
                        try:
                            student = Student(
                                name=name,
                                email=email if email else None,
                                country_code=country_code,
                                phone=phone,
                                date_of_birth=dob,
                                address=address,
                                instructor=instructor,
                                preferred_instrument=instrument,
                                skill_level=skill_level,
                                notes=notes
                            )
                            db.add(student)
                            db.commit()
                            st.success("Student added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding student: {str(e)}")
                            db.rollback()
                    else:
                        st.error("Name and Phone are required")
        
        # List students
        st.subheader("Students List")
        
        # Filter
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("Search by name")
        with col2:
            if user['role'] == 'admin':
                filter_instructor = st.selectbox("Filter by Instructor", ["All"] + Config.INSTRUCTORS)
            else:
                filter_instructor = user['instructor_name']
        with col3:
            filter_instrument = st.selectbox("Filter by Instrument", ["All"] + Config.INSTRUMENTS)
        
        # Query students
        query = db.query(Student).filter(Student.is_active == True)
        
        if user['role'] != 'admin':
            query = query.filter(Student.instructor == user['instructor_name'])
        elif filter_instructor != "All":
            query = query.filter(Student.instructor == filter_instructor)
        
        if search_name:
            query = query.filter(Student.name.ilike(f"%{search_name}%"))
        
        if filter_instrument != "All":
            query = query.filter(Student.preferred_instrument == filter_instrument)
        
        students = query.order_by(Student.name).all()
        
        if students:
            # Export functionality
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("📥 Export Students"):
                    export_data = []
                    for student in students:
                        export_data.append({
                            "name": student.name,
                            "email": student.email or "",
                            "country_code": student.country_code,
                            "phone": student.phone,
                            "whatsapp_number": student.whatsapp_number,
                            "date_of_birth": student.date_of_birth.strftime("%Y-%m-%d") if student.date_of_birth else "",
                            "address": student.address or "",
                            "instructor": student.instructor,
                            "preferred_instrument": student.preferred_instrument or "",
                            "skill_level": student.skill_level,
                            "timezone": student.timezone,
                            "notes": student.notes or ""
                        })
                    
                    export_df = pd.DataFrame(export_data)
                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"students_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            # Display as table
            students_data = []
            for student in students:
                students_data.append({
                    "ID": student.id,
                    "Name": student.name,
                    "Phone": student.phone,
                    "Instructor": student.instructor,
                    "Instrument": student.preferred_instrument,
                    "Skill Level": student.skill_level,
                    "Created": student.created_at.strftime("%Y-%m-%d") if student.created_at else ""
                })
            
            df = pd.DataFrame(students_data)
            st.dataframe(df, use_container_width=True)
            
            # Student details
            selected_student_id = st.selectbox("Select student for details", 
                                             options=[s.id for s in students],
                                             format_func=lambda x: next(s.name for s in students if s.id == x))
            
            if selected_student_id:
                student = next(s for s in students if s.id == selected_student_id)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Name:** {student.name}")
                    st.write(f"**Email:** {student.email or 'N/A'}")
                    st.write(f"**Phone:** {student.phone}")
                    st.write(f"**WhatsApp:** {student.whatsapp_number or student.phone}")
                    st.write(f"**Instructor:** {student.instructor}")
                
                with col2:
                    st.write(f"**Instrument:** {student.preferred_instrument}")
                    st.write(f"**Skill Level:** {student.skill_level}")
                    st.write(f"**DOB:** {student.date_of_birth.strftime('%Y-%m-%d') if student.date_of_birth else 'N/A'}")
                    st.write(f"**Timezone:** {student.timezone}")
                
                if student.address:
                    st.write(f"**Address:** {student.address}")
                if student.notes:
                    st.write(f"**Notes:** {student.notes}")
                
                # Edit button
                if st.button(f"✏️ Edit {student.name}", key=f"edit_{student.id}"):
                    st.session_state.edit_student_id = student.id
                    st.rerun()
        else:
            st.write("No students found")
    
    finally:
        db.close()

def payments_page():
    """Payments management page"""
    st.title("💰 Payments")
    
    user = st.session_state.user
    db = SessionLocal()
    
    try:
        # Add new payment
        with st.expander("➕ Record New Payment"):
            with st.form("add_payment"):
                # Get students for dropdown
                if user['role'] == 'admin':
                    students = db.query(Student).filter(Student.is_active == True).order_by(Student.name).all()
                else:
                    students = db.query(Student).filter(
                        Student.instructor == user['instructor_name'],
                        Student.is_active == True
                    ).order_by(Student.name).all()
                
                if students:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        student_id = st.selectbox("Student*", 
                                                options=[s.id for s in students],
                                                format_func=lambda x: next(s.name for s in students if s.id == x))
                        amount = st.number_input("Amount*", min_value=0.0, step=100.0)
                        payment_date = st.date_input("Payment Date*", value=datetime.now().date())
                        payment_method = st.selectbox("Payment Method", 
                                                    ["UPI", "Bank Transfer", "Cash", "Online", "Cheque"])
                    
                    with col2:
                        # Get enrollments for selected student
                        if student_id:
                            enrollments = db.query(Enrollment).filter(
                                Enrollment.student_id == student_id,
                                Enrollment.status == 'active'
                            ).all()
                            
                            if enrollments:
                                enrollment_id = st.selectbox("Enrollment (Optional)",
                                                           options=[None] + [e.id for e in enrollments],
                                                           format_func=lambda x: "Select..." if x is None else next(e.package_name for e in enrollments if e.id == x))
                            else:
                                enrollment_id = None
                                st.write("No active enrollments for this student")
                        
                        transaction_id = st.text_input("Transaction ID")
                        receipt_number = st.text_input("Receipt Number (auto-generated if empty)")
                        status = st.selectbox("Status", ["completed", "pending", "failed"])
                    
                    notes = st.text_area("Notes/Remarks")
                    
                    if st.form_submit_button("Record Payment"):
                        if student_id and amount > 0:
                            try:
                                from utils.helpers import generate_receipt_number
                                
                                if not receipt_number:
                                    receipt_number = generate_receipt_number()
                                
                                payment = Payment(
                                    student_id=student_id,
                                    enrollment_id=enrollment_id,
                                    receipt_number=receipt_number,
                                    amount=amount,
                                    payment_date=datetime.combine(payment_date, datetime.min.time()),
                                    payment_method=payment_method,
                                    transaction_id=transaction_id,
                                    status=status,
                                    notes=notes
                                )
                                db.add(payment)
                                db.commit()
                                
                                # Send WhatsApp receipt if payment is completed
                                if status == "completed":
                                    try:
                                        student = db.query(Student).get(student_id)
                                        enrollment = db.query(Enrollment).get(enrollment_id) if enrollment_id else None
                                        package_name = enrollment.package_name if enrollment else "General Payment"
                                        
                                        fast2sms = Fast2SMSService()
                                        fast2sms.send_payment_receipt(
                                            student_name=student.name,
                                            student_id=student.id,
                                            phone_number=student.whatsapp_number or student.phone,
                                            amount=str(amount),
                                            receipt_no=receipt_number,
                                            package_name=package_name,
                                            payment_date=payment_date.strftime("%d-%m-%Y"),
                                            remarks=notes or ""
                                        )
                                        st.success("Payment recorded and receipt sent via WhatsApp!")
                                    except Exception as e:
                                        st.warning(f"Payment recorded but WhatsApp failed: {str(e)}")
                                else:
                                    st.success("Payment recorded successfully!")
                                
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error recording payment: {str(e)}")
                                db.rollback()
                        else:
                            st.error("Student and Amount are required")
                else:
                    st.write("No students available")
        
        # List payments
        st.subheader("Payments History")
        
        # Filter
        col1, col2, col3 = st.columns(3)
        with col1:
            date_from = st.date_input("From Date", value=datetime.now().date() - timedelta(days=30))
        with col2:
            date_to = st.date_input("To Date", value=datetime.now().date())
        with col3:
            filter_status = st.selectbox("Status", ["All", "completed", "pending", "failed"])
        
        # Query payments
        query = db.query(Payment).join(Student)
        
        if user['role'] != 'admin':
            query = query.filter(Student.instructor == user['instructor_name'])
        
        query = query.filter(
            Payment.payment_date >= datetime.combine(date_from, datetime.min.time()),
            Payment.payment_date <= datetime.combine(date_to, datetime.max.time())
        )
        
        if filter_status != "All":
            query = query.filter(Payment.status == filter_status)
        
        payments = query.order_by(Payment.payment_date.desc()).all()
        
        if payments:
            payments_data = []
            total_amount = 0
            
            for payment in payments:
                payments_data.append({
                    "Receipt No": payment.receipt_number,
                    "Student": payment.student.name,
                    "Amount": f"₹{payment.amount}",
                    "Date": payment.payment_date.strftime("%Y-%m-%d"),
                    "Method": payment.payment_method,
                    "Status": payment.status.title(),
                    "Transaction ID": payment.transaction_id or ""
                })
                if payment.status == "completed":
                    total_amount += float(payment.amount)
            
            df = pd.DataFrame(payments_data)
            st.dataframe(df, use_container_width=True)
            
            st.metric("Total Completed Payments", f"₹{total_amount:,.2f}")
        else:
            st.write("No payments found for the selected period")
    
    finally:
        db.close()

def schedule_page():
    """Class scheduling page"""
    st.title("📅 Class Schedule")
    st.write("Schedule management functionality would be implemented here")

def attendance_page():
    """Attendance tracking page"""
    st.title("✅ Attendance")
    st.write("Attendance tracking functionality would be implemented here")

def materials_page():
    """Materials management page"""
    st.title("📚 Materials")
    st.write("Materials management functionality would be implemented here")

def enrollments_page():
    """Enrollments management page"""
    st.title("📝 Enrollments")
    st.write("Enrollments management functionality would be implemented here")

def reports_page():
    """Reports page"""
    st.title("📊 Reports")
    st.write("Reports functionality would be implemented here")

def notifications_page():
    """Notifications management page"""
    st.title("📱 Notifications")
    st.write("Notifications management functionality would be implemented here")

def settings_page():
    """Settings page"""
    st.title("⚙️ Settings")
    st.write("Settings functionality would be implemented here")

# Main app logic
def main():
    # Run database migration first
    try:
        import sqlite3
        import os
        
        db_path = "data/chords_crm.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if country_code column exists
            cursor.execute("PRAGMA table_info(students)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'country_code' not in columns:
                cursor.execute("ALTER TABLE students ADD COLUMN country_code VARCHAR(5) DEFAULT '+91'")
                conn.commit()
            
            conn.close()
    except Exception as e:
        pass  # Ignore migration errors, will create fresh DB
    
    # Initialize default users
    init_default_users()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()