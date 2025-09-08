# Simple fix - remove timezone and add edit button
# Replace the student creation part in app.py

# Remove timezone from form:
# timezone = st.text_input("Timezone", value="Asia/Kolkata")  # DELETE THIS LINE

# Update student creation to not use timezone:
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
    # timezone=timezone,  # REMOVE THIS LINE
    notes=notes
)

# Add edit button after student details:
if st.button(f"✏️ Edit {student.name}"):
    st.session_state.edit_mode = student.id
    st.rerun()