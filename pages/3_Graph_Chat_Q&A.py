import streamlit as st
import pandas as pd
import networkx as nx
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="GraphRAG Chat Q&A", page_icon="💬", layout="wide")

st.title("💬 Dynamic GraphRAG Natural Language Q&A")
st.markdown("Query your supply chain knowledge graph conversationally. The engine dynamically traverses the network to retrieve local contexts and synthesize answers.")

# Load data and build graph with caching for performance
@st.cache_resource
def load_graph():
    input_path = "data/supply_chain.xlsx"
    if not os.path.exists(input_path):
        return None
    
    df_suppliers = pd.read_excel(input_path, sheet_name="Suppliers")
    df_shipments = pd.read_excel(input_path, sheet_name="Shipments")
    df_incidents = pd.read_excel(input_path, sheet_name="Incidents")
    
    G = nx.Graph()
    for _, row in df_suppliers.iterrows():
        G.add_node(row["SupplierID"], type="Supplier", name=row["SupplierName"], region=row["Region"], risk=row["RiskRating"])
    for _, row in df_shipments.iterrows():
        shp_id, sup_id, wh, mat = row["ShipmentID"], row["SupplierID"], row["Warehouse"], row["MaterialCategory"]
        G.add_node(shp_id, type="Shipment", material=mat, delay=row["TransitDelayDays"], incident_flag=row["IncidentReported"])
        G.add_node(wh, type="Warehouse")
        G.add_edge(sup_id, shp_id, relation="SUPPLIES_SHIPMENT")
        G.add_edge(shp_id, wh, relation="DELIVERED_TO")
    for _, row in df_incidents.iterrows():
        inc_id, shp_id = row["IncidentID"], row["ShipmentID"]
        G.add_node(inc_id, type="Incident", root_cause=row["RootCause"], financial_impact=row["FinancialImpactUSD"])
        G.add_edge(shp_id, inc_id, relation="HAS_INCIDENT")
    return G

G = load_graph()

if G is None:
    st.error("Supply chain Excel file not found. Please ensure `data/supply_chain.xlsx` exists.")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box
if prompt := st.chat_input("e.g., Which suppliers are connected to WH-West and experienced transit delays?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Traversing graph network & synthesizing answer..."):
            # Dynamic graph entity matching based on prompt words
            relevant_nodes = set()
            for node, data in G.nodes(data=True):
                if any(term.lower() in str(node).lower() or term.lower() in str(val).lower() for term in prompt.split() for val in data.values()):
                    relevant_nodes.add(node)
            
            # Fallback or neighborhood expansion
            if not relevant_nodes:
                context_text = "General Network Sample: " + str(list(G.nodes(data=True))[:15])
            else:
                expanded_nodes = set(relevant_nodes)
                for n in relevant_nodes:
                    expanded_nodes.update(G.neighbors(n))
                
                context_lines = ["Localized Graph Neighborhood Context:"]
                for n in expanded_nodes:
                    context_lines.append(f"- Node [{n}]: Attributes={dict(G.nodes[n])}, Connected Relations={[nbr for nbr in G.neighbors(n)]}")
                context_text = "\n".join(context_lines)

            full_prompt = f"""
            You are an expert Enterprise Supply Chain GraphRAG assistant. Answer the user query thoroughly and accurately using ONLY the provided localized Knowledge Graph neighborhood context.

            {context_text}

            User Query: {prompt}
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.2
                )
                answer = response.choices[0].message.content.strip()
            except Exception as e:
                answer = f"Error communicating with OpenAI: {str(e)}"

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})