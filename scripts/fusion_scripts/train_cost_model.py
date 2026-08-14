import pandas as pd

# Load sofa dataset
data = pd.read_csv("sofa_cost_dataset.csv")

print("Sofa Cost Dataset:")
print(data)

print("\nNumber of sofa records:", len(data))

# Check whether enough real cost data is available
valid_data = data[data["total_cost"] > 0]

if len(valid_data) < 10:
    print("\nNot enough real cost data to train the model.")
    print("Collect more sofa designs with their actual total costs.")
else:
    print("\nDataset is ready for model training.")