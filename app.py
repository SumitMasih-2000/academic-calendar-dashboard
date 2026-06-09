import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
import os

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Academic Operations Dashboard",
    page_icon="🎓",
    layout="wide"
)

# =====================================================
# THEME
# =====================================================

st.markdown("""
<style>

.stApp{
    background:#F8FAFC;
}

[data-testid="stSidebar"]{
    background:#0F172A;
}

[data-testid="stSidebar"] *{
    color:white;
}

div[data-testid="metric-container"]{
    background:white;
    padding:18px;
    border-radius:15px;
    border-left:5px solid #2563EB;
    box-shadow:0 4px 12px rgba(0,0,0,.08);
}

.fc-event{
    border:none !important;
    border-radius:8px !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    files = [
        f for f in os.listdir()
        if f.endswith(".xlsx") or f.endswith(".csv")
    ]

    if not files:
        st.error("No Excel/CSV file found.")
        st.stop()

    file_name = files[0]

    if file_name.endswith(".csv"):
        df = pd.read_csv(file_name)
    else:
        df = pd.read_excel(file_name)

    return df, file_name


df, file_name = load_data()

st.sidebar.success(f"Loaded: {file_name}")

# =====================================================
# CLEAN DATA
# =====================================================

df.columns = df.columns.str.strip()

for col in df.select_dtypes(include="object").columns:
    df[col] = (
        df[col]
        .fillna("Not Assigned")
        .astype(str)
        .str.strip()
    )

# =====================================================
# DATE CONVERTER
# =====================================================

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
else:
    df["End"] = df["Start"]

# =====================================================
# CASCADING FILTERS
# =====================================================

st.sidebar.title("🎯 Dashboard Filters")

filtered = df.copy()

exclude_cols = ["Start", "End"]

filter_columns = [
    c for c in df.columns
    if c not in exclude_cols
]

# University First

priority = []

if "University" in filter_columns:
    priority.append("University")

remaining = [
    c for c in filter_columns
    if c not in priority
]

filter_columns = priority + remaining

for col in filter_columns:

    available_values = sorted(
        filtered[col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected = st.sidebar.multiselect(
        f"🔽 {col}",
        available_values,
        default=available_values,
        key=col
    )

    filtered = filtered[
        filtered[col]
        .astype(str)
        .isin(selected)
    ]

# =====================================================
# SEARCH
# =====================================================

search = st.sidebar.text_input(
    "🔍 Search Anything"
)

if search:

    filtered = filtered[
        filtered.astype(str)
        .apply(
            lambda x:
            x.str.contains(
                search,
                case=False,
                na=False
            )
        )
        .any(axis=1)
    ]

# =====================================================
# HEADER
# =====================================================

st.title("🎓 Academic Operations Dashboard")

st.info(
    f"""
    📊 Records: {len(filtered)}
    
    🏫 Universities: {filtered['University'].nunique() if 'University' in filtered.columns else 0}
    
    🎓 Programs: {filtered['Program'].nunique() if 'Program' in filtered.columns else 0}
    """
)

# =====================================================
# KPI CARDS
# =====================================================

col1,col2,col3,col4 = st.columns(4)

with col1:
    value = (
        filtered["University"].nunique()
        if "University" in filtered.columns
        else 0
    )

    st.metric(
        "🏫 Universities",
        value
    )

with col2:
    value = (
        filtered["Program"].nunique()
        if "Program" in filtered.columns
        else 0
    )

    st.metric(
        "🎓 Programs",
        value
    )

with col3:

    if "No of students" in filtered.columns:
        students = int(
            pd.to_numeric(
                filtered["No of students"],
                errors="coerce"
            ).fillna(0).sum()
        )
    else:
        students = 0

    st.metric(
        "👨‍🎓 Students",
        f"{students:,}"
    )

with col4:

    if "Mapped Trainers" in filtered.columns:
        trainers = filtered[
            "Mapped Trainers"
        ].nunique()
    else:
        trainers = 0

    st.metric(
        "👨‍🏫 Trainers",
        trainers
    )

st.divider()

# =====================================================
# CALENDAR
# =====================================================

st.subheader("📅 Academic Calendar")

st.markdown(
"""
🟢 Online &nbsp;&nbsp;
🔵 Offline &nbsp;&nbsp;
🟠 Hybrid
""",
unsafe_allow_html=True
)

events = []

for _, row in filtered.iterrows():

    if pd.isna(row["Start"]):
        continue

    mode = str(
        row.get(
            "Delivery mode",
            ""
        )
    ).lower()

    if "online" in mode:
        color = "#10B981"

    elif "offline" in mode:
        color = "#2563EB"

    elif "hybrid" in mode:
        color = "#F59E0B"

    else:
        color = "#6366F1"

    title_parts = []

    if "Program" in filtered.columns:
        title_parts.append(str(row["Program"]))

    if "University" in filtered.columns:
        title_parts.append(str(row["University"]))

    title = " | ".join(title_parts)

    end_date = (
        row["End"]
        if pd.notna(row["End"])
        else row["Start"]
    )

    events.append(
        {
            "title": title,
            "start": row["Start"].strftime("%Y-%m-%d"),
            "end": (
                end_date +
                pd.Timedelta(days=1)
            ).strftime("%Y-%m-%d"),
            "color": color
        }
    )

calendar(
    events=events,
    options={
        "initialView":"dayGridMonth",
        "height":700,
        "headerToolbar":{
            "left":"prev,next today",
            "center":"title",
            "right":"dayGridMonth,timeGridWeek,listMonth"
        }
    },
    key=f"calendar_{len(filtered)}"
)

st.divider()

# =====================================================
# CHARTS
# =====================================================

c1,c2 = st.columns(2)

with c1:

    if (
        "Program" in filtered.columns
        and
        "No of students" in filtered.columns
    ):

        chart_df = (
            filtered
            .groupby("Program")
            ["No of students"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            chart_df,
            x="Program",
            y="No of students",
            title="Students by Program"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with c2:

    if (
        "Delivery mode" in filtered.columns
        and
        "No of students" in filtered.columns
    ):

        fig = px.pie(
            filtered,
            names="Delivery mode",
            values="No of students",
            hole=0.4,
            title="Delivery Mode Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# TREEMAP
# =====================================================

if (
    "University" in filtered.columns
    and
    "Program" in filtered.columns
    and
    "No of students" in filtered.columns
):

    fig = px.treemap(
        filtered,
        path=["University","Program"],
        values="No of students",
        title="University Program Structure"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# TRAINER WORKLOAD
# =====================================================

if "Mapped Trainers" in filtered.columns:

    trainer_df = (
        filtered
        .groupby("Mapped Trainers")
        .size()
        .reset_index(name="Count")
        .sort_values(
            "Count",
            ascending=False
        )
    )

    fig = px.bar(
        trainer_df,
        x="Mapped Trainers",
        y="Count",
        title="Trainer Workload"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# DATA TABLE
# =====================================================

st.subheader("📋 Schedule Details")

display_df = filtered.copy()

for col in ["Start", "End"]:
    if col in display_df.columns:
        display_df.drop(
            columns=[col],
            inplace=True
        )

st.data_editor(
    display_df,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# DOWNLOAD
# =====================================================

csv = display_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "📥 Download Filtered Data",
    csv,
    "academic_dashboard_export.csv",
    "text/csv"
)
