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
# PROFESSIONAL CSS THEME
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
    box-shadow:0px 4px 12px rgba(0,0,0,0.08);
}

h1,h2,h3{
    color:#1E293B;
}

.fc-event{
    border:none !important;
    border-radius:8px !important;
    font-size:12px !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD FILE
# =====================================================

@st.cache_data
def load_data():

    files = [
        f for f in os.listdir()
        if f.endswith(".xlsx") or f.endswith(".csv")
    ]

    if not files:
        st.error("No Excel or CSV file found.")
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
# DATE CONVERSION
# =====================================================

def convert_date(x):

    if pd.isna(x):
        return pd.NaT

    x = str(x)

    for s in ["st","nd","rd","th"]:
        x = x.replace(s,"")

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
# SIDEBAR FILTERS
# =====================================================

st.sidebar.title("🎯 Filters")

filtered = df.copy()

for col in df.columns:

    if col not in ["Start","End"]:

        try:

            values = sorted(
                filtered[col]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected = st.sidebar.multiselect(
                f"🔽 {col}",
                values,
                default=values
            )

            filtered = filtered[
                filtered[col]
                .astype(str)
                .isin(selected)
            ]

        except:
            pass

# =====================================================
# SEARCH BOX
# =====================================================

st.title("🎓 Academic Operations Dashboard")

search = st.text_input(
    "🔍 Search Program / University / Trainer"
)

if search:

    filtered = filtered[
        filtered.astype(str)
        .apply(
            lambda x:
            x.str.contains(
                search,
                case=False
            )
        )
        .any(axis=1)
    ]

# =====================================================
# KPI SECTION
# =====================================================

students = 0
universities = 0
programs = 0
trainers = 0

if "No of students" in filtered.columns:
    students = int(
        filtered["No of students"]
        .fillna(0)
        .sum()
    )

if "University" in filtered.columns:
    universities = filtered["University"].nunique()

if "Program" in filtered.columns:
    programs = filtered["Program"].nunique()

if "Mapped Trainers" in filtered.columns:
    trainers = filtered["Mapped Trainers"].nunique()

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric(
        "🏫 Universities",
        universities
    )

with c2:
    st.metric(
        "🎓 Programs",
        programs
    )

with c3:
    st.metric(
        "👨‍🎓 Students",
        f"{students:,}"
    )

with c4:
    st.metric(
        "👨‍🏫 Trainers",
        trainers
    )

st.divider()

# =====================================================
# CALENDAR LEGEND
# =====================================================

st.markdown("""
### 📅 Training Calendar

🟢 Online &nbsp;&nbsp;&nbsp;
🔵 Offline &nbsp;&nbsp;&nbsp;
🟠 Hybrid
""")

# =====================================================
# CALENDAR EVENTS
# =====================================================

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

    title = ""

    if "Program" in filtered.columns:
        title += str(row["Program"])

    if "University" in filtered.columns:
        title += f" ({row['University']})"

    end_date = (
        row["End"]
        if pd.notna(row["End"])
        else row["Start"]
    )

    events.append({

        "title": title,

        "start":
        row["Start"].strftime("%Y-%m-%d"),

        "end":
        (
            end_date +
            pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d"),

        "color": color
    })

calendar_options = {

    "initialView":"dayGridMonth",

    "headerToolbar":{

        "left":"prev,next today",

        "center":"title",

        "right":
        "dayGridMonth,timeGridWeek,listMonth"
    },

    "height":700
}

calendar(
    events=events,
    options=calendar_options,
    key=f"calendar_{len(filtered)}"
)

st.divider()

# =====================================================
# ANALYTICS
# =====================================================

chart1, chart2 = st.columns(2)

# -----------------------------------------------------

with chart1:

    if (
        "Program" in filtered.columns and
        "No of students" in filtered.columns
    ):

        data = (
            filtered
            .groupby("Program")
            ["No of students"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            data.sort_values(
                "No of students",
                ascending=False
            ),
            x="Program",
            y="No of students",
            title="Students by Program",
            color_discrete_sequence=["#2563EB"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# -----------------------------------------------------

with chart2:

    if (
        "Delivery mode" in filtered.columns and
        "No of students" in filtered.columns
    ):

        fig = px.pie(
            filtered,
            names="Delivery mode",
            values="No of students",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# TREEMAP
# =====================================================

if (
    "University" in filtered.columns and
    "Program" in filtered.columns and
    "No of students" in filtered.columns
):

    fig = px.treemap(
        filtered,
        path=[
            "University",
            "Program"
        ],
        values="No of students",
        title="University → Program Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# TRAINER ANALYSIS
# =====================================================

if "Mapped Trainers" in filtered.columns:

    trainer_df = (
        filtered
        .groupby("Mapped Trainers")
        .size()
        .reset_index(name="Programs")
        .sort_values(
            "Programs",
            ascending=False
        )
    )

    fig = px.bar(
        trainer_df,
        x="Mapped Trainers",
        y="Programs",
        title="Trainer Workload"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# DATA TABLE
# =====================================================

st.subheader("📋 Detailed Academic Schedule")

display_df = filtered.copy()

for col in ["Start","End"]:
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
    "📥 Download CSV",
    csv,
    "academic_dashboard_export.csv",
    "text/csv"
)
