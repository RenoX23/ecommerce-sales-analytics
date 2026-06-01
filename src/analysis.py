import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

DATA_PATH = "data/processed/master_dataset.csv"

def load_master():
    df = pd.read_csv(DATA_PATH, parse_dates=['order_purchase_timestamp'])
    # Only delivered orders for revenue analysis
    df_delivered = df[df['order_status'] == 'delivered'].copy()
    return df, df_delivered

# Q1: Which product categories drive most revenue?
def revenue_by_category(df):
    cat_revenue = (
        df.groupby('product_category_name_english')['total_order_value']
        .sum()
        .reset_index()
        .sort_values('total_order_value', ascending=False)
        .head(15)
        .rename(columns={
            'product_category_name_english': 'category',
            'total_order_value': 'total_revenue'
        })
    )
    cat_revenue['total_revenue'] = cat_revenue['total_revenue'].round(2)
    return cat_revenue

# Q2: How do sales trend over time?
def sales_trend(df):
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    trend = (
        df.groupby('month')
        .agg(
            total_revenue=('total_order_value', 'sum'),
            order_count=('order_id', 'nunique')
        )
        .reset_index()
    )
    return trend

# Q3: Which states have highest orders + delays?
def state_analysis(df):
    state = (
        df.groupby('customer_state')
        .agg(
            total_orders=('order_id', 'nunique'),
            avg_delivery_days=('delivery_days', 'mean'),
            late_delivery_rate=('late_delivery', 'mean')
        )
        .reset_index()
        .sort_values('total_orders', ascending=False)
    )
    state['avg_delivery_days'] = state['avg_delivery_days'].round(1)
    state['late_delivery_rate'] = (state['late_delivery_rate'] * 100).round(1)
    return state

# Q4: Avg order value by category
def avg_order_value_by_category(df):
    aov = (
        df.groupby('product_category_name_english')['total_order_value']
        .agg(['mean', 'median', 'count'])
        .reset_index()
        .rename(columns={
            'product_category_name_english': 'category',
            'mean': 'avg_order_value',
            'median': 'median_order_value',
            'count': 'order_count'
        })
        .sort_values('avg_order_value', ascending=False)
        .head(15)
    )
    aov['avg_order_value'] = aov['avg_order_value'].round(2)
    aov['median_order_value'] = aov['median_order_value'].round(2)
    return aov

# Q5: What factors correlate with bad reviews?
def bad_review_analysis(df):
    df_reviews = df[df['review_score'].notna()].copy()
    df_reviews['bad_review'] = (df_reviews['review_score'] <= 2).astype(int)

    factors = (
        df_reviews.groupby('bad_review')
        .agg(
            avg_delivery_days=('delivery_days', 'mean'),
            avg_freight=('freight_value', 'mean'),
            late_delivery_rate=('late_delivery', 'mean'),
            avg_price=('price', 'mean')
        )
        .reset_index()
    )
    factors['avg_delivery_days'] = factors['avg_delivery_days'].round(1)
    factors['avg_freight'] = factors['avg_freight'].round(2)
    factors['late_delivery_rate'] = (factors['late_delivery_rate'] * 100).round(1)
    factors['avg_price'] = factors['avg_price'].round(2)
    return factors

if __name__ == "__main__":
    df, df_delivered = load_master()

    print("=== Q1: Top 15 Categories by Revenue ===")
    print(revenue_by_category(df_delivered).to_string())

    print("\n=== Q2: Sales Trend by Month ===")
    print(sales_trend(df_delivered).to_string())

    print("\n=== Q3: State Analysis ===")
    print(state_analysis(df_delivered).to_string())

    print("\n=== Q4: Avg Order Value by Category ===")
    print(avg_order_value_by_category(df_delivered).to_string())

    print("\n=== Q5: Bad Review Factors ===")
    print(bad_review_analysis(df_delivered).to_string())
