"""Streamlit dashboard for Maven Toys retail analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / 'data' / 'processed'


@st.cache_data

def load_processed_data() -> pd.DataFrame:
    """Load the cleaned processed dataset."""
    csv_files = list(DATA_PATH.glob('*.csv'))
    if not csv_files:
        raise FileNotFoundError(f'No processed CSV files found in {DATA_PATH}')
    for file in csv_files:
        if 'sales' in file.name.lower() or 'processed' in file.name.lower():
            return pd.read_csv(file)
    return pd.read_csv(csv_files[0])


st.set_page_config(page_title='Maven Toys Retail Performance Dashboard', layout='wide')
st.title('Maven Toys Retail Performance Dashboard')

try:
    df = load_processed_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

if df.empty:
    st.warning('The processed dataset is empty. Please run the cleaning pipeline first.')
    st.stop()

st.subheader('Executive Overview')

kpi_cols = ['revenue', 'profit', 'profit_margin', 'quantity', 'product', 'store']
for col in kpi_cols:
    if col not in df.columns:
        kpi_cols.remove(col)

col1, col2, col3, col4, col5, col6 = st.columns(6)
metrics = {
    'Revenue': df['revenue'].sum() if 'revenue' in df.columns else 0,
    'Profit': df['profit'].sum() if 'profit' in df.columns else 0,
    'Profit Margin': (df['profit'].sum() / df['revenue'].sum() * 100) if 'revenue' in df.columns and 'profit' in df.columns and df['revenue'].sum() else 0,
    'Units Sold': df['quantity'].sum() if 'quantity' in df.columns else 0,
    'Products': df['product'].nunique() if 'product' in df.columns else 0,
    'Stores': df['store'].nunique() if 'store' in df.columns else 0,
}

cards = [col1, col2, col3, col4, col5, col6]
for card, (label, value) in zip(cards, metrics.items()):
    with card:
        st.metric(label, f'{value:,.0f}' if isinstance(value, float) and label not in {'Profit Margin'} else f'{value:,.2f}' if label == 'Profit Margin' else f'{value:,.0f}')

st.subheader('Filters')
filter_cols = st.columns(4)

if 'date' in df.columns:
    date_min = pd.to_datetime(df['date'], errors='coerce').min()
    date_max = pd.to_datetime(df['date'], errors='coerce').max()
    selected_dates = st.date_input('Date range', (date_min.date(), date_max.date()))
else:
    selected_dates = None

if 'category' in df.columns:
    category = st.selectbox('Category', ['All'] + sorted(df['category'].dropna().unique().tolist()))
else:
    category = 'All'

if 'product' in df.columns:
    product = st.selectbox('Product', ['All'] + sorted(df['product'].dropna().unique().tolist()))
else:
    product = 'All'

if 'store' in df.columns:
    store = st.selectbox('Store', ['All'] + sorted(df['store'].dropna().unique().tolist()))
else:
    store = 'All'

if 'city' in df.columns:
    city = st.selectbox('City', ['All'] + sorted(df['city'].dropna().unique().tolist()))
else:
    city = 'All'

filtered_df = df.copy()
if selected_dates is not None and 'date' in filtered_df.columns:
    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])
    filtered_df = filtered_df[(pd.to_datetime(filtered_df['date'], errors='coerce') >= start_date) & (pd.to_datetime(filtered_df['date'], errors='coerce') <= end_date)]
if category != 'All' and 'category' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['category'] == category]
if product != 'All' and 'product' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['product'] == product]
if store != 'All' and 'store' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['store'] == store]
if city != 'All' and 'city' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['city'] == city]

st.subheader('Sales Trends')
if 'date' in filtered_df.columns:
    trend = filtered_df.assign(date=pd.to_datetime(filtered_df['date'], errors='coerce')).groupby(filtered_df['date'].dt.to_period('M').astype(str), as_index=False).agg(revenue=('revenue', 'sum'), profit=('profit', 'sum'), units=('quantity', 'sum'))
    fig = px.line(trend, x='date', y=['revenue', 'profit'], title='Monthly revenue and profit')
    st.plotly_chart(fig, use_container_width=True)

st.subheader('Top Products')
if 'product' in filtered_df.columns and 'revenue' in filtered_df.columns:
    product_chart = filtered_df.groupby('product', as_index=False).agg(revenue=('revenue', 'sum'), profit=('profit', 'sum')).sort_values('revenue', ascending=False).head(10)
    fig2 = px.bar(product_chart, x='revenue', y='product', orientation='h', title='Top products by revenue')
    st.plotly_chart(fig2, use_container_width=True)

st.subheader('Category Performance')
if 'category' in filtered_df.columns:
    category_summary = filtered_df.groupby('category', as_index=False).agg(revenue=('revenue', 'sum'), profit=('profit', 'sum'), units=('quantity', 'sum'))
    fig3 = px.bar(category_summary, x='category', y='revenue', title='Revenue by category')
    st.plotly_chart(fig3, use_container_width=True)

st.subheader('Store Performance')
if 'store' in filtered_df.columns:
    store_summary = filtered_df.groupby('store', as_index=False).agg(revenue=('revenue', 'sum'), profit=('profit', 'sum'), units=('quantity', 'sum')).sort_values('revenue', ascending=False)
    fig4 = px.bar(store_summary, x='store', y='revenue', title='Revenue by store')
    st.plotly_chart(fig4, use_container_width=True)

st.subheader('Data Preview')
st.dataframe(filtered_df.head(25), use_container_width=True)
