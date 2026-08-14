import pandas as pd

# -----------------------------
# 1. Read material cost data
# -----------------------------
data = pd.read_csv("material_cost.csv")

# Remove completely empty rows
data = data.dropna(how="all")

# -----------------------------
# 2. Convert values to numbers
# -----------------------------
data["unit_cost"] = pd.to_numeric(
    data["unit_cost"],
    errors="coerce"
).fillna(0)

data["quantity"] = pd.to_numeric(
    data["quantity"],
    errors="coerce"
).fillna(0)

# -----------------------------
# 3. Calculate component cost
# -----------------------------
data["total_cost"] = (
    data["unit_cost"] * data["quantity"]
)

# -----------------------------
# 4. Calculate total sofa cost
# -----------------------------
total_sofa_cost = data["total_cost"].sum()

# -----------------------------
# 5. Save component cost output
# -----------------------------
data.to_csv(
    "final_cost_output.csv",
    index=False
)

# -----------------------------
# 6. Update sofa dataset
# -----------------------------
sofa_dataset = pd.read_csv(
    "sofa_cost_dataset.csv"
)

# Remove empty rows
sofa_dataset = sofa_dataset.dropna(how="all")

# Update total cost of the first sofa
sofa_dataset.loc[0, "total_cost"] = total_sofa_cost

# Save updated sofa dataset
sofa_dataset.to_csv(
    "sofa_cost_dataset.csv",
    index=False
)

# -----------------------------
# 7. Display results
# -----------------------------
print("Component Cost Details:")
print(data)

print(
    "\nTotal Sofa Cost: Rs.",
    total_sofa_cost
)

print(
    "\nSofa cost dataset updated successfully!"
)

print(
    "Final cost output saved successfully!"
)