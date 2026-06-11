import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import base64

# Set page configuration to wide layout
st.set_page_config(page_title="Academic Task & Hours Tracker", layout="wide")

# Inject FontAwesome for standard icons
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
    unsafe_allow_html=True
)

# Custom CSS for UI layout and icon sizing
st.markdown("""
    <style>
    .filter-header { 
        font-size: 16px; 
        font-weight: 600; 
        margin-bottom: 8px; 
        display: flex; 
        align-items: center; 
    }
    .icon-spacing { margin-right: 8px; color: #4A90E2; }
    .custom-icon { width: 24px; height: 24px; margin-right: 8px; object-fit: contain; }
    </style>
""", unsafe_allow_html=True)

# Helper function to load local image files safely into HTML headers
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return ""

# Convert user icons to base64 strings
course_icon_base64 = get_image_base64("image_2b21c2.png")
trainer_icon_base64 = get_image_base64("image_2b217d.png")

# -----------------------------------------------------------------------------
# 1. DYNAMIC TODAY-MATCHED SAMPLE DATA
# -----------------------------------------------------------------------------
def get_sample_data():
    today_str = datetime.today().date().isoformat()
    return pd.DataFrame({
        "Task ID": [1, 2, 3],
        "Task Name": ["AI Architecture Setup", "Cloud Database Sync", "Neural Network Review"],
        "University": ["Stanford Tech", "MIT Lab", "Stanford Tech"],
        "Course": ["Artificial Intelligence", "Advanced Data Systems", "Artificial Intelligence"],
        "Trainer": ["Dr. Smith", "Prof. Ray", "Dr. Smith"],
        "Date": [today_str, today_str, today_str],
        "Total Allocated Hours": [12, 8, 15],
        "Completed Hours": [8, 8, 0]
    })

# -----------------------------------------------------------------------------
# 2. SMART CLEANER & COLUMN ALIGNER
# -----------------------------------------------------------------------------
def clean_and_map_dataframe(raw_df):
    processed_df = raw_df.copy()
    # Normalize inputs: clean spaces and standard case structures
    processed_df.columns = processed_df.columns.astype(str).str.strip().str.lower()
    
    mapping_dictionary = {
        'task id': ['task id', 'id', 'task_id', 'sr no', 'sr. no.', 'index'],
        'task name': ['task name', 'task', 'title', 'event', 'assignment', 'task_name', 'name'],
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
            # Safe Default Assigners
            if standard_key == 'task id':
                final_df[standard_key] = range(1, len(processed_df) + 1)
            elif standard_key in ['total allocated hours', 'completed hours']:
                final_df[standard_key] = 0.0
            elif standard_key == 'date':
                final_df[standard_key] = datetime.today().date()
            else:
                final_df[standard_key] = "General"
                
    # Format and clean columns data rules
    final_df['date'] = pd.to_datetime(final_df['date'], errors='coerce').dt.date
    final_df['date'] = final_df['date'].fillna(datetime.today().date())
    
    final_df['total allocated hours'] = pd.to_numeric(final_df['total allocated hours'], errors='coerce').fillna(0.0)
    final_df['completed hours'] = pd.to_numeric(final_df['completed hours'], errors='coerce').fillna(0.0)
    final_df['remaining hours'] = final_df['total allocated hours'] - final_df['completed hours']
    
    # Enforce String conversion on categories to prevent dropdown type mismatches
    for cat in ['university', 'course', 'trainer', 'task name']:
        final_df[cat] = final_df[cat].astype(str).str.strip()
        
    final_df.columns = final_df.columns.str.title()
    return final_df

# -----------------------------------------------------------------------------
# 3. LIVE FILE PROCESSING SYSTEM
# -----------------------------------------------------------------------------
st.title("📅 Academic Calendar & Hours Dashboard")
st.markdown("Upload your active class schedules via excel files to map live data instantly.")

st.sidebar.header("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

# Dynamic validation check 
if uploaded_file is not None:
    try:
        raw_excel_df = pd.read_excel(uploaded_file)
        df = clean_and_map_dataframe(raw_excel_df)
        st.sidebar.success("Loaded and auto-mapped file parameters successfully!")
    except Exception as e:
        st.sidebar.error(f"Error parsing sheet parameters: {e}")
        df = clean_and_map_dataframe(get_sample_data())
else:
    df = clean_and_map_dataframe(get_sample_data())
    st.sidebar.info("No data uploaded. Displaying today's workspace framework.")

# -----------------------------------------------------------------------------
# 4. INTERACTIVE AUTO-RESET FILTER CONTROLS
# -----------------------------------------------------------------------------
st.write("---")
st.markdown("### Filter Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-university icon-spacing"></i>University</div>', unsafe_allow_html=True)
    univ_options = ["All"] + sorted([x for x in df["University"].unique() if x != "nan"])
    selected_univ = st.selectbox("Select University", options=univ_options, index=0)

with col2:
    if course_icon_base64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{course_icon_base64}" class="custom-icon"/>Course</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-book icon-spacing"></i>Course</div>', unsafe_allow_html=True)
    
    # Cascade dataset checks to prevent blank dropdown locked scenarios
    filtered_courses_df = df if selected_univ == "All" else df[df["University"] == selected_univ]
    course_options = ["All"] + sorted([x for x in filtered_courses_df["Course"].unique() if x != "nan"])
    selected_course = st.selectbox("Select Course", options=course_options, index=0)

with col3:
    if trainer_icon_base64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{trainer_icon_base64}" class="custom-icon"/>Trainer</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-chalkboard-user icon-spacing"></i>Trainer</div>', unsafe_allow_html=True)
        
    filtered_trainers_df = filtered_courses_df if selected_course == "All" else filtered_courses_df[filtered_courses_df["Course"] == selected_course]
    trainer_options = ["All"] + sorted([x for x in filtered_trainers_df["Trainer"].unique() if x != "nan"])
    selected_trainer = st.selectbox("Select Trainer", options=trainer_options, index=0)

with col4:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-calendar-days icon-spacing"></i>Date Range</div>', unsafe_allow_html=True)
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    
    if min_date == max_date:
        selected_date_range = st.date_input("Select Dates", [min_date])
    else:
        selected_date_range = st.date_input("Select Dates", [min_date, max_date])

# APPLY FILTERS
filtered_df = df.copy()
if selected_univ != "All":
    filtered_df = filtered_df[filtered_df["University"] == selected_univ]
if selected_course != "All":
    filtered_df = filtered_df[filtered_df["Course"] == selected_course]
if selected_trainer != "All":
    filtered_df = filtered_df[filtered_df["Trainer"] == selected_trainer]
if isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 2:
    filtered_df = filtered_df[(filtered_df["Date"] >= selected_date_range[0]) & (filtered_df["Date"] <= selected_date_range[1])]

# -----------------------------------------------------------------------------
# 5. CALENDAR COMPONENT (Guaranteed to Render)
# -----------------------------------------------------------------------------
st.write("---")
st.subheader("🗓️ Tasks Schedule Calendar")

calendar_events = []
for idx, row in filtered_df.iterrows():
    event_title = f"{row['Task Name']} ({int(row['Completed Hours'])}h / {int(row['Total Allocated Hours'])}h)"
    calendar_events.append({
        "id": str(row['Task Id']),
        "title": event_title,
        "start": row['Date'].isoformat(),
        "end": row['Date'].isoformat(),
        "backgroundColor": "#2E7D32" if row['Remaining Hours'] <= 0 else "#D32F2F" if row['Completed Hours'] == 0 else "#F57C00",
        "borderColor": "#333333"
    })

calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "dayGridMonth",
    "initialDate": datetime.today().date().isoformat(),
    "selectable": True,
    "editable": True,
}

st.markdown("*Color Legend:  🔴 Not Started | 🟡 In Progress | 🟢 Completed*")
# Using unique dynamic keys tied directly to length keeps state synchronization live
calendar(events=calendar_events, options=calendar_options, key=f"calendar_instance_{len(calendar_events)}")

# -----------------------------------------------------------------------------
# 6. DASHBOARD ANALYTICS SYSTEM
# -----------------------------------------------------------------------------
st.write("---")
st.subheader("📊 Performance & Hours Overview Dashboard")

# Pull aggregate totals directly from full dataframe if filter results are currently empty
data_scope = filtered_df if not filtered_df.empty else df

total_allocated = data_scope['Total Allocated Hours'].sum()
total_completed = data_scope['Completed Hours'].sum()
total_remaining = data_scope['Remaining Hours'].sum()

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric(label="Total Tracked Tasks", value=len(data_scope))
with m_col2:
    st.metric(label="Allocated Hours Total", value=f"{int(total_allocated)} hrs")
with m_col3:
    st.metric(label="Completed Hours ✅", value=f"{int(total_completed)} hrs")
with m_col4:
    st.metric(label="Remaining Hours ⏳", value=f"{int(total_remaining)} hrs")

if filtered_df.empty:
    st.warning("⚠️ The current filter combinations returned 0 records. Showing overall spreadsheet trends instead.")

dash_col1, dash_col2 = st.columns(2)

with dash_col1:
    st.markdown("#### Hours breakdown by Task")
    melted_df = data_scope.melt(id_vars=["Task Name"], value_vars=["Completed Hours", "Remaining Hours"], var_name="Hour Status", value_name="Hours")
    fig_bar = px.bar(melted_df, x="Task Name", y="Hours", color="Hour Status", barmode="group", color_discrete_map={"Completed Hours": "#2E7D32", "Remaining Hours": "#D32F2F"})
    st.plotly_chart(fig_bar, use_container_width=True)

with dash_col2:
    st.markdown("#### General Completion Progress Ratio")
    if total_allocated > 0:
        fig_pie = px.pie(names=["Completed Hours", "Remaining Hours"], values=[total_completed, total_remaining], color=["Completed Hours", "Remaining Hours"], color_discrete_map={"Completed Hours": "#2E7D32", "Remaining Hours": "#D32F2F"}, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No hours values found to generate graph mappings.")
