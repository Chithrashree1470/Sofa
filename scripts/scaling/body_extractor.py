from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopoDS import TopoDS


def extract_solids(shape):
    """
    Extract all solids from the STEP model.

    Parameters
    ----------
    shape : TopoDS_Shape

    Returns
    -------
    list
        List of TopoDS_Solid objects.
    """

    explorer = TopExp_Explorer(
        shape,
        TopAbs_SOLID,
    )

    solids = []

    while explorer.More():

        solid = TopoDS.Solid_s(
            explorer.Current()
        )

        solids.append(solid)

        explorer.Next()

    print(f"\nTotal solids found: {len(solids)}")

    return solids