import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="GraphRAG Risk Analysis", page_icon="🤖", layout="wide")

st.title("🤖 GraphRAG Systemic Risk & Mitigation Dashboard")

output_path = "data/risk_analysis_output.xlsx"

if os.path.exists(output_path):
    df_results = pd.read_excel(output_path)
    
    st.success("Loaded pre-computed GraphRAG analysis report successfully!")
    
    # Summary Metrics
    high_risk_count = len(df_results[df_results["InitialRisk"] == "High"])
    st.metric("High-Risk Suppliers Identified", high_risk_count)
    
    st.subheader("Detailed Supplier GraphRAG Assessment")
    st.dataframe(df_results, use_container_width=True)
    
    with open(output_path, "rb") as f:
        st.download_button(
            label="📥 Download Styled Executive Report (.xlsx)",
            data=f,
            file_name="risk_analysis_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.gm"
        )
else:
    st.warning("Analysis output file not found. Please run your `analytics_engine.py` script to generate the insights first.")