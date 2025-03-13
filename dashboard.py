import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os

# Define the absolute path for datasets
DATA_DIR = "/app"

orders_file = os.path.join(DATA_DIR, "expanded_orders.csv")
freight_file = os.path.join(DATA_DIR, "expanded_freight.csv")
wh_costs_file = os.path.join(DATA_DIR, "expanded_wh_costs.csv")

# Check if the files exist before loading
def load_data(file_path, columns):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        print(f"⚠️ Warning: {file_path} not found. Using an empty dataset.")
        return pd.DataFrame(columns=columns)

df_orders = load_data(orders_file, ["Order Date", "Unit quantity"])
df_freight = load_data(freight_file, ["Year", "orig_port_cd", "minimum cost"])
df_wh_costs = load_data(wh_costs_file, ["Year", "WH", "Cost/unit"])

# Convert Order Date to datetime for filtering
if not df_orders.empty:
    df_orders["Order Date"] = pd.to_datetime(df_orders["Order Date"])

# Extract unique years for dropdown filtering
available_years = sorted(df_orders["Order Date"].dt.year.unique()) if not df_orders.empty else []

# Initialize Dash app with Bootstrap styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server  # Expose the server for Gunicorn

# KPI Calculations (if data is available)
total_orders = df_orders["Unit quantity"].sum() if not df_orders.empty else 0
total_cost_savings = df_wh_costs["Cost/unit"].sum() if not df_wh_costs.empty else 0
avg_wh_cost = df_wh_costs["Cost/unit"].mean() if not df_wh_costs.empty else 0

# KPI Cards
kpi_cards = dbc.Row([
    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4("Total Orders", className="card-title"),
            html.H2(f"{total_orders:,.0f}", className="card-text")
        ])
    ], color="primary", inverse=True)),

    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4("Total Cost Savings", className="card-title"),
            html.H2(f"${total_cost_savings:,.2f}M", className="card-text")
        ])
    ], color="success", inverse=True)),

    dbc.Col(dbc.Card([
        dbc.CardBody([
            html.H4("Avg Warehouse Cost", className="card-title"),
            html.H2(f"${avg_wh_cost:.2f} per unit", className="card-text")
        ])
    ], color="warning", inverse=True)),
])

# Layout with Filters & Visuals
app.layout = dbc.Container([
    html.H1("Supply Chain Logistics Dashboard", className="text-center my-4"),

    kpi_cards,  # KPI Cards Display

    html.Label("Filter by Year:") if available_years else html.Label("No data available"),
    
    dcc.Dropdown(
        id="year-filter",
        options=[{"label": str(year), "value": year} for year in available_years] if available_years else [],
        value=available_years[0] if available_years else None,
        clearable=False
    ) if available_years else html.Div(),

    dcc.Graph(id="orders-chart"),
    dcc.Graph(id="freight-chart"),
    dcc.Graph(id="warehouse-chart"),
])

# Callbacks for Interactive Filtering
@app.callback(
    [Output("orders-chart", "figure"),
     Output("freight-chart", "figure"),
     Output("warehouse-chart", "figure")],
    [Input("year-filter", "value")]
)
def update_charts(selected_year):
    if not available_years or selected_year is None:
        return px.bar(title="No Data Available"), px.bar(title="No Data Available"), px.bar(title="No Data Available")

    # Filter data based on the selected year
    filtered_orders = df_orders[df_orders["Order Date"].dt.year == selected_year] if not df_orders.empty else pd.DataFrame()
    filtered_freight = df_freight[df_freight["Year"] == selected_year] if not df_freight.empty else pd.DataFrame()
    filtered_wh_costs = df_wh_costs[df_wh_costs["Year"] == selected_year] if not df_wh_costs.empty else pd.DataFrame()

    # Order Fulfillment Chart
    fig_orders = px.bar(filtered_orders, x="Order Date", y="Unit quantity",
                        title=f"Order Fulfillment in {selected_year}",
                        labels={"Unit quantity": "Units Shipped"}) if not filtered_orders.empty else px.bar(title="No Orders Data")

    # Freight Cost Analysis
    fig_freight = px.bar(filtered_freight, x="orig_port_cd", y="minimum cost",
                          title=f"Freight Costs by Origin Port in {selected_year}",
                          labels={"minimum cost": "Cost ($)"}) if not filtered_freight.empty else px.bar(title="No Freight Data")

    # Warehouse Cost Analysis
    fig_wh_costs = px.bar(filtered_wh_costs, x="WH", y="Cost/unit",
                           title=f"Warehouse Cost Per Unit in {selected_year}",
                           labels={"Cost/unit": "Storage Cost ($)"}) if not filtered_wh_costs.empty else px.bar(title="No Warehouse Cost Data")

    return fig_orders, fig_freight, fig_wh_costs

# Run Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=7860)

