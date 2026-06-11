import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import base64

# Set page configuration to wide layout
st.set_page_config(page_title="Academic Task & Hours Tracker", layout="wide")

# Inject FontAwesome for the remaining filters (University, Date)
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
    unsafe_allow_html=True
)

# Custom CSS to align custom image icons smoothly with text
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

# Convert images to base64 strings
course_icon_base64 = get_image_base64("image_2b21c2.png")
trainer_icon_base64 = get_image_base64("image_2b217d.png")

# -----------------------------------------------------------------------------
# 1. SAMPLE DATA CREATION (Fallback if no file is uploaded)
# -----------------------------------------------------------------------------
def get_sample_data():
    return pd.DataFrame({
        "Task ID": [1, 2, 3, 4],
        "Task Name": ["Data Science Lecture", "AI Assignment", "Web Dev Workshop", "Math Exam Prep"],
        "University": ["Stanford", "MIT", "Stanford", "MIT"],
        "Course": ["Computer Science", "Artificial Intelligence", "Web Development", "Mathematics"],
        "Trainer": ["Dr. Smith", "Prof. Jones", "Alex Ray", "Dr. Alan"],
        "Date": ["2026-06-11", "2026-06-12", "2026-06-11", "2026-06-15"],
        "Total Allocated Hours": [10, 15, 8, 12],
        "Completed Hours": [6, 15, 2, 0]
    })

# -----------------------------------------------------------------------------
# 2. DATA LOADING & LIVE SYNC
# -----------------------------------------------------------------------------
st.title("📅 Academic Calendar & Hours Dashboard")
st.markdown("Upload your Excel schedule to dynamically populate the calendar and tracking metrics.")

st.sidebar.header("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("Loaded live data successfully!")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
        df = get_sample_data()
else:
    df = get_sample_data()
    st.sidebar.info("Showing sample data. Upload an Excel file to view your own schedule.")

# Ensure proper data formatting
df['Date'] = pd.to_datetime(df['Date']).dt.date
df['Total Allocated Hours'] = pd.to_numeric(df['Total Allocated Hours'], errors='coerce').fillna(0)
df['Completed Hours'] = pd.to_numeric(df['Completed Hours'], errors='coerce').fillna(0)
df['Remaining Hours'] = df['Total Allocated Hours'] - df['Completed Hours']


# -----------------------------------------------------------------------------
# 3. INTERACTIVE FILTERS WITH CUSTOM IMAGE ICONS
# -----------------------------------------------------------------------------
st.write("---")
st.markdown("### Filter Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-university icon-spacing"></i>University</div>', unsafe_allow_html=True)
    univ_options = ["All"] + sorted(df["University"].dropna().unique().tolist())
    selected_univ = st.selectbox("Select University", options=univ_options, label_visibility="collapsed")

with col2:
    # course_icon_base64 used here for image_2b21c2.png
    if course_icon_base64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{course_icon_base64}" class="custom-icon"/>Course</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-book icon-spacing"></i>Course</div>', unsafe_allow_html=True)
    
    filtered_courses = df if selected_univ == "All" else df[df["University"] == selected_univ]
    course_options = ["All"] + sorted(filtered_courses["Course"].dropna().unique().tolist())
    selected_course = st.selectbox("Select Course", options=course_options, label_visibility="collapsed")

with col3:
    # trainer_icon_base64 used here for image_2b217d.png
    if trainer_icon_base64:
        st.markdown(f'<div class="filter-header"><img src="data:image/png;base64,{trainer_icon_base64}" class="custom-icon"/>Trainer</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="filter-header"><i class="fa-solid fa-chalkboard-user icon-spacing"></i>Trainer</div>', unsafe_allow_html=True)
        
    filtered_trainers = filtered_courses if selected_course == "All" else filtered_courses[filtered_courses["Course"] == selected_course]
    trainer_options = ["All"] + sorted(filtered_trainers["Trainer"].dropna().unique().tolist())
    selected_trainer = st.selectbox("Select Trainer", options=trainer_options, label_visibility="collapsed")

with col4:
    st.markdown('<div class="filter-header"><i class="fa-solid fa-calendar-days icon-spacing"></i>Date Range</div>', unsafe_allow_html=True)
    min_date = df['Date'].min() if not df.empty else datetime.today().date()
    max_date = df['Date'].max() if not df.empty else datetime.today().date()
    
    if min_date == max_date:
        selected_date_range = st.date_input("Select Dates", [min_date], label_visibility="collapsed")
    else:
        selected_date_range = st.date_input("Select Dates", [min_date, max_date], label_visibility="collapsed")

# Apply Filters
filtered_df = df.copy()
if selected_univ != "All":
    filtered_df = filtered_df[filtered_df["University"] == selected_univ]
if selected_course != "All":
    filtered_df = filtered_df[filtered_df["Course"] == selected_course]
if selected_trainer != "All":
    filtered_df = filtered_df[filtered_df["Trainer"] == selected_trainer]
if isinstance(selected_date_range, list) or isinstance(selected_date_range, tuple):
    if len(selected_date_range) == 2:
        filtered_df = filtered_df[(filtered_df["Date"] >= selected_date_range[0]) & (filtered_df["Date"] <= selected_date_range[1])]


# -----------------------------------------------------------------------------
# 4. CALENDAR UI COMPONENT
# -----------------------------------------------------------------------------
st.write("---")

calendar_events = []
for idx, row in filtered_df.iterrows():
    event_title = f"{row['Task Name']} ({row['Completed Hours']}h / {row['Total Allocated Hours']}h)"
    
    calendar_events.append({
        "id": str(row['Task ID']),
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
    "selectable": True,
}

st.subheader("🗓️ Tasks Schedule Calendar")
st.markdown("*Color Legend:  🔴 Not Started | 🟡 In Progress | 🟢 Completed*")
calendar(events=calendar_events, options=calendar_options, key="streamlit_calendar")


# -----------------------------------------------------------------------------
# 5. METRICS & VISUAL DASHBOARD
# -----------------------------------------------------------------------------
st.write("---")
st.subheader("📊 Performance & Hours Overview Dashboard")

total_allocated = filtered_df['Total Allocated Hours'].sum()
total_completed = filtered_df['Completed Hours'].sum()
total_remaining = filtered_df['Remaining Hours'].sum()

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric(label="Total Assigned Tasks", value=len(filtered_df))
with m_col2:
    st.metric(label="Allocated Hours Total", value=f"{total_allocated} hrs")
with m_col3:
    st.metric(label="Completed Hours ✅", value=f"{total_completed} hrs")
with m_col4:
    st.metric(label="Remaining Hours ⏳", value=f"{total_remaining} hrs")

dash_col1, dash_col2 = st.columns(2)

with dash_col1:
    st.markdown("#### Hours breakdown by Task")
    if not filtered_df.empty:
        melted_df = filtered_df.melt(id_vars=["Task Name"], value_vars=["Completed Hours", "Remaining Hours"], var_name="Hour Status", value_name="Hours")
        fig_bar = px.bar(melted_df, x="Task Name", y="Hours", color="Hour Status", barmode="group", color_discrete_map={"Completed Hours": "#2E7D32", "Remaining Hours": "#D32F2F"})
        st.plotly_chart(fig_bar, use_container_width=True)

with dash_col2:
    st.markdown("#### General Completion Progress Ratio")
    if not filtered_df.empty and total_allocated > 0:
        fig_pie = px.pie(names=["Completed Hours", "Remaining Hours"], values=[total_completed, total_remaining], color=["Completed Hours", "Remaining Hours"], color_discrete_map={"Completed Hours": "#2E7D32", "Remaining Hours": "#D32F2F"}, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
