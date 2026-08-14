
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepBndLib import BRepBndLib
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.Bnd import Bnd_Box, Bnd_OBB
from OCP.gp import (
    gp_Trsf,
    gp_Vec,
    gp_Pnt,
)


# -------------------------------------------------
# OBB
# -------------------------------------------------

def get_obb(shape):

    obb = Bnd_OBB()

    BRepBndLib.AddOBB_s(
        shape,
        obb,
        True,
        True,
        True,
    )

    return obb


# -------------------------------------------------
# OBB Center
# -------------------------------------------------

def get_center(shape):

    obb = get_obb(shape)

    return obb.Center()


# -------------------------------------------------
# Vector Between Bodies
# -------------------------------------------------

def vector_between(
    shape1,
    shape2,
):

    c1 = get_center(shape1)
    c2 = get_center(shape2)

    p1 = gp_Pnt(
        c1.X(),
        c1.Y(),
        c1.Z(),
    )

    p2 = gp_Pnt(
        c2.X(),
        c2.Y(),
        c2.Z(),
    )

    return gp_Vec(
        p1,
        p2,
    )


# -------------------------------------------------
# Projection on Axis
# -------------------------------------------------

def projection_on_axis(
    vector,
    axis,
):

    axis_vec = gp_Vec(
        axis.X(),
        axis.Y(),
        axis.Z(),
    )

    return vector.Dot(axis_vec)


# -------------------------------------------------
# Attachment Classification
# -------------------------------------------------

def classify_attachment(
    px,
    py,
    pz,
):

    values = {

        "X": px,
        "Y": py,
        "Z": pz,

    }

    dominant_axis = max(
        values,
        key=lambda k: abs(values[k]),
    )

    if values[dominant_axis] >= 0:
        sign = "+"
    else:
        sign = "-"

    return sign, dominant_axis


# -------------------------------------------------
# Bounding Box
# -------------------------------------------------

def get_bbox(shape):

    box = Bnd_Box()

    BRepBndLib.Add_s(
        shape,
        box,
    )

    return box


# -------------------------------------------------
# Bounding Box Limits
# -------------------------------------------------

def get_bounds(shape):

    box = get_bbox(shape)

    return box.Get()


# -------------------------------------------------
# Overlap
# -------------------------------------------------

def get_overlap(
    reference_body,
    attached_body,
    scale_info,
):
    """
    Returns the movement required so that the
    moving body remains attached to the scaled body.
    """

    xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = get_bounds(reference_body)

    xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = get_bounds(attached_body)

    axis = scale_info["logical_axis"]

    growth = scale_info["growth"]

    if axis == "X":

        gap1 = abs(xmin2 - xmax1)
        gap2 = abs(xmax2 - xmin1)

    elif axis == "Y":

        gap1 = abs(ymin2 - ymax1)
        gap2 = abs(ymax2 - ymin1)

    else:

        gap1 = abs(zmin2 - zmax1)
        gap2 = abs(zmax2 - zmin1)

    # Move only by half of the seat growth
    return growth / 2

# -------------------------------------------------
# Move Body
# -------------------------------------------------

def move_body(
    solid,
    direction,
    distance,
):

    dx = direction.X() * distance
    dy = direction.Y() * distance
    dz = direction.Z() * distance

    trsf = gp_Trsf()

    trsf.SetTranslation(
        gp_Vec(
            dx,
            dy,
            dz,
        )
    )

    transformer = BRepBuilderAPI_Transform(
        solid,
        trsf,
        True,
    )

    # print(
    #     f"Moved body by ({dx:.2f}, {dy:.2f}, {dz:.2f})"
    # )

    return transformer.Shape()

def make_compound(shapes):
    """
    Combines multiple shapes into one compound without fusing them.
    """
    compound = TopoDS_Compound()
    builder = BRep_Builder()

    builder.MakeCompound(compound)

    for shape in shapes:
        builder.Add(compound, shape)

    return compound


def move_backrest_to_seat_edge(
    backrest,
    seat,
):
    """
    Move the backrest so that its positive-X edge
    stays attached to the negative-X edge of the seat.
    """

    seat_xmin, _, _, _, _, _ = get_bounds(seat)

    back_xmin, _, _, back_xmax, _, _ = get_bounds(
        backrest
    )

    # Backrest is positioned behind the negative-X
    # edge of the seat.
    distance = seat_xmin - back_xmax

    return move_body(
        backrest,
        gp_Vec(1, 0, 0),
        distance,
    )
def get_armrest_side(body_name):
    name = body_name.lower().replace(" ", "_")

    if name in ("left_arm", "left_armrest"):
        return "left"

    if name in ("right_arm", "right_armrest"):
        return "right"

    return None