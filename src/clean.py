import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/raw/"

def load_all_data():
    """Load all 9 CSVs"""
    data = {}
    files = os.listdir(DATA_PATH)

    for file in files:
        if file.endswith('.csv'):
            name = file.replace('.csv', '')
            data[name] = pd.read_csv(os.path.join(DATA_PATH, file))

    return data

def clean_data(data):
    """Clean and merge all tables"""

    # 1. Clean timestamps
    time_cols = ['order_purchase_timestamp', 'order_approved_at',
                 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date']
    for col in time_cols:
        data['olist_orders_dataset'][col] = pd.to_datetime(data['olist_orders_dataset'][col], errors='coerce')

    data['olist_order_reviews_dataset']['review_creation_date'] = pd.to_datetime(
        data['olist_order_reviews_dataset']['review_creation_date'], errors='coerce')

    # 2. Add category English names
    products = data['olist_products_dataset'].merge(
        data['product_category_name_translation'],
        on='product_category_name',
        how='left'
    )

    # 3. Merge: orders + items + products + payments
    master = data['olist_orders_dataset'].merge(
        data['olist_order_items_dataset'],
        on='order_id',
        how='inner'
    ).merge(
        products,
        on='product_id',
        how='left'
    ).merge(
        data['olist_order_payments_dataset'],
        on='order_id',
        how='left'
    ).merge(
        data['olist_order_reviews_dataset'],
        on='order_id',
        how='left'
    ).merge(
        data['olist_customers_dataset'],
        on='customer_id',
        how='left'
    ).merge(
        data['olist_sellers_dataset'],
        on='seller_id',
        how='left'
    )

    # 4. Calculate derived columns
    master['delivery_days'] = (
        master['order_delivered_customer_date'] - master['order_purchase_timestamp']
    ).dt.days

    master['late_delivery'] = (
        master['order_delivered_customer_date'] > master['order_estimated_delivery_date']
    ).astype(int)

    master['total_order_value'] = master['price'] + master['freight_value']

    # 5. Drop duplicates on order level (keep first)
    master = master.drop_duplicates(subset=['order_id', 'order_item_id'], keep='first')

    print(f"Master dataset shape: {master.shape}")
    print(f"Columns: {len(master.columns)}")
    print(f"\nNull values:\n{master.isnull().sum()}")

    return master

if __name__ == "__main__":
    data = load_all_data()
    master = clean_data(data)

    # Save
    master.to_csv('data/processed/master_dataset.csv', index=False)
    print("\n✓ Saved to data/processed/master_dataset.csv")
