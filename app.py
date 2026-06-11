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
# 1. SAMPLE DATA GENERATOR (Dynamically matches Today's Date)
# -----------------------------------------------------------------------------
def get_sample_data():
    today_str = datetime.today().date().isoformat()
    return pd.DataFrame({
        "Task ID": [1, 2],
        "Task Name": ["Sample Task A (No File Uploaded)", "Sample Task B (No File Uploaded)"],
        "University": ["Default University", "Default University"],
        "Course": ["General Course", "General Course"],
        "Trainer": ["Unassigned", "Unassigned"],
        "Date": [today_str, today_str],
        "Total Allocated Hours": [5, 10],
        "Completed Hours": [2, 10]
    })

# -----------------------------------------------------------------------------
# 2. SMART COLUMN MAPPER (Prevents KeyErrors)
# -----------------------------------------------------------------------------
def clean_and_map_dataframe(raw_df):
    processed_df = raw_df.copy()
    processed_df.columns = processed_df.columns.astype(str).str.strip().str.lower()
    
    mapping_dictionary = {
        'task id': ['task id', 'id', 'task_id', 'sr no', 'sr. no.'],
        'task name': ['task name', 'task', 'title', 'event', 'assignment', 'task_name'],
        'university': ['university', 'univ', 'college', 'institution', 'school'],
        'course': ['course', 'subject', 'program', 'class'],
        'trainer': ['trainer', 'instructor', 'teacher', 'professor', 'faculty', 'dr.'],
        'date': ['date', 'task date', 'due date', 'schedule date', 'timeline', 'day'],
        'total allocated hours': ['total allocated hours', 'total hours', 'allocated hours', 'hours', 'duration', 'total_hours'],
        'completed hours': ['completed hours', 'hours completed', 'done', 'hours done', 'completed_hours']
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
                final_df[standard_key] = 0
            elif standard_key == 'date':
                final_df[standard_key] = datetime.today().date()
            else:
                final_df[standard_key] = "N/A"
                
    final_df['date'] = pd.to_datetime(final_df['date'], errors='coerce').dt.date
    final_df['date'] = final_df['date'].fillna(datetime.today().date())
    
    final_df['total allocated hours'] = pd.to_numeric(final_df['total allocated hours'], errors='coerce').fillna(0)
    final_df['completed hours'] = pd.to_numeric(final_df['completed hours'], errors='coerce').fillna(0)
    final_df['remaining hours'] = final_df['total allocated hours'] - final_df['completed hours']
    
    final_df.columns = final_df.columns.str.title()
    return final_df

# -----------------------------------------------------------------------------
# 3. FILE UPLOADER & CORE SYNC
# -----------------------------------------------------------------------------
st.title("📅 Academic Calendar & Hours Dashboard")
st.markdown("Upload an Excel schedule to dynamically populate the calendar dashboard layout.")

st.sidebar.header("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        raw_excel_df = pd.read_excel(uploaded_file)
        df = clean_and_map_dataframe(raw_excel_df)
        st.sidebar.success("Loaded and mapped file successfully!")
    except Exception as e:
        st.sidebar.error(f"Error structuring your file data: {e}")
        df = get_sample_data()
        df = clean_and_map_dataframe(df)
else:
    df = get_sample_data()
    df = clean_and_map_dataframe(df)
    st.sidebar.info("No data uploaded. Displaying today's workspace schedule.")

# -----------------------------------------------------------------------------
# 4. INTERACTIVE FILTERS GRID
# -----------------------------------------------------------------------------
st.write("---")
st.markdown("### Filter Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-university icon-spacing"></i>University</div>', unsafe_allow_html=True)
    univ_options = ["All"] + sorted(df["University"].dropna().unique().tolist())
    selected_univ = st.selectbox("Select University", options=univ_options, label_visibility="collapsed")

with col2:
    if course_icon_base64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{course_icon_base64}" class="custom-icon"/>Course</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-book icon-spacing"></i>Course</div>', unsafe_allow_html=True)
    
    filtered_courses = df if selected_univ == "All" else df[df["University"] == selected_univ]
    course_options = ["All"] + sorted(filtered_courses["Course"].dropna().unique().tolist())
    selected_course = st.selectbox("Select Course", options=course_options, label_visibility="collapsed")

with col3:
    if trainer_icon_base64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{trainer_icon_base64}" class="custom-icon"/>Trainer</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-chalkboard-user icon-spacing"></i>Trainer</div>', unsafe_allow_html=True)
        
    filtered_trainers = filtered_courses if selected_course == "All" else filtered_courses[filtered_courses["Course"] == selected_course]
    trainer_options = ["All"] + sorted(filtered_trainers["Trainer"].dropna().unique().tolist())
    selected_trainer = st.selectbox("Select Trainer", options=trainer_options, label_visibility="collapsed")
