import adsk.core
import adsk.fusion
import csv
import os
import traceback


def run(context):

    app = adsk.core.Application.get()
    ui = app.userInterface

    try:

        CSV_PATH = r"G:\My Drive\sofa cost estimation\outputs\scaled_external.csv"

        if not os.path.exists(CSV_PATH):
            ui.messageBox("CSV not found:\n" + CSV_PATH)
            return

        # ---------------- Load CSV ----------------

        rows = []

        with open(CSV_PATH, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        ui.messageBox(f"Loaded {len(rows)} bodies")

        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox("No active design.")
            return

        root = design.rootComponent

        # ---------------- Delete previous components ----------------

        while root.occurrences.count > 0:
            root.occurrences.item(0).deleteMe()

        while root.bRepBodies.count > 0:
            root.bRepBodies.item(0).deleteMe()

        # Fusion internal unit = cm
        def mm(x):
            return float(x) / 10.0

        created = 0

        # ==========================================================
        # Build bodies
        # ==========================================================

        for row in rows:

            body_name = row["body"]

            L = float(row["scaled_L"])
            W = float(row["scaled_W"])
            H = float(row["scaled_H"])

            ox = float(row["scaled_min_x_mm"])
            oy = float(row["scaled_min_y_mm"])
            oz = float(row["scaled_min_z_mm"])

            if L <= 0 or W <= 0 or H <= 0:
                continue

            # ---------- create transform FIRST ----------

            transform = adsk.core.Matrix3D.create()

            transform.translation = adsk.core.Vector3D.create(
                mm(ox),
                mm(oy),
                mm(oz)
            )

            # create component already positioned correctly

            occ = root.occurrences.addNewComponent(transform)

            comp = occ.component
            comp.name = body_name

            # ---------- sketch ----------

            sketch = comp.sketches.add(comp.xYConstructionPlane)

            lines = sketch.sketchCurves.sketchLines

            lines.addTwoPointRectangle(

                adsk.core.Point3D.create(0, 0, 0),

                adsk.core.Point3D.create(
                    mm(L),
                    mm(W),
                    0
                )

            )

            profile = sketch.profiles.item(0)

            distance = adsk.core.ValueInput.createByReal(mm(H))

            extrude = comp.features.extrudeFeatures.addSimple(

                profile,

                distance,

                adsk.fusion.FeatureOperations.NewBodyFeatureOperation

            )

            body = extrude.bodies.item(0)

            body.name = body_name

            created += 1

        ui.messageBox(f"Finished!\nCreated {created} bodies.")

    except:
        ui.messageBox(traceback.format_exc())