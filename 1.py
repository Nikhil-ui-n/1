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
year_filter = st.sidebar.multiselect(
    "Year", df["year"].unique(), df["year"].unique()
)

filtered_df = df[
    (df["platform"].isin(platform_filter)) &
    (df["year"].isin(year_filter))
]

# =================================================
# FRAUD LOGIC
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
st.title("🚀 Social Media Analytics Pro – Strategy Dashboard")
st.markdown(
    "Analytics • ROI • Best Time • Fraud Detection • Video Strategy • **Content Mix Strategy**"
)

# =================================================
# KPI METRICS
# =================================================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Engagement", int(filtered_df["engagement"].sum()))
c2.metric("Avg Engagement Rate", round(filtered_df["engagement_rate"].mean(), 2))
c3.metric("Revenue (₹)", int(filtered_df["revenue_generated"].sum()))
c4.metric("Avg ROI", round(filtered_df["roi"].mean(), 2))

# =================================================
# TABS
# =================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📱 Engagement",
        "💰 ROI",
        "⏰ Best Time",
        "🚨 Fraud",
        "🎥 Video Strategy",
        "🧠 Content Mix Strategy"
    ]
)

# =================================================
# TAB 6: CONTENT MIX STRATEGY (NEW 🔥)
# =================================================
with tab6:
    st.subheader("🧠 Content Mix Optimization Strategy")

    st.markdown(
        "This analysis helps decide **how much to invest in each content type** "
        "based on **Reach, Engagement, and ROI**."
    )

    # Aggregate by content type
    content_strategy = (
        filtered_df.groupby("content_type")
        .agg(
            avg_reach=("reach", "mean"),
            avg_engagement=("engagement", "mean"),
            avg_roi=("roi", "mean"),
            post_count=("content_type", "count")
        )
        .reset_index()
    )

    st.markdown("### 📊 Content Type Performance Summary")
    st.dataframe(content_strategy)

    # Charts
    st.markdown("### 📈 Engagement by Content Type")
    st.bar_chart(content_strategy, x="content_type", y="avg_engagement")

    st.markdown("### 👀 Reach by Content Type")
    st.bar_chart(content_strategy, x="content_type", y="avg_reach")

    st.markdown("### 💰 ROI by Content Type")
    st.bar_chart(content_strategy, x="content_type", y="avg_roi")

    # Best content decisions
    best_engagement = content_strategy.loc[
        content_strategy["avg_engagement"].idxmax(), "content_type"
    ]
    best_reach = content_strategy.loc[
        content_strategy["avg_reach"].idxmax(), "content_type"
    ]
    best_roi = content_strategy.loc[
        content_strategy["avg_roi"].idxmax(), "content_type"
    ]

    st.success(f"🔥 Best for Engagement: **{best_engagement}**")
    st.success(f"👀 Best for Reach: **{best_reach}**")
    st.success(f"💰 Best for ROI: **{best_roi}**")

    # Strategy recommendation
    st.markdown("""
### ✅ Content Mix Recommendation
- Use **high-engagement content** to boost interaction and visibility  
- Use **high-reach content** for brand awareness  
- Invest ad budget on **high-ROI content types**  
- Balance the posting calendar using a mix of all three objectives
    """)

# =================================================
# OTHER TABS (SUMMARY)
# =================================================
with tab1:
    st.subheader("Platform-wise Engagement Rate")
    st.bar_chart(
        filtered_df.groupby("platform")["engagement_rate"].mean().reset_index(),
        x="platform",
        y="engagement_rate"
    )

with tab2:
    st.subheader("Campaign ROI")
    camp = filtered_df[filtered_df["campaign_name"].notna()]
    st.dataframe(
        camp.groupby("campaign_name")[["roi","revenue_generated"]].mean().reset_index()
    )

with tab3:
    st.subheader("Best Posting Time")
    hourly = filtered_df.groupby("post_hour")["engagement"].mean().reset_index()
    st.line_chart(hourly, x="post_hour", y="engagement")

with tab4:
    st.subheader("Fraud Detection")
    st.metric("Suspicious Posts", len(fraud_df))

with tab5:
    st.subheader("Video Strategy")
    video_df = filtered_df[filtered_df["content_type"].str.lower().str.contains("video")]
    if not video_df.empty:
        st.bar_chart(
            video_df.groupby("platform")["reach"].mean().reset_index(),
            x="platform",
            y="reach"
        )

# =================================================
# FOOTER
# =================================================
st.markdown("---")
st.markdown(
    "📌 Project 8 • Social Media Engagement Analytics • Strategy & Decision Intelligence"
)
