import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
import os

# ---------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(
    page_title="Academic Calendar Dashboard",
    page_icon="📅",
    layout="wide"
)

# ---------------------------------------------------
# 2. APPLE PREMIUM BLUE THEME (CSS INJECTION)
# ---------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F5F5F7;
}

[data-testid="stSidebar"] {
    background-color: white;
}

div[data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.06);
    border: 1px solid #E5E5EA;
}

/* Force full calendar events to look premium blue */
.fc-event {
    background-color: #007AFF !important;
    border-color: #007AFF !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# 3. AUTOMATIC DATA ENGINE PIPELINE
# ---------------------------------------------------
@st.cache_data
def load_data():
    # Automatically scan directory for any matching Excel or CSV data sheets
    supported_files = [f for f in os.listdir() if f.endswith(".xlsx") or f.endswith(".csv")]
    
    if not supported_files:
        st.error("❌ Data Engine Failure: Ensure your training spreadsheet dataset is saved right inside your script folder.")
        st.stop()
        
    file_name = supported_files[0]
    
    if file_name.endswith(".csv"):
        df = pd.read_csv(file_name)
    else:
        df = pd.read_excel(file_name)
        
    return df, file_name

df, file_name = load_data()
st.sidebar.success(f"📦 Loaded File: {file_name}")

# Standardize spaces out of column headers and text strings
df.columns = df.columns.str.strip()
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].fillna("Not Assigned").astype(str).str.strip()

# ---------------------------------------------------
# 4. ROBUST DATE REPAIR CONVERTER
# ---------------------------------------------------
def convert_date(x):
    if pd.isna(x) or str(x).strip() == "" or str(x).lower().strip() == "nan":
        return pd.NaT
    x = str(x)
    for suffix in ["st", "nd", "rd", "th"]:
        x = x.replace(suffix, "")
    try:
        # Standardize timelines into a single operational anchor year
        return pd.to_datetime(x + " 2025", errors="coerce")
    except:
        return pd.NaT

if "Start date" in df.columns:
    df["Start"] = df["Start date"].apply(convert_date)
if "Closing date" in df.columns:
    df["End"] = df["Closing date"].apply(convert_date)
else:
    df["End"] = df["Start"]

# ---------------------------------------------------
# 5. INTEGRATED GLOBAL SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.title("💠 Operations Controls")

filtered = df.copy()

# Filter 1: University
if "University" in df.columns:
    university_opts = sorted(df["University"].dropna().unique())
    selected_uni = st.sidebar.multiselect("🏫 University / Institution", university_opts, default=university_opts)
    filtered = filtered[filtered["University"].isin(selected_uni)]

# Filter 2: Program Path
if "Program" in df.columns:
    program_opts = sorted(df["Program"].dropna().unique())
    selected_prog = st.sidebar.multiselect("🎓 Academic Program", program_opts, default=program_opts)
    filtered = filtered[filtered["Program"].isin(selected_prog)]

# Filter 3: Course Module Papers
if "Courses/ Name of the paper" in df.columns:
    paper_opts = sorted(df["Courses/ Name of the paper"].dropna().unique())
    selected_papers = st.sidebar.multiselect("📚 Course Module Paper", paper_opts, default=paper_opts)
    filtered = filtered[filtered["Courses/ Name of the paper"].isin(selected_papers)]

# Filter 4: Delivery Format Modality
if "Delivery mode" in df.columns:
    mode_opts = sorted(df["Delivery mode"].dropna().unique())
    selected_modes = st.sidebar.multiselect("💻 Delivery Modality Mode", mode_opts, default=mode_opts)
    filtered = filtered[filtered["Delivery mode"].isin(selected_modes)]

# Filter 5: NEW SCHEDULE TYPE FEATURE INCLUDED HERE
if "Weekly/ Blocked" in df.columns:
    schedule_opts = sorted(df["Weekly/ Blocked"].dropna().unique())
    selected_schedules = st.sidebar.multiselect("📅 Schedule Type Pattern", schedule_opts, default=schedule_opts)
    filtered = filtered[filtered["Weekly/ Blocked"].isin(selected_schedules)]

# Filter 6: Assigned Faculty Trainer
if "Mapped Trainers" in df.columns:
    trainer_opts = sorted(df["Mapped Trainers"].dropna().unique())
    selected_trainers = st.sidebar.multiselect("👨‍🏫 Assigned Faculty Trainer", trainer_opts)
    if selected_trainers:
        filtered = filtered[filtered["Mapped Trainers"].isin(selected_trainers)]

# ---------------------------------------------------
# 6. CORE APP TITLE & HEADLINE METRICS (KPIs)
# ---------------------------------------------------
st.title("📅 Enterprise Academic Operations Dashboard")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if "University" in filtered.columns:
        st.metric("Institutions Active", filtered["University"].nunique())
with col2:
    if "Program" in filtered.columns:
        st.metric("Programs Managed", filtered["Program"].nunique())
with col3:
    if "No of students" in filtered.columns:
        st.metric("Total Trainees Enrolled", f"{int(filtered['No of students'].fillna(0).sum()):,}")
with col4:
    if "Trainers required" in filtered.columns:
        st.metric("Allocated Faculty Slots", int(filtered["Trainers required"].fillna(0).sum()))

st.divider()

# ---------------------------------------------------
# 7. CORPORATE BLUE TRAINING CALENDAR MATRIX
# ---------------------------------------------------
st.subheader("📋 Interactive Training Program Grid")

events = []
for _, row in filtered.iterrows():
    if pd.isna(row["Start"]):
        continue
        
    # Corporate Blue Palette Mapping Strategy (Replaces Green/Orange with Blues)
    mode = str(row.get("Delivery mode", "")).lower().strip()
    if "online" in mode:
        color = "#0A84FF"      # Light Electric Apple Blue
    elif "offline" in mode:
        color = "#1E3A8A"     # Deep Navy Corporate Blue
    else:
        color = "#007AFF"      # Standard Apple System Blue

    # Construct clean event label descriptors
    title_components = []
    if "Program" in filtered.columns: title_components.append(str(row["Program"]))
    if "Courses/ Name of the paper" in filtered.columns: title_components.append(str(row["Courses/ Name of the paper"]))
    if "University" in filtered.columns: title_components.append(str(row["University"]))
    
    event_title = " | ".join(title_components)
    
    # Calculate reliable ending date boundaries safely
    end_date = row["End"] if pd.notna(row["End"]) else row["Start"]
    # Add 1 day padding rule for calendar framework visibility requirements
    end_calendar_str = (end_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    events.append({
        "title": event_title,
        "start": row["Start"].strftime("%Y-%m-%d"),
        "end": end_calendar_str,
        "color": color,
        "backgroundColor": color,
        "borderColor": color,
        "textColor": "#FFFFFF"
    })

# Anchor view layout onto May 2025 so records populate instantly
calendar_options = {
    "initialView": "dayGridMonth",
    "initialDate": "2025-05-01",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,listMonth"
    },
    "editable": True,
    "selectable": True,
    "nowIndicator": True,
    "height": 700
}

# Unique dynamic key forces the calendar widget to refresh cleanly when filters change
unique_calendar_key = f"apple_blue_matrix_{len(filtered)}"

calendar(
    events=events,
    options=calendar_options,
    key=unique_calendar_key
)

st.divider()

# ---------------------------------------------------
# 8. REFINED ANALYTICS SYSTEM (EXECUTIVE BLUES)
# ---------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if "Program" in filtered.columns and "No of students" in filtered.columns:
        chart_data = filtered.groupby("Program")["No of students"].sum().reset_index()
        
        # Sorted bar chart rendered in high contrast corporate blues
        fig1 = px.bar(
            chart_data.sort_values(by="No of students", ascending=False),
            x="Program",
            y="No of students",
            title="Student Density Breakdown by Program",
            color_discrete_sequence=["#007AFF"]
        )
        fig1.update_layout(plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)", template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    if "Delivery mode" in filtered.columns and "No of students" in filtered.columns:
        # Pie chart using clean blue variations
        fig2 = px.pie(
            filtered,
            names="Delivery mode",
            values="No of students",
            title="Volume Delivery Mode Share Ratio",
            hole=0.4,
            color_discrete_sequence=["#1E3A8A", "#0A84FF", "#5AC8FA"]
        )
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# 9. COMPREHENSIVE DATA ENGINE SHEET LOOKUP & EXPORT
# ---------------------------------------------------
st.subheader("📋 Production Schedule Operational Log")

# Drop internal processing column vectors cleanly before presenting to users
display_df = filtered.copy()
for col in ["Start", "End"]:
    if col in display_df.columns:
        display_df = display_df.drop(columns=[col])

st.dataframe(display_df, use_container_width=True)

csv_data = display_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Cleaned Working Dataset (CSV)",
    data=csv_data,
    file_name="academic_schedule_export.csv",
    mime="text/csv"
)
