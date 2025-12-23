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
# ADVANCED CSS + ANIMATIONS
# =================================================
st.markdown("""
<style>
.main {
    background: linear-gradient(to right, #141E30, #243B55);
}

.gradient-text {
    background: linear-gradient(90deg,#00c6ff,#0072ff,#7f00ff,#e100ff);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientMove 6s infinite linear;
}

@keyframes gradientMove {
    0% { background-position: 0%; }
    100% { background-position: 300%; }
}

.metric-card {
    padding: 20px;
    border-radius: 18px;
    color: white;
    text-align: center;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-8px) scale(1.03);
}

.blue { background: linear-gradient(135deg,#396afc,#2948ff); }
.green { background: linear-gradient(135deg,#11998e,#38ef7d); }
.orange { background: linear-gradient(135deg,#f7971e,#ffd200); }
.red { background: linear-gradient(135deg,#ff416c,#ff4b2b); }
.purple { background: linear-gradient(135deg,#667eea,#764ba2); }

.progress-bar {
    height: 12px;
    width: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg,#38ef7d,#11998e);
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
    return df

df = load_data()

# =================================================
# DERIVED METRICS
# =================================================
df["revenue_generated"] = df["ad_spend"] * (1 + df["roi"])

# =================================================
# SIDEBAR FILTERS
# =================================================
st.sidebar.markdown("## 🎛️ Dashboard Controls")

platform_filter = st.sidebar.multiselect(
    "📱 Platform", df["platform"].unique(), df["platform"].unique()
)

content_filter = st.sidebar.multiselect(
    "🖼️ Content Type", df["content_type"].unique(), df["content_type"].unique()
)

year_filter = st.sidebar.multiselect(
    "📅 Year", df["year"].unique(), df["year"].unique()
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
<h1 class="gradient-text" style="text-align:center;">
🚀 Social Media Analytics Pro Dashboard
</h1>
<p style="text-align:center;color:#dcdcdc;font-size:18px;">
Engagement • Content • Campaign ROI • Revenue • Best Posting Time
</p>
""", unsafe_allow_html=True)

# =================================================
# FILTER SUMMARY
# =================================================
st.info(
    f"""
    🔎 **Current Selection**
    • Platform: {', '.join(platform_filter)}
    • Content Type: {', '.join(content_filter)}
    • Year: {', '.join(map(str, year_filter))}
    """
)

# =================================================
# KPI CARDS
# =================================================
c1, c2, c3, c4, c5 = st.columns(5)

c1.markdown(f"""
<div class="metric-card blue">
<h3>Total Engagement</h3>
<h2>{int(filtered_df["engagement"].sum())}</h2>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="metric-card green">
<h3>Avg Engagement Rate</h3>
<h2>{round(filtered_df["engagement_rate"].mean(),2)}%</h2>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="metric-card orange">
<h3>Ad Spend</h3>
<h2>₹ {int(filtered_df["ad_spend"].sum())}</h2>
</div>
""", unsafe_allow_html=True)

c4.markdown(f"""
<div class="metric-card red">
<h3>Revenue Generated</h3>
<h2>₹ {int(filtered_df["revenue_generated"].sum())}</h2>
</div>
""", unsafe_allow_html=True)

c5.markdown(f"""
<div class="metric-card purple">
<h3>Avg ROI</h3>
<h2>{round(filtered_df["roi"].mean(),2)}</h2>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="progress-bar"></div>', unsafe_allow_html=True)

# =================================================
# TOP CONTENT INSIGHT
# =================================================
top_content = (
    filtered_df.groupby("content_type")["engagement_rate"]
    .mean()
    .idxmax()
)

st.success(f"🔥 Best Performing Content Type: **{top_content}**")

# =================================================
# TABS (ONE EXTRA TAB ADDED)
# =================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📱 Engagement", "🖼️ Content", "💰 Campaign ROI", "⏰ Best Time", "📈 Trends"]
)

# ---------------- TAB 1 ----------------
with tab1:
    platform_eng = filtered_df.groupby("platform")["engagement_rate"].mean().reset_index()
    st.bar_chart(platform_eng, x="platform", y="engagement_rate")

    best_platform = platform_eng.loc[
        platform_eng["engagement_rate"].idxmax(), "platform"
    ]
    st.info(f"📈 Highest engagement is observed on **{best_platform}**")

# ---------------- TAB 2 ----------------
with tab2:
    content_perf = filtered_df.groupby("content_type")[["likes","comments","shares","engagement"]].mean().reset_index()
    st.dataframe(content_perf)
    st.bar_chart(content_perf, x="content_type", y="engagement")

# ---------------- TAB 3 ----------------
with tab3:
    campaign_df = filtered_df[filtered_df["campaign_name"].notna()]
    campaign_summary = campaign_df.groupby("campaign_name")[["ad_spend","revenue_generated","roi"]].mean().reset_index()
    st.dataframe(campaign_summary)
    st.bar_chart(campaign_summary, x="campaign_name", y="revenue_generated")
    st.bar_chart(campaign_summary, x="campaign_name", y="roi")

# ---------------- TAB 4 ----------------
with tab4:
    hourly = filtered_df.groupby("post_hour")["engagement"].mean().reset_index()
    st.line_chart(hourly, x="post_hour", y="engagement")

    best_hour = hourly.loc[hourly["engagement"].idxmax(), "post_hour"]
    st.success(f"🔥 Best Posting Time: **{best_hour}:00 hrs**")

    st.warning(
        f"""
        📌 **System Recommendation**
        - Post **{top_content}** content
        - Around **{best_hour}:00 hrs**
        - Focus on **{best_platform}**
        """
    )

# ---------------- TAB 5 : TRENDS ----------------
with tab5:
    st.markdown("### 📈 Engagement Trend Over Time")

    trend_df = (
        filtered_df.groupby(["year", "month"])["engagement"]
        .mean()
        .reset_index()
        .sort_values(["year", "month"])
    )

    st.line_chart(trend_df, x="month", y="engagement")

    best_month = trend_df.loc[
        trend_df["engagement"].idxmax(), "month"
    ]

    st.info(f"📊 Highest average engagement observed in **Month {best_month}**")

# =================================================
# DOWNLOAD
# =================================================
st.download_button(
    "⬇️ Download Filtered Data",
    filtered_df.to_csv(index=False),
    "filtered_social_media_data.csv",
    "text/csv"
)

# =================================================
# FOOTER
# =================================================
st.markdown("""
<hr>
<p style="text-align:center;color:#bbbbbb;">
Project 8 • Social Media Engagement Analytics • Built with ❤️ & Streamlit
</p>
""", unsafe_allow_html=True)
