import streamlit as st

st.set_page_config(
    page_title="Enterprise GraphRAG Hub",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Enterprise GraphRAG Intelligence Hub")
st.markdown("""
Welcome to the **Supply Chain GraphRAG & Network Analytics** system. This platform bridges relational Excel sheets with advanced Graph Knowledge Networks and OpenAI reasoning.

### Available Modules:
1. **Network Explorer (`pages/1_Network_Explorer.py`):** Inspect raw data sheets, view network metrics, and check structural graph connectivity.
2. **GraphRAG Analysis (`pages/2_GraphRAG_Analysis.py`):** Review localized graph-neighborhood insights, systemic risk summaries, and download the styled executive Excel report.

*Use the sidebar navigation to switch between pages.*
""")