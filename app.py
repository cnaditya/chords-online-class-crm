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

# Enhanced page config with custom CSS
st.set_page_config(
    page_title="Chords Music Academy CRM",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f4e79;
        --secondary-color: #2e86ab;
        --accent-color: #a23b72;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --light-bg: #f8f9fa;
        --dark-text: #2c3e50;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid var(--secondary-color);
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Form styling */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--primary-color), var(--secondary-color));
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Status badges */
    .status-active { 
        background: var(--success-color); 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 15px; 
        font-size: 0.8rem;
    }
    
    .status-pending { 
        background: var(--warning-color); 
        color: white; 
        padding: 0.25rem 0.5rem; 
        border-radius: 15px; 
        font-size: 0.8rem;
    }
    
    /* Section headers */
    .section-header {
        color: var(--primary-color);
        border-bottom: 2px solid var(--secondary-color);
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Quick stats */
    .quick-stat {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Action buttons */
    .action-btn {
        background: var(--accent-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .action-btn:hover {
        background: #8b2f5f;
        transform: scale(1.05);
    }
    
    /* Search and filter section */
    .filter-section {
        background: var(--light-bg);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

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
    """Enhanced login page with better UX"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎵 Chords Music Academy</h1>
        <h3>Student Management System</h3>
        <p>Empowering musical education through technology</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form in centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown('<div class="section-header"><h2>🔐 Login</h2></div>', unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    submit = st.form_submit_button("🚀 Login", use_container_width=True)
                
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
                                st.success("🎉 Login successful! Redirecting...")
                                st.rerun()
                            else:
                                st.error("❌ Invalid credentials. Please try again.")
                        finally:
                            db.close()
                    else:
                        st.warning("⚠️ Please enter both username and password")
        
        # Credentials info
        with st.expander("🔑 Demo Credentials", expanded=True):
            st.markdown("""
            **Administrator Access:**
            - Username: `admin` | Password: `admin123`
            
            **Instructor Access:**
            - Username: `aditya` | Password: `instructor123`
            - Username: `brahmani` | Password: `instructor123`
            """)

def main_app():
    """Enhanced main application with better navigation"""
    user = st.session_state.user
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; margin-bottom: 1rem;">
            <h2>🎵 Chords CRM</h2>
            <p><strong>{user['full_name']}</strong></p>
            <span class="status-active">{user['role'].title()}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
        
        st.markdown("---")
        
        # Enhanced navigation with icons
        if user['role'] == 'admin':
            nav_options = {
                "📊 Dashboard": "Dashboard",
                "👥 Students": "Students", 
                "📝 Enrollments": "Enrollments",
                "💰 Payments": "Payments",
                "✅ Attendance": "Attendance",
                "📅 Schedule": "Schedule",
                "📚 Materials": "Materials",
                "📈 Reports": "Reports",
                "📱 Notifications": "Notifications",
                "⚙️ Settings": "Settings"
            }
        elif user['role'] == 'instructor':
            nav_options = {
                "📊 Dashboard": "Dashboard",
                "👥 My Students": "My Students",
                "📅 My Schedule": "My Schedule", 
                "✅ Attendance": "Attendance",
                "📚 Materials": "Materials",
                "💰 Payments": "Payments"
            }
        else:
            nav_options = {
                "📚 My Classes": "My Classes",
                "📖 My Materials": "My Materials", 
                "💳 My Payments": "My Payments"
            }
        
        selected_nav = st.selectbox("Navigate", list(nav_options.keys()))
        page = nav_options[selected_nav]
    
    # Main content with better spacing
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
    """Enhanced dashboard with better metrics visualization"""
    st.markdown('<div class="main-header"><h1>📊 Dashboard Overview</h1><p>Real-time insights into your music academy</p></div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    db = SessionLocal()
    
    try:
        instructor_filter = user['instructor_name'] if user['role'] != 'admin' else None
        
        # Enhanced metrics with better styling
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if instructor_filter:
                total_students = db.query(Student).filter(Student.instructor == instructor_filter, Student.is_active == True).count()
            else:
                total_students = db.query(Student).filter(Student.is_active == True).count()
            
            st.markdown(f"""
            <div class="quick-stat">
                <h2>👥</h2>
                <h3>{total_students}</h3>
                <p>Active Students</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if instructor_filter:
                active_enrollments = db.query(Enrollment).join(Student).filter(
                    Student.instructor == instructor_filter, 
                    Enrollment.status == 'active'
                ).count()
            else:
                active_enrollments = db.query(Enrollment).filter(Enrollment.status == 'active').count()
            
            st.markdown(f"""
            <div class="quick-stat">
                <h2>📝</h2>
                <h3>{active_enrollments}</h3>
                <p>Active Enrollments</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            today = datetime.now().date()
            today_classes = 0  # Placeholder
            
            st.markdown(f"""
            <div class="quick-stat">
                <h2>📅</h2>
                <h3>{today_classes}</h3>
                <p>Today's Classes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            expiring_packages = 0  # Placeholder
            
            st.markdown(f"""
            <div class="quick-stat">
                <h2>⚠️</h2>
                <h3>{expiring_packages}</h3>
                <p>Expiring Soon</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Enhanced activity sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header"><h3>📈 Recent Activity</h3></div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown("""
                <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p>🎯 <strong>New Student:</strong> John Doe enrolled in Piano</p>
                    <p>💰 <strong>Payment:</strong> ₹5,000 received from Jane Smith</p>
                    <p>📅 <strong>Class:</strong> Guitar lesson completed with Mike</p>
                    <p>📝 <strong>Enrollment:</strong> Sarah joined Carnatic Vocal</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-header"><h3>💰 Revenue Overview</h3></div>', unsafe_allow_html=True)
            
            # Sample revenue data
            revenue_data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'Revenue': [45000, 52000, 48000, 61000, 58000]
            })
            
            st.line_chart(revenue_data.set_index('Month'))
    
    finally:
        db.close()

def students_page():
    """Enhanced students page with better UX"""
    st.markdown('<div class="main-header"><h1>👥 Student Management</h1><p>Manage your students efficiently</p></div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    db = SessionLocal()
    
    try:
        # Enhanced action bar
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add Student", use_container_width=True):
                st.session_state.show_add_form = True
        
        with col2:
            if st.button("📥 Download Template", use_container_width=True):
                from utils.bulk_import import create_student_template
                template_df = create_student_template()
                csv = template_df.to_csv(index=False)
                st.download_button(
                    label="📄 Get Template",
                    data=csv,
                    file_name="student_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col3:
            uploaded_file = st.file_uploader(
                "📤 Bulk Import",
                type=['xlsx', 'xls', 'csv'],
                help="Upload Excel or CSV file"
            )
        
        with col4:
            if uploaded_file and st.button("🚀 Import", use_container_width=True):
                from utils.bulk_import import import_students_from_excel
                instructor_filter = None if user['role'] == 'admin' else user['instructor_name']
                success, message = import_students_from_excel(uploaded_file, instructor_filter)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        st.markdown("---")
        
        # Enhanced add student form
        if st.session_state.get('show_add_form', False):
            with st.container():
                st.markdown('<div class="section-header"><h3>➕ Add New Student</h3></div>', unsafe_allow_html=True)
                
                with st.form("add_student", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("👤 Full Name *", placeholder="Enter student's full name")
                        email = st.text_input("📧 Email", placeholder="student@example.com")
                        
                        from utils.countries import get_country_options, extract_country_code
                        country_options = get_country_options()
                        default_index = next((i for i, option in enumerate(country_options) if "India" in option), 0)
                        
                        selected_country = st.selectbox("🌍 Country *", country_options, index=default_index)
                        country_code = extract_country_code(selected_country)
                        
                        phone = st.text_input("📱 Phone Number *", placeholder=f"Without {country_code}")
                        dob = st.date_input("🎂 Date of Birth", value=None, min_value=datetime(1940, 1, 1).date(), max_value=datetime(2090, 12, 31).date())
                    
                    with col2:
                        if user['role'] == 'admin':
                            instructor = st.selectbox("👨‍🏫 Instructor *", Config.INSTRUCTORS)
                        else:
                            instructor = user['instructor_name']
                            st.info(f"👨‍🏫 Instructor: **{instructor}**")
                        
                        instrument = st.selectbox("🎹 Preferred Instrument", Config.INSTRUMENTS)
                        skill_level = st.selectbox("📊 Skill Level", ["Beginner", "Intermediate", "Advanced"])
                        address = st.text_area("🏠 Address", placeholder="Enter full address")
                    
                    notes = st.text_area("📝 Notes", placeholder="Any additional information...")
                    
                    col_a, col_b, col_c = st.columns([1, 1, 1])
                    with col_a:
                        if st.form_submit_button("✅ Add Student", use_container_width=True):
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
                                    st.success("🎉 Student added successfully!")
                                    st.session_state.show_add_form = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                                    db.rollback()
                            else:
                                st.error("⚠️ Name and Phone are required")
                    
                    with col_c:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.show_add_form = False
                            st.rerun()
        
        # Enhanced filters
        st.markdown('<div class="section-header"><h3>🔍 Search & Filter</h3></div>', unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                search_name = st.text_input("🔍 Search by name", placeholder="Type student name...")
            
            with col2:
                if user['role'] == 'admin':
                    filter_instructor = st.selectbox("👨‍🏫 Instructor", ["All"] + Config.INSTRUCTORS)
                else:
                    filter_instructor = user['instructor_name']
                    st.info(f"Showing: **{filter_instructor}'s students**")
            
            with col3:
                filter_instrument = st.selectbox("🎹 Instrument", ["All"] + Config.INSTRUMENTS)
            
            with col4:
                filter_skill = st.selectbox("📊 Skill Level", ["All", "Beginner", "Intermediate", "Advanced"])
        
        # Query students with filters
        query = db.query(Student).filter(Student.is_active == True)
        
        if user['role'] != 'admin':
            query = query.filter(Student.instructor == user['instructor_name'])
        elif filter_instructor != "All":
            query = query.filter(Student.instructor == filter_instructor)
        
        if search_name:
            query = query.filter(Student.name.ilike(f"%{search_name}%"))
        
        if filter_instrument != "All":
            query = query.filter(Student.preferred_instrument == filter_instrument)
        
        if filter_skill != "All":
            query = query.filter(Student.skill_level == filter_skill)
        
        students = query.order_by(Student.name).all()
        
        st.markdown("---")
        
        if students:
            # Enhanced student display - collapsed by default
            with st.expander(f"📋 Students List ({len(students)} found)", expanded=False):
                # Export button
                col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("📥 Export All", use_container_width=True):
                    export_data = []
                    for student in students:
                        export_data.append({
                            "name": student.name,
                            "email": student.email or "",
                            "country_code": student.country_code,
                            "phone": student.phone,
                            "whatsapp_number": student.whatsapp_number,
                            "instructor": student.instructor,
                            "preferred_instrument": student.preferred_instrument or "",
                            "skill_level": student.skill_level,
                            "notes": student.notes or ""
                        })
                    
                    export_df = pd.DataFrame(export_data)
                    csv = export_df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv,
                        file_name=f"students_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            # Enhanced student cards
            for i, student in enumerate(students):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="padding: 1rem;">
                            <h4>👤 {student.name}</h4>
                            <p><strong>ID:</strong> CMA{student.id}</p>
                            <p>📧 {student.email or 'No email'}</p>
                            <p>📱 {student.whatsapp_number}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="padding: 1rem;">
                            <p><strong>👨‍🏫 Instructor:</strong> {student.instructor}</p>
                            <p><strong>🎹 Instrument:</strong> {student.preferred_instrument}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style="padding: 1rem;">
                            <span class="status-active">📊 {student.skill_level}</span><br><br>
                            <small>📅 Added: {student.created_at.strftime('%Y-%m-%d') if student.created_at else 'N/A'}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        if st.button("✏️ Edit", key=f"edit_{student.id}", use_container_width=True):
                            st.session_state.edit_student_id = student.id
                            st.rerun()
                
                if i < len(students) - 1:
                    st.markdown("---")
        
        # Enhanced edit form
        if st.session_state.get('edit_student_id'):
            edit_student = db.query(Student).get(st.session_state.edit_student_id)
            if edit_student:
                st.markdown("---")
                st.markdown(f'<div class="section-header"><h3>✏️ Edit Student: {edit_student.name}</h3></div>', unsafe_allow_html=True)
                
                with st.form("edit_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("👤 Name", value=edit_student.name)
                        new_email = st.text_input("📧 Email", value=edit_student.email or "")
                        new_phone = st.text_input("📱 Phone", value=edit_student.phone)
                    
                    with col2:
                        new_instructor = st.selectbox("👨‍🏫 Instructor", Config.INSTRUCTORS, 
                                                    index=Config.INSTRUCTORS.index(edit_student.instructor))
                        new_instrument = st.selectbox("🎹 Instrument", Config.INSTRUMENTS,
                                                    index=Config.INSTRUMENTS.index(edit_student.preferred_instrument))
                        new_skill = st.selectbox("📊 Skill", ["Beginner", "Intermediate", "Advanced"],
                                               index=["Beginner", "Intermediate", "Advanced"].index(edit_student.skill_level))
                    
                    new_notes = st.text_area("📝 Notes", value=edit_student.notes or "")
                    
                    col_a, col_b, col_c = st.columns([1, 1, 1])
                    with col_a:
                        if st.form_submit_button("💾 Update Student", use_container_width=True):
                            edit_student.name = new_name
                            edit_student.email = new_email if new_email else None
                            edit_student.phone = new_phone
                            edit_student.instructor = new_instructor
                            edit_student.preferred_instrument = new_instrument
                            edit_student.skill_level = new_skill
                            edit_student.notes = new_notes if new_notes else None
                            db.commit()
                            st.success("🎉 Student updated successfully!")
                            del st.session_state.edit_student_id
                            st.rerun()
                    
                    with col_b:
                        if st.form_submit_button("🗑️ Delete Student", use_container_width=True, type="secondary"):
                            if st.session_state.get('confirm_delete') == edit_student.id:
                                edit_student.is_active = False
                                db.commit()
                                st.success("🗑️ Student deleted successfully!")
                                del st.session_state.edit_student_id
                                if 'confirm_delete' in st.session_state:
                                    del st.session_state.confirm_delete
                                st.rerun()
                            else:
                                st.session_state.confirm_delete = edit_student.id
                                st.warning("⚠️ Click Delete again to confirm")
                    
                    with col_c:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            del st.session_state.edit_student_id
                            if 'confirm_delete' in st.session_state:
                                del st.session_state.confirm_delete
                            st.rerun()
        
        if not students:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 10px;">
                <h3>🔍 No students found</h3>
                <p>Try adjusting your search criteria or add a new student</p>
            </div>
            """, unsafe_allow_html=True)
    
    finally:
        db.close()

def payments_page():
    """Enhanced payments page"""
    st.markdown('<div class="main-header"><h1>💰 Payment Management</h1><p>Track and manage all payments</p></div>', unsafe_allow_html=True)
    st.info("🚧 Payment functionality will be implemented here")

def schedule_page():
    """Enhanced schedule page"""
    st.markdown('<div class="main-header"><h1>📅 Class Schedule</h1><p>Manage class schedules and bookings</p></div>', unsafe_allow_html=True)
    st.info("🚧 Schedule functionality will be implemented here")

def attendance_page():
    """Enhanced attendance page"""
    st.markdown('<div class="main-header"><h1>✅ Attendance Tracking</h1><p>Monitor student attendance</p></div>', unsafe_allow_html=True)
    st.info("🚧 Attendance functionality will be implemented here")

def materials_page():
    """Enhanced materials page"""
    st.markdown('<div class="main-header"><h1>📚 Learning Materials</h1><p>Manage course materials and resources</p></div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    db = SessionLocal()
    
    try:
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add Material", use_container_width=True):
                st.session_state.show_add_material = True
        
        with col2:
            if st.button("📤 Share to Students", use_container_width=True):
                st.session_state.show_share_material = True
        
        st.markdown("---")
        
        # Add material form
        if st.session_state.get('show_add_material', False):
            st.markdown('<div class="section-header"><h3>➕ Add New Material</h3></div>', unsafe_allow_html=True)
            
            with st.form("add_material"):
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("📝 Material Title *", placeholder="e.g., Piano Scales Practice")
                    description = st.text_area("📄 Description", placeholder="Brief description")
                    material_type = st.selectbox("📁 Type", ["PDF", "Video", "Audio", "Link", "Document"])
                
                with col2:
                    instrument = st.selectbox("🎹 Instrument", Config.INSTRUMENTS)
                    skill_level = st.selectbox("📊 Skill Level", ["Beginner", "Intermediate", "Advanced", "All Levels"])
                    file_url = st.text_input("🔗 URL/Link", placeholder="https://example.com/material")
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.form_submit_button("✅ Add Material", use_container_width=True):
                        if title and instrument and skill_level:
                            try:
                                material = Material(
                                    title=title,
                                    description=description,
                                    material_type=material_type,
                                    instrument=instrument,
                                    skill_level=skill_level,
                                    file_url=file_url or None,
                                    uploaded_by=user['id']
                                )
                                db.add(material)
                                db.commit()
                                st.success("🎉 Material added successfully!")
                                st.session_state.show_add_material = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                db.rollback()
                        else:
                            st.error("⚠️ Title, Instrument, and Skill Level are required")
                
                with col_b:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_add_material = False
                        st.rerun()
        
        # Share material form
        if st.session_state.get('show_share_material', False):
            st.markdown('<div class="section-header"><h3>📤 Share Material with Students</h3></div>', unsafe_allow_html=True)
            
            with st.form("share_material"):
                col1, col2 = st.columns(2)
                
                with col1:
                    materials = db.query(Material).all()
                    if materials:
                        material_id = st.selectbox("📚 Select Material", 
                                                 options=[m.id for m in materials],
                                                 format_func=lambda x: next(m.title for m in materials if m.id == x))
                    else:
                        st.warning("No materials available. Add materials first.")
                        material_id = None
                
                with col2:
                    share_instrument = st.selectbox("🎹 Instrument", ["All"] + Config.INSTRUMENTS)
                    share_skill = st.selectbox("📊 Skill Level", ["All", "Beginner", "Intermediate", "Advanced"])
                    if user['role'] == 'admin':
                        share_instructor = st.selectbox("👨🏫 Instructor", ["All"] + Config.INSTRUCTORS)
                    else:
                        share_instructor = user['instructor_name']
                        st.info(f"Sharing to: **{share_instructor}'s students**")
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.form_submit_button("📤 Share Material", use_container_width=True):
                        if material_id:
                            try:
                                query = db.query(Student).filter(Student.is_active == True)
                                
                                if user['role'] != 'admin':
                                    query = query.filter(Student.instructor == user['instructor_name'])
                                elif share_instructor != "All":
                                    query = query.filter(Student.instructor == share_instructor)
                                
                                if share_instrument != "All":
                                    query = query.filter(Student.preferred_instrument == share_instrument)
                                
                                if share_skill != "All":
                                    query = query.filter(Student.skill_level == share_skill)
                                
                                target_students = query.all()
                                material = db.query(Material).get(material_id)
                                sent_count = len(target_students)
                                
                                st.success(f"🎉 Material '{material.title}' shared with {sent_count} students!")
                                st.session_state.show_share_material = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                        else:
                            st.error("⚠️ Please select a material to share")
                
                with col_b:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_share_material = False
                        st.rerun()
        
        # Materials library
        st.markdown('<div class="section-header"><h3>📚 Materials Library</h3></div>', unsafe_allow_html=True)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_instrument = st.selectbox("🎹 Filter Instrument", ["All"] + Config.INSTRUMENTS, key="mat_inst")
        with col2:
            filter_skill = st.selectbox("📊 Filter Skill", ["All", "Beginner", "Intermediate", "Advanced"], key="mat_skill")
        with col3:
            filter_type = st.selectbox("📁 Filter Type", ["All", "PDF", "Video", "Audio", "Link", "Document"], key="mat_type")
        
        # Query materials
        query = db.query(Material)
        
        if filter_instrument != "All":
            query = query.filter(Material.instrument == filter_instrument)
        if filter_skill != "All":
            query = query.filter(Material.skill_level == filter_skill)
        if filter_type != "All":
            query = query.filter(Material.material_type == filter_type)
        
        materials = query.order_by(Material.created_at.desc()).all()
        
        if materials:
            for material in materials:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="padding: 1rem;">
                            <h4>📚 {material.title}</h4>
                            <p>{material.description or 'No description'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="padding: 1rem;">
                            <p><strong>🎹 Instrument:</strong> {material.instrument}</p>
                            <p><strong>📁 Type:</strong> {material.material_type}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style="padding: 1rem;">
                            <span class="status-active">📊 {material.skill_level}</span><br><br>
                            <small>📅 Added: {material.created_at.strftime('%Y-%m-%d') if material.created_at else 'N/A'}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        if material.file_url:
                            st.link_button("🔗 Open", material.file_url, use_container_width=True)
                
                st.markdown("---")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 10px;">
                <h3>📚 No materials found</h3>
                <p>Add materials to start building your library</p>
            </div>
            """, unsafe_allow_html=True)
    
    finally:
        db.close()

def enrollments_page():
    """Enhanced enrollments page"""
    st.markdown('<div class="main-header"><h1>📝 Student Enrollments</h1><p>Manage course enrollments and packages</p></div>', unsafe_allow_html=True)
    st.info("🚧 Enrollments functionality will be implemented here")

def reports_page():
    """Enhanced reports page"""
    st.markdown('<div class="main-header"><h1>📈 Reports & Analytics</h1><p>Insights and performance metrics</p></div>', unsafe_allow_html=True)
    st.info("🚧 Reports functionality will be implemented here")

def notifications_page():
    """Enhanced notifications page"""
    st.markdown('<div class="main-header"><h1>📱 Notifications</h1><p>Manage WhatsApp and email notifications</p></div>', unsafe_allow_html=True)
    st.info("🚧 Notifications functionality will be implemented here")

def settings_page():
    """Enhanced settings page"""
    st.markdown('<div class="main-header"><h1>⚙️ System Settings</h1><p>Configure system preferences</p></div>', unsafe_allow_html=True)
    st.info("🚧 Settings functionality will be implemented here")

# Main app logic
def main():
    # Database migration - recreate table to remove email unique constraint
    try:
        import sqlite3
        import os
        
        db_path = "data/chords_crm.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Force recreate students table without unique email constraint
            cursor.execute("DROP TABLE IF EXISTS students_backup")
            cursor.execute("CREATE TABLE students_backup AS SELECT * FROM students")
            cursor.execute("DROP TABLE students")
            
            # Create new table without unique constraint on email
            cursor.execute("""
                CREATE TABLE students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    country_code VARCHAR(5) DEFAULT '+91',
                    phone VARCHAR(20) NOT NULL,
                    whatsapp_number VARCHAR(25),
                    date_of_birth DATE,
                    address TEXT,
                    instructor VARCHAR(50) NOT NULL,
                    preferred_instrument VARCHAR(50),
                    skill_level VARCHAR(20) DEFAULT 'Beginner',
                    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Copy data back
            cursor.execute("INSERT INTO students SELECT * FROM students_backup")
            cursor.execute("DROP TABLE students_backup")
            
            conn.commit()
            conn.close()
    except Exception as e:
        pass
    
    # Initialize default users
    init_default_users()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()