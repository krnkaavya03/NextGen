import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# =========================
# Load Dataset
# =========================
df = pd.read_csv("user_data.csv")
df['date'] = pd.to_datetime(df['date'])
df = df[df['domain'].str.lower() != "medium"]  # Remove 'medium' domain

# =========================
# Page Configuration
# =========================
st.set_page_config(page_title="NextGen Dashboard", layout="wide", page_icon="🚀")

# =========================
# Dark Theme Styling
# =========================
st.markdown("""
<style>
body {background-color:#111; color:white; font-family: 'Arial';}
h1, h2, h3, h4, h5, h6 {color:white;}
.stButton>button, .stDownloadButton>button {border-radius:12px; height:3em;}
.stDownloadButton>button {background-color:#ff7f0e; color:white;}
.stButton>button {background-color:#1f77b4; color:white;}
div.stButton > button:hover, div.stDownloadButton > button:hover {opacity:0.85;}
</style>
""", unsafe_allow_html=True)

# =========================
# Dashboard Header
# =========================
st.title("📊 NextGen - User Engagement Dashboard")
st.markdown("**Interactive insights into user behavior across multiple domains.**")

# =========================
# Sidebar Filters
# =========================
st.sidebar.header("🔎 Filters")

with st.sidebar.expander("Domain Filters", expanded=True):
    all_domains = df['domain'].unique().tolist()
    select_all_domains = st.checkbox("Select All Domains", value=True, key="domains_all")
    domain_filter = st.multiselect(
        "Select Domain(s)",
        options=all_domains,
        default=all_domains if select_all_domains else []
    )

with st.sidebar.expander("User Type Filters", expanded=True):
    all_user_types = df['user_type'].unique().tolist()
    select_all_users = st.checkbox("Select All User Types", value=True, key="users_all")
    user_type_filter = st.multiselect(
        "Select User Type(s)",
        options=all_user_types,
        default=all_user_types if select_all_users else []
    )

with st.sidebar.expander("Date & Session Filters", expanded=True):
    date_range = st.date_input("Select Date Range", [df['date'].min(), df['date'].max()])
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

    session_range = st.slider(
        "Session Duration (min)",
        int(df['session_duration'].min()),
        int(df['session_duration'].max()),
        (int(df['session_duration'].min()), int(df['session_duration'].max()))
    )

# =========================
# Filter Data
# =========================
filtered_df = df[
    (df['domain'].isin(domain_filter)) &
    (df['user_type'].isin(user_type_filter)) &
    (df['date'] >= start_date) & (df['date'] <= end_date) &
    (df['session_duration'] >= session_range[0]) & (df['session_duration'] <= session_range[1])
]

# =========================
# KPIs with Cards
# =========================
total_engagement = filtered_df['engagement_score'].sum()
avg_engagement = round(filtered_df['engagement_score'].mean(), 2) if not filtered_df.empty else 0
most_active_domain = filtered_df.groupby('domain')['engagement_score'].sum().idxmax() if not filtered_df.empty else "N/A"
max_session = filtered_df['session_duration'].max() if not filtered_df.empty else 0

prev_start = start_date - timedelta(days=7)
prev_end = start_date - timedelta(days=1)
prev_df = df[(df['date'] >= prev_start) & (df['date'] <= prev_end)]
delta_total = total_engagement - prev_df['engagement_score'].sum() if not prev_df.empty else 0

st.markdown("### ⚡ Key Metrics")
kpi_cols = st.columns(4)
kpi_cols[0].metric("Total Engagement", total_engagement, delta=f"{delta_total:+}", delta_color="inverse")
kpi_cols[1].metric("Average Engagement", avg_engagement)
kpi_cols[2].metric("Most Active Domain", most_active_domain)
kpi_cols[3].metric("Max Session Duration (min)", max_session)

st.markdown("---")

# =========================
# Tabs for Charts
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trend Analysis", "🏆 Domain Insights", "👥 User Type Analysis",
    "📊 Additional Insights", "📥 Summary & Download"
])

# -------------------------
# Tab 1: Engagement Trend
# -------------------------
with tab1:
    st.subheader("Engagement Trend Over Time")
    if not filtered_df.empty:
        trend_fig = px.line(
            filtered_df, x='date', y='engagement_score', color='domain', markers=True,
            template='plotly_dark', title='Engagement Trend by Domain'
        )
        trend_fig.update_layout(xaxis_title='Date', yaxis_title='Engagement Score', legend_title='Domain',
                                hovermode='x unified')
        trend_fig.update_xaxes(rangeslider_visible=True)
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# -------------------------
# Tab 2: Domain Insights
# -------------------------
with tab2:
    st.subheader("Top Domains by Engagement")
    if not filtered_df.empty:
        domain_engagement = filtered_df.groupby('domain')['engagement_score'].sum().reset_index().sort_values(by='engagement_score', ascending=False)
        bar_fig = px.bar(domain_engagement, x='domain', y='engagement_score', color='domain',
                         text='engagement_score', template='plotly_dark', title='Total Engagement per Domain')
        st.plotly_chart(bar_fig, use_container_width=True)
        pie_fig = px.pie(domain_engagement, values='engagement_score', names='domain',
                         template='plotly_dark', color_discrete_sequence=px.colors.sequential.Plasma,
                         title='Engagement Distribution by Domain')
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# -------------------------
# Tab 3: User Type Analysis
# -------------------------
with tab3:
    st.subheader("User Type vs Domain Heatmap")
    if not filtered_df.empty:
        heatmap_data = filtered_df.pivot_table(values='engagement_score', index='user_type', columns='domain', aggfunc='mean').fillna(0)
        heatmap_fig = go.Figure(data=go.Heatmap(z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index,
                                                colorscale='Viridis', hoverongaps=False))
        heatmap_fig.update_layout(template='plotly_dark', xaxis_title='Domain', yaxis_title='User Type',
                                  title='Average Engagement by User Type and Domain')
        st.plotly_chart(heatmap_fig, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# -------------------------
# Tab 4: Additional Insights
# -------------------------
with tab4:
    st.subheader("Session Duration Distribution")
    if not filtered_df.empty:
        hist_fig = px.histogram(filtered_df, x='session_duration', nbins=20, template='plotly_dark',
                                title="Session Duration (minutes)")
        st.plotly_chart(hist_fig, use_container_width=True)

        st.subheader("Clicks vs Completed Lessons Scatter")
        scatter_fig = px.scatter(filtered_df, x='clicks', y='completed_lessons', color='domain', size='engagement_score',
                                 hover_data=['user_id','user_type'], template='plotly_dark',
                                 title="Clicks vs Completed Lessons by Domain")
        st.plotly_chart(scatter_fig, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# -------------------------
# Tab 5: Summary & Download
# -------------------------
with tab5:
    st.subheader("📥 Download Filtered Data & Summary")
    if not filtered_df.empty:
        st.dataframe(filtered_df.head(20))  # show top 20 rows as preview
        st.download_button("📥 Download Filtered Data CSV", filtered_df.to_csv(index=False), "filtered_user_data.csv")
        summary_df = filtered_df.groupby(['domain','user_type']).agg({
            'engagement_score':'sum', 'session_duration':'mean', 'clicks':'sum', 'completed_lessons':'sum'
        }).reset_index()
        st.markdown("**Summary Statistics by Domain & User Type**")
        st.dataframe(summary_df)
    else:
        st.info("No data available for selected filters.")
