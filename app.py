
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import os

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Academic Operations Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# PROFESSIONAL THEME
# =====================================================
st.markdown("""
<style>
:root{
    --bg:#F8FAFC;
    --sidebar:#1E3A8A;
    --accent:#2563EB;
    --card:#FFFFFF;
    --text:#0F172A;
}
.stApp{background-color:var(--bg);}
[data-testid="stSidebar"]{background:var(--sidebar);}
[data-testid="stSidebar"] *{color:white !important;}
div[data-testid="metric-container"]{
 background:white;
 border-radius:14px;
 padding:16px;
 border-left:5px solid #2563EB;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# DATA LOADER
# =====================================================
st.sidebar.title("Academic Filters")

uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset",
    type=["xlsx","csv"]
)

@st.cache_data
def load_data(file):
    if file is not None:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        return pd.read_excel(file)

    files = [f for f in os.listdir() if f.endswith((".xlsx",".csv"))]
    if not files:
        st.stop()

    if files[0].endswith(".csv"):
        return pd.read_csv(files[0])

    return pd.read_excel(files[0])

df = load_data(uploaded_file)

df.columns = df.columns.str.strip()

# =====================================================
# DATE HANDLING
# =====================================================
st.sidebar.markdown("---")
st.sidebar.subheader("Schedule Filters")

filtered = df.copy()

if not valid_dates.empty:

    years = sorted(valid_dates.dt.year.unique())

    selected_years = st.sidebar.multiselect(
        "Academic Year",
        years,
        default=years
    )

    filtered = filtered[
        filtered["Start"].dt.year.isin(selected_years)
    ]

    months = sorted(
        filtered["Start"].dropna().dt.month.unique()
    )

    selected_months = st.sidebar.multiselect(
        "Month",
        months,
        default=months
    )

    filtered = filtered[
        filtered["Start"].dt.month.isin(selected_months)
    ]

    min_date = filtered["Start"].min().date()
    max_date = filtered["Start"].max().date()

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date)
    )

    if len(date_range) == 2:
        start_filter, end_filter = date_range

        filtered = filtered[
            (filtered["Start"].dt.date >= start_filter) &
            (filtered["Start"].dt.date <= end_filter)
        ]

# =====================================================
# CASCADING FILTERS
# =====================================================
filter_cols = [
    c for c in [
        "University",
        "Program",
        "Courses/ Name of the paper",
        "Mapped Trainers",
        "Delivery mode"
    ] if c in filtered.columns
]

labels = {
    "University":"University",
    "Program":"Program",
    "Courses/ Name of the paper":"Course",
    "Mapped Trainers":"Faculty",
    "Delivery mode":"Delivery Mode"
}

for col in filter_cols:
    opts = sorted(filtered[col].dropna().astype(str).unique())
    selected = st.sidebar.multiselect(
        labels[col],
        opts,
        default=opts
    )
    filtered = filtered[filtered[col].astype(str).isin(selected)]
    
#MAIN AREA DASHBOARD DESIGN LAYOUT

st.markdown("""
<div style="
background:linear-gradient(135deg,#1E3A8A,#2563EB);
padding:20px;
border-radius:15px;
color:white;
margin-bottom:20px;
">
<h1>Academic Operations Dashboard</h1>
<p>Training Calendar | Faculty Allocation | Program Monitoring</p>
</div>
""", unsafe_allow_html=True)
# =====================================================
# KPI SECTION
# =====================================================
c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric("Universities",
              filtered["University"].nunique() if "University" in filtered.columns else 0)

with c2:
    st.metric("Programs",
              filtered["Program"].nunique() if "Program" in filtered.columns else 0)

with c3:
    st.metric("Students",
              int(filtered["No of students"].fillna(0).sum()) if "No of students" in filtered.columns else 0)

with c4:
    st.metric("Faculty",
              filtered["Mapped Trainers"].nunique() if "Mapped Trainers" in filtered.columns else 0)

# Hours
if "Delivery hrs" in filtered.columns:
    total_hours = filtered["Delivery hrs"].fillna(0).sum()

    completed_hours = filtered[
        filtered["End"] < pd.Timestamp.today()
    ]["Delivery hrs"].fillna(0).sum()

    remaining_hours = total_hours - completed_hours

    a,b,c = st.columns(3)
    a.metric("Training Hours", int(total_hours))
    b.metric("Hours Completed", int(completed_hours))
    c.metric("Hours Remaining", int(remaining_hours))

# =====================================================
# CALENDAR
# =====================================================
st.subheader("Academic Training Calendar")

events = []

if not filtered.empty:
    for idx,row in filtered.iterrows():
        if pd.isna(row["Start"]):
            continue

        title = f"{row.get('Courses/ Name of the paper','')} | {row.get('Mapped Trainers','')}"

        events.append({
            "id":f"evt_{idx}",
            "title":title,
            "start":row["Start"].strftime("%Y-%m-%d"),
            "end":row["End"].strftime("%Y-%m-%d") if pd.notna(row["End"]) else row["Start"].strftime("%Y-%m-%d")
        })

calendar_response = calendar(
    events=events,
    options={
        "initialView":"dayGridMonth",
        "height":700
    },
    key="calendar"
)

selected_uni = []
if "University" in st.session_state:
    selected_uni = st.session_state["University"]

if "University" in filtered.columns and not filtered.empty:
    st.info(
        "Current University Scope: " +
        ", ".join(filtered["University"].astype(str).unique())
    )

# =====================================================
# SESSION DETAILS
# =====================================================
if calendar_response and "eventClick" in calendar_response:

    clicked = calendar_response["eventClick"]
    idx = int(clicked["event"]["id"].replace("evt_",""))

    row = filtered.loc[idx]

    st.markdown("### Session Details")
    st.write({
        "University":row.get("University"),
        "Program":row.get("Program"),
        "Course":row.get("Courses/ Name of the paper"),
        "Faculty":row.get("Mapped Trainers"),
        "Students":row.get("No of students"),
        "Hours":row.get("Delivery hrs"),
        "Delivery Mode":row.get("Delivery mode")
    })

# =====================================================
# ANALYTICS
# =====================================================
st.subheader("Analytics")

if "Program" in filtered.columns and "No of students" in filtered.columns:
    chart = filtered.groupby("Program")["No of students"].sum().reset_index()
    st.plotly_chart(
        px.bar(chart,x="Program",y="No of students"),
        use_container_width=True
    )

if "Mapped Trainers" in filtered.columns:
    workload = filtered.groupby("Mapped Trainers").size().reset_index(name="Sessions")
    st.plotly_chart(
        px.bar(workload,x="Mapped Trainers",y="Sessions"),
        use_container_width=True
    )

# =====================================================
# UPCOMING SESSIONS
# =====================================================
st.subheader("Upcoming Sessions")

if "Start" in filtered.columns:
    upcoming = filtered.sort_values("Start").head(10)
    st.dataframe(upcoming, use_container_width=True)

# =====================================================
# DATA REGISTRY
# =====================================================
st.subheader("Academic Registry")
st.data_editor(filtered, use_container_width=True)

csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Data",
    csv_data,
    file_name="academic_registry_export.csv",
    mime="text/csv"
)
