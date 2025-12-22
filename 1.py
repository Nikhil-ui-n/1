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
# CUSTOM CSS (COLORFUL)
# =================================================
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #141E30, #243B55);
}
.main {
    background: linear-gradient(to right, #141E30, #243B55);
}
h1, h2, h3 {
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
<h1 style='text-align:center;'>🚀 Social Media Analytics Pro Dashboard</h1>
<p style='text-align:center;color:#dcdcdc;font-size:18px;'>
Analytics • ROI • Best Time • Strategy • Detection
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
c5.markdown(f"<div class='metric-card blue'><h3>Avg ROI</h3><h2>{round(filtered_df['roi'].mean(),2)}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# =================================================
# TABS
# =================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📱 Engagement",
        "🖼️ Content",
        "💰 Campaign ROI",
        "⏰ Best Time",
        "🎥 Video Strategy",
        "🚀 Smart Promotion Strategy"
    ]
)

# ---------------- TAB 6: SMART PROMOTION (DETECTION) ----------------
with tab6:
    st.subheader("🚀 High-Impact Content Detection")

    # Detection thresholds
    high_engagement_cutoff = filtered_df["engagement"].quantile(0.80)
    avg_engagement_rate = filtered_df["engagement_rate"].mean()

    high_impact_df = filtered_df[
        (filtered_df["engagement"] >= high_engagement_cutoff) &
        (filtered_df["engagement_rate"] >= avg_engagement_rate) &
        (filtered_df["roi"] > 0)
    ]

    if high_impact_df.empty:
        st.warning("No high-impact content detected for selected filters.")
    else:
        impact_summary = (
            high_impact_df
            .groupby(["platform", "content_type"])
            .size()
            .reset_index(name="high_impact_posts")
            .sort_values(by="high_impact_posts", ascending=False)
        )

        st.bar_chart(impact_summary, x="platform", y="high_impact_posts")

        top_row = impact_summary.iloc[0]

        st.markdown(f"""
<div class="metric-card green">
<h3>🔥 Best Promotion Opportunity</h3>
<h2>{top_row['content_type']} on {top_row['platform']}</h2>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
### 🧠 Strategy Insight
- Detected posts with **exceptionally high engagement**
- These posts also show **strong engagement rate and positive ROI**
- Promoting similar content increases growth probability
        """)

        st.markdown("""
### ✅ Action Plan
- Increase promotional budget for detected content type
- Replicate creative format and posting style
- Schedule during optimal posting time
- Track ROI closely for scaling
        """)

# =================================================
# FOOTER
# =================================================
st.markdown("""
<hr>
<p style='text-align:center;color:#bbbbbb;'>
Project 8 • Social Media Engagement Analytics • Strategy & Detection Engine
</p>
""", unsafe_allow_html=True)
