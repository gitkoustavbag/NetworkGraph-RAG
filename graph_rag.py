import os
import pandas as pd
import networkx as nx
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

client = OpenAI(api_key=api_key)

print("1. Loading supply chain data from Excel...")
input_path = "data/supply_chain.xlsx"
df_suppliers = pd.read_excel(input_path, sheet_name="Suppliers")
df_shipments = pd.read_excel(input_path, sheet_name="Shipments")
df_incidents = pd.read_excel(input_path, sheet_name="Incidents")

print("2. Constructing Knowledge Graph...")
G = nx.Graph()

# Add Supplier Nodes & Attributes
for _, row in df_suppliers.iterrows():
    G.add_node(row["SupplierID"], type="Supplier", name=row["SupplierName"], region=row["Region"], risk=row["RiskRating"])

# Add Shipment & Warehouse Edges/Nodes
for _, row in df_shipments.iterrows():
    shp_id = row["ShipmentID"]
    sup_id = row["SupplierID"]
    wh = row["Warehouse"]
    mat = row["MaterialCategory"]
    
    G.add_node(shp_id, type="Shipment", material=mat, delay=row["TransitDelayDays"], incident_flag=row["IncidentReported"])
    G.add_node(wh, type="Warehouse")
    
    # Connect Supplier -> Shipment -> Warehouse
    G.add_edge(sup_id, shp_id, relation="SUPPLIES_SHIPMENT")
    G.add_edge(shp_id, wh, relation="DELIVERED_TO")

# Add Incident Nodes & Edges
for _, row in df_incidents.iterrows():
    inc_id = row["IncidentID"]
    shp_id = row["ShipmentID"]
    
    G.add_node(inc_id, type="Incident", root_cause=row["RootCause"], financial_impact=row["FinancialImpactUSD"])
    G.add_edge(shp_id, inc_id, relation="HAS_INCIDENT")

print(f"Graph built successfully with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

print("3. Executing GraphRAG Retrieval & LLM Reasoning per Supplier...")
analysis_results = []

for _, supplier in df_suppliers.iterrows():
    sup_id = supplier["SupplierID"]
    sup_name = supplier["SupplierName"]
    
    # GraphRAG Neighborhood Retrieval (1-hop and 2-hop neighbors)
    subgraph_nodes = set([sup_id])
    for neighbor in G.neighbors(sup_id):
        subgraph_nodes.add(neighbor)
        for sub_neighbor in G.neighbors(neighbor):
            subgraph_nodes.add(sub_neighbor)
            
    # Build text context from the local graph subgraph
    context_lines = [f"Supplier Profile: {sup_name} (ID: {sup_id}, Initial Risk: {supplier['RiskRating']}, Region: {supplier['Region']})"]
    for node in subgraph_nodes:
        if node != sup_id:
            node_data = G.nodes[node]
            context_lines.append(f"- Connected Entity [{node}]: Type={node_data.get('type')}, Attributes={dict(node_data)}")
            
    graph_context_text = "\n".join(context_lines)
    
    # Prompt OpenAI with Graph Context
    prompt = f"""
    You are an expert Enterprise Supply Chain Risk Analyst. Using the following localized Knowledge Graph neighborhood data, evaluate this supplier's systemic risk, identify underlying structural vulnerabilities, and provide a short mitigation strategy.

    Graph Neighborhood Data:
    {graph_context_text}

    Provide your response in 2 distinct parts separated by a pipe character (|):
    1. Systemic Risk Summary & Root Cause Analysis
    2. Recommended Mitigation Action
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        ai_output = response.choices[0].message.content.strip()
        if "|" in ai_output:
            parts = ai_output.split("|", 1)
            risk_summary = parts[0].strip()
            mitigation = parts[1].strip()
        else:
            risk_summary = ai_output
            mitigation = "Monitor logistics closely."
    except Exception as e:
        risk_summary = f"Error calling OpenAI API: {str(e)}"
        mitigation = "N/A"

    analysis_results.append({
        "SupplierID": sup_id,
        "SupplierName": sup_name,
        "InitialRisk": supplier["RiskRating"],
        "GraphRAG_Risk_Assessment": risk_summary,
        "Recommended_Mitigation": mitigation
    })

print("4. Saving structured output to Excel...")
df_output = pd.DataFrame(analysis_results)
output_path = "data/risk_analysis_output.xlsx"
os.makedirs("data", exist_ok=True)
df_output.to_excel(output_path, index=False)

print(f"GraphRAG execution complete! Output saved to: {output_path}")