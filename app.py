#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Olist E-Commerce Dashboard", 
    page_icon="🛒", 
    layout="wide"
)

st.title("🛍️ Olist E-Commerce Analytics Dashboard")
st.markdown("An interactive exploration of Brazil's e-commerce retail performance.")

# 2. DATA LOADING & CACHING
@st.cache_data
def load_data():
    items = pd.read_csv('olist_order_items_dataset.csv')
    products = pd.read_csv('olist_products_dataset.csv')
    orders = pd.read_csv('olist_orders_dataset.csv')

# Merge tables
    df = pd.merge(items, products, on='product_id', how='left')
    df = pd.merge(df, orders, on='order_id', how='left')
    
    # Datetime transformation
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Feature Engineering & Cleaning
    df['total_revenue'] = df['price'] + df['freight_value']
    df['product_category_name'] = df['product_category_name'].fillna('unknown')
    
    # Category Translation Dictionary
    category_translation = {
        'cama_mesa_banho': 'bed_bath_table',
        'beleza_saude': 'health_beauty',
        'esporte_lazer': 'sports_leisure',
        'moveis_decoracao': 'furniture_decor',
        'informatica_acessorios': 'computers_accessories',
        'utilidades_domesticas': 'housewares',
        'relogios_presentes': 'watches_gifts',
        'telefonia': 'telephony',
        'ferramentas_jardim': 'garden_tools',
        'automotivo': 'auto',
        'brinquedos': 'toys',
        'cool_stuff': 'cool_stuff',
        'perfumaria': 'perfumery',
        'bebes': 'baby',
        'eletronicos': 'electronics',
        'papelaria': 'stationery',
        'fashion_bolsas_e_acessorios': 'fashion_bags_accessories',
        'pet_shop': 'pet_shop',
        'moveis_escritorio': 'office_furniture',
        'consoles_games': 'consoles_games',
        'malas_acessorios': 'luggage_accessories',
        'construcao_ferramentas_construcao': 'construction_tools',
        'eletrodomesticos': 'home_appliances',
        'instrumentos_musicais': 'musical_instruments',
        'eletroportateis': 'small_appliances',
        'unknown': 'unknown'
    }
    
    df['product_category'] = df['product_category_name'].map(category_translation).fillna('other')
    return df

# Load the dataset
df = load_data()

# 3. SIDEBAR / FILTERS
st.sidebar.header("Filter Options")

# Category Filter
categories = ['All'] + sorted(df['product_category'].unique().tolist())
selected_category = st.sidebar.selectbox("Select Product Category", categories)

st.sidebar.markdown("---")

# Date Filter
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

# Creates a date slider for a date range
selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date), # Default selection (Start, End)
    min_value=min_date,         # Absolute limit left
    max_value=max_date          # Absolute limit right
)

# Filtering data
filtered_df = df.copy()
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['product_category'] == selected_category]

# Apply filter only if the user selected both start and end dates
if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[
        (filtered_df['order_purchase_timestamp'].dt.date >= start_date) & 
        (filtered_df['order_purchase_timestamp'].dt.date <= end_date)
    ]

# 4. BUSINESS RECOMMENDATIONS
st.markdown("---")
st.subheader("💡 Business Recommendations")
st.markdown("""
* **Targeted Marketing Campaigns:** Deploy high-impact push notifications and email marketing during the identified daily peak windows (**11:00-14:00** and **20:00-22:00**), specifically on **Mondays and Tuesdays**, to maximize conversion rates when user activity is organic and high.
* **Black Friday Preparedness:** Since November is the platform's critical revenue driver, logistics and inventory partnerships must be stress-tested by Q3. Sellers in top categories should be offered incentive structures to prevent stockouts.
* **Tiered Shipping Strategies:** Address the freight value friction in lower-priced categories (like *bed_bath_table*) by testing flat-rate shipping or free shipping thresholds to increase the Average Order Value (AOV).
""")

# 5. MAIN DASHBOARD / KPI METRICS
# Creating columns for high-level numbers
st.markdown("---")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    total_rev = filtered_df['total_revenue'].sum()
    st.metric(label="Total Revenue (BRL)", value=f"R$ {total_rev:,.2f}".replace(',', ' '))

with kpi2:
    total_orders = filtered_df['order_id'].nunique()
    st.metric(label="Total Orders", value=f"{total_orders:,}".replace(',', ' '))

with kpi3:
    aov = filtered_df['total_revenue'].mean() if not filtered_df.empty else 0
    st.metric(label="Average Item Value", value=f"R$ {aov:.2f}")

with kpi4:
    if not filtered_df.empty and len(filtered_df) > 1:
        # Agrupar por Ano-Mês para ver a evolução
        filtered_df.loc[:, 'year_month'] = filtered_df['order_purchase_timestamp'].dt.to_period('M')
        monthly_sales = filtered_df.groupby('year_month')['total_revenue'].sum().sort_index()
        
        if len(monthly_sales) >= 2:
            last_month_val = monthly_sales.iloc[-1]
            prev_month_val = monthly_sales.iloc[-2]
            # Cálculo da variação percentual
            mom_growth = ((last_month_val - prev_month_val) / prev_month_val) * 100
            st.metric(
                label="MoM Revenue Change", 
                value=f"{mom_growth:+.1f}%", 
                delta=f"{mom_growth:+.1f}% vs Last Month"
            )
        else:
            st.metric(label="MoM Revenue Change", value="N/A", delta="Need 2 months of data")
    else:
        st.metric(label="MoM Revenue Change", value="N/A")

st.markdown("---")
st.write(f"Showing data for category: **{selected_category}** ({len(filtered_df):,} items found)")

# 6. VISUALIZATIONS: SALES TRENDS
# Financial Performance Over Time
st.subheader("📈 Financial Performance Over Time")

# Aggregating daily sales based on the filtered data
daily_sales = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.date)['total_revenue'].sum().reset_index()

if not daily_sales.empty:
    fig1, ax1 = plt.subplots(figsize=(12, 4))
    
    # Setting up the plot
    daily_sales_plot = daily_sales.set_index('order_purchase_timestamp')
    ax1.plot(daily_sales_plot.index, daily_sales_plot['total_revenue'], color='#1f77b4', linewidth=1.5)
    
    # Customizing the look inside Streamlit
    ax1.set_title('Daily Revenue Trend (BRL)', fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('Purchase Date')
    ax1.set_ylabel('Total Revenue')
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    st.pyplot(fig1)
else:
    st.warning("No data available for the selected filters to plot trends.")

# Product Category Performance
st.markdown("---")
st.subheader("🏷️ Product Category Performance")

# Volume vs. Value tension proved in the EDA
metric_choice = st.radio(
    "Analyze Top 10 Categories by:",
    options=["Total Revenue", "Order Volume (Units Sold)"],
    horizontal=True
)

HIGHLIGHT_COLOR = '#1f77b4'
MUTED_COLOR = '#e2e8f0'
GRID_COLOR = '#f1f5f9'

col_left, col_right = st.columns(2)

with col_left:
    if metric_choice == "Total Revenue":
        st.markdown("#### Top 10 Revenue Drivers")
        global_categories = df.groupby('product_category')['total_revenue'].sum().reset_index()
        global_categories = global_categories.sort_values(by='total_revenue', ascending=False).head(10)
        value_column = 'total_revenue'
        xlabel_text = 'Total Revenue (BRL)'
    else:
        st.markdown("#### Top 10 Volume Drivers")
        global_categories = df.groupby('product_category')['order_id'].count().reset_index()
        global_categories = global_categories.sort_values(by='order_id', ascending=False).head(10)
        value_column = 'order_id'
        xlabel_text = 'Items Sold (Units)'

    top_10_names = global_categories['product_category'].tolist()
    
    colors_left = [
        HIGHLIGHT_COLOR if (selected_category == 'All' or cat == selected_category) 
        else MUTED_COLOR 
        for cat in top_10_names
    ]
    
    if not global_categories.empty:
        # Aumentámos ligeiramente o tamanho da figura para acomodar a rotação do texto
        fig2, ax2 = plt.subplots(figsize=(6, 4.5)) 
        ax2.barh(global_categories['product_category'], global_categories[value_column], color=colors_left, alpha=0.9)
        ax2.set_xlabel(xlabel_text)
        ax2.set_ylabel('')
        ax2.invert_yaxis()
        
        # CORREÇÃO DA SOBREPOSIÇÃO NO EIXO X:
        if metric_choice == "Total Revenue":
            # Formata os valores como Milhões (M) para reduzir o tamanho da string (ex: R$ 1.2M)
            ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x*1e-6:.1f}M'))
        else:
            # Para volumes/unidades, apenas adiciona a separação de milhares limpa
            ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
        # Roda os labels em 45 graus e inclina-os para a direita para prevenir qualquer colisão
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#cbd5e1')
        ax2.spines['bottom'].set_color('#cbd5e1')
        ax2.grid(True, linestyle='--', alpha=0.6, axis='x', color=GRID_COLOR)
        plt.tight_layout()
        st.pyplot(fig2)
    else:
        st.info("No category data available.")

with col_right:
    st.markdown("#### AOV Comparison")
    
    global_category_aov = df.groupby('product_category')['total_revenue'].mean().reset_index()
    
    if not global_categories.empty:
        filtered_aov = global_category_aov[global_category_aov['product_category'].isin(top_10_names)].copy()
        filtered_aov['product_category'] = pd.Categorical(filtered_aov['product_category'], categories=top_10_names, ordered=True)
        filtered_aov = filtered_aov.sort_values('product_category')
        
        colors_right = [
            HIGHLIGHT_COLOR if (selected_category == 'All' or cat == selected_category) 
            else MUTED_COLOR 
            for cat in top_10_names
        ]
        
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.barh(filtered_aov['product_category'], filtered_aov['total_revenue'], color=colors_right, alpha=0.9)
        ax3.set_xlabel('Average Value per Item (BRL)')
        ax3.set_ylabel('')
        ax3.invert_yaxis()
        
        ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.spines['left'].set_color('#cbd5e1')
        ax3.spines['bottom'].set_color('#cbd5e1')
        ax3.grid(True, linestyle='--', alpha=0.6, axis='x', color=GRID_COLOR)
        plt.tight_layout()
        st.pyplot(fig3)
    else:
        st.info("No AOV data available.")

st.markdown("---")
st.subheader("📈 Sales Trends & Behaviors")

if not filtered_df.empty:
    # Seasonality analysis based on EDA insights
    tab_monthly, tab_weekday, tab_hourly = st.tabs(["📅 Monthly Evolution", "📆 Day of the Week", "⏰ Hourly Activity"])
    
    with tab_monthly:
        st.markdown("#### Monthly Revenue Performance")
        filtered_df['year_month'] = filtered_df['order_purchase_timestamp'].dt.to_period('M')
        monthly_sales = filtered_df.groupby('year_month')['total_revenue'].sum().reset_index()
        monthly_sales['year_month'] = monthly_sales['year_month'].astype(str)
        
        fig, ax = plt.subplots(figsize=(12, 5)) # Aumentámos ligeiramente a altura para dar espaço aos labels
        ax.plot(monthly_sales['year_month'], monthly_sales['total_revenue'], marker='o', color='#1f77b4', linewidth=2)
        
        # BLACK FRIDAY ANNOTATION
        if "2017-11" in monthly_sales['year_month'].values:
            bf_revenue = monthly_sales[monthly_sales['year_month'] == "2017-11"]['total_revenue'].values[0]
            ax.annotate(
                '🔥 Black Friday Peak!', 
                xy=("2017-11", bf_revenue), 
                xytext=("2017-05", bf_revenue * 0.9),
                arrowprops=dict(facecolor='red', shrink=0.05, width=1, headwidth=6),
                fontweight='bold', color='red'
            )
            
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Revenue (BRL)')
        st.caption("EDA Insight: The platform experienced consistent growth throughout 2017, culminating in a unmatched revenue spike in November driven by Black Friday. " \
        "This highlights Black Friday as the most critical sales event for Olist's yearly performance, followed by a stabilized revenue in 2018.")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'.replace(',', '.')))
        
        plt.xticks(rotation=45, ha='right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        
    with tab_weekday:
        st.markdown("#### Order Distribution by Day of the Week")
        st.caption("EDA Insight: Transaction volumes peak early in the week (Monday and Tuesday) and experience a significant drop during weekends.")
        
        filtered_df['day_of_week'] = filtered_df['order_purchase_timestamp'].dt.day_name()
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        weekday_counts = filtered_df.groupby('day_of_week')['order_id'].nunique().reindex(weekday_order).reset_index()
        
        fig_w, ax_w = plt.subplots(figsize=(12, 4))
        # Highlight Monday and Tuesday with a stronger color
        colors_w = ['#1f77b4', '#1f77b4', '#aec7e8', '#aec7e8', '#aec7e8', '#cbd5e1', '#cbd5e1']
        ax_w.bar(weekday_counts['day_of_week'], weekday_counts['order_id'], color=colors_w, alpha=0.9)
        ax_w.set_ylabel('Unique Orders')
        ax_w.spines['top'].set_visible(False)
        ax_w.spines['right'].set_visible(False)
        ax_w.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_w)
        
    with tab_hourly:
        st.markdown("#### Hourly Transaction Patterns")
        st.caption("EDA Insight: Transactions follow a clear double-peak pattern during daytime hours (11:00-14:00 and 20:00-22:00).")
        
        filtered_df['hour'] = filtered_df['order_purchase_timestamp'].dt.hour
        hourly_orders = filtered_df.groupby('hour')['order_id'].nunique().reset_index()
        
        fig_h, ax_h = plt.subplots(figsize=(12, 4))
        ax_h.plot(hourly_orders['hour'], hourly_orders['order_id'], color='#2ca02c', marker='s', linewidth=2)
        ax_h.set_xlabel('Hour of the Day')
        ax_h.set_ylabel('Unique Orders')
        ax_h.set_xticks(range(0, 24))
        
        # Peak hours identified in EDA
        ax_h.axvspan(11, 14, color='yellow', alpha=0.2, label='Lunch Peak (11h-14h)')
        ax_h.axvspan(20, 22, color='orange', alpha=0.2, label='Evening Peak (20h-22h)')
        ax_h.legend()
        
        ax_h.spines['top'].set_visible(False)
        ax_h.spines['right'].set_visible(False)
        ax_h.grid(True, linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_h)
else:
    st.info("No trend data available for the selected filters.")

# Logistics & Insights
st.markdown("---")
st.subheader("📦 Logistics & Insights")

if not filtered_df.empty:
    sample_size = min(2000, len(filtered_df))
    scatter_data = filtered_df.sample(n=sample_size, random_state=42)
    
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    
    ax4.scatter(scatter_data['price'], scatter_data['freight_value'], color='#1f77b4', alpha=0.4, edgecolors='none')
    
    ax4.set_title(f"Product Price vs. Freight Value (Sample of {sample_size} items)", fontsize=12, fontweight='bold', pad=10)
    ax4.set_xlabel("Product Price (BRL)")
    ax4.set_ylabel("Freight Value (BRL)")
    
    ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['left'].set_color('#cbd5e1')
    ax4.spines['bottom'].set_color('#cbd5e1')
    ax4.grid(True, linestyle='--', alpha=0.5, color='#f1f5f9')
    
    plt.tight_layout()
    st.pyplot(fig4)
else:
    st.info("No data available to plot logistics insights.")

