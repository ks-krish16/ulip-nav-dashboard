import os
import pandas as pd
import streamlit as st

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="ULIP Fund Comparison Dashboard",
    layout="wide"
)
st.markdown("""
<style>

/* Main background */

.main{
    background-color:white;
}

/* Hide Streamlit menu */

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

/* Sidebar */

section[data-testid="stSidebar"]{

    background:white;

    border-right:1px solid #DDDDDD;

}

/* Metric cards */

div[data-testid="metric-container"]{

    background:white;

    border:1px solid #DDDDDD;

    padding:20px;

    border-radius:8px;

}

/* Tables */

thead tr th{

    background:#F8F8F8 !important;

}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# FILE PATH
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR,
    "output_result",
    "category_comparision",
    "Category_Comparison.xlsx"
)

# ==========================================================
# LOAD DATA
# ==========================================================


def load_data():

    return pd.read_excel(DATA_FILE)


def get_rating(score):

    if pd.isna(score):
        return "Insufficient Data"
    elif score >= 80:
        return "Strong"
    elif score >= 65:
        return "Good"
    elif score >= 50:
        return "Average"
    else:
        return "Weak / Review"


def rating_color(rating):

    if rating == "Strong":
        return "#0F9D58"

    elif rating == "Good":
        return "#3F51B5"

    elif rating == "Average":
        return "#F9A825"

    elif rating == "Weak / Review":
        return "#D32F2F"

    else:
        return "#757575"


df = load_data()

df["Final Rating"] = df["Final Score"].apply(get_rating)

# ==========================================================
# DASHBOARD TITLE
# ==========================================================

st.title("ULIP Fund Comparison Dashboard")

st.markdown("---")
# ==========================================================
# PHASE 1
# ==========================================================

# ==========================================================
# SIDEBAR FILTERS
# ==========================================================

st.sidebar.title("Filters")

# ---------------- Insurer ---------------- #

insurer = st.sidebar.selectbox(

    "Select Insurer",

    ["All"] + sorted(df["Insurer"].dropna().unique())

)

# ---------------- Broad Category ---------------- #

broad_category = st.sidebar.selectbox(

    "Select Broad Category",

    ["All"] + sorted(df["Broad Category"].dropna().unique())

)

# ---------------- Fund ---------------- #

fund = st.sidebar.selectbox(

    "Select Fund",

    ["All"] + sorted(df["Fund Name"].dropna().unique())

)

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered_df = df.copy()

if insurer != "All":

    filtered_df = filtered_df[
        filtered_df["Insurer"] == insurer
    ]

if broad_category != "All":

    filtered_df = filtered_df[
        filtered_df["Broad Category"] == broad_category
    ]

if fund != "All":

    filtered_df = filtered_df[
        filtered_df["Fund Name"] == fund
    ]

# ==========================================================
# KPI CARDS
# ==========================================================

st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(

        "Total Funds",

        len(filtered_df)

    )

with col2:

    st.metric(

        "Average Return Score",

        round(filtered_df["Return Score"].mean(), 2)

    )

with col3:

    st.metric(

        "Average Risk Score",

        round(filtered_df["Risk Score"].mean(), 2)

    )

with col4:

    st.metric(

        "Average Consistency Score",

        round(filtered_df["Consistency Score"].mean(), 2)

    )



# ==========================================================
# PHASE 2
# ==========================================================


# ==========================================================
# FUND RANKING TABLE
# ==========================================================

st.markdown("---")

st.subheader("Fund Rankings")

display_df = filtered_df.copy()

display_df = display_df.sort_values(
    by="Final Score",
    ascending=False
)

display_df.insert(
    0,
    "Rank",
    range(1, len(display_df) + 1)
)

columns = [
    "Rank",
    "Fund Name",
    "Insurer",
    "Broad Category",
    "Final Score",
    "Return Score",
    "Risk Score",
    "Consistency Score"
]

st.dataframe(
    display_df[columns],
    use_container_width=True,
    height=500
)

# ==========================================================
# TOP 10 FUNDS
# ==========================================================

st.markdown("---")

st.subheader("Top 10 Funds")

top10 = (
    filtered_df
    .sort_values(
        "Final Score",
        ascending=False
    )
    .head(10)
)

import plotly.express as px

fig = px.bar(

    top10,

    x="Final Score",

    y="Fund Name",

    orientation="h",

    text="Final Score"

)

fig.update_layout(

    template="simple_white",

    title="",

    xaxis_title="Final Score",

    yaxis_title="",

    height=500

)

fig.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# PHASE 3
# ==========================================================

# ==========================================================
# RISK VS RETURN
# ==========================================================

st.markdown("---")

st.subheader("Risk vs Return Analysis")

left, right = st.columns([3,2])

with left:

    scatter = filtered_df.dropna(
        subset=[
            "Risk Score",
            "Return Score"
        ]
    )

    fig = px.scatter(

        scatter,

        x="Risk Score",

        y="Return Score",

        hover_name="Fund Name",

        hover_data=[
            "Insurer",
            "Broad Category",
            "Final Score"
        ],

        symbol="Broad Category"

    )

    fig.update_traces(

        marker=dict(

            color="black",

            size=10,

            line=dict(

                color="white",

                width=1

            )

        )

    )

    fig.update_layout(

        template="simple_white",

        height=520,

        xaxis_title="Risk Score",

        yaxis_title="Return Score",

        legend_title="Broad Category"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# FUND DETAILS
# ==========================================================

with right:

    st.subheader("Fund Details")

    fund = st.selectbox(

        "Select Fund",

        sorted(
            filtered_df["Fund Name"].dropna().unique()
        )

    )

    row = filtered_df[
        filtered_df["Fund Name"] == fund
    ].iloc[0]
    color = rating_color(row["Final Rating"])

    st.markdown(
        f"""
        <div style="
            background:{color};
            color:white;
            padding:10px;
            border-radius:6px;
            text-align:center;
            font-weight:600;
            font-size:18px;
        ">
            {row["Final Rating"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.metric(
        "Final Score",
        "-" if pd.isna(row["Final Score"]) else round(row["Final Score"],2)
    )

    st.metric(
        "Return Score",
        "-" if pd.isna(row["Return Score"]) else round(row["Return Score"],2)
    )

    st.metric(
        "Risk Score",
        "-" if pd.isna(row["Risk Score"]) else round(row["Risk Score"],2)
    )

    st.metric(
        "Consistency Score",
        "-" if pd.isna(row["Consistency Score"]) else round(row["Consistency Score"],2)
    )

    st.markdown("---")

    st.write("**Insurer**")
    st.write(row["Insurer"])

    st.write("**Broad Category**")
    st.write(row["Broad Category"])

    st.write("**Category**")
    st.write(row["Category"])

    st.write("**Category Rank**")
    st.write(
        "-"
        if pd.isna(row["Category Rank"])
        else int(row["Category Rank"])
    )

# ==========================================================
# DOWNLOAD SECTION
# ==========================================================

st.markdown("---")

st.subheader("Download")

with open(DATA_FILE, "rb") as file:

    st.download_button(

        label="Download Category Comparison",

        data=file,

        file_name="Category_Comparison.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

# ==========================================================
# PHASE 4
# ==========================================================


# ==========================================================
# FINAL FUND RATINGS
# ==========================================================

st.markdown("---")

st.subheader("Final Fund Ratings")

rating_table = filtered_df[
    [
        "Fund Name",
        "Insurer",
        "Broad Category",
        "Final Score",
        "Final Rating"
    ]
].copy()

rating_table = rating_table.sort_values(
    "Final Score",
    ascending=False,
    na_position="last"
)


def color_rating(val):

    if val == "Strong":
        return "background-color:#0F9D58; color:white"

    elif val == "Good":
        return "background-color:#3F51B5; color:white"

    elif val == "Average":
        return "background-color:#F9A825; color:black"

    elif val == "Weak / Review":
        return "background-color:#D32F2F; color:white"

    else:
        return "background-color:#757575; color:white"

styled = rating_table.style.map(
    color_rating,
    subset=["Final Rating"]
)

st.dataframe(
    styled,
    use_container_width=True,
    hide_index=True
)
# ==========================================================
# RATING DISTRIBUTION
# ==========================================================

st.markdown("---")
st.subheader("Rating Distribution")

rating_count = (
    filtered_df["Final Rating"]
    .value_counts()
    .reindex(
        [
            "Strong",
            "Good",
            "Average",
            "Weak / Review",
            "Insufficient Data"
        ],
        fill_value=0
    )
)

rating_df = rating_count.reset_index()
rating_df.columns = ["Final Rating", "Number of Funds"]

fig = px.bar(
    rating_df,
    x="Number of Funds",
    y="Final Rating",
    orientation="h",
    text="Number of Funds",
    color="Final Rating",
    color_discrete_map={
        "Strong": "#0F9D58",             # Green
        "Good": "#3F51B5",               # Blue
        "Average": "#F9A825",            # Orange
        "Weak / Review": "#D32F2F",      # Red
        "Insufficient Data": "#757575"   # Grey
    }
)

fig.update_layout(
    height=350,
    showlegend=False,
    xaxis_title="Number of Funds",
    yaxis_title="",
    template="simple_white"
)

fig.update_traces(textposition="outside")

st.plotly_chart(
    fig,
    use_container_width=True
)


st.markdown("---")
st.subheader("Final Rating Scale")

rating_df = pd.DataFrame({

    "Score Range": [
        "80 - 100",
        "65 - 79",
        "50 - 64",
        "Below 50",
        "No Score"
    ],

    "Rating": [
        "Strong",
        "Good",
        "Average",
        "Weak / Review",
        "Insufficient Data"
    ],

    "Meaning": [
        "Good performance with acceptable risk",
        "Suitable for most investment profiles",
        "Needs further review before recommendation",
        "Lower priority for recommendation",
        "Insufficient historical NAV data"
    ]

})

st.dataframe(
    rating_df,
    use_container_width=True,
    hide_index=True
)