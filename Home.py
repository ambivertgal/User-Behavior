import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-highlight {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff7f0e;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_summary_data():
    """Load summary data for the home page"""
    try:
        users = pd.read_csv("users.csv", parse_dates=["registration_date"])
        products = pd.read_csv("products.csv")
        events = pd.read_csv("events.csv", parse_dates=["timestamp"])
        return users, products, events
    except FileNotFoundError:
        return None, None, None

# Load data
users, products, events = load_summary_data()

# Main title
st.markdown('<h1 class="main-header">🛒 E-commerce Analytics Dashboard</h1>', unsafe_allow_html=True)

# Welcome message
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p style='font-size: 1.2rem; color: #666;'>
        Welcome to your comprehensive e-commerce analytics platform. 
        Explore user behavior patterns, customer segmentation, and business insights.
    </p>
</div>
""", unsafe_allow_html=True)

# Quick stats if data is available
if users is not None and products is not None and events is not None:
    st.subheader("📊 Quick Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", f"{users['user_id'].nunique():,}")
    
    with col2:
        st.metric("Total Products", f"{len(products):,}")
    
    with col3:
        st.metric("Total Events", f"{len(events):,}")
    
    with col4:
        purchase_events = events[events['event_type'] == 'purchase']
        total_revenue = (purchase_events['price'] * purchase_events['quantity']).sum() if len(purchase_events) > 0 else 0
        st.metric("Total Revenue", f"${total_revenue:,.2f}")

# Dashboard Features
st.subheader("🚀 Dashboard Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Basic Analytics</h3>
        <ul>
        <li>Interactive filters and drill-downs</li>
        <li>Event type distribution analysis</li>
        <li>Category performance insights</li>
        <li>Conversion funnel visualization</li>
        <li>Time series analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 Advanced Analytics</h3>
        <ul>
        <li>RFM customer segmentation</li>
        <li>Behavioral clustering with K-means</li>
        <li>Detailed conversion analysis</li>
        <li>Business intelligence insights</li>
        <li>Strategic recommendations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Data Overview
st.subheader("📈 Data Overview")

if users is not None and products is not None and events is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-highlight">
            <h4>📊 Dataset Statistics</h4>
            <ul>
            <li><strong>Users:</strong> {:,} registered customers</li>
            <li><strong>Products:</strong> {:,} items across {:,} categories</li>
            <li><strong>Events:</strong> {:,} user interactions</li>
            <li><strong>Time Span:</strong> {} to {}</li>
            </ul>
        </div>
        """.format(
            users['user_id'].nunique(),
            len(products),
            products['category'].nunique(),
            len(events),
            events['timestamp'].min().strftime('%Y-%m-%d'),
            events['timestamp'].max().strftime('%Y-%m-%d')
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-highlight">
            <h4>🎯 Key Insights</h4>
            <ul>
            <li><strong>Conversion Rate:</strong> {:.1f}% of sessions result in purchase</li>
            <li><strong>Avg Order Value:</strong> ${:.2f}</li>
            <li><strong>Top Category:</strong> {}</li>
            <li><strong>Active Users:</strong> {:,} in selected period</li>
            </ul>
        </div>
        """.format(
            len(events[events['event_type'] == 'purchase']) / len(events[events['event_type'] == 'session_start']) * 100 if len(events[events['event_type'] == 'session_start']) > 0 else 0,
            (events[events['event_type'] == 'purchase']['price'] * events[events['event_type'] == 'purchase']['quantity']).sum() / len(events[events['event_type'] == 'purchase']) if len(events[events['event_type'] == 'purchase']) > 0 else 0,
            products['category'].value_counts().index[0] if len(products) > 0 else "N/A",
            events['user_id'].nunique()
        ), unsafe_allow_html=True)

# Navigation Guide
st.subheader("🧭 Navigation Guide")

st.markdown("""
<div class="feature-card">
    <h4>📱 How to Use This Dashboard</h4>
    <ol>
    <li><strong>Basic Dashboard:</strong> Start with fundamental analytics including event distribution, category performance, and conversion funnels</li>
    <li><strong>Advanced Analytics:</strong> Explore sophisticated analysis including:
        <ul>
        <li><strong>RFM Segmentation:</strong> Customer value analysis and strategic recommendations</li>
        <li><strong>Behavioral Clustering:</strong> K-means clustering for user behavior patterns</li>
        <li><strong>Conversion Analysis:</strong> Detailed funnel metrics and optimization insights</li>
        <li><strong>Business Intelligence:</strong> Executive summary and strategic recommendations</li>
        </ul>
    </li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Technical Information
st.subheader("⚙️ Technical Information")

st.markdown("""
<div class="feature-card">
    <h4>🛠️ Built With</h4>
    <ul>
    <li><strong>Streamlit:</strong> Web application framework</li>
    <li><strong>Pandas:</strong> Data manipulation and analysis</li>
    <li><strong>Plotly:</strong> Interactive visualizations</li>
    <li><strong>Scikit-learn:</strong> Machine learning (K-means clustering)</li>
    <li><strong>NumPy:</strong> Numerical computing</li>
    </ul>
    
    <h4>📊 Data Sources</h4>
    <ul>
    <li><strong>users.csv:</strong> Customer information and segments</li>
    <li><strong>products.csv:</strong> Product catalog and categories</li>
    <li><strong>events.csv:</strong> User interaction events and sessions</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🛒 E-commerce Analytics Dashboard | Week 1 & 2 Features</p>
        <p>Basic Analytics • RFM Segmentation • Behavioral Clustering • Business Intelligence</p>
        <p>Data generated from synthetic e-commerce user behavior patterns</p>
    </div>
    """,
    unsafe_allow_html=True
) 