def materials_page():
    """Enhanced materials page"""
    st.markdown('<div class="main-header"><h1>📚 Learning Materials</h1><p>Manage course materials and resources</p></div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    db = SessionLocal()
    
    try:
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Add Material", use_container_width=True):
                st.session_state.show_add_material = True
        
        with col2:
            if st.button("📤 Share Material", use_container_width=True):
                st.session_state.show_share_material = True
        
        st.markdown("---")
        
        # Add material form
        if st.session_state.get('show_add_material', False):
            st.markdown('<div class="section-header"><h3>➕ Add New Material</h3></div>', unsafe_allow_html=True)
            
            with st.form("add_material"):
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("📝 Material Title *", placeholder="e.g., Piano Scales Practice")
                    description = st.text_area("📄 Description", placeholder="Brief description of the material")
                    material_type = st.selectbox("📁 Type", ["PDF", "Video", "Audio", "Document", "Link", "Image"])
                
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
                    materials = db.query(Material).filter(Material.is_active == True).all()
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
        
        # Materials list
        st.markdown('<div class="section-header"><h3>📚 Materials Library</h3></div>', unsafe_allow_html=True)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_instrument = st.selectbox("🎹 Filter by Instrument", ["All"] + Config.INSTRUMENTS, key="mat_inst")
        with col2:
            filter_skill = st.selectbox("📊 Filter by Skill", ["All", "Beginner", "Intermediate", "Advanced"], key="mat_skill")
        with col3:
            filter_type = st.selectbox("📁 Filter by Type", ["All", "PDF", "Video", "Audio", "Document", "Link", "Image"], key="mat_type")
        
        # Query materials
        query = db.query(Material).filter(Material.is_active == True)
        
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