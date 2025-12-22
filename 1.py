import streamlit as st
import pandas as pd

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Social Media Analytics Pro",
    page_icon="🚀",
    layout="wide"
)

# =================================================
# CUSTOM CSS
# =================================================
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #141E30, #243B55);
}
.main {
    background: linear-gradient(to right, #141E30, #243B55);
}
h1, h2, h3, h4 {
    color: white;
}
.metric-card {
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
}
.metric-card.green {
    background: linear-gradient(135deg, #11998e, #38ef7d);
}
.metric-card.orange {
    background: linear-gradient(135deg, #f7971e, #ffd200);
}
.metric-card.red {
    background: linear-gradient(135deg, #ff416c, #ff4b2b);
}
.metric-card.blue {
    background: linear-gradient(135deg, #396afc, #2948ff);
}
</style>
""", unsafe_allow_html=True)

# =================================================
# LOAD DATA
# =================================================
@st.cache_data
def load_data():
    df = pd.read_csv("social_media_engagement_enhanced (1).csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["post_hour"] = df["date"].dt.hour
    df["engagement"] = df["likes"] + df["comments"] + df["shares"]
    df["engagement_rate"] = (df["engagement"] / df["reach"]) * 100
    df["revenue_generated"] = df["ad_spend"] * (1 + df["roi"])
    return df

df = load_data()

# =================================================
# SIDEBAR FILTERS
# =================================================
st.sidebar.markdown("## 🎛️ Dashboard Controls")

platform_filter = st.sidebar.multiselect(
    "📱 Platform",
    df["platform"].unique(),
    df["platform"].unique()
)

content_filter = st.sidebar.multiselect(
    "🖼️ Content Type",
    df["content_type"].unique(),
    df["content_type"].unique()
)

year_filter = st.sidebar.multiselect(
    "📅 Year",
    df["year"].unique(),
    df["year"].unique()
)

filtered_df = df[
    (df["platform"].isin(platform_filter)) &
    (df["content_type"].isin(content_filter)) &
    (df["year"].isin(year_filter))
]

# =================================================
# HEADER
# =================================================
st.markdown("""
<h1 style='text-align:center;'>🚀 Social Media Analytics Pro Dashboard</h1>
<p style='text-align:center;color:#dcdcdc;font-size:18px;'>
Engagement • Content • Campaign ROI • Revenue • Best Posting Time • Strategy
</p>
""", unsafe_allow_html=True)

# =================================================
# KPI CARDS
# =================================================
c1, c2, c3, c4, c5 = st.columns(5)

c1.markdown(f"<div class='metric-card blue'><h3>Total Engagement</h3><h2>{int(filtered_df['engagement'].sum())}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card green'><h3>Avg Engagement Rate</h3><h2>{round(filtered_df['engagement_rate'].mean(),2)}%</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card orange'><h3>Total Ad Spend</h3><h2>₹ {int(filtered_df['ad_spend'].sum())}</h2></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card red'><h3>Revenue Generated</h3><h2>₹ {int(filtered_df['revenue_generated'].sum())}</h2></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='metric-card blue'><h3>Average ROI</h3><h2>{round(filtered_df['roi'].mean(),2)}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# =================================================
# TABS (ADDED STRATEGY TAB)
# =================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📱 Engagement", "🖼️ Content", "💰 Campaign ROI", "⏰ Best Time", "🎥 Video Promotion Strategy"]
)

# ---------------- TAB 1 ----------------
with tab1:
    st.subheader("📱 Platform Engagement Comparison")
    platform_eng = filtered_df.groupby("platform")["engagement_rate"].mean().reset_index()
    st.bar_chart(platform_eng, x="platform", y="engagement_rate")
    best_platform = platform_eng.loc[platform_eng["engagement_rate"].idxmax(), "platform"]
    st.success(f"🏆 Best Platform: **{best_platform}**")

# ---------------- TAB 2 ----------------
with tab2:
    st.subheader("🖼️ Content Performance")
    content_perf = filtered_df.groupby("content_type")[["likes","comments","shares","engagement"]].mean().reset_index()
    st.dataframe(content_perf)
    st.bar_chart(content_perf, x="content_type", y="engagement")

# ---------------- TAB 3 ----------------
with tab3:
    st.subheader("💰 Campaign ROI & Revenue")
    campaign_df = filtered_df[filtered_df["campaign_name"].notna()]
    campaign_summary = campaign_df.groupby("campaign_name")[["ad_spend","revenue_generated","roi"]].mean().reset_index()
    st.dataframe(campaign_summary)
    st.bar_chart(campaign_summary, x="campaign_name", y="revenue_generated")
    st.bar_chart(campaign_summary, x="campaign_name", y="roi")

# ---------------- TAB 4 ----------------
with tab4:
    st.subheader("⏰ Optimal Posting Time")
    hourly = filtered_df.groupby("post_hour")["engagement"].mean().reset_index()
    st.line_chart(hourly, x="post_hour", y="engagement")
    best_hour = hourly.loc[hourly["engagement"].idxmax(), "post_hour"]
    st.success(f"🔥 Best Posting Time: **{best_hour}:00 hrs**")

# ---------------- TAB 5 (NEW STRATEGY) ----------------
with tab5:
    st.subheader("🎥 Platform Strategy for Promotional Videos")

    video_df = filtered_df[
        filtered_df["content_type"].str.lower().str.contains("video")
    ]

    if video_df.empty:
        st.warning("No video content available for selected filters.")
    else:
        video_platform = (
            video_df.groupby("platform")["reach"]
            .mean()
            .reset_index()
            .sort_values(by="reach", ascending=False)
        )

        st.bar_chart(video_platform, x="platform", y="reach")

        best_video_platform = video_platform.iloc[0]["platform"]
        st.success(
            f"🚀 Best platform to post MORE promotional videos: **{best_video_platform}**"
        )

        st.markdown("""
### 🧠 Insight
- Video reach varies significantly by platform  
- Focus promotional video campaigns on the top-performing platform  
- Combine with optimal posting time for maximum visibility
        """)

# =================================================
# FOOTER
# =================================================
st.markdown("""
<hr>
<p style='text-align:center;color:#bbbbbb;'>
Project 8 • Social Media Engagement Analytics • Built with ❤️ using Streamlit
</p>
""", unsafe_allow_html=True)
Project 8 • Social Media Engagement Analytics • Built with ❤️ using Streamlit
</p>
""", unsafe_allow_html=True)
