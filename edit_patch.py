# Add this code right before the "else: st.write('No students found')" line in students_page()

        # Edit form
        if 'edit_student_id' in st.session_state and st.session_state.edit_student_id:
            edit_student = db.query(Student).get(st.session_state.edit_student_id)
            if edit_student:
                st.markdown("---")
                st.subheader(f"✏️ Edit {edit_student.name}")
                
                with st.form("edit_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Name", value=edit_student.name)
                        new_email = st.text_input("Email", value=edit_student.email or "")
                        new_phone = st.text_input("Phone", value=edit_student.phone)
                    
                    with col2:
                        new_instructor = st.selectbox("Instructor", Config.INSTRUCTORS, 
                                                    index=Config.INSTRUCTORS.index(edit_student.instructor))
                        new_instrument = st.selectbox("Instrument", Config.INSTRUMENTS,
                                                    index=Config.INSTRUMENTS.index(edit_student.preferred_instrument))
                        new_skill = st.selectbox("Skill", ["Beginner", "Intermediate", "Advanced"],
                                               index=["Beginner", "Intermediate", "Advanced"].index(edit_student.skill_level))
                    
                    new_notes = st.text_area("Notes", value=edit_student.notes or "")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Update"):
                            edit_student.name = new_name
                            edit_student.email = new_email if new_email else None
                            edit_student.phone = new_phone
                            edit_student.instructor = new_instructor
                            edit_student.preferred_instrument = new_instrument
                            edit_student.skill_level = new_skill
                            edit_student.notes = new_notes if new_notes else None
                            db.commit()
                            st.success("Student updated!")
                            del st.session_state.edit_student_id
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            del st.session_state.edit_student_id
                            st.rerun()