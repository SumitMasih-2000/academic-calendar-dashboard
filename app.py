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
st.set_page_config(
    page_title="Academic Operations Dashboard",
    page_icon="🎓",
    layout="wide"
)

# Premium executive high-contrast custom dashboard presentation styles
st.markdown("""
<style>

/* Main Background */
.stApp {
    background-color: #F4F7FC;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0F172A;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Keep dropdown text readable */
[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: black !important;
}

/* KPI Cards */
div[data-testid="metric-container"] {
    background: white;
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #14B8A6;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Headers */
h1, h2, h3 {
    color: #0F172A;
}

/* Buttons */
.stButton > button {
    background-color: #14B8A6;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #0F766E;
    color: white;
}

/* Download Button */
.stDownloadButton > button {
    background-color: #14B8A6;
    color: white;
    border-radius: 8px;
}

/* Data Editor / Tables */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Calendar Events */
.fc-event {
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600;
    padding: 2px;
}

/* Info Boxes */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 600;
}

/* Metric Labels */
[data-testid="metric-container"] label {
    color: #0F172A !important;
}

/* Metric Values */
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0F172A;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 2. DATA INGESTION MATRIX
# =====================================================
@st.cache_data
def load_data():
    files = [f for f in os.listdir() if f.endswith(".xlsx") or f.endswith(".csv")]
    if not files:
        st.error("❌ Data Engine Failure: No Excel/CSV dataset discovered in the root application directory.")
        st.stop()
    
    file_name = files[0]
    if file_name.endswith(".csv"):
        df = pd.read_csv(file_name)
    else:
        df = pd.read_excel(file_name)
    return df, file_name

df, file_name = load_data()
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
st.sidebar.title("🎯 Cascading Filters Matrix")

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
# 6. UNIVERSAL GLOBAL TEXT SEARCH STRATEGIES
# =====================================================
search = st.sidebar.text_input("🔍 Search Anything")
if search:
    filtered = filtered[
        filtered.astype(str)
        .apply(lambda x: x.str.contains(search, case=False, na=False))
        .any(axis=1)
    ]

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

with col5:
    session_count = len(filtered)
    st.metric("📚 Total Sessions", session_count)

st.divider()

# =====================================================
# 8. HIGH-CONTRAST INTERACTIVE BLUE CALENDAR COMPONENT
# =====================================================
st.subheader("📅 Academic Operational Scheduler Calendar")

st.markdown("""
🟢 **Online Modality** &nbsp;&nbsp;|&nbsp;&nbsp; 
🔵 **Offline Classrooms** &nbsp;&nbsp;|&nbsp;&nbsp; 
🟠 **Hybrid Configurations** &nbsp;&nbsp;|&nbsp;&nbsp; 
🟣 **Unassigned Schedules**
""", unsafe_allow_html=True)

events = []
for idx, row in filtered.iterrows():
    if pd.isna(row["Start"]):
        continue

    mode = str(row.get("Delivery mode", "")).lower()
    if "online" in mode: color = "#10B981"
    elif "offline" in mode: color = "#2563EB"
    elif "hybrid" in mode: color = "#F59E0B"
    else: color = "#6366F1"

    title_parts = []
    if "Program" in filtered.columns: title_parts.append(str(row["Program"]))
    if "University" in filtered.columns: title_parts.append(str(row["University"]))
    title = " | ".join(title_parts)

    events.append({
        "id": f"evt_{idx}",
        "title": title,
        "start": row["Start"].strftime("%Y-%m-%d"),
        "end": (row["End"] + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
        "backgroundColor": color,
        "borderColor": color,
        "textColor": "#FFFFFF"
    })

# The dynamic key prevents calendar redraw lockups during multi-variable sidebar selection changes
calendar(
    events=events,
    options={
        "initialView": "dayGridMonth",
        "height": 650,
        "navLinks": True,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listMonth"
        }
    },
    key=f"dynamic_calendar_{len(filtered)}"
)

st.divider()

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
