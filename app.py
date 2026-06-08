import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Academic Calendar Dashboard",
    page_icon="📅",
    layout="wide"
)

# ---------------------------------------------------
# APPLE STYLE
# ---------------------------------------------------

st.markdown("""
<style>

.stApp{
    background-color:#F5F5F7;
}

[data-testid="stSidebar"]{
    background-color:white;
}

div[data-testid="metric-container"]{
    background:white;
    border-radius:12px;
    padding:15px;
    box-shadow:0px 2px 10px rgba(0,0,0,0.08);
}

h1,h2,h3{
    color:#1d1d1f;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():
    return pd.read_excel(
        "Sample _data.xlsx",
        sheet_name="Dataset"
    )

df = load_data()

# ---------------------------------------------------
# DATE CONVERSION
# ---------------------------------------------------

def convert_date(date_text):

    if pd.isna(date_text):
        return pd.NaT

    try:
        cleaned = str(date_text)

        for suffix in ["st","nd","rd","th"]:
            cleaned = cleaned.replace(suffix,"")

        return pd.to_datetime(
            cleaned + " 2025",
            errors="coerce"
        )

    except:
        return pd.NaT


df["Start"] = df["Start date"].apply(convert_date)
df["End"] = df["Closing date"].apply(convert_date)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("Filters")

university = st.sidebar.multiselect(
    "University",
    sorted(df["University "].dropna().unique())
)

program = st.sidebar.multiselect(
    "Program",
    sorted(df["Program"].dropna().unique())
)

trainer = st.sidebar.multiselect(
    "Trainer",
    sorted(df["Mapped Trainers"].dropna().unique())
)

delivery = st.sidebar.multiselect(
    "Delivery Mode",
    sorted(df["Delivery mode"].dropna().unique())
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

if delivery:
    filtered = filtered[
        filtered["Delivery mode"].isin(delivery)
    ]

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("📅 Academic Calendar Dashboard")

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

col1,col2,col3,col4 = st.columns(4)

with col1:
    st.metric(
        "Universities",
        filtered["University "].nunique()
    )

with col2:
    st.metric(
        "Programs",
        filtered["Program"].nunique()
    )

with col3:
    st.metric(
        "Students",
        int(filtered["No of students"].sum())
    )

with col4:
    st.metric(
        "Trainers Required",
        int(filtered["Trainers required"].sum())
    )

st.markdown("---")

# ---------------------------------------------------
# CALENDAR EVENTS
# ---------------------------------------------------

events = []

for _, row in filtered.iterrows():

    if pd.isna(row["Start"]):
        continue

    color = "#007AFF"

    if str(row["Delivery mode"]).lower() == "online":
        color = "#34C759"

    elif str(row["Delivery mode"]).lower() == "offline":
        color = "#007AFF"

    else:
        color = "#8E8E93"

    events.append(
        {
            "title":
                f"{row['Program']} - "
                f"{row['University ']}",

            "start":
                row["Start"].strftime("%Y-%m-%d"),

            "end":
                row["End"].strftime("%Y-%m-%d")
                if pd.notna(row["End"])
                else row["Start"].strftime("%Y-%m-%d"),

            "color":
                color
        }
    )

# ---------------------------------------------------
# CALENDAR
# ---------------------------------------------------

st.subheader("Training Schedule")

calendar_options = {
    "initialView":"dayGridMonth",

    "headerToolbar":{
        "left":"prev,next today",
        "center":"title",
        "right":"dayGridMonth,timeGridWeek,timeGridDay"
    },

    "editable":True,
    "selectable":True,
    "nowIndicator":True,
    "height":800
}

calendar(
    events=events,
    options=calendar_options
)

st.markdown("---")

# ---------------------------------------------------
# CHARTS
# ---------------------------------------------------

col1,col2 = st.columns(2)

with col1:

    students_chart = (
        filtered.groupby("Program")["No of students"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        students_chart,
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
        title="Delivery Mode Distribution"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ---------------------------------------------------
# UNIVERSITY CHART
# ---------------------------------------------------

uni_chart = (
    filtered.groupby("University ")["No of students"]
    .sum()
    .reset_index()
)

fig3 = px.bar(
    uni_chart,
    x="University ",
    y="No of students",
    title="Students by University"
)

st.plotly_chart(
    fig3,
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
    label="⬇ Download Filtered Data",
    data=csv,
    file_name="academic_schedule.csv",
    mime="text/csv"
)
