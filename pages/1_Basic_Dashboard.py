import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Basic Dashboard",
    page_icon="📊",
    layout="wide"
)

# Import data generator from main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Home import generate_sample_data

@st.cache_data
def load_data():
    """Generate sample data for the dashboard"""
    try:
        users, products, events = generate_sample_data(num_users=1000, num_days=180)
        return users, products, events
    except Exception as e:
        st.error(f"Error generating data: {e}")
        return None, None, None

# Load data
with st.spinner("Loading data..."):
    users, products, events = load_data()

if users is None:
    st.stop()

# Main title
st.markdown('<h1 class="main-header">🛒 Basic E-commerce Dashboard</h1>', unsafe_allow_html=True)

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

# Main content
if not filtered_events.empty:
    # Key Metrics
    st.subheader("📈 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", f"{filtered_events['user_id'].nunique():,}")
    
    with col2:
        st.metric("Total Sessions", f"{filtered_events['session_id'].nunique():,}")
    
    with col3:
        purchase_events = filtered_events[filtered_events["event_type"] == "purchase"]
        st.metric("Total Purchases", f"{len(purchase_events):,}")
    
    with col4:
        if len(purchase_events) > 0:
            total_revenue = (purchase_events['price'] * purchase_events['quantity']).sum()
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        else:
            st.metric("Total Revenue", "$0.00")

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
        <p>📊 Basic E-commerce Dashboard | Made with Streamlit</p>
        <p>Data generated from synthetic e-commerce user behavior patterns</p>
    </div>
    """,
    unsafe_allow_html=True
) 