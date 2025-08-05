import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
import random
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Advanced Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS - Dark mode compatible
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: rgba(240, 242, 246, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .insight-box {
        background-color: rgba(232, 244, 253, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff7f0e;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .metric-card h3, .metric-card h4, .metric-card p, .metric-card li {
        color: inherit;
    }
    .insight-box h4, .insight-box p, .insight-box li {
        color: inherit;
    }
    .metric-card ul, .insight-box ul {
        color: inherit;
    }
</style>
""", unsafe_allow_html=True)

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

def calculate_rfm_scores(users, events):
    """Calculate RFM scores for customer segmentation"""
    # Get purchase events
    purchases = events[events['event_type'] == 'purchase'].copy()
    
    if purchases.empty:
        return pd.DataFrame()
    
    # Calculate RFM metrics
    rfm = purchases.groupby('user_id').agg({
        'timestamp': lambda x: (datetime.now() - x.max()).days,  # Recency
        'event_id': 'count',  # Frequency
        'price': lambda x: (x * purchases.loc[x.index, 'quantity']).sum()  # Monetary
    }).reset_index()
    
    rfm.columns = ['user_id', 'recency', 'frequency', 'monetary']
    
    # Calculate RFM scores (1-5 scale, 5 being best)
    rfm['R_score'] = pd.qcut(rfm['recency'], q=5, labels=[5,4,3,2,1])
    rfm['F_score'] = pd.qcut(rfm['frequency'], q=5, labels=[1,2,3,4,5])
    rfm['M_score'] = pd.qcut(rfm['monetary'], q=5, labels=[1,2,3,4,5])
    
    # Convert to numeric
    rfm['R_score'] = rfm['R_score'].astype(int)
    rfm['F_score'] = rfm['F_score'].astype(int)
    rfm['M_score'] = rfm['M_score'].astype(int)
    
    # Calculate RFM score
    rfm['RFM_score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']
    
    # Segment customers
    def segment_customers(row):
        if row['RFM_score'] >= 13:
            return 'Champions'
        elif row['RFM_score'] >= 10:
            return 'Loyal Customers'
        elif row['RFM_score'] >= 8:
            return 'At Risk'
        elif row['RFM_score'] >= 6:
            return 'Can\'t Lose'
        else:
            return 'Lost'
    
    rfm['segment'] = rfm.apply(segment_customers, axis=1)
    
    return rfm

def perform_behavioral_clustering(events, users):
    """Perform K-means clustering on behavioral features"""
    # Create behavioral features
    user_behavior = events.groupby('user_id').agg({
        'session_id': 'nunique',  # Number of sessions
        'event_id': 'count',  # Total events
        'product_id': 'nunique',  # Unique products viewed
        'category': 'nunique'  # Unique categories viewed
    }).reset_index()
    
    # Add purchase behavior
    purchases = events[events['event_type'] == 'purchase']
    if not purchases.empty:
        purchase_behavior = purchases.groupby('user_id').agg({
            'event_id': 'count',  # Number of purchases
            'price': lambda x: (x * purchases.loc[x.index, 'quantity']).sum()  # Total spent
        }).reset_index()
        purchase_behavior.columns = ['user_id', 'purchase_count', 'total_spent']
        user_behavior = user_behavior.merge(purchase_behavior, on='user_id', how='left')
    else:
        user_behavior['purchase_count'] = 0
        user_behavior['total_spent'] = 0
    
    # Fill NaN values
    user_behavior = user_behavior.fillna(0)
    
    # Prepare features for clustering
    features = ['session_id', 'event_id', 'product_id', 'category', 'purchase_count', 'total_spent']
    X = user_behavior[features].values
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    user_behavior['behavioral_cluster'] = kmeans.fit_predict(X_scaled)
    
    # Name clusters based on behavior patterns
    cluster_names = {
        0: 'Casual Browsers',
        1: 'Active Shoppers', 
        2: 'High-Value Customers',
        3: 'Occasional Buyers'
    }
    user_behavior['behavioral_segment'] = user_behavior['behavioral_cluster'].map(cluster_names)
    
    return user_behavior

def calculate_conversion_metrics(events):
    """Calculate detailed conversion metrics"""
    # Session-level conversion funnel
    sessions = events[events['event_type'] == 'session_start']['session_id'].unique()
    
    conversion_data = []
    for session in sessions:
        session_events = events[events['session_id'] == session]
        
        has_view = 'product_view' in session_events['event_type'].values
        has_cart = 'add_to_cart' in session_events['event_type'].values
        has_purchase = 'purchase' in session_events['event_type'].values
        
        conversion_data.append({
            'session_id': session,
            'has_view': has_view,
            'has_cart': has_cart,
            'has_purchase': has_purchase
        })
    
    conversion_df = pd.DataFrame(conversion_data)
    
    # Calculate conversion rates
    total_sessions = len(conversion_df)
    view_rate = conversion_df['has_view'].sum() / total_sessions * 100
    cart_rate = conversion_df['has_cart'].sum() / total_sessions * 100
    purchase_rate = conversion_df['has_purchase'].sum() / total_sessions * 100
    
    return {
        'total_sessions': total_sessions,
        'view_rate': view_rate,
        'cart_rate': cart_rate,
        'purchase_rate': purchase_rate,
        'conversion_df': conversion_df
    }

# Load data
users, products, events = load_data()

if users is None:
    st.stop()

# Main title
st.markdown('<h1 class="main-header">📊 Advanced E-commerce Analytics</h1>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("🔧 Dashboard Controls")

# Analysis type selector
analysis_type = st.sidebar.selectbox(
    "📈 Analysis Type",
    ["RFM Segmentation", "Behavioral Clustering", "Conversion Analysis", "Business Insights"]
)

# Date range filter
if not events.empty:
    min_date = events['timestamp'].min().date()
    max_date = events['timestamp'].max().date()
    
    date_range = st.sidebar.date_input(
        "📅 Date Range",
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

# Main content based on analysis type
if analysis_type == "RFM Segmentation":
    st.header("🎯 RFM Customer Segmentation")
    
    # Calculate RFM scores
    rfm_data = calculate_rfm_scores(users, filtered_events)
    
    if not rfm_data.empty:
        # RFM Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 RFM Score Distribution")
            fig_rfm = px.histogram(rfm_data, x='RFM_score', nbins=20, title="RFM Score Distribution")
            st.plotly_chart(fig_rfm, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Customer Segments")
            segment_counts = rfm_data['segment'].value_counts()
            fig_segment = px.pie(values=segment_counts.values, names=segment_counts.index, title="Customer Segments")
            st.plotly_chart(fig_segment, use_container_width=True)
        
        # RFM Metrics by Segment
        st.subheader("📈 RFM Metrics by Segment")
        segment_metrics = rfm_data.groupby('segment').agg({
            'recency': 'mean',
            'frequency': 'mean', 
            'monetary': 'mean',
            'user_id': 'count'
        }).round(2)
        segment_metrics.columns = ['Avg Recency (days)', 'Avg Frequency', 'Avg Monetary ($)', 'Customer Count']
        st.dataframe(segment_metrics, use_container_width=True)
        
        # Business Insights
        st.subheader("💡 Business Insights")
        
        champions = rfm_data[rfm_data['segment'] == 'Champions']
        at_risk = rfm_data[rfm_data['segment'] == 'At Risk']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Champions", f"{len(champions):,}", f"{len(champions)/len(rfm_data)*100:.1f}%")
        with col2:
            st.metric("At Risk", f"{len(at_risk):,}", f"{len(at_risk)/len(rfm_data)*100:.1f}%")
        with col3:
            avg_rfm = rfm_data['RFM_score'].mean()
            st.metric("Avg RFM Score", f"{avg_rfm:.1f}")
        
        # Recommendations
        st.markdown("""
        <div class="insight-box">
        <h4>🎯 Strategic Recommendations:</h4>
        <ul>
        <li><strong>Champions:</strong> VIP treatment, early access to new products</li>
        <li><strong>Loyal Customers:</strong> Loyalty programs, personalized recommendations</li>
        <li><strong>At Risk:</strong> Re-engagement campaigns, special offers</li>
        <li><strong>Can't Lose:</strong> Win-back campaigns, customer service outreach</li>
        <li><strong>Lost:</strong> Reactivation campaigns, new product introductions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.warning("No purchase data available for RFM analysis.")

elif analysis_type == "Behavioral Clustering":
    st.header("🧠 Behavioral Clustering Analysis")
    
    # Perform behavioral clustering
    behavioral_data = perform_behavioral_clustering(filtered_events, users)
    
    if not behavioral_data.empty:
        # Cluster distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Behavioral Segments")
            cluster_counts = behavioral_data['behavioral_segment'].value_counts()
            fig_cluster = px.pie(values=cluster_counts.values, names=cluster_counts.index, title="Behavioral Segments")
            st.plotly_chart(fig_cluster, use_container_width=True)
        
        with col2:
            st.subheader("📊 Segment Characteristics")
            segment_stats = behavioral_data.groupby('behavioral_segment').agg({
                'session_id': 'mean',
                'event_id': 'mean',
                'product_id': 'mean',
                'purchase_count': 'mean',
                'total_spent': 'mean'
            }).round(2)
            segment_stats.columns = ['Avg Sessions', 'Avg Events', 'Avg Products', 'Avg Purchases', 'Avg Spent ($)']
            st.dataframe(segment_stats, use_container_width=True)
        
        # Behavioral patterns visualization
        st.subheader("📈 Behavioral Patterns")
        
        # Create radar chart for segment comparison
        fig_radar = go.Figure()
        
        for segment in behavioral_data['behavioral_segment'].unique():
            segment_data = behavioral_data[behavioral_data['behavioral_segment'] == segment]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=[segment_data['session_id'].mean(), 
                   segment_data['event_id'].mean(),
                   segment_data['product_id'].mean(),
                   segment_data['purchase_count'].mean(),
                   segment_data['total_spent'].mean()],
                theta=['Sessions', 'Events', 'Products', 'Purchases', 'Spending'],
                fill='toself',
                name=segment
            ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, behavioral_data[['session_id', 'event_id', 'product_id', 'purchase_count', 'total_spent']].max().max()])),
            showlegend=True,
            title="Behavioral Patterns by Segment"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Business insights
        st.subheader("💡 Behavioral Insights")
        
        high_value = behavioral_data[behavioral_data['behavioral_segment'] == 'High-Value Customers']
        casual = behavioral_data[behavioral_data['behavioral_segment'] == 'Casual Browsers']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High-Value Customers", f"{len(high_value):,}", f"{len(high_value)/len(behavioral_data)*100:.1f}%")
        with col2:
            st.metric("Casual Browsers", f"{len(casual):,}", f"{len(casual)/len(behavioral_data)*100:.1f}%")
        with col3:
            avg_spent = behavioral_data['total_spent'].mean()
            st.metric("Avg Customer Value", f"${avg_spent:.2f}")

elif analysis_type == "Conversion Analysis":
    st.header("🔄 Conversion Funnel Analysis")
    
    # Calculate conversion metrics
    conversion_metrics = calculate_conversion_metrics(filtered_events)
    
    # Conversion funnel
    st.subheader("📊 Conversion Funnel")
    
    funnel_data = pd.DataFrame({
        "Stage": ["Sessions", "Product Views", "Cart Adds", "Purchases"],
        "Count": [
            conversion_metrics['total_sessions'],
            int(conversion_metrics['total_sessions'] * conversion_metrics['view_rate'] / 100),
            int(conversion_metrics['total_sessions'] * conversion_metrics['cart_rate'] / 100),
            int(conversion_metrics['total_sessions'] * conversion_metrics['purchase_rate'] / 100)
        ],
        "Rate": [100, conversion_metrics['view_rate'], conversion_metrics['cart_rate'], conversion_metrics['purchase_rate']]
    })
    
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_data["Stage"],
        x=funnel_data["Count"],
        textinfo="value+percent initial"
    ))
    fig_funnel.update_layout(title="Conversion Funnel")
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Conversion rates
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("View Rate", f"{conversion_metrics['view_rate']:.1f}%")
    with col2:
        st.metric("Cart Rate", f"{conversion_metrics['cart_rate']:.1f}%")
    with col3:
        st.metric("Purchase Rate", f"{conversion_metrics['purchase_rate']:.1f}%")
    
    # Conversion insights
    st.subheader("💡 Conversion Insights")
    
    if conversion_metrics['purchase_rate'] < 5:
        insight = "⚠️ Low conversion rate detected. Consider optimizing checkout process and reducing friction."
    elif conversion_metrics['purchase_rate'] < 15:
        insight = "📈 Moderate conversion rate. Focus on cart abandonment and checkout optimization."
    else:
        insight = "🎉 Excellent conversion rate! Focus on customer retention and upselling."
    
    st.markdown(f"""
    <div class="insight-box">
    <h4>🔍 Analysis:</h4>
    <p>{insight}</p>
    <ul>
    <li><strong>View to Cart:</strong> {conversion_metrics['cart_rate']/conversion_metrics['view_rate']*100:.1f}% of viewers add to cart</li>
    <li><strong>Cart to Purchase:</strong> {conversion_metrics['purchase_rate']/conversion_metrics['cart_rate']*100:.1f}% of cart additions result in purchase</li>
    <li><strong>Overall Conversion:</strong> {conversion_metrics['purchase_rate']:.1f}% of sessions result in purchase</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

elif analysis_type == "Business Insights":
    st.header("💼 Business Intelligence Dashboard")
    
    # Executive Summary
    st.subheader("📋 Executive Summary")
    
    total_users = filtered_events['user_id'].nunique()
    total_sessions = filtered_events['session_id'].nunique()
    purchase_events = filtered_events[filtered_events["event_type"] == "purchase"]
    total_revenue = (purchase_events['price'] * purchase_events['quantity']).sum() if len(purchase_events) > 0 else 0
    avg_order_value = total_revenue / len(purchase_events) if len(purchase_events) > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Users", f"{total_users:,}")
    with col2:
        st.metric("Total Sessions", f"{total_sessions:,}")
    with col3:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col4:
        st.metric("Avg Order Value", f"${avg_order_value:.2f}")
    
    # Category Performance
    st.subheader("🏷️ Category Performance")
    
    if not filtered_events.empty and 'category' in filtered_events.columns:
        category_performance = filtered_events.groupby('category').agg({
            'event_id': 'count',
            'price': lambda x: (x * filtered_events.loc[x.index, 'quantity']).sum() if 'quantity' in filtered_events.columns else 0
        }).reset_index()
        category_performance.columns = ['Category', 'Events', 'Revenue']
        
        fig_category = px.bar(
            category_performance, 
            x='Category', 
            y='Revenue',
            title="Revenue by Category",
            color='Revenue',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    # Time-based Analysis
    st.subheader("⏰ Time-based Trends")
    
    # Daily trends
    daily_metrics = filtered_events.groupby(filtered_events['timestamp'].dt.date).agg({
        'user_id': 'nunique',
        'session_id': 'nunique',
        'event_id': 'count'
    }).reset_index()
    daily_metrics.columns = ['Date', 'Unique Users', 'Sessions', 'Events']
    
    fig_trends = px.line(
        daily_metrics,
        x='Date',
        y=['Unique Users', 'Sessions'],
        title="Daily User Activity Trends"
    )
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Business Recommendations
    st.subheader("🎯 Strategic Recommendations")
    
    # Calculate key metrics for recommendations
    conversion_metrics = calculate_conversion_metrics(filtered_events)
    rfm_data = calculate_rfm_scores(users, filtered_events)
    
    recommendations = []
    
    if conversion_metrics['purchase_rate'] < 10:
        recommendations.append("🔴 **Low Conversion Rate:** Implement A/B testing for checkout process")
    
    if not rfm_data.empty and len(rfm_data[rfm_data['segment'] == 'At Risk']) > len(rfm_data) * 0.3:
        recommendations.append("🟡 **High At-Risk Customers:** Launch retention campaigns")
    
    if avg_order_value < 50:
        recommendations.append("💰 **Low AOV:** Implement upselling and cross-selling strategies")
    
    if len(recommendations) == 0:
        recommendations.append("✅ **Strong Performance:** Focus on customer retention and expansion")
    
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    # KPI Summary
    st.subheader("📊 KPI Summary")
    
    kpi_data = {
        'Metric': ['Conversion Rate', 'Avg Order Value', 'Customer Acquisition Cost', 'Customer Lifetime Value'],
        'Value': [
            f"{conversion_metrics['purchase_rate']:.1f}%",
            f"${avg_order_value:.2f}",
            "N/A (requires cost data)",
            "N/A (requires historical data)"
        ],
        'Status': [
            "🟢 Good" if conversion_metrics['purchase_rate'] > 10 else "🟡 Needs Improvement",
            "🟢 Good" if avg_order_value > 50 else "🟡 Needs Improvement",
            "⚪ Not Available",
            "⚪ Not Available"
        ]
    }
    
    kpi_df = pd.DataFrame(kpi_data)
    st.dataframe(kpi_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>📊 Advanced E-commerce Analytics | Week 2 Features</p>
        <p>RFM Segmentation • Behavioral Clustering • Conversion Analysis • Business Intelligence</p>
    </div>
    """,
    unsafe_allow_html=True
) 