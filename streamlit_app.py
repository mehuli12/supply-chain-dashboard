import streamlit as st
import pandas as pd
import plotly.express as px

# Set title
st.title("📦 Supply Chain Logistics Dashboard")

# Load datasets
orders_file = "expanded_orders.csv"
freight_file = "expanded_freight.csv"
wh_costs_file = "expanded_wh_costs.csv"

@st.cache_data
def load_data():
    df_orders = pd.read_csv(orders_file)
    df_orders["Order Date"] = pd.to_datetime(df_orders["Order Date"])
    
    df_freight = pd.read_csv(freight_file)
    df_wh_costs = pd.read_csv(wh_costs_file)
    
    return df_orders, df_freight, df_wh_costs

df_orders, df_freight, df_wh_costs = load_data()

# Sidebar filter
year_options = sorted(df_orders["Order Date"].dt.year.unique())
selected_year = st.sidebar.selectbox("Select Year", year_options)

# Filter data
filtered_orders = df_orders[df_orders["Order Date"].dt.year == selected_year]
filtered_freight = df_freight[df_freight["Year"] == selected_year]
filtered_wh_costs = df_wh_costs[df_wh_costs["Year"] == selected_year]

# KPI Metrics
st.metric("📦 Total Orders", f"{filtered_orders['Unit quantity'].sum():,.0f}")
st.metric("💰 Total Cost Savings", f"${filtered_wh_costs['Cost/unit'].sum():,.2f}M")
st.metric("🏢 Avg Warehouse Cost", f"${filtered_wh_costs['Cost/unit'].mean():,.2f} per unit")

# Order Chart
st.subheader(f"📊 Order Fulfillment in {selected_year}")
fig_orders = px.bar(filtered_orders, x="Order Date", y="Unit quantity", labels={"Unit quantity": "Units Shipped"})
st.plotly_chart(fig_orders, use_container_width=True)

# Freight Chart
st.subheader(f"🚢 Freight Costs by Origin Port in {selected_year}")
fig_freight = px.bar(filtered_freight, x="orig_port_cd", y="minimum cost", labels={"minimum cost": "Cost ($)"})
st.plotly_chart(fig_freight, use_container_width=True)

# Warehouse Cost Chart
st.subheader(f"🏭 Warehouse Cost Per Unit in {selected_year}")
fig_wh_costs = px.bar(filtered_wh_costs, x="WH", y="Cost/unit", labels={"Cost/unit": "Storage Cost ($)"})
st.plotly_chart(fig_wh_costs, use_container_width=True)

