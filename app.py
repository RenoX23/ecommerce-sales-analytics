import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.analysis import (
    load_master,
    revenue_by_category,
    sales_trend,
    state_analysis,
    avg_order_value_by_category,
    bad_review_analysis
)

st.set_page_config(
    page_title="Brazilian E-commerce Analytics",
    page_icon="🛒",
    layout="wide"
)

# Load data
@st.cache_data
def get_data():
    return load_master()

df, df_delivered = get_data()

# Sidebar
st.sidebar.title("🛒 E-commerce Analytics")
st.sidebar.markdown("**Dataset:** Olist Brazilian E-commerce")
st.sidebar.markdown(f"**Total Orders:** {df['order_id'].nunique():,}")
st.sidebar.markdown(f"**Total Revenue:** R$ {df_delivered['total_order_value'].sum():,.2f}")
st.sidebar.markdown(f"**Date Range:** Sep 2016 – Aug 2018")

page = st.sidebar.radio("Navigate", [
    "📊 Revenue by Category",
    "📈 Sales Trend",
    "🗺️ State Analysis",
    "💰 Avg Order Value",
    "⭐ Review Analysis"
])

# ─── PAGE 1 ───
if page == "📊 Revenue by Category":
    st.title("📊 Revenue by Product Category")
    st.markdown("**Business Question:** Which product categories drive the most revenue?")

    data = revenue_by_category(df_delivered)

    fig = px.bar(
        data,
        x='total_revenue',
        y='category',
        orientation='h',
        color='total_revenue',
        color_continuous_scale='Blues',
        labels={'total_revenue': 'Total Revenue (R$)', 'category': 'Category'},
        title='Top 15 Categories by Revenue'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("🥇 Top Category", "Health & Beauty", f"R$ {data.iloc[0]['total_revenue']:,.0f}")
    col2.metric("🥈 2nd Category", "Watches & Gifts", f"R$ {data.iloc[1]['total_revenue']:,.0f}")
    col3.metric("🥉 3rd Category", "Bed Bath Table", f"R$ {data.iloc[2]['total_revenue']:,.0f}")

    st.markdown("**💡 Insight:** Health & Beauty leads with R$1.4M. Top 3 categories account for over 30% of total revenue.")

# ─── PAGE 2 ───
elif page == "📈 Sales Trend":
    st.title("📈 Sales Trend Over Time")
    st.markdown("**Business Question:** How do sales trend over time? Any seasonality?")

    data = sales_trend(df_delivered)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['month'], y=data['total_revenue'],
        name='Revenue', mode='lines+markers',
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Bar(
        x=data['month'], y=data['order_count'],
        name='Order Count', yaxis='y2',
        opacity=0.4, marker_color='orange'
    ))
    fig.update_layout(
        title='Monthly Revenue and Order Count',
        yaxis=dict(title='Revenue (R$)'),
        yaxis2=dict(title='Order Count', overlaying='y', side='right'),
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("📈 Peak Month", "Nov 2017", "R$ 1,153,364")
    col2.metric("📊 Growth (Jan→Nov 2017)", "10x", "R$127K → R$1.15M")

    st.markdown("**💡 Insight:** 10x revenue growth in 2017. Nov 2017 spike likely Black Friday. Growth plateaued mid-2018.")

# ─── PAGE 3 ───
elif page == "🗺️ State Analysis":
    st.title("🗺️ State-wise Orders & Delivery Analysis")
    st.markdown("**Business Question:** Which states have highest orders and worst delivery delays?")

    data = state_analysis(df_delivered)

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(
            data.head(10),
            x='customer_state', y='total_orders',
            color='total_orders', color_continuous_scale='Blues',
            title='Top 10 States by Order Volume'
        )
        fig1.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            data.sort_values('late_delivery_rate', ascending=False).head(10),
            x='customer_state', y='late_delivery_rate',
            color='late_delivery_rate', color_continuous_scale='Reds',
            title='Top 10 States by Late Delivery Rate (%)'
        )
        fig2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(data, use_container_width=True)
    st.markdown("**💡 Insight:** SP has 40K orders but only 8.3 day delivery. Northern states (AL, MA, CE) suffer 20–24% late delivery rates.")

# ─── PAGE 4 ───
elif page == "💰 Avg Order Value":
    st.title("💰 Average Order Value by Category")
    st.markdown("**Business Question:** What is the avg order value and how does it vary by category?")

    data = avg_order_value_by_category(df_delivered)

    fig = px.scatter(
        data,
        x='avg_order_value',
        y='median_order_value',
        size='order_count',
        color='avg_order_value',
        hover_name='category',
        color_continuous_scale='Viridis',
        title='Avg vs Median Order Value by Category (bubble size = order count)'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(data, use_container_width=True)
    st.markdown("**💡 Insight:** Computers have highest AOV (R$1,147). Large mean/median gap in categories like Musical Instruments indicates price outliers skewing averages.")

# ─── PAGE 5 ───
elif page == "⭐ Review Analysis":
    st.title("⭐ What Drives Bad Reviews?")
    st.markdown("**Business Question:** What factors correlate with bad reviews (score ≤ 2)?")

    data = bad_review_analysis(df_delivered)

    metrics = ['avg_delivery_days', 'avg_freight', 'late_delivery_rate', 'avg_price']
    labels = ['Avg Delivery Days', 'Avg Freight (R$)', 'Late Delivery Rate (%)', 'Avg Price (R$)']

    fig = go.Figure()
    for metric, label in zip(metrics, labels):
        fig.add_trace(go.Bar(
            name=label,
            x=['Good Review (3-5)', 'Bad Review (1-2)'],
            y=data[metric],
            text=data[metric].round(1),
            textposition='auto'
        ))
    fig.update_layout(
        barmode='group',
        title='Good vs Bad Reviews — Key Factors Comparison'
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("⏱️ Extra Delivery Days", "+7.4 days", "Bad vs Good reviews")
    col2.metric("🚚 Late Delivery Rate", "28.9% vs 4.1%", "7x higher for bad reviews")
    col3.metric("💸 Price Difference", "Negligible", "Not a factor")

    st.markdown("**💡 Key Insight:** Late delivery is the #1 driver of bad reviews. Price has almost no impact. Fix logistics = fix satisfaction.")
