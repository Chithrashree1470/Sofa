import re


def get_step_body_names(step_path):
    """
    Reads MANIFOLD_SOLID_BREP names
    from a STEP file in the order
    they appear.
    """

    names = []

    pattern = re.compile(
        r"MANIFOLD_SOLID_BREP\('([^']+)'",
        re.IGNORECASE,
    )

    with open(
        step_path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as f:

        for line in f:

            match = pattern.search(line)

            if match:

                names.append(
                    match.group(1)
                )

    return names