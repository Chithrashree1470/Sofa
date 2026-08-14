from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.STEPControl import (
    STEPControl_Writer,
    STEPControl_AsIs,
)
from OCP.IFSelect import IFSelect_RetDone


def export_step(
    solids,
    filename,
):
    """
    Export all processed solids
    as a STEP file.
    """

    builder = BRep_Builder()

    compound = TopoDS_Compound()

    builder.MakeCompound(
        compound,
    )

    for solid in solids:

        builder.Add(
            compound,
            solid,
        )

    writer = STEPControl_Writer()

    writer.Transfer(
        compound,
        STEPControl_AsIs,
    )

    status = writer.Write(
        filename,
    )

    if status == IFSelect_RetDone:

        print("\nSTEP exported successfully!")

        print(filename)

    else:

        print("\nSTEP export failed!")