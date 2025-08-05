import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Dark mode compatible
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: rgba(248, 249, 250, 0.1);
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .metric-highlight {
        background-color: rgba(232, 244, 253, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff7f0e;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .feature-card h3, .feature-card h4, .feature-card p, .feature-card li {
        color: inherit;
    }
    .metric-highlight h4, .metric-highlight p, .metric-highlight li {
        color: inherit;
    }
    .feature-card ul, .metric-highlight ul {
        color: inherit;
    }
</style>
""", unsafe_allow_html=True)

class EcommerceDataGenerator:
    def __init__(self, num_users=1000, num_days=180, start_date='2023-01-01'):
        """
        Initialize data generator with smaller default values for Streamlit Cloud
        """
        self.num_users = num_users
        self.num_days = num_days
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = self.start_date + timedelta(days=num_days)
        
        # Product categories and items
        self.categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Beauty', 'Toys']
        self.products = self.generate_products()
        
        # User segments (for realistic behavior patterns)
        self.user_segments = ['High Value', 'Regular', 'Occasional', 'New']
        
    def generate_products(self):
        """Generate product catalog"""
        products = []
        product_names = {
            'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Tablet', 'Smartwatch', 'Camera'],
            'Clothing': ['T-shirt', 'Jeans', 'Dress', 'Jacket', 'Shoes', 'Sweater'],
            'Home & Garden': ['Coffee Maker', 'Vacuum', 'Plant Pot', 'Lamp', 'Curtains', 'Pillow'],
            'Books': ['Fiction Novel', 'Cookbook', 'Biography', 'Self-help', 'Textbook', 'Comics'],
            'Sports': ['Running Shoes', 'Yoga Mat', 'Dumbbell', 'Bicycle', 'Football', 'Water Bottle'],
            'Beauty': ['Skincare Set', 'Makeup Kit', 'Perfume', 'Shampoo', 'Moisturizer', 'Lipstick'],
            'Toys': ['Board Game', 'Action Figure', 'Puzzle', 'Building Blocks', 'Doll', 'Remote Car']
        }
        
        for category in self.categories:
            for product_name in product_names[category]:
                price = round(random.uniform(10, 500), 2)
                products.append({
                    'product_id': f"P{len(products)+1:04d}",
                    'product_name': product_name,
                    'category': category,
                    'price': price
                })
        
        return products
    
    def generate_users(self):
        """Generate user base with segments"""
        users = []
        
        for i in range(self.num_users):
            segment = np.random.choice(self.user_segments, p=[0.1, 0.5, 0.3, 0.1])
            
            # Registration date (some users joined recently, others are old)
            if segment == 'New':
                reg_date = self.start_date + timedelta(days=random.randint(150, 180))
            else:
                reg_date = self.start_date + timedelta(days=random.randint(0, 100))
                
            users.append({
                'user_id': f"U{i+1:06d}",
                'email': f"user{i+1}@example.com",
                'registration_date': reg_date,
                'age': random.randint(18, 65),
                'gender': random.choice(['M', 'F']),
                'location': f"City{i+1}",
                'segment': segment
            })
        
        return users
    
    def generate_user_events(self, users):
        """Generate realistic user behavior events (optimized for smaller dataset)"""
        events = []
        
        for user in users:
            user_id = user['user_id']
            segment = user['segment']
            reg_date = user['registration_date']
            
            # Different behavior patterns by segment
            if segment == 'High Value':
                sessions_per_month = random.randint(4, 10)
                purchase_probability = 0.3
                avg_session_length = random.randint(3, 8)
            elif segment == 'Regular':
                sessions_per_month = random.randint(2, 6)
                purchase_probability = 0.15
                avg_session_length = random.randint(2, 5)
            elif segment == 'Occasional':
                sessions_per_month = random.randint(1, 3)
                purchase_probability = 0.08
                avg_session_length = random.randint(1, 3)
            else:  # New
                sessions_per_month = random.randint(1, 2)
                purchase_probability = 0.05
                avg_session_length = random.randint(1, 2)
            
            # Generate sessions from registration date to end date
            days_active = (self.end_date - reg_date).days
            if days_active <= 0:
                continue
                
            total_sessions = int((days_active / 30) * sessions_per_month)
            total_sessions = min(total_sessions, 20)  # Limit sessions per user
            
            for session_num in range(total_sessions):
                # Random session date
                session_date = reg_date + timedelta(days=random.randint(0, days_active))
                session_id = f"S{len(events)+1:08d}"
                
                # Session start
                session_start = session_date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )
                
                events.append({
                    'event_id': f"E{len(events)+1:08d}",
                    'user_id': user_id,
                    'session_id': session_id,
                    'event_type': 'session_start',
                    'timestamp': session_start,
                    'product_id': None,
                    'category': None,
                    'price': None,
                    'quantity': None
                })
                
                # Generate events within session
                current_time = session_start
                session_products = []
                
                # Browse products
                num_products_viewed = random.randint(1, avg_session_length)
                for _ in range(num_products_viewed):
                    product = random.choice(self.products)
                    session_products.append(product)
                    
                    current_time += timedelta(minutes=random.randint(1, 5))
                    
                    events.append({
                        'event_id': f"E{len(events)+1:08d}",
                        'user_id': user_id,
                        'session_id': session_id,
                        'event_type': 'product_view',
                        'timestamp': current_time,
                        'product_id': product['product_id'],
                        'category': product['category'],
                        'price': product['price'],
                        'quantity': None
                    })
                
                # Add to cart (subset of viewed products)
                if session_products:
                    cart_products = random.sample(session_products, 
                                                min(len(session_products), random.randint(1, 2)))
                    
                    for product in cart_products:
                        current_time += timedelta(minutes=random.randint(1, 3))
                        
                        events.append({
                            'event_id': f"E{len(events)+1:08d}",
                            'user_id': user_id,
                            'session_id': session_id,
                            'event_type': 'add_to_cart',
                            'timestamp': current_time,
                            'product_id': product['product_id'],
                            'category': product['category'],
                            'price': product['price'],
                            'quantity': random.randint(1, 3)
                        })
                    
                    # Purchase decision
                    if random.random() < purchase_probability and cart_products:
                        # Purchase subset of cart items
                        purchase_products = random.sample(cart_products, 
                                                        random.randint(1, len(cart_products)))
                        
                        for product in purchase_products:
                            current_time += timedelta(minutes=random.randint(1, 2))
                            quantity = random.randint(1, 2)
                            
                            events.append({
                                'event_id': f"E{len(events)+1:08d}",
                                'user_id': user_id,
                                'session_id': session_id,
                                'event_type': 'purchase',
                                'timestamp': current_time,
                                'product_id': product['product_id'],
                                'category': product['category'],
                                'price': product['price'],
                                'quantity': quantity
                            })
                
                # Session end
                current_time += timedelta(minutes=random.randint(1, 5))
                events.append({
                    'event_id': f"E{len(events)+1:08d}",
                    'user_id': user_id,
                    'session_id': session_id,
                    'event_type': 'session_end',
                    'timestamp': current_time,
                    'product_id': None,
                    'category': None,
                    'price': None,
                    'quantity': None
                })
        
        return events

@st.cache_data
def generate_sample_data(num_users=1000, num_days=180):
    """
    Generate sample data for the Streamlit app
    This function is cached to avoid regenerating data on every interaction
    """
    # Set random seeds for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Generate data
    generator = EcommerceDataGenerator(num_users=num_users, num_days=num_days)
    users = generator.generate_users()
    events = generator.generate_user_events(users)
    products = generator.products
    
    # Convert to DataFrames
    users_df = pd.DataFrame(users)
    products_df = pd.DataFrame(products)
    events_df = pd.DataFrame(events)
    
    # Convert date columns
    users_df['registration_date'] = pd.to_datetime(users_df['registration_date'])
    events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])
    
    return users_df, products_df, events_df

def get_data_summary(users_df, products_df, events_df):
    """Generate summary statistics for the data"""
    summary = {
        'total_users': users_df['user_id'].nunique(),
        'total_products': len(products_df),
        'total_events': len(events_df),
        'date_range': f"{events_df['timestamp'].min().strftime('%Y-%m-%d')} to {events_df['timestamp'].max().strftime('%Y-%m-%d')}",
        'unique_sessions': events_df['session_id'].nunique(),
        'purchase_events': len(events_df[events_df['event_type'] == 'purchase']),
        'total_revenue': (events_df[events_df['event_type'] == 'purchase']['price'] * 
                         events_df[events_df['event_type'] == 'purchase']['quantity']).sum()
    }
    return summary

# Generate data
with st.spinner("Generating sample data..."):
    users, products, events = generate_sample_data(num_users=1000, num_days=180)

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

# Quick stats
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

summary = get_data_summary(users, products, events)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-highlight">
        <h4>📊 Dataset Statistics</h4>
        <ul>
        <li><strong>Users:</strong> {summary['total_users']:,} registered customers</li>
        <li><strong>Products:</strong> {summary['total_products']:,} items across 7 categories</li>
        <li><strong>Events:</strong> {summary['total_events']:,} user interactions</li>
        <li><strong>Sessions:</strong> {summary['unique_sessions']:,} unique user sessions</li>
        <li><strong>Purchases:</strong> {summary['purchase_events']:,} completed transactions</li>
        <li><strong>Revenue:</strong> ${summary['total_revenue']:,.2f} total sales</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    with col2:
        # Calculate additional metrics
        conversion_rate = len(events[events['event_type'] == 'purchase']) / len(events[events['event_type'] == 'session_start']) * 100 if len(events[events['event_type'] == 'session_start']) > 0 else 0
        avg_order_value = (events[events['event_type'] == 'purchase']['price'] * events[events['event_type'] == 'purchase']['quantity']).sum() / len(events[events['event_type'] == 'purchase']) if len(events[events['event_type'] == 'purchase']) > 0 else 0
        top_category = products['category'].value_counts().index[0] if len(products) > 0 else "N/A"
        active_users = events['user_id'].nunique()
        
        st.markdown(f"""
        <div class="metric-highlight">
            <h4>📅 Data Period</h4>
            <p><strong>Date Range:</strong> {summary['date_range']}</p>
            <p><strong>Duration:</strong> 6 months of user activity</p>
            <p><strong>Data Type:</strong> Synthetic e-commerce data</p>
            <p><strong>User Segments:</strong> High Value, Regular, Occasional, New</p>
        </div>
        """, unsafe_allow_html=True)

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