import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import base64
import os

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
    .todo-title { font-size: 17px; font-weight: 600; color: #0F172A; margin: 0 0 6px 0; }
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
# AUTOMATED LIVE FILE WATCHER SYSTEM
# -----------------------------------------------------------------------------
st.sidebar.header("📁 Live Data Management")
EXCEL_FILE_PATH = "academic_schedule.xlsx" 
file_path_input = st.sidebar.text_input("Local Excel File Path:", value=EXCEL_FILE_PATH)

is_data_loaded = False

if os.path.exists(file_path_input):
    try:
        last_modified_timestamp = os.path.getmtime(file_path_input)
        
        @st.cache_data(ttl=1)
        def fetch_live_data(path, mod_time):
            raw_excel_df = pd.read_excel(path)
            return clean_and_map_dataframe(raw_excel_df)
            
        df = fetch_live_data(file_path_input, last_modified_timestamp)
        st.sidebar.success("🟢 Live Tracking Mode Active!")
        st.sidebar.caption(f"Synced: {datetime.fromtimestamp(last_modified_timestamp).strftime('%H:%M:%S')}")
        is_data_loaded = True
    except Exception as e:
        st.sidebar.error(f"Error accessing file system: {e}")
        df = get_empty_dataframe()
else:
    df = get_empty_dataframe()
    st.sidebar.warning(f"⚠️ Target file missing at: '{file_path_input}'")

# -----------------------------------------------------------------------------
# BRANDING HEADERS WITH ASSET ICON
# -----------------------------------------------------------------------------
if main_calendar_base64:
    st.markdown(f"""
    <div class="title-container">
        <img src="data:image/png;base64,{main_calendar_base64}" class
