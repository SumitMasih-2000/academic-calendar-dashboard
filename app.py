# training-calendar-dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import os
import re

# =====================================================
# 1. PAGE LAYOUT CONFIGURATION
# =====================================================
st.markdown("""

<style>

/* ==============================
   EXECUTIVE BLUE THEME
   ============================== */

:root{
    --bg:#F8FAFC;
    --sidebar:#1E3A8A;
    --accent:#2563EB;
    --hover:#1D4ED8;
    --card:#FFFFFF;
    --text:#0F172A;
}

/* Main App */
.stApp{
    background-color: var(--bg);
}

/* Sidebar */
[data-testid="stSidebar"]{
    background: var(--sidebar);
}

[data-testid="stSidebar"] *{
    color:white !important;
}

/* Upload Dataset Header */
[data-testid="stSidebar"] h2 {
    color: black !important;
}

/* File Uploader */
[data-testid="stFileUploader"] * {
    color: black !important;
   
}

/* Keep dropdown text visible */
[data-testid="stSidebar"] div[data-baseweb="select"] *{
    color:black !important;
}

/* KPI Cards */
div[data-testid="metric-container"]{
    background: var(--card);
    padding: 18px;
    border-radius: 15px;
    border-left: 6px solid var(--accent);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* KPI Labels */
[data-testid="metric-container"] label{
    color: var(--text) !important;
    font-weight:600;
}

/* KPI Values */
[data-testid="stMetricValue"]{
    color: var(--text);
    font-weight:700;
}

/* Headers */
h1{
    color: var(--text);
    font-weight:700;
}

h2,h3,h4{
    color: var(--text);
    font-weight:600;
}

/* Buttons */
.stButton > button{
    background-color: var(--accent);
    color:white;
    border:none;
    border-radius:10px;
    padding:0.5rem 1rem;
    font-weight:600;
    transition:0.3s;
}

.stButton > button:hover{
    background-color: var(--hover);
    color:white;
}

/* Download Button */
.stDownloadButton > button{
    background-color: var(--accent);
    color:white;
    border:none;
    border-radius:10px;
    font-weight:600;
}

.stDownloadButton > button:hover{
    background-color: var(--hover);
}

/* DataFrames */
[data-testid="stDataFrame"]{
    border-radius:12px;
    overflow:hidden;
    border:1px solid #E2E8F0;
}

/* Alerts */
[data-testid="stAlert"]{
    border-radius:12px;
}

/* Tabs */
button[data-baseweb="tab"]{
    font-weight:600;
}

/* Calendar Events */
.fc-event{
    border:none !important;
    border-radius:8px !important;
    font-weight:600;
    padding:2px;
}

/* Calendar Toolbar */
.fc-toolbar-title{
    color: var(--text) !important;
    font-weight:700 !important;
}

/* Calendar Buttons */
.fc-button{
    background: var(--accent) !important;
    border:none !important;
}

.fc-button:hover{
    background: var(--hover) !important;
}

/* Select Boxes */
div[data-baseweb="select"]{
    border-radius:10px;
}

/* Multiselect */
.stMultiSelect{
    border-radius:10px;
}

/* Expander */
.streamlit-expanderHeader{
    font-weight:600;
}

/* Horizontal Line */
hr{
    border:1px solid #E2E8F0;
}

/* Plotly Charts */
.js-plotly-plot{
    border-radius:12px;
    background:white;
    padding:10px;
}

/* Scrollbar */
::-webkit-scrollbar{
    width:8px;
}

::-webkit-scrollbar-track{
    background:#E2E8F0;
}

::-webkit-scrollbar-thumb{
    background:#94A3B8;
    border-radius:10px;
}

::-webkit-scrollbar-thumb:hover{
    background:#64748B;
}

</style>
""", unsafe_allow_html=True)
# =====================================================
# 2. DATA INGESTION MATRIX
# =====================================================
st.sidebar.header("📤 Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Choose Excel or CSV File",
    type=["xlsx", "csv"]
)

@st.cache_data
def load_data(uploaded_file):

    # If user uploads file
    if uploaded_file is not None:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        return df, uploaded_file.name

    # Otherwise load default local file
    files = [
        f for f in os.listdir()
        if f.endswith(".xlsx") or f.endswith(".csv")
    ]

    if not files:
        st.error(
            "❌ No Excel/CSV file found. Please upload a dataset."
        )
        st.stop()

    file_name = files[0]

    if file_name.endswith(".csv"):
        df = pd.read_csv(file_name)
    else:
        df = pd.read_excel(file_name)

    return df, file_name


df, file_name = load_data(uploaded_file)

st.sidebar.success(f"📂 Active Source Matrix: {file_name}")
# =====================================================
# 3. COMPREHENSIVE TEXT CLEANING
# =====================================================
df.columns = df.columns.str.strip()

for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].fillna("Not Assigned").astype(str).str.strip()

# Standardize values for numeric calculation processing blocks
if "No of students" in df.columns:
    df["No of students"] = pd.to_numeric(df["No of students"], errors="coerce").fillna(0).astype(int)

# =====================================================
# 4. ADVANCED SYSTEM DATE PARSER Engine (Handles text string days like '1st', '31st')
# =====================================================
def convert_date(x, fallback_day=1, default_month=5, default_year=2024):
    if pd.isna(x) or str(x).strip() == "" or str(x).lower().strip() == "nan":
        return pd.NaT
        
    clean_str = str(x).lower().strip()
    
    # Strip day suffixes (st, nd, rd, th) securely 
    day_digits = re.search(r'\d+', clean_str)
    day = int(day_digits.group()) if day_digits else fallback_day
    
    # Process written alphabetic month blocks accurately
    month = default_month
    if "april" in clean_str: month = 4
    elif "may" in clean_str: month = 5
    elif "june" in clean_str: month = 6
    
    try:
        return datetime(default_year, month, day)
    except:
        return pd.NaT

if "Start date" in df.columns:
    df["Start"] = df["Start date"].apply(lambda x: convert_date(x, fallback_day=1))
else:
    df["Start"] = pd.NaT

if "Closing date" in df.columns:
    df["End"] = df["Closing date"].apply(lambda x: convert_date(x, fallback_day=31))
else:
    df["End"] = df["Start"]

# Structural chronology check fallback logic
invalid_end_mask = (df["End"] < df["Start"]) | pd.isna(df["End"])
df.loc[invalid_end_mask, "End"] = df.loc[invalid_end_mask, "Start"] + pd.Timedelta(days=7)

# =====================================================
# 5. AUTOMATED TRUE CASCADING FILTERS WINDOW
# =====================================================
st.sidebar.title("🎯 Cascading Filters")

exclude_cols = ["Start", "End", "Start date", "Closing date", "No of students", "Delivery hrs", "No. of batches", "Trainers required"]
filter_columns = [c for c in df.columns if c not in exclude_cols]

# Prioritize University as top master node structure layout tracking block
if "University" in filter_columns:
    filter_columns.remove("University")
    filter_columns = ["University"] + filter_columns

# Instantiating the sequential row reduction framework
filtered = df.copy()

for col in filter_columns:
    # Crucial change step: options dynamically shrink based on the rows left from previous selections
    available_values = sorted(
        filtered[col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    
    if not available_values:
        available_values = ["Not Assigned"]

    # Auto-select the choices safely if a master filter shrinks options to 1 single record slot
    selected = st.sidebar.multiselect(
        f"🔽 Filter: {col}",
        options=available_values,
        default=available_values,
        key=f"cascade_{col}"
    )
    
    # Inject constraint modification immediately on current tracking data block
    filtered = filtered[filtered[col].astype(str).isin(selected)]
    # =====================================================
# DATE FILTERING SYSTEM
# =====================================================

if "Start" in filtered.columns:

    valid_dates = filtered["Start"].dropna()

    if not valid_dates.empty:

        st.sidebar.markdown("---")
        st.sidebar.subheader("📅 Date Filters")

        # Year Filter
        years = sorted(valid_dates.dt.year.unique())

        selected_years = st.sidebar.multiselect(
            "Select Year",
            years,
            default=years
        )

        filtered = filtered[
            filtered["Start"].dt.year.isin(selected_years)
        ]

        # Month Filter
        month_names = {
            1:"Jan",2:"Feb",3:"Mar",4:"Apr",
            5:"May",6:"Jun",7:"Jul",8:"Aug",
            9:"Sep",10:"Oct",11:"Nov",12:"Dec"
        }

        months_available = sorted(
            filtered["Start"].dropna().dt.month.unique()
        )

        selected_months = st.sidebar.multiselect(
            "Select Month",
            options=months_available,
            default=months_available,
            format_func=lambda x: month_names[x]
        )

        filtered = filtered[
            filtered["Start"].dt.month.isin(selected_months)
        ]

        # Default calendar focus
        if not filtered.empty:
            calendar_focus_date = filtered["Start"].min().strftime("%Y-%m-%d")
        else:
            calendar_focus_date = datetime.now().strftime("%Y-%m-%d")

        # Date Range Filter

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Date Filters")

# Date Range Filter

valid_dates = filtered["Start"].dropna()

if valid_dates.empty:

    min_date = datetime.now().date()
    max_date = datetime.now().date()

    calendar_focus_date = datetime.now().strftime("%Y-%m-%d")

else:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    calendar_focus_date = valid_dates.min().strftime("%Y-%m-%d")

selected_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="date_range_filter"
)

if len(selected_range) == 2 and not valid_dates.empty:

    start_filter, end_filter = selected_range

    filtered = filtered[
        (filtered["Start"].dt.date >= start_filter) &
        (filtered["Start"].dt.date <= end_filter)
    ]

    calendar_focus_date = start_filter.strftime("%Y-%m-%d")
   
        # Date Range Filter

        from datetime import datetime, date

if filtered.empty:
    calendar_focus_date = datetime.now().strftime("%Y-%m-%d")
else:
    calendar_focus_date = filtered["Start"].min().strftime("%Y-%m-%d")

# =====================================================
# 6. UNIVERSAL GLOBAL TEXT SEARCH STRATEGIES
# =====================================================


# =====================================================
# 7. MAIN AREA DASHBOARD DESIGN LAYOUT
# =====================================================
st.info(
    f"""
    📊 **Active Display Focus:** {len(filtered)} Matching Cohort Records Found.
    """
)

# KPI Cards Presentation Grid Setup
col1, col2, col3, col4 = st.columns(4)

with col1:
    uni_val = filtered['University'].nunique() if 'University' in filtered.columns else 0
    st.metric("🏫 Active Universities", uni_val)

with col2:
    prog_val = filtered['Program'].nunique() if 'Program' in filtered.columns else 0
    st.metric("🎓 Track Programs", prog_val)

with col3:
    student_sum = int(filtered["No of students"].sum()) if "No of students" in filtered.columns else 0
    st.metric("👨‍🎓 Total Enrollees", f"{student_sum:,}")

with col4:
    trainer_val = filtered['Mapped Trainers'].nunique() if 'Mapped Trainers' in filtered.columns else 0
    st.metric("👨‍🏫 Allocated Faculty", trainer_val)

st.divider()

# =====================================================
# 8. HIGH-CONTRAST INTERACTIVE BLUE CALENDAR COMPONENT
# =====================================================
st.subheader("📅 Academic Operational Scheduler Calendar")
st.markdown("""
🟢 Online Modality &nbsp;&nbsp;&nbsp; |
🔵 Offline Classrooms &nbsp;&nbsp;&nbsp; |
🟠 Hybrid Configurations &nbsp;&nbsp;&nbsp; |
🟣 Unassigned Schedules &nbsp;&nbsp;&nbsp; |
""", unsafe_allow_html=True)

events = []
# University Color Mapping

university_colors = {
    "Delhi University": "#2563EB",      # Blue
    "Amity University": "#10B981",      # Green
    "Chandigarh University": "#F59E0B", # Orange
    "LPU": "#8B5CF6",                   # Purple
    "Manipal University": "#EF4444",    # Red
}

default_colors = [
    "#2563EB",
    "#10B981",
    "#F59E0B",
    "#8B5CF6",
    "#EF4444",
    "#EC4899",
    "#14B8A6",
    "#F97316",
    "#6366F1",
    "#84CC16"
]

# Auto assign colors to any new university
universities = sorted(
    filtered["University"]
    .dropna()
    .astype(str)
    .unique()
)

for i, uni in enumerate(universities):
    if uni not in university_colors:
        university_colors[uni] = default_colors[i % len(default_colors)]

for idx, row in filtered.iterrows():

    if pd.isna(row["Start"]):
        continue

    university = str(row.get("University", "Unknown"))

    color = university_colors.get(
        university,
        "#6366F1"
    )

    events.append({
        "id": f"evt_{idx}",
        "title": university,
        "start": row["Start"].strftime("%Y-%m-%d"),
        "end": row["End"].strftime("%Y-%m-%d"),
        "backgroundColor": color,
        "borderColor": color
    })

# The dynamic key prevents calendar redraw lockups during multi-variable sidebar selection changes
if filtered.empty:
   st.warning("No records found. Calendar is showing today's date.")
calendar_response = calendar(
    events=events,
    options={
        "initialView": "dayGridMonth",
        "initialDate": calendar_focus_date,
        "height": 750,
        "eventDisplay": "block",
        "dayMaxEvents": False,

        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listMonth"
        }
    },
    key=f"dynamic_calendar_{len(filtered)}"
)
st.divider()
# ==========================================
# EVENT CLICK DETAILS
# ==========================================

st.write(calendar_response)   # Temporary test

if calendar_response and "eventClick" in calendar_response:

    clicked_event = calendar_response["eventClick"]

    event_id = clicked_event["event"]["id"]

    idx = int(event_id.replace("evt_", ""))

    row = filtered.loc[idx]

    st.success(
        f"""
### 📋 Session Details

🏫 University: {row.get('University','N/A')}

🎓 Program: {row.get('Program','N/A')}

📚 Course: {row.get('Course','N/A')}

👨‍🏫 Trainer: {row.get('Mapped Trainers','N/A')}

👨‍🎓 Students: {row.get('No of students','N/A')}

📅 Start: {row['Start'].strftime('%d-%b-%Y')}

📅 End: {row['End'].strftime('%d-%b-%Y')}

💻 Delivery Mode: {row.get('Delivery mode','N/A')}
"""
    )

# =====================================================
# 9. GRAPHICAL STATISTICAL METRIC INSIGHTS
# =====================================================
c1, c2 = st.columns(2)

with c1:
    if "Program" in filtered.columns and "No of students" in filtered.columns and not filtered.empty:
        chart_df = filtered.groupby("Program")["No of students"].sum().reset_index()
        fig = px.bar(chart_df, x="Program", y="No of students", title="Student Volume Distribution per Program Stream", color="Program")
        st.plotly_chart(fig, use_container_width=True)

with c2:
    if "Delivery mode" in filtered.columns and "No of students" in filtered.columns and not filtered.empty:
        fig = px.pie(filtered, names="Delivery mode", values="No of students", hole=0.4, title="Active Mode Enrolment Ratio Setup")
        st.plotly_chart(fig, use_container_width=True)

# Treemap Implementation view
if "University" in filtered.columns and "Program" in filtered.columns and "No of students" in filtered.columns and not filtered.empty:
    fig_tree = px.treemap(filtered, path=["University", "Program"], values="No of students", title="Institutional Structural Distribution Breakdowns")
    st.plotly_chart(fig_tree, use_container_width=True)

# Instructor Workload Data Component Chart panel
if "Mapped Trainers" in filtered.columns and not filtered.empty:
    trainer_df = filtered.groupby("Mapped Trainers").size().reset_index(name="Active Class Formations Count").sort_values("Active Class Formations Count", ascending=False)
    fig_trainer = px.bar(trainer_df, x="Mapped Trainers", y="Active Class Formations Count", title="Assigned Training Faculty Cohort Loads", color="Active Class Formations Count")
    st.plotly_chart(fig_trainer, use_container_width=True)

# =====================================================
# 10. CLEAN AND PRECISELY ALIGNED DATA PREVIEW GRID
# =====================================================
st.subheader("📋 Comprehensive Operations Registry")

display_df = filtered.copy()

# Format timestamps to a clean text date string layout before outputting
if "Start" in display_df.columns:
    display_df["Start date"] = display_df["Start"].dt.strftime("%Y-%m-%d").fillna("Missing Date")
if "Closing date" in display_df.columns:
    display_df["Closing date"] = display_df["End"].dt.strftime("%Y-%m-%d").fillna("Missing Date")

# Drop messy custom backend timestamp columns
display_df.drop(columns=["Start", "End"], errors="ignore", inplace=True)

# Enforce clean custom alignment sequence headers
clean_sequence = [col for col in df.columns if col not in ["Start", "End"]]
display_df = display_df[clean_sequence]

st.data_editor(
    display_df,
    use_container_width=True,
    hide_index=True
)

# Data packet file download transaction mechanism pipeline
csv_data = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Currently Filtered Registry Dataset (CSV Format)",
    data=csv_data,
    file_name=f"academic_registry_export_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
