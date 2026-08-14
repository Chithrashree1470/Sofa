# import pandas as pd

# # Read both CSV files
# fusion_data = pd.read_csv("fusion_component_map.csv")
# material_data = pd.read_csv("material_cost.csv")

# # Remove empty rows
# fusion_data = fusion_data.dropna(how="all")
# material_data = material_data.dropna(how="all")

# # Keep material information without its quantity
# material_info = material_data[
#     ["component_name", "material", "unit", "unit_cost"]
# ]

# # Connect Fusion components with their materials
# final_data = pd.merge(
#     fusion_data,
#     material_info,
#     on="component_name",
#     how="left"
# )

# # Convert unit cost to number
# final_data["unit_cost"] = pd.to_numeric(
#     final_data["unit_cost"],
#     errors="coerce"
# ).fillna(0)

# # Calculate cost
# final_data["total_cost"] = (
#     final_data["quantity"] * final_data["unit_cost"]
# )

# # Save result
# final_data.to_csv("final_cost_output.csv", index=False)

# print(final_data)

# print("\nTotal Sofa Cost:", final_data["total_cost"].sum())
# print("Final output saved as final_cost_output.csv")

from pathlib import Path
import pandas as pd

# Folder where this script is located
BASE_DIR = Path(__file__).parent

# Read both CSV files
fusion_data = pd.read_csv(BASE_DIR / "fusion_component_map.csv")
material_data = pd.read_csv(BASE_DIR / "material_cost.csv")

# Remove empty rows
fusion_data = fusion_data.dropna(how="all")
material_data = material_data.dropna(how="all")

# Keep material information without its quantity
material_info = material_data[
    ["component_name", "material", "unit", "unit_cost"]
]

# Connect Fusion components with their materials
final_data = pd.merge(
    fusion_data,
    material_info,
    on="component_name",
    how="left"
)

# Convert unit cost to number
final_data["unit_cost"] = pd.to_numeric(
    final_data["unit_cost"],
    errors="coerce"
).fillna(0)

# Calculate cost
final_data["total_cost"] = (
    final_data["quantity"] * final_data["unit_cost"]
)

# Save result in the same folder as this script
output_file = BASE_DIR / "final_cost_output.csv"
final_data.to_csv(output_file, index=False)

print(final_data)

print("\nTotal Sofa Cost:", final_data["total_cost"].sum())
print(f"Final output saved as: {output_file}")