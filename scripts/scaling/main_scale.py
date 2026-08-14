"""
Main pipeline for STEP processing.
"""
from dotenv import load_dotenv
import os
from body_names import get_step_body_names
from step_reader import read_step
from assembly_parser import get_reference_shape
from body_extractor import extract_solids
from scaling_pipeline import process_dimension
from step_reader import load_metadata
from scale_step import (
    scale_body,
    get_logical_dimension,
)
from step_reader import (
    read_step,
    load_metadata,
    get_template_frame,
    get_assembly_dimensions,
    get_body_dimensions,
    get_category_dimensions,
    get_body_axis_map,
    print_global_length_bounds,
    get_body_global_dimensions,
)
from bbox_engine import (
    compute_bbox,
    compute_obb,
    print_bbox,
    print_obb,
)

from scale_step import (
    scale_body,
    get_logical_dimension,
)

from position_engine import (
    get_overlap,
    move_body,
    vector_between,
    get_obb,
    projection_on_axis,
    classify_attachment,
)

from export_step import export_step

load_dotenv()
load_dotenv()

STEP_FILE = os.getenv("STEP_FILE")
OUTPUT_STEP = os.getenv("OUTPUT_STEP")
METADATA_FILE = os.getenv("METADATA_FILE")

metadata = load_metadata(METADATA_FILE)
print("\n========== PATH CONFIGURATION ==========")
print("STEP_FILE     :", STEP_FILE)
print("OUTPUT_STEP   :", OUTPUT_STEP)
print("METADATA_FILE :", METADATA_FILE)

if not os.path.exists(STEP_FILE):
    raise FileNotFoundError(
        f"STEP file not found:\n{STEP_FILE}"
    )

if not os.path.exists(METADATA_FILE):
    raise FileNotFoundError(
        f"Metadata file not found:\n{METADATA_FILE}"
    )

print("All required input paths exist.")

print(type(metadata))
print(metadata)
SCALING_RULES = {
    "length": ["seat"],
    "width": ["seat", "armrest"],
    "height": ["backrest"],
}
def main():

    body_names = get_step_body_names(STEP_FILE)

    # print("\nBodies found:")

    # for i, name in enumerate(body_names, start=1):
    #     print(f"{i}. {name}")

    shape_tool = read_step(STEP_FILE)

    shape = get_reference_shape(shape_tool)

    solids = extract_solids(shape)
    print("\nSeat Body OBB Axes")

    for solid, body_name in zip(solids, body_names):

        if body_name in metadata["seat"]:

            obb = compute_obb(solid)
            axis_map = get_body_axis_map(obb)

            print("Axis Mapping:")
            print(axis_map)

            print("OBB Sizes:")
            print(
                "X:", 2 * obb.XHSize(),
                "Y:", 2 * obb.YHSize(),
                "Z:", 2 * obb.ZHSize()
            )

            print(f"\n{body_name}")

            print(
                "X:",
                obb.XDirection().X(),
                obb.XDirection().Y(),
                obb.XDirection().Z()
            )

            print(
                "Y:",
                obb.YDirection().X(),
                obb.YDirection().Y(),
                obb.YDirection().Z()
            )

            print(
                "Z:",
                obb.ZDirection().X(),
                obb.ZDirection().Y(),
                obb.ZDirection().Z()
            )
    assembly_dimensions = get_assembly_dimensions(
        solids,
    )

    print("\nCurrent Assembly Dimensions")

    for k, v in assembly_dimensions.items():
        print(f"{k}: {v:.2f}")
    

    # ---------------------------------------
    # Find seat category
    # ---------------------------------------
    print("\nDEBUG BODY NAME MAPPING")

    for solid, body_name in zip(solids, body_names):
        print("BODY:", body_name)
    seat_shape = None

    for solid, body_name in zip(solids, body_names):

        if body_name =="seat":
            seat_shape = solid
            break

    print("\nDEBUG seat_shape:")
    print(seat_shape)
    print("seat_shape is None:", seat_shape is None)
    seat_obb = compute_obb(seat_shape)
    template_frame = get_template_frame(
        seat_shape,
    )
    for category in metadata:

        dimensions = get_category_dimensions(
            category,
            metadata,
            solids,
            body_names,
            template_frame,
        )

        print(f"\n{category.upper()}")

        for k, v in dimensions.items():
            print(f"{k}: {v:.2f}")

    seat_body_dimensions = get_body_dimensions(
        "seat",
        metadata,
        solids,
        body_names,
    )

    print("\nSeat Body Dimensions")

    for body_name, dimensions in seat_body_dimensions.items():

        print(f"\n{body_name}")

        for dimension, value in dimensions.items():
            print(f"{dimension}: {value:.2f}")
    
    seat_dimensions = get_category_dimensions(
    "seat",
    metadata,
    solids,
    body_names,
    template_frame,
)

    # ---------------------------------------
    # User input
    # ---------------------------------------

    target_length = float(input("Target Length (mm): "))
    target_width = float(input("Target Width (mm): "))
    target_height = float(input("Target Height (mm): "))

     # ---------------------------------------
# Calculate target seat length
# ---------------------------------------
# The final assembly length is:
#
#   left arm + seat + right arm
#
# The armrests are positioned outside the seat.
# Therefore the seat must occupy only the
# remaining length.

    left_arm_length = None
    right_arm_length = None

    for solid, body_name in zip(solids, body_names):

        if body_name in ("left_arm", "right_arm"):

            box = compute_bbox(solid)

            xmin, ymin, zmin, xmax, ymax, zmax = box.Get()

            arm_length = xmax - xmin

            if body_name == "left_arm":
                left_arm_length = arm_length

            elif body_name == "right_arm":
                right_arm_length = arm_length


    if left_arm_length is None or right_arm_length is None:
        raise ValueError(
        "Could not determine left/right armrest lengths."
    )


    target_seat_length = (
        target_length
        - left_arm_length
        - right_arm_length
)

    if target_seat_length <= 0:
        raise ValueError(
        "Target length is too small for the current armrests."
    )


    length_factor = (
        target_seat_length
    / seat_dimensions["length"]
)

    print("\nLength Calculation")

    print(f"Current Seat Length : {seat_dimensions['length']:.2f} mm")
    print(f"Left Arm Length     : {left_arm_length:.2f} mm")
    print(f"Right Arm Length    : {right_arm_length:.2f} mm")

    print(f"Target Assembly     : {target_length:.2f} mm")
    print(f"Target Seat Length  : {target_seat_length:.2f} mm")
    width_factor = target_width / seat_dimensions["width"]
    height_factor = target_height / seat_dimensions["height"]

    print("\nScale Factors")
    print(f"Length : {length_factor:.3f}")
    print(f"Width  : {width_factor:.3f}")
    print(f"Height : {height_factor:.3f}")

    processed_solids = solids

    factors = {
        "length": length_factor,
        "width": width_factor,
        "height": height_factor,
    }

    for logical_dimension in [
        "length",
        "width",
        "height",
    ]:

        for category in SCALING_RULES[logical_dimension]:
            targets = {
                "length": target_length,
                "width": target_width,
                "height": target_height,
            }
            category_dimensions = get_category_dimensions(
                category,
                metadata,
                processed_solids,
                body_names,
                template_frame,
            )

            if logical_dimension == "length" and category == "seat":
                factor = length_factor
            else:
                factor = (
                    targets[logical_dimension]
                    /
                    category_dimensions[logical_dimension]
                )
            print_global_length_bounds(
                processed_solids,
                body_names,
            )
            processed_solids = process_dimension(
                solids=processed_solids,
                body_names=body_names,
                logical_dimension=logical_dimension,
                factor=factor,
                reference_category=category,
                metadata=metadata,
                target_length=target_length,
            )
            print_global_length_bounds(
                processed_solids,
                body_names,
            )
            

            # ----------------------------------------------------
# FINAL DIMENSIONS
# ----------------------------------------------------

            final_dimensions = get_assembly_dimensions(
            processed_solids
)

            print("\n" + "=" * 60)
            print("FINAL ASSEMBLY DIMENSIONS")
            print("=" * 60)

            print(
    f"Length : {final_dimensions['length']:.2f} mm"
)

            print(
    f"Width  : {final_dimensions['width']:.2f} mm"
)

            print(
    f"Height : {final_dimensions['height']:.2f} mm"
)

            print("\nTARGET DIMENSIONS")

            print(
    f"Length : {target_length:.2f} mm"
)

            print(
    f"Width  : {target_width:.2f} mm"
)

            print(
    f"Height : {target_height:.2f} mm"
)

            print("\nDIMENSION ERROR")

            print(
    f"Length Error : "
    f"{final_dimensions['length'] - target_length:.2f} mm"
)

            print(
    f"Width Error  : "
    f"{final_dimensions['width'] - target_width:.2f} mm"
)

            print(
    f"Height Error : "
    f"{final_dimensions['height'] - target_height:.2f} mm"
)

            print("=" * 60)

    # ----------------------------------------------------
    # Export STEP
    # ----------------------------------------------------

    export_step(
        processed_solids,
        OUTPUT_STEP,
    )


if __name__ == "__main__":
    main()