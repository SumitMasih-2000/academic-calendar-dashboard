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
    /* Global styles and clean headings */
    .title-container {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 5px;
    }
    .main-title { font-size: 32px; font-weight: 700; color: #1E293B; margin: 0; }
    .sub-title { font-size: 15px; color: #64748B; margin-top: 5px; margin-bottom: 25px; }
    .section-header { font-size: 20px; font-weight: 600; color: #1E293B; margin-top: 20px; margin-bottom: 15px; }
    
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
    
    /* Elegant To-Do List Cards */
    .todo-box {
        padding: 16px 20px;
        border-radius: 12px;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #0EA5E9;
        margin-bottom: 12px;
    }
    .todo-title { font-size: 16px; font-weight: 600; color: #1E293B; margin: 0 0 6px 0; }
    .todo-meta { font-size: 13px; color: #64748B; margin: 0 0 6px 0; }
    .todo-status { font-size: 13px; font-weight: 500; margin: 0; }
    
    /* Premium Minimalist KPI Cards (Sized down for Sidebar compatibility) */
    .kpi-card {
        background-color: #ffffff;
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        text-align: left;
        margin-bottom: 10px;
    }
    .kpi-title { font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 22px; color: #0F172A; font-weight: 700; margin-top: 4px; }
    
    /* Calendar UI custom colors match override */
    .fc-theme-standard .fc-scrollgrid { border-color: #E2E8F0 !important; }
    .fc-header-toolbar .fc-button-primary { background-color: #0EA5E9 !important; border-color: #0EA5E9 !important; }
    .fc-header-toolbar .fc-button-primary:hover { background-color: #0284C7 !important; border-color: #0284C7 !important; }
    </style>
""", unsafe_allow_html=True)

# Helper function to process uploaded images safely to base64 strings
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        # Fallback to prevent code execution crash on white screen if file asset is missing
        return ""

# Convert all asset images safely to base64 strings
main_calendar_base64 = get_image_base64("image_1134f1.png")
course_icon_base64 = get_image_base64("image_2b21c2.png")
trainer_icon_base64 = get_image_base64("image_2b217d.png")

# -----------------------------------------------------------------------------
# 1. EMPTY TEMPLATE SCHEMA GENERATOR
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
    final_df
