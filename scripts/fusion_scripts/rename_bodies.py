import adsk.core
import adsk.fusion
import traceback
import re


def run(context):

    ui = None

    try:

        app = adsk.core.Application.get()
        ui = app.userInterface

        design = app.activeProduct
        root = design.rootComponent

        renamed = 0

        for body in root.bRepBodies:

            name = body.name

            # =====================================================
            # FOAM / MAIN EXTERNAL COMPONENTS
            # =====================================================

            # Foam Pink -> cushion/internal cushion
            if name == "Foam Pink":
                body.name = "cusion"
                renamed += 1
                continue

            # Foam Black -> seat top
            if name == "Foam Black":
                body.name = "seat_top"
                renamed += 1
                continue

            # Body87 -> seat front
            if name == "Body87":
                body.name = "seat_front"
                renamed += 1
                continue

            # Body88 -> fabric
            if name == "Body88":
                body.name = "fabric"
                renamed += 1
                continue

            # Body89 -> backrest front
            if name == "Body89":
                body.name = "backrest_front"
                renamed += 1
                continue

            # Body90 -> backrest top
            if name == "Body90":
                body.name = "backrest_top"
                renamed += 1
                continue

            # Body95 -> backrest back
            if name == "Body95":
                body.name = "backrest_back"
                renamed += 1
                continue


            # =====================================================
            # CLIPS
            # =====================================================

            # Body7 and all its copies
            if name == "Body7" or name.startswith("Body7 ("):

                body.name = "Clip"
                renamed += 1
                continue


            # =====================================================
            # NUMBERED INTERNAL BODIES
            # =====================================================

            match = re.fullmatch(r"Body(\d+)", name)

            if match:

                num = int(match.group(1))

                # ---------------------------------------------
                # Springs
                # ---------------------------------------------

                if 53 <= num <= 63:

                    body.name = "Spring"
                    renamed += 1
                    continue


                # ---------------------------------------------
                # Seat Belts
                # ---------------------------------------------

                elif 67 <= num <= 69:

                    body.name = "Seat Belt"
                    renamed += 1
                    continue


                # ---------------------------------------------
                # Back Rest Belts
                # ---------------------------------------------

                elif 70 <= num <= 84:

                    body.name = "Back Rest Belt"
                    renamed += 1
                    continue


                # ---------------------------------------------
                # Wood Frame
                # ---------------------------------------------

                elif (
                    (4 <= num <= 11)
                    or
                    (13 <= num <= 18)
                    or
                    (21 <= num <= 29)
                ):

                    body.name = "Wood Frame"
                    renamed += 1
                    continue


                # ---------------------------------------------
                # Handle Frames
                # ---------------------------------------------

                elif (
                    (98 <= num <= 100)
                    or
                    (102 <= num <= 109)
                    or
                    (132 <= num <= 142)
                ):

                    body.name = "Handle Frame"
                    renamed += 1
                    continue


            # =====================================================
            # HANDLE FOAM
            # =====================================================

            # Right-side handle foam bodies
            if name in [
                "Body130",
                "Body146",
                "Body147",
                "Body150",
                "Body153",
            ]:

                body.name = "Right Handle Foam"
                renamed += 1
                continue


            # Left-side handle foam bodies
            if name in [
                "Body143",
                "Body148",
                "Body149",
                "Body154",
                "Body155",
            ]:

                body.name = "Left Handle Foam"
                renamed += 1
                continue


        # =====================================================
        # SECOND PASS:
        # SPLIT HANDLE FRAMES INTO LEFT / RIGHT
        # =====================================================

        for body in root.bRepBodies:

            name = body.name

            # -------------------------------------------------
            # Right Handle Frame
            # -------------------------------------------------

            if name == "Handle Frame":

                body.name = "Right Handle Frame"
                renamed += 1
                continue

            match = re.fullmatch(
                r"Handle Frame \((\d+)\)",
                name
            )

            if match:

                idx = int(match.group(1))

                # Right side
                if 1 <= idx <= 11:

                    body.name = "Left Handle Frame"
                    renamed += 1

                # Left side
                elif 12 <= idx <= 22:

                    body.name = "Right Handle Frame"
                    renamed += 1


        ui.messageBox(
            f"Renaming completed.\n\n"
            f"Renamed bodies: {renamed}"
        )


    except:

        if ui:
            ui.messageBox(
                traceback.format_exc()
            )