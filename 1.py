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
    "Engagement • Content • Campaign ROI • Best Time • Fraud Detection • Strategy"
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "📱 Engagement",
        "🖼️ Content",
        "💰 Campaign ROI",
        "⏰ Best Time",
        "🚨 Fraud Detection",
        "🎥 Video Strategy",
        "🧠 Content Mix Strategy"
    ]
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
    st.subheader("Content Performance Comparison")
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
    st.subheader("Campaign ROI & Revenue")
    campaign_df = filtered_df[filtered_df["campaign_name"].notna()]
    campaign_summary = (
        campaign_df.groupby("campaign_name")[["ad_spend", "revenue_generated", "roi"]]
        .mean()
        .reset_index()
    )
    st.dataframe(campaign_summary)
    st.bar_chart(campaign_summary, x="campaign_name", y="roi")

# =================================================
# TAB 4: BEST TIME
# =================================================
with tab4:
    st.subheader("Optimal Posting Time (Hour-wise)")
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

    # Heatmap
    st.markdown("### 🔥 Fraud Heatmap (Day × Hour)")
    fraud_heatmap = (
        fraud_df.groupby(["day_of_week", "post_hour"])
        .size()
        .reset_index(name="fraud_count")
    )

    if not fraud_heatmap.empty:
        heatmap = alt.Chart(fraud_heatmap).mark_rect().encode(
            x="post_hour:O",
            y=alt.Y(
                "day_of_week:O",
                sort=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            ),
            color=alt.Color("fraud_count:Q", scale=alt.Scale(scheme="reds")),
            tooltip=["day_of_week", "post_hour", "fraud_count"]
        )
        st.altair_chart(heatmap, use_container_width=True)

    # Pie chart
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
        )
        st.altair_chart(pie, use_container_width=True)

        peak_day = fraud_by_day.loc[
            fraud_by_day["fraud_count"].idxmax(), "day_of_week"
        ]
        st.warning(f"⚠️ Highest suspicious activity on **{peak_day}**")

    # Safe time
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
            f"Safest time: **{safest['day_of_week']} at {safest['post_hour']}:00 hrs**"
        )

# =================================================
# TAB 6: VIDEO PROMOTION STRATEGY
# =================================================
with tab6:
    st.subheader("🎥 Video Promotion Strategy")

    video_df = filtered_df[
        filtered_df["content_type"].str.lower().str.contains("video")
    ]

    if video_df.empty:
        st.warning("No video data available")
    else:
        video_platform_reach = (
            video_df.groupby("platform")["reach"]
            .mean()
            .reset_index()
            .sort_values(by="reach", ascending=False)
        )

        st.bar_chart(video_platform_reach, x="platform", y="reach")

        best_platform = video_platform_reach.iloc[0]["platform"]
        st.success(
            f"🚀 Best platform to post more promotional videos: **{best_platform}**"
        )

# =================================================
# TAB 7: CONTENT MIX STRATEGY
# =================================================
with tab7:
    st.subheader("🧠 Content Mix Optimization Strategy")

    content_strategy = (
        filtered_df.groupby("content_type")
        .agg(
            avg_reach=("reach", "mean"),
            avg_engagement=("engagement", "mean"),
            avg_roi=("roi", "mean")
        )
        .reset_index()
    )

    st.dataframe(content_strategy)

    st.bar_chart(content_strategy, x="content_type", y="avg_engagement")
    st.bar_chart(content_strategy, x="content_type", y="avg_reach")
    st.bar_chart(content_strategy, x="content_type", y="avg_roi")

    best_eng = content_strategy.loc[
        content_strategy["avg_engagement"].idxmax(), "content_type"
    ]
    best_reach = content_strategy.loc[
        content_strategy["avg_reach"].idxmax(), "content_type"
    ]
    best_roi = content_strategy.loc[
        content_strategy["avg_roi"].idxmax(), "content_type"
    ]

    st.success(f"🔥 Best for Engagement: **{best_eng}**")
    st.success(f"👀 Best for Reach: **{best_reach}**")
    st.success(f"💰 Best for ROI: **{best_roi}**")

# =================================================
# FOOTER
# =================================================
st.markdown("---")
st.markdown(
    "📌 Project 8 • Social Media Engagement Analytics • Full Strategy & Fraud Intelligence"
)
st.markdown(
    "📌 Project 8 • Social Media Engagement Analytics • Strategy & Decision Intelligence"
)
