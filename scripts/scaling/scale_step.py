from OCP.gp import (
    gp_Ax3,
    gp_Pnt,
    gp_Dir,
    gp_Mat,
    gp_GTrsf,
    gp_XYZ,
    
)
from step_reader import get_body_axis_map
from bbox_engine import compute_obb
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_GTransform,
   
)

def get_logical_dimension(obb, obb_axis):
    """
    Convert an OBB axis to its logical dimension.
    """

    mapping = get_body_axis_map(obb)

    for logical, axis in mapping.items():

        if axis == obb_axis:
            return logical

    return None

# -------------------------------------------------
# Build OBB Coordinate System
# -------------------------------------------------

def build_obb_frame(obb):

    center = obb.Center()

    xdir = obb.XDirection()
    ydir = obb.YDirection()
    zdir = obb.ZDirection()


    frame = gp_Ax3(
        gp_Pnt(
            center.X(),
            center.Y(),
            center.Z(),
        ),

        gp_Dir(
            zdir.X(),
            zdir.Y(),
            zdir.Z(),
        ),

        gp_Dir(
            xdir.X(),
            xdir.Y(),
            xdir.Z(),
        ),
    )


    return frame



# -------------------------------------------------
# Rotation Matrix
# -------------------------------------------------

def build_rotation_matrix(obb):

    xdir = obb.XDirection()
    ydir = obb.YDirection()
    zdir = obb.ZDirection()


    R = gp_Mat(
        xdir.X(), ydir.X(), zdir.X(),
        xdir.Y(), ydir.Y(), zdir.Y(),
        xdir.Z(), ydir.Z(), zdir.Z(),
    )


    return R, R.Inverted()



# -------------------------------------------------
# Scale Matrix
# -------------------------------------------------

def build_scale_matrix(
    logical_axis,
    factor,
):

    axis_map = {

        "X": 1,
        "Y": 2,
        "Z": 3,
    }


    S = gp_Mat()

    S.SetIdentity()


    axis = axis_map[logical_axis]


    S.SetValue(
        axis,
        axis,
        factor,
    )


    return S



# -------------------------------------------------
# Final Matrix
# -------------------------------------------------

def build_final_matrix(
    R,
    R_inv,
    S,
):

    RS = R.Multiplied(S)

    FINAL = RS.Multiplied(R_inv)

    return FINAL

# -------------------------------------------------
# Translation
# -------------------------------------------------

def compute_translation(
    center,
    FINAL,
):

    cx = center.X()
    cy = center.Y()
    cz = center.Z()


    tx = cx - (
        FINAL.Value(1,1) * cx +
        FINAL.Value(1,2) * cy +
        FINAL.Value(1,3) * cz
    )


    ty = cy - (
        FINAL.Value(2,1) * cx +
        FINAL.Value(2,2) * cy +
        FINAL.Value(2,3) * cz
    )


    tz = cz - (
        FINAL.Value(3,1) * cx +
        FINAL.Value(3,2) * cy +
        FINAL.Value(3,3) * cz
    )


    return tx, ty, tz

# -------------------------------------------------
# Apply Transformation
# -------------------------------------------------

def apply_transform(
    solid,
    FINAL,
    tx,
    ty,
    tz,
):

    gtrsf = gp_GTrsf()


    gtrsf.SetVectorialPart(
        FINAL
    )


    gtrsf.SetTranslationPart(
        gp_XYZ(
            tx,
            ty,
            tz,
        )
    )


    transformer = BRepBuilderAPI_GTransform(
        solid,
        gtrsf,
        True,
    )


    return transformer.Shape()



# -------------------------------------------------
# Scale Body
# -------------------------------------------------

def scale_body(
    solid,
    obb,
    body_name,
    logical_dimension,
    factor,
):
    axis_map = get_body_axis_map(obb)
    obb_axis = axis_map[logical_dimension]
    print("\n========== SCALE DEBUG ==========")
    print("Body:", body_name)
    print("Logical dimension:", logical_dimension)
    print("Scale factor:", factor)
    print("Axis map:", axis_map)
    print("Selected OBB axis:", obb_axis)
    print("OLD OBB SIZE:")
    print("X:", 2 * obb.XHSize())
    print("Y:", 2 * obb.YHSize())
    print("Z:", 2 * obb.ZHSize())
    print("================================")

    # -----------------------------------------
    # Correct Fusion 360 orientation first
    # -----------------------------------------

    build_obb_frame(obb)


    # -----------------------------------------
    # OBB scaling
    # -----------------------------------------
    R, R_inv = build_rotation_matrix(
        obb
    )


    S = build_scale_matrix(
    obb_axis,
    factor,
)
    FINAL = build_final_matrix(
        R,
        R_inv,
        S,
    )
    tx, ty, tz = compute_translation(
        obb.Center(),
        FINAL,
    )
    scaled = apply_transform(
        solid,
        FINAL,
        tx,
        ty,
        tz,
    )


    direction_map = {

        "X": obb.XDirection(),
        "Y": obb.YDirection(),
        "Z": obb.ZDirection(),
    }


    size_map = {

        "X": 2 * obb.XHSize(),
        "Y": 2 * obb.YHSize(),
        "Z": 2 * obb.ZHSize(),
    }


    old_size = size_map[obb_axis]


    scale_info = {

    # OBB axis
    "logical_axis": obb_axis,

    # Unit direction of scaling
    "direction": direction_map[obb_axis],

    # User-selected logical dimension
    "logical_dimension": logical_dimension,

    # Sizes
    "old_size": old_size,
    "new_size": old_size * factor,

    # Amount added during scaling
    "growth": (old_size * factor) - old_size,

    # Scale factor
    "factor": factor,

    # OBB itself (needed later)
    "obb": obb,
    }
    return scaled, scale_info