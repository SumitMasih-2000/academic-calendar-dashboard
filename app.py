import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import base64

# Set wide layout configuration
st.set_page_config(page_title="Academic Task & Hours Tracker", layout="wide")

# Inject FontAwesome styling framework
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
    unsafe_allow_html=True
)

# Custom layout and tracking styles
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
    .todo-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #f8f9fa;
        border-left: 5px solid #4A90E2;
        margin-bottom: 10px;
    }
    /* KPI Card styling to keep everything clean and structurally aligned */
    .kpi-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
        text-align: center;
    }
    .kpi-title { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .kpi-value { font-size: 28px; color: #1e293b; font-weight: 700; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# Process icons to base64
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return ""

course_icon_base64 = get_image_base64("image_2b21c2.png")
trainer_icon_base64 = get_image_base64("image_2b217d.png")

# -----------------------------------------------------------------------------
# 1. EMPTY TEMPLATE SCHEMA GENERATOR (Maintains structure when empty)
# -----------------------------------------------------------------------------
def get_empty_dataframe():
    return pd.DataFrame(columns=[
        "Task ID", "Task Name", "University", "Course", 
        "Trainer", "Date", "Total Allocated Hours", "Completed Hours", "Remaining Hours"
    ])

# -----------------------------------------------------------------------------
# 2. INTUITIVE SHEET DATA NORMALIZER
# -----------------------------------------------------------------------------
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
    final_df['date'] = final_df
