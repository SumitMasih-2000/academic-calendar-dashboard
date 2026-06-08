import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import plotly.express as px
from datetime import datetime

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Academic Calendar Dashboard",
    page_icon="📅",
    layout="wide"
)

# -----------------------------------
# APPLE THEME CSS
# -----------------------------------

st.markdown("""
<style>

.main {
    background-color:#f5f5f7;
}

[data-testid="stSidebar"]{
    background-color:white;
}

.kpi{
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# LOAD DATA
# -----------------------------------

@st.cache_data
def load_data():
    df = pd.read_excel(
        "Sample_data.xlsx",
        sheet_name="Dataset"
    )
    return df

df = load_data()

# -----------------------------------
# DATE CLEANING
# -----------------------------------

year = 2025

def clean_date(x):

    if pd.isna(x):
        return None

    x = str(x).lower()

    x = x.replace("st","")
    x = x.replace("nd","")
    x = x.replace("rd","")
    x = x.replace("th","")

    try:
        return pd.to_datetime(
            f"{x} {year}",
            format="%d %B %Y"
        )
    except:
        return pd.NaT


df["Start"] = df["Start date"].apply(clean_date)
df["End"] = df["Closing date"].apply(clean_date)

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("Filters")

university = st.sidebar.multiselect(
    "University",
    df["University "].unique()
)

program = st.sidebar.multiselect(
    "Program",
    df["Program"].unique()
)

trainer = st.sidebar.multiselect(
    "Trainer",
    df["Mapped Trainers"].dropna().unique()
)

filtered = df.copy()

if university:
    filtered = filtered[
        filtered["University "].isin(university)
    ]

if program:
    filtered = filtered[
        filtered["Program"].isin(program)
    ]

if trainer:
    filtered = filtered[
        filtered["Mapped Trainers"].isin(trainer)
    ]

# -----------------------------------
# KPI SECTION
# -----------------------------------

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric(
        "Universities",
        filtered["University "].nunique()
    )

with c2:
    st.metric(
        "Programs",
        filtered["Program"].nunique()
    )

with c3:
    st.metric(
        "Students",
        filtered["No of students"].sum()
    )

with c4:
    st.metric(
        "Trainers Required",
        filtered["Trainers required"].sum()
    )

st.divider()

# -----------------------------------
# CALENDAR EVENTS
# -----------------------------------

events = []

for _, row in filtered.iterrows():

    color = "#007AFF"

    if row["Delivery mode"] == "Online":
        color = "#34C759"

    elif row["Delivery mode"] == "Offline":
        color = "#007AFF"

    else:
        color = "#8E8E93"

    events.append(
        {
            "title":
                f"{row['Program']} | "
                f"{row['University ']}",

            "start":
                row["Start"].strftime("%Y-%m-%d"),

            "end":
                row["End"].strftime("%Y-%m-%d"),

            "color":
                color
        }
    )

# -----------------------------------
# CALENDAR OPTIONS
# -----------------------------------

calendar_options = {
    "initialView":"dayGridMonth",

    "headerToolbar":{
        "left":"prev,next today",
        "center":"title",
        "right":"dayGridMonth,timeGridWeek,timeGridDay"
    },

    "editable":True,
    "selectable":True,
    "height":800
}

st.subheader("📅 Academic Delivery Calendar")

calendar(
    events=events,
    options=calendar_options
)

# -----------------------------------
# CHARTS
# -----------------------------------

st.divider()

col1,col2 = st.columns(2)

with col1:

    fig = px.bar(
        filtered.groupby("Program")
        ["No of students"]
        .sum()
        .reset_index(),

        x="Program",
        y="No of students",
        title="Students by Program"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig2 = px.pie(
        filtered,
        names="Delivery mode",
        values="No of students",
        title="Delivery Mode"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# -----------------------------------
# TABLE
# -----------------------------------

st.subheader("Schedule Details")

st.dataframe(
    filtered,
    use_container_width=True
)

# -----------------------------------
# EXPORT
# -----------------------------------

csv = filtered.to_csv(index=False)

st.download_button(
    "Download Filtered Data",
    csv,
    file_name="academic_schedule.csv"
)