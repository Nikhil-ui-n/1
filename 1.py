import streamlit as st
import pandas as pd

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Social Media Analytics Pro Dashboard",
    page_icon="🚀",
    layout="wide"
)

# =================================================
# CUSTOM CSS (COLORFUL UI)
# =================================================
st.markdown("""
<style>
body, .main {
    background: linear-gradient(to right, #141E30, #243B55);
}
h1, h2, h3, h4 {
    color: white;
}
.metric-card {
    padding: 25px;
    border-radius: 18px;
    color: white;
    text-align: center;
    font-weight: bold;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.4);
}
.blue { background: linear-gradient(135deg,#396afc,#2948ff); }
.green { background: linear-gradient(135deg,#11998e,#38ef7d); }
.orange { background: linear-gradient(135deg,#f7971e,#ffd200); }
.red { background: linear-gradient(135deg,#ff416c,#ff4b2b); }
.purple { background: linear-gradient(135deg,#667eea,#764ba2); }
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
st.sidebar.markdown("## 🎛️ Dashboard Filters")

platform_filter = st.sidebar.multiselect("📱 Platform", df["platform"].unique(), df["platform"].unique())
content_filter = st.sidebar.multiselect("🖼️ Content Type", df["content_type"].unique(), df["content_type"].unique())
year_filter = st.sidebar.multiselect("📅 Year", df["year"].unique(), df["year"].unique())

filtered_df = df[
    (df["platform"].isin(platform_filter)) &
    (df["content_type"].isin(content_filter)) &
    (df["year"].isin(year_filter))
]

# =================================================
# HEADER
# =================================================
st.markdown("""
<h1 style="text-align:center;">🚀 Social Media Analytics Pro Dashboard</h1>
<p style="text-align:center;color:#dcdcdc;font-size:18px;">
Engagement • ROI • Strategy • Detection • Growth
</p>
""", unsafe_allow_html=True)

# =================================================
# KPI CARDS
# =================================================
c1, c2, c3, c4, c5 = st.columns(5)

c1.markdown(f"<div class='metric-card blue'><h3>Total Engagement</h3><h2>{int(filtered_df['engagement'].sum())}</h2></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card green'><h3>Avg Engagement Rate</h3><h2>{round(filtered_df['engagement_rate'].mean(),2)}%</h2></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card orange'><h3>Ad Spend</h3><h2>₹ {int(filtered_df['ad_spend'].sum())}</h2></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card red'><h3>Revenue</h3><h2>₹ {int(filtered_df['revenue_generated'].sum())}</h2></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='metric-card purple'><h3>Avg ROI</h3><h2>{round(filtered_df['roi'].mean(),2)}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# =================================================
# TABS
# =================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📱 Engagement",
    "🖼️ Content",
    "💰 Campaign ROI",
    "⏰ Best Time",
    "🎥 Video Strategy",
    "🚀 Smart Promotion Detection"
])

# =================================================
# TAB 1: ENGAGEMENT
# =================================================
with tab1:
    st.subheader("📱 Platform Engagement Rate")
    platform_eng = filtered_df.groupby("platform")["engagement_rate"].mean().reset_index()
    st.bar_chart(platform_eng, x="platform", y="engagement_rate")
    best_platform = platform_eng.loc[platform_eng["engagement_rate"].idxmax(),"platform"]
    st.success(f"🏆 Best Engagement Platform: **{best_platform}**")

# =================================================
# TAB 2: CONTENT PERFORMANCE
# =================================================
with tab2:
    st.subheader("🖼️ Content Performance Comparison")
    content_perf = filtered_df.groupby("content_type")[["likes","comments","shares","engagement"]].mean().reset_index()
    st.dataframe(content_perf)
    st.bar_chart(content_perf, x="content_type", y="engagement")

# =================================================
# TAB 3: CAMPAIGN ROI
# =================================================
with tab3:
    st.subheader("💰 Campaign ROI & Revenue")
    campaign_df = filtered_df[filtered_df["campaign_name"].notna()]
    campaign_summary = campaign_df.groupby("campaign_name")[["ad_spend","revenue_generated","roi"]].mean().reset_index()
    st.dataframe(campaign_summary)
    st.bar_chart(campaign_summary, x="campaign_name", y="roi")

# =================================================
# TAB 4: BEST POSTING TIME
# =================================================
with tab4:
    st.subheader("⏰ Optimal Posting Time")
    hourly = filtered_df.groupby("post_hour")["engagement"].mean().reset_index()
    st.line_chart(hourly, x="post_hour", y="engagement")
    best_hour = hourly.loc[hourly["engagement"].idxmax(),"post_hour"]
    st.success(f"🔥 Best Time to Post: **{best_hour}:00 hrs**")

# =================================================
# TAB 5: VIDEO STRATEGY
# =================================================
with tab5:
    st.subheader("🎥 Promotional Video Strategy")
    video_df = filtered_df[filtered_df["content_type"].str.lower().str.contains("video")]
    if video_df.empty:
        st.warning("No video data available.")
    else:
        video_platform = video_df.groupby("platform")["reach"].mean().reset_index().sort_values(by="reach", ascending=False)
        st.bar_chart(video_platform, x="platform", y="reach")
        st.success(f"🚀 Best Platform for Promotional Videos: **{video_platform.iloc[0]['platform']}**")

# =================================================
# TAB 6: SMART PROMOTION DETECTION
# =================================================
with tab6:
    st.subheader("🚀 High-Impact Content Detection")

    high_engagement_cutoff = filtered_df["engagement"].quantile(0.80)
    avg_er = filtered_df["engagement_rate"].mean()

    high_impact_df = filtered_df[
        (filtered_df["engagement"] >= high_engagement_cutoff) &
        (filtered_df["engagement_rate"] >= avg_er) &
        (filtered_df["roi"] > 0)
    ]

    if high_impact_df.empty:
        st.warning("No high-impact content detected.")
    else:
        impact_summary = high_impact_df.groupby(["platform","content_type"]).size().reset_index(name="high_impact_posts")
        st.bar_chart(impact_summary, x="platform", y="high_impact_posts")

        top = impact_summary.iloc[0]
        st.markdown(f"""
<div class="metric-card green">
<h3>🔥 Best Promotion Opportunity</h3>
<h2>{top['content_type']} on {top['platform']}</h2>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
### 🧠 Insight
High engagement + strong engagement rate + positive ROI  
→ This content should be aggressively promoted.
        """)

# =================================================
# FOOTER
# =================================================
st.markdown("""
<hr>
<p style="text-align:center;color:#bbbbbb;">
Project 8 • Social Media Engagement Analytics • Strategy & Detection Dashboard
</p>
""", unsafe_allow_html=True)
