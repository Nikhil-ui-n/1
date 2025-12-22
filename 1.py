import streamlit as st
import pandas as pd
import altair as alt

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Social Media Analytics Pro – Fraud Intelligence",
    page_icon="🚀",
    layout="wide"
)

# =================================================
# LOAD DATA (USE SAME DATABASE)
# =================================================
@st.cache_data
def load_data():
    df = pd.read_csv("social_media_engagement.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# =================================================
# DERIVED METRICS
# =================================================
df["revenue_generated"] = df["ad_spend"] * (1 + df["roi"])
df["day_of_week"] = df["date"].dt.day_name()

# =================================================
# SIDEBAR FILTERS
# =================================================
st.sidebar.header("🎛️ Dashboard Controls")

platform_filter = st.sidebar.multiselect(
    "Platform", df["platform"].unique(), df["platform"].unique()
)
year_filter = st.sidebar.multiselect(
    "Year", df["year"].unique(), df["year"].unique()
)

filtered_df = df[
    (df["platform"].isin(platform_filter)) &
    (df["year"].isin(year_filter))
]

# =================================================
# HEADER
# =================================================
st.title("🚨 Fraud Intelligence – Social Media Analytics")
st.markdown(
    "Detecting **suspicious marketing activity** using abnormal engagement & ROI patterns"
)

# =================================================
# FRAUD LOGIC (CORE)
# =================================================
high_engagement_threshold = filtered_df["engagement"].quantile(0.90)

filtered_df["suspicious"] = (
    (filtered_df["engagement"] > high_engagement_threshold) &
    (filtered_df["roi"] <= 0)
)

fraud_df = filtered_df[filtered_df["suspicious"]]

# =================================================
# 1️⃣ FRAUD RISK SCORE (LOW / MEDIUM / HIGH)
# =================================================
st.header("1️⃣ Fraud Risk Score")

total_posts = len(filtered_df)
fraud_posts = len(fraud_df)

fraud_ratio = (fraud_posts / total_posts) * 100 if total_posts > 0 else 0

if fraud_ratio < 5:
    risk_level = "LOW 🟢"
elif fraud_ratio < 15:
    risk_level = "MEDIUM 🟠"
else:
    risk_level = "HIGH 🔴"

c1, c2, c3 = st.columns(3)
c1.metric("Total Posts", total_posts)
c2.metric("Suspicious Posts", fraud_posts)
c3.metric("Fraud Risk Level", risk_level)

# =================================================
# 2️⃣ FRAUD HEATMAP (DAY × HOUR)
# =================================================
st.markdown("---")
st.header("2️⃣ Fraud Heatmap (Day vs Hour)")

fraud_heatmap = (
    fraud_df
    .groupby(["day_of_week", "post_hour"])
    .size()
    .reset_index(name="fraud_count")
)

if fraud_heatmap.empty:
    st.success("✅ No suspicious marketing patterns detected")
else:
    heatmap = alt.Chart(fraud_heatmap).mark_rect().encode(
        x=alt.X("post_hour:O", title="Posting Hour"),
        y=alt.Y(
            "day_of_week:O",
            sort=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            title="Day of Week"
        ),
        color=alt.Color(
            "fraud_count:Q",
            scale=alt.Scale(scheme="reds"),
            title="Fraud Intensity"
        ),
        tooltip=["day_of_week", "post_hour", "fraud_count"]
    ).properties(
        height=350
    )

    st.altair_chart(heatmap, use_container_width=True)

# =================================================
# 3️⃣ AUTO FRAUD INSIGHTS & RECOMMENDATIONS
# =================================================
st.markdown("---")
st.header("3️⃣ Fraud Insights & Recommendations")

if fraud_df.empty:
    st.success("🟢 Marketing activity looks healthy with no abnormal patterns.")
else:
    peak_hour = (
        fraud_df.groupby("post_hour").size().idxmax()
        if not fraud_df.empty else "N/A"
    )

    peak_day = (
        fraud_df.groupby("day_of_week").size().idxmax()
        if not fraud_df.empty else "N/A"
    )

    peak_platform = (
        fraud_df.groupby("platform").size().idxmax()
        if not fraud_df.empty else "N/A"
    )

    st.warning("⚠️ Potential Fraud Patterns Detected")

    st.markdown(f"""
### 🔍 Key Observations
- Highest suspicious activity observed around **{peak_hour}:00 hrs**
- Riskier days: **{peak_day}**
- Platform with more anomalies: **{peak_platform}**

### 🧠 Recommendations
- Avoid aggressive ad spending during **{peak_day} at {peak_hour}:00 hrs**
- Review engagement sources for **{peak_platform}**
- Validate traffic quality before scaling campaigns
- Implement stricter monitoring for high-engagement / low-ROI posts
""")

# =================================================
# FOOTER
# =================================================
st.markdown("---")
st.markdown(
    "📌 **Fraud Intelligence Module – Project 8 (Social Media Engagement Analytics)**"
)
