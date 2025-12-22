import streamlit as st
import pandas as pd
import altair as alt

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Social Media Analytics Pro",
    page_icon="🚀",
    layout="wide"
)

# =================================================
# LOAD DATA
# =================================================
@st.cache_data
def load_data():
    df = pd.read_csv("social_media_engagement_enhanced (1).csv")
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
st.sidebar.header("🎛️ Filters")

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
# FRAUD DETECTION LOGIC
# =================================================
high_engagement_threshold = filtered_df["engagement"].quantile(0.90)

filtered_df["suspicious"] = (
    (filtered_df["engagement"] > high_engagement_threshold) &
    (filtered_df["roi"] <= 0)
)

fraud_df = filtered_df[filtered_df["suspicious"]]

# =================================================
# HEADER
# =================================================
st.title("🚨 Fraud Detection – Social Media Analytics")
st.markdown(
    "Analysis of **suspicious marketing activity** using abnormal engagement and ROI patterns"
)

# =================================================
# KPI SUMMARY
# =================================================
c1, c2, c3 = st.columns(3)

total_posts = len(filtered_df)
fraud_posts = len(fraud_df)
fraud_prob = (fraud_posts / total_posts) * 100 if total_posts else 0

if fraud_prob < 5:
    risk_level = "LOW 🟢"
elif fraud_prob < 15:
    risk_level = "MEDIUM 🟠"
else:
    risk_level = "HIGH 🔴"

c1.metric("Total Posts", total_posts)
c2.metric("Suspicious Posts", fraud_posts)
c3.metric("Fraud Risk", risk_level)

# =================================================
# FRAUD HEATMAP (DAY × HOUR)
# =================================================
st.markdown("---")
st.subheader("🔥 Fraud Heatmap (Day × Hour)")

fraud_heatmap = (
    fraud_df.groupby(["day_of_week", "post_hour"])
    .size()
    .reset_index(name="fraud_count")
)

if fraud_heatmap.empty:
    st.success("✅ No suspicious activity detected")
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
    ).properties(height=350)

    st.altair_chart(heatmap, use_container_width=True)

# =================================================
# PIE CHART – DAY-WISE FRAUD DISTRIBUTION
# =================================================
st.markdown("---")
st.subheader("🥧 Day-wise Fraud Distribution")

fraud_by_day = (
    fraud_df.groupby("day_of_week")
    .size()
    .reset_index(name="fraud_count")
)

if fraud_by_day.empty:
    st.success("✅ No fraud data available for pie chart")
else:
    pie = alt.Chart(fraud_by_day).mark_arc(innerRadius=60).encode(
        theta=alt.Theta("fraud_count:Q", title="Fraud Count"),
        color=alt.Color(
            "day_of_week:N",
            legend=alt.Legend(title="Day of Week")
        ),
        tooltip=["day_of_week", "fraud_count"]
    ).properties(
        width=400,
        height=400
    )

    st.altair_chart(pie, use_container_width=True)

# =================================================
# DAY-WISE FRAUD ANALYSIS (TEXT)
# =================================================
st.markdown("### 📊 Day-wise Fraud Analysis")

if not fraud_by_day.empty:
    for _, row in fraud_by_day.iterrows():
        st.write(
            f"• **{row['day_of_week']}** → {row['fraud_count']} suspicious post(s)"
        )

    peak_day = fraud_by_day.loc[
        fraud_by_day["fraud_count"].idxmax(), "day_of_week"
    ]

    st.warning(
        f"⚠️ Highest suspicious marketing activity observed on **{peak_day}**"
    )

# =================================================
# SAFE TIME TO POST
# =================================================
st.markdown("---")
st.subheader("🛡️ Safe Time to Post")

safe_df = (
    filtered_df[~filtered_df["suspicious"]]
    .groupby(["day_of_week", "post_hour"])
    .size()
    .reset_index(name="safe_posts")
)

if not safe_df.empty:
    safest = safe_df.loc[safe_df["safe_posts"].idxmax()]
    st.success(
        f"✅ Safest time to post: **{safest['day_of_week']} at {safest['post_hour']}:00 hrs**"
    )

# =================================================
# RECOMMENDATIONS
# =================================================
st.markdown("---")
st.subheader("🧠 Recommendations")

st.markdown("""
• Avoid posting during high-risk days and hours  
• Monitor high engagement but low ROI posts  
• Focus campaigns during safe posting windows  
• Perform manual review on suspicious campaigns  
""")

# =================================================
# FOOTER
# =================================================
st.markdown("---")
st.markdown(
    "📌 Project 8 • Social Media Engagement Analytics • Fraud Detection Module"
)
