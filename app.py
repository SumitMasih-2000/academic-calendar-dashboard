import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
import os

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Academic Calendar Dashboard",
    page_icon="📅",
    layout="wide"
)

# ---------------------------------------------------
# APPLE THEME
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
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD EXCEL FILE AUTOMATICALLY
# ---------------------------------------------------

@st.cache_data
def load_data():

    excel_files = [f for f in os.listdir() if f.endswith(".xlsx")]

    if not excel_files:
        st.error("No Excel file found in repository.")
        st.stop()

    file_name = excel_files[0]

    df = pd.read_excel(file_name)

    return df, file_name


df, file_name = load_data()

st.sidebar.success(f"Loaded File: {file_name}")

# ---------------------------------------------------
# COLUMN CLEANING
# ---------------------------------------------------

df.columns = df.columns.str.strip()

# ---------------------------------------------------
# DATE CONVERSION
# ---------------------------------------------------

def convert_date(x):

    if pd.isna(x):
        return pd.NaT

    x = str(x)

    for suffix in ["st", "nd", "rd", "th"]:
        x = x.replace(suffix, "")

    try:
        return pd.to_datetime(
            x + " 2025",
            errors="coerce"
        )
    except:
        return pd.NaT


if "Start date" in df.columns:
    df["Start"] = df["Start date"].apply(convert_date)

if "Closing date" in df.columns:
    df["End"] = df["Closing date"].apply(convert_date)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.title("Filters")

filtered = df.copy()

if "University" in df.columns:

    university = st.sidebar.multiselect(
        "University",
        sorted(df["University"].dropna().unique())
    )

    if university:
        filtered = filtered[
            filtered["University"].isin(university)
        ]

if "Program" in df.columns:

    program = st.sidebar.multiselect(
        "Program",
        sorted(df["Program"].dropna().unique())
    )

    if program:
        filtered = filtered[
            filtered["Program"].isin(program)
        ]

if "Mapped Trainers" in df.columns:

    trainer = st.sidebar.multiselect(
        "Trainer",
        sorted(df["Mapped Trainers"].dropna().unique())
    )

    if trainer:
        filtered = filtered[
            filtered["Mapped Trainers"].isin(trainer)
        ]

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("📅 Academic Calendar Dashboard")

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:

    if "University" in filtered.columns:
        st.metric(
            "Universities",
            filtered["University"].nunique()
        )

with col2:

    if "Program" in filtered.columns:
        st.metric(
            "Programs",
            filtered["Program"].nunique()
        )

with col3:

    if "No of students" in filtered.columns:
        st.metric(
            "Students",
            int(filtered["No of students"].fillna(0).sum())
        )

with col4:

    if "Trainers required" in filtered.columns:
        st.metric(
            "Trainers Required",
            int(filtered["Trainers required"].fillna(0).sum())
        )

st.divider()

# ---------------------------------------------------
# CALENDAR EVENTS
# ---------------------------------------------------

events = []

if "Start" in filtered.columns:

    for _, row in filtered.iterrows():

        if pd.isna(row["Start"]):
            continue

        color = "#007AFF"

        if "Delivery mode" in filtered.columns:

            mode = str(row["Delivery mode"]).lower()

            if mode == "online":
                color = "#34C759"

            elif mode == "offline":
                color = "#007AFF"

            else:
                color = "#8E8E93"

        title = ""

        if "Program" in filtered.columns:
            title += str(row["Program"])

        if "University" in filtered.columns:
            title += " | " + str(row["University"])

        events.append({
            "title": title,
            "start": row["Start"].strftime("%Y-%m-%d"),
            "end": row["End"].strftime("%Y-%m-%d")
            if pd.notna(row["End"])
            else row["Start"].strftime("%Y-%m-%d"),
            "color": color
        })

# ---------------------------------------------------
# CALENDAR
# ---------------------------------------------------

st.subheader("Training Calendar")

calendar_options = {
    "initialView": "dayGridMonth",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "editable": True,
    "selectable": True,
    "nowIndicator": True,
    "height": 800
}

calendar(
    events=events,
    options=calendar_options
)

st.divider()

# ---------------------------------------------------
# PROGRAM CHART
# ---------------------------------------------------

if (
    "Program" in filtered.columns and
    "No of students" in filtered.columns
):

    chart = (
        filtered.groupby("Program")["No of students"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        chart,
        x="Program",
        y="No of students",
        title="Students by Program"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# DELIVERY MODE CHART
# ---------------------------------------------------

if (
    "Delivery mode" in filtered.columns and
    "No of students" in filtered.columns
):

    fig2 = px.pie(
        filtered,
        names="Delivery mode",
        values="No of students",
        title="Delivery Mode Distribution"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ---------------------------------------------------
# DATA TABLE
# ---------------------------------------------------

st.subheader("Schedule Details")

st.dataframe(
    filtered,
    use_container_width=True
)

# ---------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------

csv = filtered.to_csv(index=False)

st.download_button(
    "⬇ Download Filtered Data",
    csv,
    "academic_schedule.csv",
    "text/csv"
)
