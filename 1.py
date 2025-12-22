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
st.sidebar.header("🎛️ Dashboard Filters")

platform_filter = st.sidebar.multiselect(
    "Platform", df["platform"].unique(), df["platform"].unique()
)
content_filter = st.sidebar.multiselect(
    "Content Type", df["content_type"].unique(), df["content_type"].unique()
)
year_filter = st.sidebar.multiselect(
    "Year", df["year"].unique(), df["year"].unique()
)

filtered_df = df[
    (df["platform"].isin(platform_filter)) &
    (df["content_type"].isin(content_filter)) &
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
st.title("🚀 Social Media Analytics Pro Dashboard")
st.markdown(
    "Engagement • Content • Campaign ROI • Best Time • **Fraud Detection**"
)

# =================================================
# KPI METRICS
# =================================================
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Engagement", int(filtered_df["engagement"].sum()))
c2.metric("Avg Engagement Rate (%)", round(filtered_df["engagement_rate"].mean(), 2))
c3.metric("Ad Spend (₹)", int(filtered_df["ad_spend"].sum()))
c4.metric("Revenue (₹)", int(filtered_df["revenue_generated"].sum()))
c5.metric("Avg ROI", round(filtered_df["roi"].mean(), 2))

# =================================================
# TABS
# =================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📱 Engagement", "🖼️ Content", "💰 Campaign ROI", "⏰ Best Time", "🚨 Fraud Detection"]
)

# =================================================
# TAB 1: ENGAGEMENT
# =================================================
with tab1:
    st.subheader("Platform-wise Engagement Rate")
    platform_eng = (
        filtered_df.groupby("platform")["engagement_rate"]
        .mean()
        .reset_index()
    )
    st.bar_chart(platform_eng, x="platform", y="engagement_rate")

# =================================================
# TAB 2: CONTENT PERFORMANCE
# =================================================
with tab2:
    st.subheader("Content Performance")
    content_perf = (
        filtered_df.groupby("content_type")[["likes", "comments", "shares", "engagement"]]
        .mean()
        .reset_index()
    )
    st.dataframe(content_perf)
    st.bar_chart(content_perf, x="content_type", y="engagement")

# =================================================
# TAB 3: CAMPAIGN ROI
# =================================================
with tab3:
    st.subheader("Campaign ROI Analysis")
    campaign_df = filtered_df[filtered_df["campaign_name"].notna()]
    campaign_summary = (
        campaign_df.groupby("campaign_name")[["ad_spend", "revenue_generated", "roi"]]
        .mean()
        .reset_index()
    )
    st.dataframe(campaign_summary)
    st.bar_chart(campaign_summary, x="campaign_name", y="roi")

# =================================================
# TAB 4: OPTIMAL POSTING TIME
# =================================================
with tab4:
    st.subheader("Best Posting Time (Hour-wise)")
    hourly = (
        filtered_df.groupby("post_hour")["engagement"]
        .mean()
        .reset_index()
    )
    st.line_chart(hourly, x="post_hour", y="engagement")

    best_hour = hourly.loc[hourly["engagement"].idxmax(), "post_hour"]
    st.success(f"✅ Best time to post: **{best_hour}:00 hrs**")

# =================================================
# TAB 5: FRAUD DETECTION
# =================================================
with tab5:
    st.subheader("🚨 Fraud Detection & Analysis")

    total_posts = len(filtered_df)
    fraud_posts = len(fraud_df)
    fraud_probability = (fraud_posts / total_posts) * 100 if total_posts else 0

    if fraud_probability < 5:
        risk_level = "LOW 🟢"
    elif fraud_probability < 15:
        risk_level = "MEDIUM 🟠"
    else:
        risk_level = "HIGH 🔴"

    a, b, c = st.columns(3)
    a.metric("Total Posts", total_posts)
    b.metric("Suspicious Posts", fraud_posts)
    c.metric("Fraud Risk", risk_level)

    # ---------- HEATMAP ----------
    st.markdown("### 🔥 Fraud Heatmap (Day × Hour)")
    fraud_heatmap = (
        fraud_df.groupby(["day_of_week", "post_hour"])
        .size()
        .reset_index(name="fraud_count")
    )

    if fraud_heatmap.empty:
        st.success("No suspicious activity detected")
    else:
        heatmap = alt.Chart(fraud_heatmap).mark_rect().encode(
            x="post_hour:O",
            y=alt.Y(
                "day_of_week:O",
                sort=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            ),
            color=alt.Color("fraud_count:Q", scale=alt.Scale(scheme="reds")),
            tooltip=["day_of_week", "post_hour", "fraud_count"]
        ).properties(height=350)

        st.altair_chart(heatmap, use_container_width=True)

    # ---------- PIE CHART ----------
    st.markdown("### 🥧 Day-wise Fraud Distribution")
    fraud_by_day = (
        fraud_df.groupby("day_of_week")
        .size()
        .reset_index(name="fraud_count")
    )

    if not fraud_by_day.empty:
        pie = alt.Chart(fraud_by_day).mark_arc(innerRadius=60).encode(
            theta="fraud_count:Q",
            color="day_of_week:N",
            tooltip=["day_of_week", "fraud_count"]
        ).properties(height=400)

        st.altair_chart(pie, use_container_width=True)

        for _, row in fraud_by_day.iterrows():
            st.write(f"• **{row['day_of_week']}** → {row['fraud_count']} suspicious post(s)")

        peak_day = fraud_by_day.loc[
            fraud_by_day["fraud_count"].idxmax(), "day_of_week"
        ]
        st.warning(f"⚠️ Highest suspicious activity on **{peak_day}**")

    # ---------- SAFE TIME ----------
    st.markdown("### 🛡️ Safe Time to Post")
    safe_df = (
        filtered_df[~filtered_df["suspicious"]]
        .groupby(["day_of_week", "post_hour"])
        .size()
        .reset_index(name="safe_posts")
    )

    if not safe_df.empty:
        safest = safe_df.loc[safe_df["safe_posts"].idxmax()]
        st.success(
            f"Safest time to post: **{safest['day_of_week']} at {safest['post_hour']}:00 hrs**"
        )

    # ---------- RECOMMENDATIONS ----------
    st.markdown("### 🧠 Recommendations")
    st.markdown("""
    • Avoid posting during high-risk days and hours  
    • Monitor posts with high engagement but low ROI  
    • Focus campaigns during safe posting windows  
    • Review suspicious campaigns manually  
    """)

# =================================================
# FOOTER
# =================================================
st.markdown("---")
st.markdown(
    "📌 Project 8 • Social Media Engagement Analytics • Fraud Detection Module"
)
