import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="E-commerce User Behavior Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load data from CSV files"""
    try:
        users = pd.read_csv("users.csv", parse_dates=["registration_date"])
        products = pd.read_csv("products.csv")
        events = pd.read_csv("events.csv", parse_dates=["timestamp"])
        return users, products, events
    except FileNotFoundError as e:
        st.error(f"Error loading data: {e}")
        st.info("Please make sure the CSV files (users.csv, products.csv, events.csv) are in the same directory as this dashboard.")
        return None, None, None

# Load data
users, products, events = load_data()

if users is None:
    st.stop()

# Main title
st.markdown('<h1 class="main-header">🛒 E-commerce User Behavior Dashboard</h1>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("📊 Dashboard Filters")

# Date range filter
if not events.empty:
    min_date = events['timestamp'].min().date()
    max_date = events['timestamp'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_events = events[
            (events['timestamp'].dt.date >= start_date) & 
            (events['timestamp'].dt.date <= end_date)
        ]
    else:
        filtered_events = events
else:
    filtered_events = events

# Event type filter
event_types = st.sidebar.multiselect(
    "Event Types",
    options=events["event_type"].unique() if not events.empty else [],
    default=list(events["event_type"].unique()) if not events.empty else []
)

if event_types:
    filtered_events = filtered_events[filtered_events["event_type"].isin(event_types)]

# Category filter
if not products.empty:
    category_options = ["All Categories"] + sorted(products["category"].unique())
    selected_category = st.sidebar.selectbox("Product Category", category_options)
    
    if selected_category != "All Categories":
        filtered_events = filtered_events[filtered_events["category"] == selected_category]

# User segment filter
if not users.empty:
    segment_options = ["All Segments"] + sorted(users["segment"].unique())
    selected_segment = st.sidebar.selectbox("User Segment", segment_options)
    
    if selected_segment != "All Segments":
        segment_users = users[users["segment"] == selected_segment]["user_id"].tolist()
        filtered_events = filtered_events[filtered_events["user_id"].isin(segment_users)]

# Main content
if not filtered_events.empty:
    # Key Metrics
    st.subheader("📈 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Users",
            value=f"{filtered_events['user_id'].nunique():,}",
            delta=f"{filtered_events['user_id'].nunique() - events['user_id'].nunique():,}" if len(filtered_events) != len(events) else None
        )
    
    with col2:
        st.metric(
            label="Total Sessions",
            value=f"{filtered_events['session_id'].nunique():,}",
            delta=f"{filtered_events['session_id'].nunique() - events['session_id'].nunique():,}" if len(filtered_events) != len(events) else None
        )
    
    with col3:
        purchase_events = filtered_events[filtered_events["event_type"] == "purchase"]
        st.metric(
            label="Total Purchases",
            value=f"{len(purchase_events):,}",
            delta=f"{len(purchase_events) - len(events[events['event_type'] == 'purchase']):,}" if len(filtered_events) != len(events) else None
        )
    
    with col4:
        if len(purchase_events) > 0:
            total_revenue = (purchase_events['price'] * purchase_events['quantity']).sum()
            st.metric(
                label="Total Revenue",
                value=f"${total_revenue:,.2f}"
            )
        else:
            st.metric(label="Total Revenue", value="$0.00")

    # Event Type Distribution
    st.subheader("📊 Event Type Distribution")
    event_counts = filtered_events["event_type"].value_counts()
    
    fig_event = px.bar(
        x=event_counts.index,
        y=event_counts.values,
        title="Events by Type",
        labels={'x': 'Event Type', 'y': 'Count'},
        color=event_counts.values,
        color_continuous_scale='viridis'
    )
    fig_event.update_layout(showlegend=False)
    st.plotly_chart(fig_event, use_container_width=True)

    # Category Performance
    if not filtered_events.empty and 'category' in filtered_events.columns:
        st.subheader("🏷️ Category Performance")
        
        # Product views by category
        views_by_category = filtered_events[filtered_events["event_type"] == "product_view"]["category"].value_counts()
        
        fig_category = px.pie(
            values=views_by_category.values,
            names=views_by_category.index,
            title="Product Views by Category"
        )
        st.plotly_chart(fig_category, use_container_width=True)

    # Conversion Funnel
    st.subheader("🔄 Conversion Funnel")
    
    total_sessions = filtered_events[filtered_events["event_type"] == "session_start"]["session_id"].nunique()
    sessions_with_views = filtered_events[filtered_events["event_type"] == "product_view"]["session_id"].nunique()
    sessions_with_cart = filtered_events[filtered_events["event_type"] == "add_to_cart"]["session_id"].nunique()
    sessions_with_purchase = filtered_events[filtered_events["event_type"] == "purchase"]["session_id"].nunique()
    
    funnel_data = pd.DataFrame({
        "Stage": ["Sessions", "Product Views", "Cart Adds", "Purchases"],
        "Count": [total_sessions, sessions_with_views, sessions_with_cart, sessions_with_purchase],
        "Conversion Rate": [
            100,
            (sessions_with_views / total_sessions * 100) if total_sessions > 0 else 0,
            (sessions_with_cart / total_sessions * 100) if total_sessions > 0 else 0,
            (sessions_with_purchase / total_sessions * 100) if total_sessions > 0 else 0
        ]
    })
    
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_data["Stage"],
        x=funnel_data["Count"],
        textinfo="value+percent initial"
    ))
    fig_funnel.update_layout(title="Conversion Funnel")
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Time Series Analysis
    st.subheader("⏰ Time Series Analysis")
    
    # Daily events over time
    daily_events = filtered_events.groupby(filtered_events['timestamp'].dt.date)['event_id'].count().reset_index()
    daily_events.columns = ['date', 'event_count']
    
    fig_time = px.line(
        daily_events,
        x='date',
        y='event_count',
        title="Daily Event Count",
        labels={'date': 'Date', 'event_count': 'Number of Events'}
    )
    st.plotly_chart(fig_time, use_container_width=True)

    # User Segment Analysis
    if not users.empty:
        st.subheader("👥 User Segment Analysis")
        
        # Merge user data with events
        user_events = filtered_events.merge(users[['user_id', 'segment']], on='user_id', how='left')
        segment_activity = user_events.groupby('segment')['event_id'].count().reset_index()
        segment_activity.columns = ['Segment', 'Event Count']
        
        fig_segment = px.bar(
            segment_activity,
            x='Segment',
            y='Event Count',
            title="Activity by User Segment",
            color='Event Count',
            color_continuous_scale='plasma'
        )
        st.plotly_chart(fig_segment, use_container_width=True)

    # Raw Data Preview
    with st.expander("📋 Raw Data Preview (First 1000 rows)"):
        st.dataframe(
            filtered_events.head(1000),
            use_container_width=True
        )

else:
    st.warning("No data available for the selected filters. Please adjust your filter criteria.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>📊 E-commerce User Behavior Dashboard | Made with Streamlit</p>
        <p>Data generated from synthetic e-commerce user behavior patterns</p>
    </div>
    """,
    unsafe_allow_html=True
) 