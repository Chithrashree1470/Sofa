from OCP.Bnd import Bnd_Box, Bnd_OBB
from OCP.BRepBndLib import BRepBndLib


def compute_bbox(solid):
    """
    Compute the axis-aligned bounding box (AABB)
    of a solid.
    """

    box = Bnd_Box()

    BRepBndLib.Add_s(
        solid,
        box,
    )

    return box


def compute_obb(solid):
    """
    Compute the oriented bounding box (OBB)
    of a solid.
    """

    

    obb = Bnd_OBB()

    BRepBndLib.AddOBB_s(
        solid,
        obb,
        True,   # use triangulation
        True,   # optimal
        True,   # shape tolerance
    )


    return obb


def print_bbox(body_name, bbox):
    """
    Print axis-aligned bounding box.
    """

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    print("\n" + "=" * 60)
    print(body_name)

    print(f"X : {xmin:.2f} -> {xmax:.2f}")
    print(f"Y : {ymin:.2f} -> {ymax:.2f}")
    print(f"Z : {zmin:.2f} -> {zmax:.2f}")

    print(f"L = {xmax - xmin:.2f}")
    print(f"W = {ymax - ymin:.2f}")
    print(f"H = {zmax - zmin:.2f}")


def print_obb(body_name, obb):
    """
    Print oriented bounding box information.
    """

    print("\n" + "=" * 60)
    print(f"OBB for {body_name}")

    center = obb.Center()

    print(
        f"Center : ({center.X():.2f}, "
        f"{center.Y():.2f}, "
        f"{center.Z():.2f})"
    )

    xdir = obb.XDirection()
    ydir = obb.YDirection()
    zdir = obb.ZDirection()

    print(
        f"Local X : ({xdir.X():.3f}, "
        f"{xdir.Y():.3f}, "
        f"{xdir.Z():.3f})"
    )

    print(
        f"Local Y : ({ydir.X():.3f}, "
        f"{ydir.Y():.3f}, "
        f"{ydir.Z():.3f})"
    )

    print(
        f"Local Z : ({zdir.X():.3f}, "
        f"{zdir.Y():.3f}, "
        f"{zdir.Z():.3f})"
    )

    print(
        f"OBB X Size : {2 * obb.XHSize():.2f}"
    )

    print(
        f"OBB Y Size : {2 * obb.YHSize():.2f}"
    )

    print(
        f"OBB Z Size : {2 * obb.ZHSize():.2f}"
    )