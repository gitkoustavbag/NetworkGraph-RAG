import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Network Explorer & Graph Viz", page_icon="📊", layout="wide")

st.title("📊 Supply Chain Data & Interactive Network Graph")

input_path = "data/supply_chain.xlsx"

try:
    df_suppliers = pd.read_excel(input_path, sheet_name="Suppliers")
    df_shipments = pd.read_excel(input_path, sheet_name="Shipments")
    df_incidents = pd.read_excel(input_path, sheet_name="Incidents")
    df_inventory = pd.read_excel(input_path, sheet_name="InventoryLevels")
    df_routes = pd.read_excel(input_path, sheet_name="TransportRoutes")
except Exception as e:
    st.error(f"Error loading Excel file: {e}. Please run `generate_data.py` first.")
    st.stop()

# Tabs for Data Preview & Network Visualizer
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Suppliers", "Shipments", "Incidents", "Inventory", "Routes", "Interactive Network Graph"
])

with tab1:
    st.dataframe(df_suppliers, use_container_width=True)
with tab2:
    st.dataframe(df_shipments, use_container_width=True)
with tab3:
    st.dataframe(df_incidents, use_container_width=True)
with tab4:
    st.dataframe(df_inventory, use_container_width=True)
with tab5:
    st.dataframe(df_routes, use_container_width=True)

with tab6:
    st.subheader("🕸️ Interactive Knowledge Graph Visualization")
    st.markdown("Explore the multi-entity supply chain network. Nodes are color-coded by category (Suppliers, Shipments, Warehouses, Incidents, Routes).")

    # Build NetworkX graph incorporating all sheets
    G = nx.Graph()

    for _, row in df_suppliers.iterrows():
        G.add_node(row["SupplierID"], label=row["SupplierName"], group="Supplier", title=f"Region: {row['Region']}<br>Risk: {row['RiskRating']}")

    for _, row in df_shipments.iterrows():
        shp_id = row["ShipmentID"]
        sup_id = row["SupplierID"]
        wh = row["Warehouse"]
        G.add_node(shp_id, label=shp_id, group="Shipment", title=f"Material: {row['MaterialCategory']}<br>Delay: {row['TransitDelayDays']} days")
        G.add_node(wh, label=wh, group="Warehouse", title=f"Warehouse Facility: {wh}")
        G.add_edge(sup_id, shp_id, title="Supplies Shipment")
        G.add_edge(shp_id, wh, title="Delivered To")

    for _, row in df_incidents.iterrows():
        inc_id = row["IncidentID"]
        shp_id = row["ShipmentID"]
        G.add_node(inc_id, label=inc_id, group="Incident", title=f"Root Cause: {row['RootCause']}<br>Impact: ${row['FinancialImpactUSD']}")
        G.add_edge(shp_id, inc_id, title="Has Incident")

    for _, row in df_routes.iterrows():
        rt_id = row["RouteID"]
        wh = row["DestinationWarehouse"]
        G.add_node(rt_id, label=rt_id, group="Route", title=f"Origin: {row['OriginRegion']}<br>Cost: ${row['BaseFreightCostUSD']}")
        if wh in G.nodes:
            G.add_edge(rt_id, wh, title="Route Destination")

    # Generate Pyvis Interactive Network
    net = Network(height="600px", width="100%", bgcolor="#0e1117", font_color="white", notebook=False)
    net.from_nx(G)
    
    # Customize physics options for smoother layout
    net.repulsion(node_distance=150, central_gravity=0.3, spring_length=200)
    
    # Save and render graph inside Streamlit
    html_path = "data/network_graph.html"
    net.save_graph(html_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    components.html(html_content, height=620)