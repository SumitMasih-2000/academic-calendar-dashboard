import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import base64

# Set wide layout configuration and theme colors
st.set_page_config(page_title="Academic Task & Hours Tracker", layout="wide")

# Inject FontAwesome styling framework
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
    unsafe_allow_html=True
)

# Custom layout and sleek typography styles
st.markdown("""
    <style>
    /* Global Background and Typography Setup */
    .stApp { background-color: #F8FAFC; }
    
    .title-container {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 5px;
    }
    .main-title { font-size: 32px; font-weight: 700; color: #1E293B; margin: 0; }
    .sub-title { font-size: 15px; color: #64748B; margin-top: 5px; margin-bottom: 25px; }
    .section-header { font-size: 20px; font-weight: 600; color: #1E293B; margin-top: 20px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
    
    /* Filter Grid Custom Styling */
    .filter-header { 
        font-size: 14px; 
        font-weight: 600; 
        color: #475569;
        margin-bottom: 8px; 
        display: flex; 
        align-items: center; 
    }
    .icon-spacing { margin-right: 8px; color: #0EA5E9; font-size: 16px; }
    .custom-icon { width: 22px; height: 22px; margin-right: 8px; object-fit: contain; }
    .main-header-icon { width: 42px; height: 42px; object-fit: contain; }
    
    /* Premium Timeline Container Cards */
    .todo-box {
        padding: 18px 22px;
        border-radius: 12px;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 6px solid #0EA5E9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 14px;
    }
    .todo-title { font-size: 17px; font-weight: 600; color: #0F172A; margin: 0 0 6px 0; display: flex; align-items: center; gap: 8px; }
    .todo-meta { font-size: 13px; color: #64748B; margin: 0 0 8px 0; }
    .todo-status { font-size: 13px; font-weight: 600; margin: 0; display: flex; align-items: center; gap: 6px; }
    
    /* Premium Minimalist Sidebar KPI Cards */
    .kpi-card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(15, 23, 42, 0.04);
        border: 1px solid #E2E8F0;
        text-align: left;
        margin-bottom: 12px;
    }
    .kpi-title { font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.75px; }
    .kpi-value { font-size: 24px; color: #0F172A; font-weight: 700; margin-top: 4px; }
    
    /* Calendar Standard UI Elements Overrides */
    .fc-theme-standard .fc-scrollgrid { border-color: #E2E8F0 !important; background-color: #FFFFFF; }
    .fc-header-toolbar .fc-button-primary { background-color: #0EA5E9 !important; border-color: #0EA5E9 !important; font-weight: 500 !important; }
    .fc-header-toolbar .fc-button-primary:hover { background-color: #0284C7 !important; border-color: #0284C7 !important; }
    .fc .fc-daygrid-day.fc-day-today { background-color: #F0F9FF !important; }
    </style>
""", unsafe_allow_html=True)

# Safe Image Extraction Utility
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return ""

# Convert all assets to string tokens safely
main_calendar_base64 = get_image_base64("image_1134f1.png")
course_icon_base64 = get_image_base64("image_2b21c2.png")
trainer_icon_base64 = get_image_base64("image_2b217d.png")

def get_empty_dataframe():
    return pd.DataFrame(columns=[
        "Task ID", "Task Name", "University", "Course", 
        "Trainer", "Date", "Total Allocated Hours", "Completed Hours", "Remaining Hours"
    ])

def clean_and_map_dataframe(raw_df):
    processed_df = raw_df.copy()
    processed_df.columns = processed_df.columns.astype(str).str.strip().str.lower()
    
    mapping_dictionary = {
        'task id': ['task id', 'id', 'task_id', 'sr no', 'sr. no.', 'index'],
        'task name': ['task name', 'task', 'title', 'event', 'assignment', 'task_name', 'name', 'todo', 'to do'],
        'university': ['university', 'univ', 'college', 'institution', 'school', 'varsity'],
        'course': ['course', 'subject', 'program', 'class', 'branch'],
        'trainer': ['trainer', 'instructor', 'teacher', 'professor', 'faculty', 'dr.', 'mentor'],
        'date': ['date', 'task date', 'due date', 'schedule date', 'timeline', 'day', 'timestamp'],
        'total allocated hours': ['total allocated hours', 'total hours', 'allocated hours', 'hours', 'duration', 'total_hours', 'allocated_hours'],
        'completed hours': ['completed hours', 'hours completed', 'done', 'hours done', 'completed_hours', 'hrs completed']
    }
    
    final_df = pd.DataFrame()
    
    for standard_key, variations in mapping_dictionary.items():
        matched_col = None
        for col in processed_df.columns:
            if col in variations:
                matched_col = col
                break
        
        if matched_col is not None:
            final_df[standard_key] = processed_df[matched_col]
        else:
            if standard_key == 'task id':
                final_df[standard_key] = range(1, len(processed_df) + 1)
            elif standard_key in ['total allocated hours', 'completed hours']:
                final_df[standard_key] = 0.0
            elif standard_key == 'date':
                final_df[standard_key] = datetime.today().date()
            else:
                final_df[standard_key] = "General"
                
    final_df['date'] = pd.to_datetime(final_df['date'], errors='coerce').dt.date
    final_df['date'] = final_df['date'].fillna(datetime.today().date())
    
    final_df['total allocated hours'] = pd.to_numeric(final_df['total allocated hours'], errors='coerce').fillna(0.0)
    final_df['completed hours'] = pd.to_numeric(final_df['completed hours'], errors='coerce').fillna(0.0)
    final_df['remaining hours'] = final_df['total allocated hours'] - final_df['completed hours']
    
    for cat in ['university', 'course', 'trainer', 'task name']:
        final_df[cat] = final_df[cat].astype(str).str.strip()
        
    final_df.columns = final_df.columns.str.title()
    return final_df

# -----------------------------------------------------------------------------
# STANDARD DRAG-AND-DROP FILE UPLOADER SIDEBAR (No Emojis)
# -----------------------------------------------------------------------------
st.sidebar.markdown('### <i class="fa-solid fa-folder-open" style="color:#0EA5E9; margin-right:8px;"></i>Data Management', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

is_data_loaded = False

if uploaded_file is not None:
    try:
        raw_excel_df = pd.read_excel(uploaded_file)
        df = clean_and_map_dataframe(raw_excel_df)
        st.sidebar.success("Loaded and synced dynamic dataset successfully!")
        is_data_loaded = True
    except Exception as e:
        st.sidebar.error(f"Mapping pipeline mismatch error: {e}")
        df = get_empty_dataframe()
else:
    df = get_empty_dataframe()
    st.sidebar.info("Waiting for Excel data upload.")

# -----------------------------------------------------------------------------
# BRANDING HEADERS WITH ASSET ICON
# -----------------------------------------------------------------------------
if main_calendar_base64:
    st.markdown(f"""
    <div class="title-container">
        <img src="data:image/png;base64,{main_calendar_base64}" class="main-header-icon"/>
        <div class="main-title">Academic Calendar & Hours Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="title-container"><div class="main-title"><i class="fa-solid fa-calendar-days" style="color:#0EA5E9; margin-right:12px;"></i>Academic Calendar & Hours Dashboard</div></div>', unsafe_allow_html=True)

st.markdown('<div class="sub-title">Drop your course Excel sheets to dynamically generate task calendars, manage timelines, and audit hours metrics.</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FILTER WORKSPACE INTERFACE (No Emojis)
# -----------------------------------------------------------------------------
st.markdown('<div class="section-header"><i class="fa-solid fa-magnifying-glass" style="color:#0EA5E9;"></i>Filter Workspace</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-university icon-spacing"></i>University</div>', unsafe_allow_html=True)
    univ_options = ["All"] + sorted([x for x in df["University"].unique() if x != "nan"]) if is_data_loaded else ["All"]
    selected_univ = st.selectbox("Select University", options=univ_options, label_visibility="collapsed")

with col2:
    if course_icon_base64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{course_icon_base64}" class="custom-icon"/>Course</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-book icon-spacing"></i>Course</div>', unsafe_allow_html=True)
    filtered_courses_df = df if selected_univ == "All" else df[df["University"] == selected_univ]
    course_options = ["All"] + sorted([x for x in filtered_courses_df["Course"].unique() if x != "nan"]) if is_data_loaded else ["All"]
    selected_course = st.selectbox("Select Course", options=course_options, label_visibility="collapsed")

with col3:
    if trainer_icon_base64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{trainer_icon_base64}" class="custom-icon"/>Trainer</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-chalkboard-user icon-spacing"></i>Trainer</div>', unsafe_allow_html=True)
    filtered_trainers_df = filtered_courses_df if selected_course == "All" else filtered_courses_df[filtered_courses_df["Course"] == selected_course]
    trainer_options = ["All"] + sorted([x for x in filtered_trainers_df["Trainer"].unique() if x != "nan"]) if is_data_loaded else ["All"]
    selected_trainer = st.selectbox("Select Trainer", options=trainer_options, label_visibility="collapsed")

with col4:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-calendar-check icon-spacing"></i>Focused Target Date</div>', unsafe_allow_html=True)
    selected_date_focus = st.date_input("Target Date Selection", datetime.today().date(), label_visibility="collapsed")

# Data processing and focal binding matrices
filtered_df = df.copy()
if is_data_loaded:
    if selected_univ != "All":
        filtered_df = filtered_df[filtered_df["University"] == selected_univ]
    if selected_course != "All":
        filtered_df = filtered_df[filtered_df["Course"] == selected_course]
    if selected_trainer != "All":
        filtered_df = filtered_df[filtered_df["Trainer"] == selected_trainer]

calendar_view_date = selected_date_focus.isoformat()
todo_df = filtered_df[filtered_df["Date"] == selected_date_focus] if is_data_loaded else pd.DataFrame()

# Compute aggregate values
total_allocated = filtered_df['Total Allocated Hours'].sum() if is_data_loaded else 0
total_completed = filtered_df['Completed Hours'].sum() if is_data_loaded else 0
total_remaining = filtered_df['Remaining Hours'].sum() if is_data_loaded else 0
task_count = len(filtered_df) if is_data_loaded else 0

# Inject Balanced KPI Sidebar (No Emojis)
st.sidebar.markdown("---")
st.sidebar.markdown('### <i class="fa-solid fa-chart-simple" style="color:#0EA5E9; margin-right:8px;"></i>KPI Performance Logs', unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title"><i class="fa-solid fa-list-check" style="color:#0EA5E9;"></i> Total Tasks</div>
    <div class="kpi-value">{task_count}</div>
</div>
<div class="kpi-card">
    <div class="kpi-title"><i class="fa-solid fa-hourglass" style="color:#64748B;"></i> Allocated Hours</div>
    <div class="kpi-value">{int(total_allocated)}h</div>
</div>
<div class="kpi-card">
    <div class="kpi-title"><i class="fa-solid fa-circle-check" style="color:#10B981;"></i> Hours Completed</div>
    <div class="kpi-value">{int(total_completed)}h</div>
</div>
<div class="kpi-card">
    <div class="kpi-title"><i class="fa-solid fa-clock-rotate-left" style="color:#F43F5E;"></i> Hours Remaining</div>
    <div class="kpi-value">{int(total_remaining)}h</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SCHEDULE MATRIX CALENDAR
# -----------------------------------------------------------------------------
st.write("---")
st.markdown('<div class="section-header"><i class="fa-solid fa-calendar-days" style="color:#0EA5E9;"></i>Schedule Matrix Calendar</div>', unsafe_allow_html=True)

calendar_events = []
if is_data_loaded:
    for idx, row in filtered_df.iterrows():
        event_title = f"{row['Task Name']} ({int(row['Completed Hours'])}h/{int(row['Total Allocated Hours'])}h)"
        
        # Mapping to premium soft color scheme
        bg_color = "#6EE7B7" if row['Remaining Hours'] <= 0 else "#FDA4AF" if row['Completed Hours'] == 0 else "#FDE047"
        text_color = "#064E3B" if row['Remaining Hours'] <= 0 else "#9F1239" if row['Completed Hours'] == 0 else "#78350F"
        
        calendar_events.append({
            "id": str(row['Task Id']),
            "title": event_title,
            "start": row['Date'].isoformat(),
            "end": row['Date'].isoformat(),
            "backgroundColor": bg_color,
            "borderColor": bg_color,
            "textColor": text_color
        })

calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "dayGridMonth",
    "initialDate": calendar_view_date,
    "selectable": True,
}

st.markdown("<span style='color:#FDA4AF;font-weight:700;'>■</span> Not Started &nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#FDE047;font-weight:700;'>■</span> In Progress &nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#6EE7B7;font-weight:700;'>■</span> Fully Completed", unsafe_allow_html=True)
st.write("")
calendar(events=calendar_events, options=calendar_options, key=f"cal_state_{calendar_view_date}_{len(calendar_events)}")

# -----------------------------------------------------------------------------
# TIMELINE DEEP DIVE LOGS
# -----------------------------------------------------------------------------
st.write("---")
st.markdown(f'<div class="section-header"><i class="fa-solid fa-list-ol" style="color:#0EA5E9;"></i>Day Timeline Logs: {selected_date_focus.strftime("%B %d, %Y")}</div>', unsafe_allow_html=True)

if is_data_loaded and not todo_df.empty:
    for idx, row in todo_df.iterrows():
        if row['Remaining Hours'] <= 0:
            status_text, dot_color, label_color = "Completed", "#10B981", "#064E3B"
        elif row['Completed Hours'] == 0:
            status_text, dot_color, label_color = "Not Started", "#F43F5E", "#9F1239"
        else:
            status_text, dot_color, label_color = "In Progress", "#F59E0B", "#78350F"
            
        st.markdown(f"""
        <div class="todo-box">
            <div class="todo-title"><i class="fa-solid fa-thumbtack" style="color:#0EA5E9; font-size:14px;"></i> {row['Task Name']}</div>
            <div class="todo-meta"><b>University:</b> {row['University']} &nbsp;|&nbsp; <b>Course:</b> {row['Course']} &nbsp;|&nbsp; <b>Instructor:</b> {row['Trainer']}</div>
            <div class="todo-status" style="color: {label_color};"><span style="color:{dot_color};">●</span> {status_text} — ({int(row['Completed Hours'])}h Completed / {int(row['Remaining Hours'])}h Remaining)</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info(f"No tasks recorded for {selected_date_focus.strftime('%B %d, %Y')}.")

# -----------------------------------------------------------------------------
# GRAPHICAL DATA VISUALIZATIONS
# -----------------------------------------------------------------------------
st.write("---")
st.markdown('<div class="section-header"><i class="fa-solid fa-chart-pie" style="color:#0EA5E9;"></i>Visual Data Analytics</div>', unsafe_allow_html=True)
dash_col1, dash_col2 = st.columns(2)

with dash_col1:
    st.markdown("#### Operational Breakdown by Task")
    if is_data_loaded and not filtered_df.empty:
        melted_df = filtered_df.melt(id_vars=["Task Name"], value_vars=["Completed Hours", "Remaining Hours"], var_name="Hour Status", value_name="Hours")
        fig_bar = px.bar(
            melted_df, x="Task Name", y="Hours", color="Hour Status", barmode="group",
            color_discrete_map={"Completed Hours": "#6EE7B7", "Remaining Hours": "#FDA4AF"},
            template="plotly_white"
        )
        fig_bar.update_layout(margin=dict(l=20, r=20, t=10, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        empty_fig = px.bar(title="Waiting for Data File...", template="plotly_white")
        st.plotly_chart(empty_fig, use_container_width=True)

with dash_col2:
    st.markdown("#### Performance Metric Volume Allocation")
    if is_data_loaded and total_allocated > 0:
        fig_pie = px.pie(
            names=["Completed Hours", "Remaining Hours"], values=[total_completed, total_remaining],
            color=["Completed Hours", "Remaining Hours"],
            color_discrete_map={"Completed Hours": "#6EE7B7", "Remaining Hours": "#FDA4AF"},
            hole=0.45, template="plotly_white"
        )
        fig_pie.update_layout(margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        empty_pie = px.pie(names=["No Logs Active"], values=[1], color_discrete_sequence=["#E2E8F0"], hole=0.45, template="plotly_white")
        st.plotly_chart(empty_pie, use_container_width=True)
