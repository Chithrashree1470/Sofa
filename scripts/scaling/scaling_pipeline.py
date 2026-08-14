#this is scaling_pipeline
from bbox_engine import (
    compute_obb,
    print_bbox,
)
from OCP.gp import gp_Vec, gp_Pnt
from step_reader import get_category_bounds
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
    make_compound,
    get_bounds,
)

SCALING_RULES = {
    "length": [
        "seat",
    ],
    "width": [
        "seat",
        "armrest",
    ],
    "height": [
        "backrest",
    ],
}

def get_armrest_side(body_name):

    name = body_name.lower().replace(" ", "_")

    if name in ("left_arm", "left_armrest"):
        return "left"

    if name in ("right_arm", "right_armrest"):
        return "right"

    return None

def get_global_attachment(reference_shape, body_shape):
    """
    Determine which global direction the body lies from
    the reference category.

    Global convention:
        X = length
        Z = width
        Y = height
    """

    ref_obb = get_obb(reference_shape)
    body_obb = get_obb(body_shape)

    ref = ref_obb.Center()
    body = body_obb.Center()

    dx = body.X() - ref.X()
    dy = body.Y() - ref.Y()
    dz = body.Z() - ref.Z()

    values = {
        "length": dx,
        "width": dz,
        "height": dy,
    }

    logical_dimension = max(
        values,
        key=lambda k: abs(values[k])
    )

    value = values[logical_dimension]

    sign = "+" if value >= 0 else "-"

    return sign, logical_dimension

def belongs_to_category(body_name, category):

    name = body_name.lower().replace(" ", "_")

    if category == "seat":
        return name == "seat"

    if category == "backrest":
        return name == "backrest"

    if category == "armrest":
        return name in ("left_arm", "right_arm", "left_armrest", "right_armrest")

    return False

def process_dimension(
    solids,
    body_names,
    logical_dimension,
    factor,
    metadata,
    target_length=None,
    reference_category="seat",
):
    old_reference_bounds = get_category_bounds(
        reference_category,
        metadata,
        solids,
        body_names,
    )       
    processed_solids = []
    scaled_reference_bodies = {}

    all_bodies = []

    reference_shapes = []
    reference_shape = None
    reference_scale_info = None

   

    # ----------------------------------------------------
    # Process all bodies
    # ----------------------------------------------------

    for solid, body_name in zip(solids, body_names):

        # print("\n" + "=" * 60)
        # print(body_name)

        # print_bbox(
        #     body_name,
        #     bbox,
        # )

        obb = compute_obb(solid)

        # print_obb(
        #     body_name,
        #     obb,
        # )
        # print(f"\n{body_name}")
        # print("X:", obb.XDirection().X(), obb.XDirection().Y(), obb.XDirection().Z())
        # print("Y:", obb.YDirection().X(), obb.YDirection().Y(), obb.YDirection().Z())
        # print("Z:", obb.ZDirection().X(), obb.ZDirection().Y(), obb.ZDirection().Z())

        if belongs_to_category(body_name, reference_category):

            solid, scale_info = scale_body(
                solid=solid,
                obb=obb,
                body_name=reference_category,
                logical_dimension=logical_dimension,
                factor=factor,
            )

            scaled_reference_bodies[body_name] = solid

            reference_shapes.append(solid)

            if reference_scale_info is None:
                reference_scale_info = scale_info


        all_bodies.append(
            {
                "name": body_name,
                "shape": solid,
            }
        )

        processed_solids.append(solid)
    new_reference_bounds = get_category_bounds(
        reference_category,
        metadata,
        processed_solids,
        body_names,
    )

    # -----------------------------------------
    # Calculate ACTUAL growth
    # -----------------------------------------

    old_xmin, old_ymin, old_zmin, old_xmax, old_ymax, old_zmax = old_reference_bounds

    new_xmin, new_ymin, new_zmin, new_xmax, new_ymax, new_zmax = new_reference_bounds


    growth = {
        "length": (new_xmax - new_xmin) - (old_xmax - old_xmin),
        "width":  (new_zmax - new_zmin) - (old_zmax - old_zmin),
        "height": (new_ymax - new_ymin) - (old_ymax - old_ymin),
    }

    # print("\nOverlap :", overlap)
    reference_shape = make_compound(reference_shapes)

    # ----------------------------------------------------
    # Build attachment map
    # ----------------------------------------------------

    attachment_map = []

    for body in all_bodies:

        if belongs_to_category(body["name"], reference_category):
            continue

        sign, logical = get_global_attachment(
            reference_shape,
            body["shape"],
        )

        attachment_map.append(
            {
                "name": body["name"],
                "shape": body["shape"],
                "attachment": f"{sign}{logical}",
            }
        )  
    # print("\nAttachment Map")

    # for item in attachment_map:

    #     print(
    #         item["name"],
    #         "->",
    #         item["attachment"],
    #     )

    # ----------------------------------------------------
    # Move attached bodies
    # ----------------------------------------------------
    # ----------------------------------------------------
    # Move armrests as complete left/right groups
    # ----------------------------------------------------
    # ----------------------------------------------------
# Move armrests when seat length increases
# ----------------------------------------------------
    # ----------------------------------------------------
# Move armrests when seat length increases
# ----------------------------------------------------

    if (
    reference_category == "seat"
    and logical_dimension == "length"
):

        target_half_length = target_length / 2.0

        for item in all_bodies:

            side = get_armrest_side(item["name"])

            if side is None:
                continue

            xmin, ymin, zmin, xmax, ymax, zmax = get_bounds(
            item["shape"]
        )

            if side == "left":

                target_x = -target_half_length

                distance = target_x - xmax

                print(
                f"\nMoving LEFT ARM"
                f"\nCurrent X max : {xmax:.2f}"
                f"\nTarget X max  : {target_x:.2f}"
                f"\nMovement       : {distance:.2f}"
            )

                item["shape"] = move_body(
                item["shape"],
                gp_Vec(1, 0, 0),
                distance,
            )

            elif side == "right":

                target_x = target_half_length

                distance = target_x - xmin

                print(
                f"\nMoving RIGHT ARM"
                f"\nCurrent X min : {xmin:.2f}"
                f"\nTarget X min  : {target_x:.2f}"
                f"\nMovement       : {distance:.2f}"
            )

                item["shape"] = move_body(
                item["shape"],
                gp_Vec(1, 0, 0),
                distance,
            )
    

       
# ----------------------------------------------------
# Keep backrest attached to the scaled seat
# ----------------------------------------------------

    # ----------------------------------------------------
# Keep backrest attached to the scaled seat
# ----------------------------------------------------

    if (
    reference_category == "seat"
    and logical_dimension == "length"
):

        seat_shape = None
        backrest_shape = None

        for item in all_bodies:

            if item["name"] == "seat":
                seat_shape = item["shape"]

            elif item["name"] == "backrest":
                backrest_shape = item["shape"]

        if seat_shape is not None and backrest_shape is not None:

            from position_engine import move_backrest_to_seat_edge

            print("\nRepositioning BACKREST...")

            backrest_shape = move_backrest_to_seat_edge(
                backrest_shape,
                seat_shape,
        )
        

        for item in all_bodies:

            if item["name"] == "backrest":

                item["shape"] = backrest_shape

                break
    for i, body_name in enumerate(body_names):

        for item in all_bodies:

            if item["name"] == body_name:

                processed_solids[i] = item["shape"]
                break

    return processed_solids