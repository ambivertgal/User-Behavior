# User Behavior Analytics Platform - 4-Week Sprint

## 📋 Project Overview
Build a focused analytics platform showcasing cohort analysis, funnel analysis, and user segmentation - the core features that matter most to recruiters.

## 🎯 Final Deliverables
- Interactive Streamlit dashboard with 3 key analytics modules
- Clean data pipeline with synthetic user event data
- User segmentation using ML clustering
- Professional GitHub repository with clear documentation
- LinkedIn post with key insights

---

## 🛠️ Simplified Tech Stack
**Core**: Python, Pandas, Streamlit, SQLite
**ML**: Scikit-learn (K-means, preprocessing)
**Visualization**: Plotly (built into Streamlit)
**Deployment**: Streamlit Cloud (free and easy)

## 📊 MVP Success Metrics
- [ ] 3 analytics modules: Cohort + Funnel + Segmentation
- [ ] Interactive dashboard deployed live
- [ ] 50K+ synthetic events processed
- [ ] Professional documentation
- [ ] LinkedIn post published

## 📊 Data Structure

The project uses synthetic e-commerce data with the following structure:

### Users Table (`users.csv`)
- `user_id`: Unique user identifier (U000001, U000002, etc.)
- `email`: User email address
- `registration_date`: When user joined the platform
- `age`: User age (18-65)
- `gender`: M/F
- `location`: City name
- `segment`: User segment (High Value, Regular, Occasional, New)

### Products Table (`products.csv`)
- `product_id`: Unique product identifier (P0001, P0002, etc.)
- `product_name`: Product name
- `category`: Product category (Electronics, Clothing, Home & Garden, etc.)
- `price`: Product price ($10-$500)

### Events Table (`events.csv`)
- `event_id`: Unique event identifier
- `user_id`: User who performed the action
- `session_id`: Session identifier
- `event_type`: Type of event (session_start, product_view, add_to_cart, purchase, session_end)
- `timestamp`: When the event occurred
- `product_id`: Product involved (if applicable)
- `category`: Product category (if applicable)
- `price`: Product price (if applicable)
- `quantity`: Quantity (for cart/purchase events)

### Data Generation
Run the `User_Behavior_Data.ipynb` notebook to generate fresh data:
```python
generator = EcommerceDataGenerator(num_users=5000, num_days=365)
users_df, products_df, events_df = generator.create_database()
```

**Note**: CSV files are excluded from git due to size (>100MB). Generate data locally as needed.

## ⚡ Time-Saving Tips
- Use Streamlit (faster than building React frontend)
- Generate synthetic data (no need to find perfect dataset)
- Focus on 3 core features vs 10 basic ones
- Use existing visualization libraries
- Deploy early and iterate

---

*This focused 4-week sprint delivers maximum impact with minimal time investment. Every feature is chosen for resume/interview value!*