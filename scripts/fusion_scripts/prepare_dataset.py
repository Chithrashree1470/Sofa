import pandas as pd

# Read Fusion component map
data = pd.read_csv("fusion_component_map.csv")
data = data.dropna(how="all")

# Create dictionary: component name -> quantity
quantities = dict(zip(data["component_name"], data["quantity"]))

# Automatically get quantities
sofa_data = {
    "sofa_type": "3_Seater",
    "wood_frame_qty": quantities.get("Wood Frame", 0),
    "plywood_qty": quantities.get("Plywood", 0),
    "spring_qty": quantities.get("Springs", 0),
    "clip_qty": quantities.get("Clips", 0),
    "seat_belt_qty": quantities.get("Seat Belts", 0),
    "back_rest_belt_qty": quantities.get("Back Rest Belts", 0),
    "foam_qty": quantities.get("Foam", 0),
    "handle_foam_qty": quantities.get("Handle Foam", 0),
    "fabric_qty": quantities.get("Fabric", 0),
    "handle_frame_qty": quantities.get("Handle Frame", 0),
    "total_cost": 0
}

# Convert into DataFrame
new_row = pd.DataFrame([sofa_data])

# Save dataset
new_row.to_csv("sofa_cost_dataset.csv", index=False)

print("Fusion quantities extracted automatically!")
print(new_row)