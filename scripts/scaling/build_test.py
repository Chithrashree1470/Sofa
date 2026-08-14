#used to build new step file its a test of concept.
import os
import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(
    CURRENT_DIR,
    "test_sofa.csv",
)

OUTPUT_STEP = os.path.join(
    CURRENT_DIR,
    "scaled_step.step",
)

# ---------------------------------------------------------
# Template Sofa Dimensions
# ---------------------------------------------------------

TEMPLATE_LENGTH = 110.0
TEMPLATE_DEPTH = 70.0
TEMPLATE_HEIGHT = 40.0

# ---------------------------------------------------------
# User Input
# ---------------------------------------------------------

print("\n========== TARGET SOFA ==========\n")

user_length = float(input("Overall Length (mm): "))
user_depth = float(input("Overall Depth (mm): "))
user_height = float(input("Overall Height (mm): "))

SL = user_length / TEMPLATE_LENGTH
SD = user_depth / TEMPLATE_DEPTH
SH = user_height / TEMPLATE_HEIGHT

print("\nScale Factors")
print(f"Length Scale : {SL:.4f}")
print(f"Depth  Scale : {SD:.4f}")
print(f"Height Scale : {SH:.4f}")

# ---------------------------------------------------------
# Read CSV
# ---------------------------------------------------------
import cadquery as cq
df = pd.read_csv(CSV_FILE)
print(df["body"])

# ---------------------------------------------------------
# Create Assembly
# ---------------------------------------------------------

assembly = cq.Assembly()

# ---------------------------------------------------------
# Build Bodies
# ---------------------------------------------------------

for _, row in df.iterrows():

    body = row["body"]

    L = float(row["L_mm"])
    W = float(row["W_mm"])
    H = float(row["H_mm"])

    cx = float(row["center_x_mm"])
    cy = float(row["center_y_mm"])
    cz = float(row["center_z_mm"])

    # -----------------------------------------------------
    # Phase 1 Scaling Rules
    # -----------------------------------------------------

    if body == "seat":

        L *= SL
        W *= SD
        # H unchanged

    elif body == "backrest":

        L *= SL
        H *= SH
        # W unchanged

    elif "arm" in body:

        # Armrests remain unchanged
        pass

    # -----------------------------------------------------
    # Build Box
    #
    # Convention:
    # X = Length
    # Y = Height
    # Z = Depth
    # -----------------------------------------------------

    solid = (
        cq.Workplane("XY")
        .box(
            L,
            H,
            W,
            centered=(True, True, True),
        )
        .translate((cx, cy, cz))
    )

    assembly.add(
        solid,
        name=body,
    )

    print(
        f"{body:15s}"
        f"L={L:7.2f}"
        f" W={W:7.2f}"
        f" H={H:7.2f}"
    )

# ---------------------------------------------------------
# Export STEP
# ---------------------------------------------------------

assembly.save(
    OUTPUT_STEP,
    exportType="STEP",
)

print("\n===================================")
print("Scaled STEP generated successfully!")
print(OUTPUT_STEP)
print("===================================")