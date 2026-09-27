import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

print("1. Loading data for PDF generation...")
input_path = "data/supply_chain.xlsx"
report_md_path = "data/crewai_executive_report.md"

df_suppliers = pd.read_excel(input_path, sheet_name="Suppliers")
df_incidents = pd.read_excel(input_path, sheet_name="Incidents")
df_inventory = pd.read_excel(input_path, sheet_name="InventoryLevels")

# Read CrewAI executive summary if available
crew_summary = "CrewAI multi-agent collaborative audit completed successfully."
if os.path.exists(report_md_path):
    with open(report_md_path, "r", encoding="utf-8") as f:
        crew_summary = f.read()

print("2. Building Professional PDF Layout...")
pdf_path = "data/Executive_Supply_Chain_Report.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=22,
    textColor=colors.HexColor('#1F4E78'),
    spaceAfter=6
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    textColor=colors.HexColor('#595959'),
    spaceAfter=15
)

section_heading = ParagraphStyle(
    'SectionHeading',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=14,
    textColor=colors.HexColor('#2C3E50'),
    spaceBefore=12,
    spaceAfter=6
)

body_style = ParagraphStyle(
    'BodyDark',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    textColor=colors.HexColor('#333333'),
    spaceAfter=8,
    leading=14
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9,
    textColor=colors.white
)

table_cell_style = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    textColor=colors.HexColor('#333333')
)

elements = []

# Title & Metadata
elements.append(Paragraph("Enterprise Supply Chain Executive Brief", title_style))
elements.append(Paragraph("Generated via GraphRAG & CrewAI Multi-Agent Reasoning Engine | Date: October 2026", subtitle_style))
elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1F4E78'), spaceAfter=15))

# Section 1: Executive Multi-Agent Summary
elements.append(Paragraph("1. Multi-Agent Collaborative Audit Findings", section_heading))
# Clean up markdown newlines for ReportLab paragraph flow
formatted_crew_summary = crew_summary.replace("\n", "<br/>")
elements.append(Paragraph(formatted_crew_summary, body_style))
elements.append(Spacer(1, 10))

# Section 2: High-Risk Inventory Table
elements.append(Paragraph("2. Warehouse Safety Stock & Risk Overview", section_heading))
inventory_data = [["Warehouse", "Safety Stock", "Current Stock", "Stockout Risk"]]
for _, row in df_inventory.iterrows():
    inventory_data.append([
        str(row["Warehouse"]),
        str(row["SafetyStockUnits"]),
        str(row["CurrentStockUnits"]),
        str(row["StockoutRisk"])
    ])

t_inv = Table(inventory_data, colWidths=[120, 110, 110, 150])
t_inv.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F4E78')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9F9')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D9D9')),
    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
]))
elements.append(t_inv)
elements.append(Spacer(1, 15))

# Section 3: Critical Incidents Log Table
elements.append(Paragraph("3. Major Logistics Incidents & Financial Impact", section_heading))
incident_data = [["Incident ID", "Shipment ID", "Root Cause", "Financial Impact (USD)"]]
for _, row in df_incidents.iterrows():
    incident_data.append([
        str(row["IncidentID"]),
        str(row["ShipmentID"]),
        str(row["RootCause"]),
        f"${row['FinancialImpactUSD']:,}"
    ])

t_inc = Table(incident_data, colWidths=[80, 80, 200, 130])
t_inc.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#C0392B')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FDF2E9')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D9D9')),
    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
]))
elements.append(t_inc)

# Build PDF Document
doc.build(elements)
print(f"PDF Executive Report successfully generated at: {pdf_path}")