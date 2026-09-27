import os
import pandas as pd
import networkx as nx
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing in your .env file.")

# Configure LLM for CrewAI using gpt-4o-mini
llm = LLM(model="gpt-4o-mini", temperature=0.2, api_key=api_key)

print("1. Loading expanded multi-sheet supply chain data...")
input_path = "data/supply_chain.xlsx"
df_suppliers = pd.read_excel(input_path, sheet_name="Suppliers")
df_shipments = pd.read_excel(input_path, sheet_name="Shipments")
df_incidents = pd.read_excel(input_path, sheet_name="Incidents")
df_inventory = pd.read_excel(input_path, sheet_name="InventoryLevels")
df_routes = pd.read_excel(input_path, sheet_name="TransportRoutes")
df_contracts = pd.read_excel(input_path, sheet_name="ContractTerms")

# Quick context summarization for agents
data_context = f"""
SUPPLIERS COUNT: {len(df_suppliers)}
TOTAL SHIPMENTS: {len(df_shipments)}
TOTAL INCIDENTS: {len(df_incidents)}
INVENTORY STATUS: {df_inventory.to_string()}
CONTRACT TERMS: {df_contracts.to_string()}
INCIDENTS DATA: {df_incidents.to_string()}
"""

print("2. Defining Specialized CrewAI Agents...")

# Agent 1: Logistics & Route Specialist
logistics_agent = Agent(
    role='Senior Logistics & Network Route Specialist',
    goal='Analyze transit delays, route costs, warehouse inventory risks, and bottlenecks across the supply chain.',
    backstory="You are an expert operations researcher who specializes in spotting structural friction, high transit delay corridors, and warehouse stockout vulnerabilities.",
    verbose=True,
    llm=llm,
    allow_delegation=False
)

# Agent 2: Financial Risk & SLA Analyst
risk_agent = Agent(
    role='Financial Risk & Contract Compliance Analyst',
    goal='Evaluate incident financial losses, supplier risk ratings, and contractual SLA penalty clauses.',
    backstory="You audit supply chain vendors for financial exposure, reviewing root-cause incident losses and ensuring suppliers comply with agreed SLA delay limits.",
    verbose=True,
    llm=llm,
    allow_delegation=False
)

# Agent 3: Chief Supply Chain Officer (Synthesizer)
strategist_agent = Agent(
    role='Chief Supply Chain Strategist',
    goal='Synthesize logistics bottlenecks and financial risk reports into an executive mitigation action plan.',
    backstory="You lead global supply chain resilience, combining operational insights and financial risk metrics to deliver crystal-clear executive strategy.",
    verbose=True,
    llm=llm,
    allow_delegation=False
)

print("3. Defining Collaborative Tasks...")

task_logistics = Task(
    description=f"Examine the inventory levels, transport routes, and shipment delays from this data summary:\n{data_context}\nIdentify the most vulnerable warehouses and high-delay transport paths.",
    expected_output="A detailed logistics bottleneck report highlighting high-risk warehouses and transit bottlenecks.",
    agent=logistics_agent
)

task_risk = Task(
    description=f"Examine the supplier risk ratings, incident financial impacts, and contract SLA penalty terms from this summary:\n{data_context}\nIdentify which suppliers are violating SLAs and causing excessive financial loss.",
    expected_output="A financial risk assessment detailing vendor violations, incident costs, and contract liabilities.",
    agent=risk_agent
)

task_strategy = Task(
    description="Review the reports from the Logistics Specialist and Financial Risk Analyst. Combine their findings into a structured executive recommendation report outlining immediate vendor interventions and inventory rebalancing.",
    expected_output="A comprehensive executive action plan formatted with clear bullet points and remediation strategies.",
    agent=strategist_agent
)

# Form the Crew
supply_chain_crew = Crew(
    agents=[logistics_agent, risk_agent, strategist_agent],
    tasks=[task_logistics, task_risk, task_strategy],
    process=Process.sequential,
    verbose=True
)

print("4. Launching Multi-Agent Collaborative Reasoning Workflow...")
result = supply_chain_crew.kickoff()

print("\n================== CREWAI EXECUTION RESULT ==================\n")
print(result)

# Save result to a text/markdown file for executive review
output_report_path = "data/crewai_executive_report.md"
with open(output_report_path, "w", encoding="utf-8") as f:
    f.write(str(result))

print(f"\nExecutive report successfully saved to: {output_report_path}")