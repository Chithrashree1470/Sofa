import pandas as pd

# Read the component CSV file
data = pd.read_csv("fusion_component_map.csv")

# Remove empty rows
data = data.dropna(how="all")

print("SOFA COMPONENT ANALYSIS")
print("-----------------------")

# Display each component and quantity
for index, row in data.iterrows():
    print(
        row["component_name"],
        "- Quantity:",
        row["quantity"]
    )

# Calculate total quantity
total = data["quantity"].sum()

print("-----------------------")
print("Total Components:", total)