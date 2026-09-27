import os
import pandas as pd

os.makedirs("data", exist_ok=True)

# 1. Suppliers (Expanded)
df_suppliers = pd.DataFrame({
    "SupplierID": ["SUP-001", "SUP-002", "SUP-003", "SUP-004", "SUP-005", "SUP-006", "SUP-007"],
    "SupplierName": ["Apex Chemicals", "Boral Logistics", "Zenith Solvents", "Delta Packaging", "Nova Polymers", "Vanguard Steel", "Pacific Oils"],
    "Region": ["North America", "Europe", "Asia-Pacific", "North America", "Asia-Pacific", "Europe", "Asia-Pacific"],
    "RiskRating": ["Low", "Medium", "High", "Low", "Medium", "High", "Low"],
    "PrimaryContact": ["john@apex.com", "sarah@boral.com", "chen@zenith.com", "mike@delta.com", "priya@nova.com", "lars@vanguard.com", "mei@pacific.com"]
})

# 2. Shipments & Routes (Expanded)
df_shipments = pd.DataFrame({
    "ShipmentID": ["SHP-101", "SHP-102", "SHP-103", "SHP-104", "SHP-105", "SHP-106", "SHP-107", "SHP-108"],
    "SupplierID": ["SUP-001", "SUP-002", "SUP-003", "SUP-001", "SUP-004", "SUP-005", "SUP-006", "SUP-007"],
    "MaterialCategory": ["Bulk Chemical", "Solvents", "Specialty Additives", "Bulk Chemical", "Packaging", "Polymers", "Raw Metals", "Lubricants"],
    "Warehouse": ["WH-East", "WH-West", "WH-Central", "WH-West", "WH-East", "WH-Central", "WH-West", "WH-East"],
    "TransitDelayDays": [2, 7, 14, 1, 3, 9, 12, 0],
    "IncidentReported": ["No", "Yes", "Yes", "No", "No", "Yes", "Yes", "No"]
})

# 3. Incident Logs (Expanded)
df_incidents = pd.DataFrame({
    "IncidentID": ["INC-501", "INC-502", "INC-503", "INC-504", "INC-505"],
    "ShipmentID": ["SHP-102", "SHP-103", "SHP-106", "SHP-107", "SHP-102"],
    "RootCause": ["Customs Clearance Delay", "Port Congestion & Labor Strike", "Raw Material Shortage at Plant", "Severe Weather / Typhoon", "Documentation Error"],
    "FinancialImpactUSD": [12500, 45000, 28000, 62000, 8500]
})

# 4. Inventory Levels (Expanded)
df_inventory = pd.DataFrame({
    "Warehouse": ["WH-East", "WH-West", "WH-Central"],
    "SafetyStockUnits": [5000, 8000, 6500],
    "CurrentStockUnits": [4200, 3100, 7000],
    "StockoutRisk": ["Medium", "High", "Low"]
})

# 5. Transport Routes (Expanded)
df_routes = pd.DataFrame({
    "RouteID": ["RT-01", "RT-02", "RT-03", "RT-04", "RT-05"],
    "OriginRegion": ["North America", "Europe", "Asia-Pacific", "North America", "Europe"],
    "DestinationWarehouse": ["WH-East", "WH-West", "WH-Central", "WH-West", "WH-East"],
    "BaseFreightCostUSD": [1200, 4500, 6800, 2100, 4900]
})

# 6. NEW SHEET: Procurement Contracts & SLA Terms
df_contracts = pd.DataFrame({
    "SupplierID": ["SUP-001", "SUP-002", "SUP-003", "SUP-004", "SUP-005", "SUP-006", "SUP-007"],
    "ContractType": ["Exclusive", "Preferred", "Standard", "Preferred", "Exclusive", "Standard", "Preferred"],
    "SLA_AllowedDelayDays": [3, 5, 2, 4, 3, 5, 4],
    "PenaltyClauseActive": ["No", "Yes", "Yes", "No", "No", "Yes", "No"]
})

# Save to Excel with 6 sheets
output_path = "data/supply_chain.xlsx"
with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    df_suppliers.to_excel(writer, sheet_name="Suppliers", index=False)
    df_shipments.to_excel(writer, sheet_name="Shipments", index=False)
    df_incidents.to_excel(writer, sheet_name="Incidents", index=False)
    df_inventory.to_excel(writer, sheet_name="InventoryLevels", index=False)
    df_routes.to_excel(writer, sheet_name="TransportRoutes", index=False)
    df_contracts.to_excel(writer, sheet_name="ContractTerms", index=False)

print(f"Successfully generated expanded dataset with 6 sheets at: {output_path}")