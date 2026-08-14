# External STEP-File Sofa Scaling --- Complete Technical Documentation

## 1. Purpose

This document describes the current **external STEP-file scaling
approach** for the sofa cost-estimation project.

The pipeline operates directly on a `.step` CAD file using Python +
OpenCascade/OCP. It does **not** use the Fusion 360 API.

The pipeline:

1.  Reads a STEP file.
2.  Extracts its individual solids.
3.  Obtains body names.
4.  Groups bodies using a metadata JSON file.
5.  Calculates OBBs and logical dimensions.
6.  Calculates assembly/category bounding boxes.
7.  Reads target length/width/height.
8.  Calculates scaling factors.
9.  Scales selected reference bodies using their OBB coordinate systems.
10. Calculates how much the reference category changed.
11. Repositions external/attached bodies.
12. Repeats the configured stages.
13. Exports the resulting solids as a new STEP file.

### Current status

The **seat scaling foundation is working**, especially logical length
scaling.

The following are implemented:

-   STEP loading
-   body extraction
-   body-name extraction
-   metadata category grouping
-   OBB calculation
-   OBB-axis-to-logical-axis mapping
-   body dimensions
-   category dimensions
-   assembly dimensions
-   OBB-based geometric scaling
-   scaling around the body's OBB center
-   seat length scaling
-   seat width scaling infrastructure
-   category growth calculation
-   external-body movement infrastructure
-   STEP export

The following are **not final**:

-   fully generic attachment detection
-   fully generic positioning
-   final armrest scaling/positioning
-   final backrest scaling/positioning
-   final generic width/height strategy

Backrest and armrest scaling are intentionally left for the other team
members.

------------------------------------------------------------------------

# 2. Current Architecture

``` text
main_scale.py
    |
    +-- body_names.py
    +-- step_reader.py
    +-- assembly_parser.py
    +-- body_extractor.py
    +-- scaling_pipeline.py
    +-- scale_step.py
    +-- position_engine.py
    +-- bbox_engine.py
    +-- export_step.py
```

### Responsibilities

  -----------------------------------------------------------------------
  File                                Responsibility
  ----------------------------------- -----------------------------------
  `main_scale.py`                     Main execution flow, target inputs,
                                      scale factors, processing order,
                                      export

  `step_reader.py`                    STEP loading, metadata loading,
                                      dimensions, bounds, OBB axis
                                      mapping

  `scale_step.py`                     Geometric scaling of individual
                                      solids around their OBB

  `scaling_pipeline.py`               Category scaling + reference
                                      growth + external positioning

  `position_engine.py`                OBBs, bounding boxes, attachment
                                      utilities, translation, compounds

  `bbox_engine.py`                    Bounding-box/OBB helpers

  `body_names.py`                     Extracts body names from STEP

  `body_extractor.py`                 Extracts individual solids

  `assembly_parser.py`                Obtains the reference shape

  `export_step.py`                    Writes final STEP
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 3. Current Test Model

The current test STEP contains **16 solids**.

Observed body names:

``` text
cusion
seat_top
seat_front

backrest_front
backrest_top
backrest_back

left_armrest top
right_armrest_top
left_armrest_front
left_armrest_back
right_armrest_front
right_armrest_back

left_armrest_top (1)
left_armrest_base
right_armrest_top (1)
right_armrest_base
```

The source model spells `cusion` this way. Do not silently rename it
unless body-name extraction and metadata are changed together.

------------------------------------------------------------------------

# 4. Metadata

Current metadata:

``` json
{
  "seat": [
    "seat_top",
    "seat_front",
    "cusion"
  ],
  "backrest": [
    "backrest_front",
    "backrest_top",
    "backrest_back"
  ],
  "armrest": [
    "right_armrest_top",
    "left_armrest_top",
    "right_armrest_front",
    "right_armrest_back",
    "left_armrest_front",
    "left_armrest_back",
    "right_armrest_top (1)",
    "right_armrest_base",
    "left_armrest_top (1)",
    "left_armrest_base"
  ]
}
```

The metadata is therefore the category-to-body mapping.

------------------------------------------------------------------------

# 5. STEP Loading

`step_reader.py` uses:

``` python
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
```

The loading process is:

``` python
reader = STEPControl_Reader()
status = reader.ReadFile(step_file)

if status != IFSelect_RetDone:
    raise RuntimeError("STEP reading failed")

reader.TransferRoots()
return reader.OneShape()
```

The current model successfully reports:

``` text
STEP file loaded successfully
Total solids found: 16
```

The body names are obtained separately:

``` python
body_names = get_step_body_names(STEP_FILE)
```

The pipeline repeatedly relies on:

``` python
for solid, body_name in zip(solids, body_names):
```

Therefore the solid/name ordering must remain compatible.

------------------------------------------------------------------------

# 6. Global Coordinate Convention

The current model uses:

``` text
Global X = logical length
Global Z = logical width
Global Y = logical height
```

Therefore:

``` text
length -> X
width  -> Z
height -> Y
```

This convention is fundamental.

It is used for:

-   assembly dimensions
-   category dimensions
-   logical OBB mapping
-   attachment classification
-   positioning

Do not assume that an individual body's OBB X/Y/Z axes are the same as
global length/width/height.

------------------------------------------------------------------------

# 7. Why OBBs Are Needed

Different bodies may be oriented differently.

For example, the current `cusion` OBB has approximately:

``` text
OBB X direction = global X
OBB Y direction = global -Z
OBB Z direction = global -Y
```

Another body can have a different OBB axis ordering.

Therefore the system first determines:

``` text
Which OBB axis corresponds to logical length?
Which OBB axis corresponds to logical width?
Which OBB axis corresponds to logical height?
```

------------------------------------------------------------------------

# 8. OBB Axis Mapping

`get_body_axis_map()` compares OBB directions against the global logical
axes.

``` python
global_axes = {
    "length": (1, 0, 0),
    "width":  (0, 0, 1),
    "height": (0, 1, 0),
}
```

The OBB directions are:

``` python
obb_axes = {
    "X": obb.XDirection(),
    "Y": obb.YDirection(),
    "Z": obb.ZDirection(),
}
```

For every logical dimension, the algorithm computes the absolute dot
product between the OBB axis and the corresponding global axis. The axis
with the largest score is selected.

`used_obb_axes` prevents the same OBB axis from being assigned twice.

Example:

``` text
{
    "length": "X",
    "width": "Y",
    "height": "Z"
}
```

Another valid result:

``` text
{
    "length": "Y",
    "width": "Z",
    "height": "X"
}
```

This is expected.

------------------------------------------------------------------------

# 9. OBB Sizes

OCP returns half-extents through:

``` python
obb.XHSize()
obb.YHSize()
obb.ZHSize()
```

Therefore full sizes are:

``` python
2 * obb.XHSize()
2 * obb.YHSize()
2 * obb.ZHSize()
```

------------------------------------------------------------------------

# 10. Body Dimensions

`get_body_dimensions()` calculates dimensions for every body belonging
to a category.

For each body:

``` python
obb = compute_obb(solid)
mapping = get_body_axis_map(obb)
```

It obtains:

``` python
axis_sizes = {
    "X": 2 * obb.XHSize(),
    "Y": 2 * obb.YHSize(),
    "Z": 2 * obb.ZHSize(),
}
```

Then converts the OBB axis sizes to logical dimensions.

Example:

``` text
cusion
length: 1600.00
width: 615.08
height: 50.80
```

------------------------------------------------------------------------

# 11. Category Dimensions

`get_category_dimensions()` is different from `get_body_dimensions()`.

It calculates the **global enclosing AABB** of all bodies belonging to a
category.

For every matching body:

``` python
box = compute_bbox(solid)
```

The global minimum and maximum X/Y/Z values are accumulated.

Final logical dimensions:

``` python
{
    "length": xmax - xmin,
    "width":  zmax - zmin,
    "height": ymax - ymin,
}
```

Because:

``` text
X = length
Z = width
Y = height
```

Current original results:

``` text
SEAT
length: 1600.00
width: 641.48
height: 180.06

BACKREST
length: 1610.00
width: 262.82
height: 692.01

ARMREST
length: 2058.80
width: 841.00
height: 437.03
```

These are category extents, not necessarily the dimensions of any
individual body.

------------------------------------------------------------------------

# 12. Assembly Dimensions

`get_assembly_dimensions()` creates an AABB around all solids.

``` python
return {
    "length": xmax - xmin,
    "width": zmax - zmin,
    "height": ymax - ymin,
}
```

Original model:

``` text
length: 2058.81 mm
width:   844.43 mm
height:  692.02 mm
```

The overall length is larger than the seat length because the armrests
extend beyond the seat.

------------------------------------------------------------------------

# 13. Main Scaling Rules

Current rules:

``` python
SCALING_RULES = {
    "length": ["seat"],
    "width": ["seat", "armrest"],
    "height": ["backrest"],
}
```

The main loop processes:

``` text
length:
    seat

width:
    seat
    armrest

height:
    backrest
```

This is the current configuration, not a statement that all three stages
are finished.

------------------------------------------------------------------------

# 14. User Input

The program asks:

``` text
Target Length (mm):
Target Width (mm):
Target Height (mm):
```

The target dimensions are converted to floats.

------------------------------------------------------------------------

# 15. Critical Seat-Length Logic

The most important completed logic is the treatment of overall sofa
length.

The target length means:

``` text
TARGET OVERALL SOFA LENGTH
```

It does **not** mean:

``` text
TARGET SEAT LENGTH
```

Original model:

``` text
seat length     = 1600 mm
assembly length = 2058.8 mm
```

If target overall length is 3000 mm, the required overall change is:

``` text
3000 - 2058.8 ≈ +941.2 mm
```

The seat is therefore increased by approximately that amount.

The code does:

``` python
remaining = target_length - assembly_dimensions["length"]

target_seat_length = (
    seat_dimensions["length"] + remaining
)
```

Then:

``` python
length_factor = (
    target_seat_length / seat_dimensions["length"]
)
```

Mathematically:

``` text
target seat length
=
original seat length
+
(target overall length - original overall length)
```

This is deliberate.

------------------------------------------------------------------------

# 16. Example: Target Length 3000 mm

Original:

``` text
assembly = 2058.8
seat     = 1600
```

Required assembly change:

``` text
3000 - 2058.8 ≈ 941.2
```

Target seat:

``` text
1600 + 941.2 ≈ 2541.2
```

Factor:

``` text
2541.2 / 1600 ≈ 1.588
```

Observed final global X extent after positioning:

``` text
approximately -1500.04 to +1500.04
```

giving:

``` text
GLOBAL LENGTH ≈ 3000.08 mm
```

The tiny error is numerical/CAD transformation tolerance.

------------------------------------------------------------------------

# 17. Example: Target Length 1000 mm

Original:

``` text
assembly ≈ 2058.8
seat = 1600
```

Required assembly change:

``` text
1000 - 2058.8 ≈ -1058.8
```

Target seat:

``` text
1600 - 1058.8 ≈ 541.2
```

Factor:

``` text
≈ 0.338
```

Observed seat bounds after scaling:

``` text
X ≈ -270.59 to +270.59
```

which gives approximately:

``` text
541.18 mm
```

This confirms that the length formula is based on overall logical sofa
length.

------------------------------------------------------------------------

# 18. Width and Height Factors

Current main code calculates:

``` python
width_factor = target_width / seat_dimensions["width"]
height_factor = target_height / seat_dimensions["height"]
```

These formulas are currently part of the infrastructure.

The final generic multi-category strategy for width and height is not
complete.

------------------------------------------------------------------------

# 19. `scale_step.py` --- Individual Body Scaling

`scale_body()` scales one solid according to its OBB.

First:

``` python
axis_map = get_body_axis_map(obb)
obb_axis = axis_map[logical_dimension]
```

Therefore if logical length corresponds to OBB Y for a body, that body's
Y OBB axis is scaled.

The system does not blindly scale global X/Y/Z.

------------------------------------------------------------------------

# 20. OBB Coordinate Transformation

`build_rotation_matrix()` creates:

``` text
R
```

from the OBB's X/Y/Z direction vectors.

Its inverse:

``` text
R_inv
```

is also calculated.

The scale matrix `S` places the factor on the relevant OBB axis.

The final transformation is:

``` python
FINAL = R.Multiplied(S)
FINAL = FINAL.Multiplied(R_inv)
```

Conceptually:

``` text
global coordinates
       |
       v
transform into OBB coordinates
       |
       v
scale selected OBB axis
       |
       v
transform back to global coordinates
```

------------------------------------------------------------------------

# 21. Scaling Around the OBB Center

Without correction, scaling could cause the body to move because the
transformation is relative to the global origin.

`compute_translation()` therefore calculates a translation that
preserves the original OBB center.

Conceptually:

``` text
original center
      |
      v
apply scale matrix
      |
      v
scaled center
      |
      v
translation correction
      |
      v
original center preserved
```

The transformation is applied using:

``` python
BRepBuilderAPI_GTransform
```

------------------------------------------------------------------------

# 22. `scale_body()` Returns Scale Information

The returned `scale_info` contains:

``` python
{
    "logical_axis": obb_axis,
    "direction": direction_map[obb_axis],
    "logical_dimension": logical_dimension,
    "old_size": old_size,
    "new_size": old_size * factor,
    "growth": (old_size * factor) - old_size,
    "factor": factor,
    "obb": obb,
}
```

Important values:

``` text
old_size
new_size
growth
factor
```

------------------------------------------------------------------------

# 23. `process_dimension()` --- Category Processing

The function receives:

``` python
process_dimension(
    solids,
    body_names,
    logical_dimension,
    factor,
    metadata,
    target_length=None,
    reference_category="seat",
)
```

The `reference_category` is the category being scaled in that particular
call.

For example:

``` text
length -> seat
width  -> seat
width  -> armrest
height -> backrest
```

The function:

1.  Gets old reference bounds.
2.  Scales reference bodies.
3.  Gets new reference bounds.
4.  Calculates actual growth.
5.  Builds a compound of scaled reference bodies.
6.  Builds an attachment map.
7.  Moves external bodies.
8.  Reconstructs `processed_solids`.

------------------------------------------------------------------------

# 24. Old and New Reference Bounds

Before scaling:

``` python
old_reference_bounds = get_category_bounds(
    reference_category,
    metadata,
    solids,
    body_names,
)
```

After scaling:

``` python
new_reference_bounds = get_category_bounds(
    reference_category,
    metadata,
    processed_solids,
    body_names,
)
```

Each returns:

``` text
xmin
ymin
zmin
xmax
ymax
zmax
```

------------------------------------------------------------------------

# 25. Actual Category Growth

The pipeline calculates:

``` python
growth = {
    "length": (new_xmax - new_xmin) - (old_xmax - old_xmin),
    "width":  (new_zmax - new_zmin) - (old_zmax - old_zmin),
    "height": (new_ymax - new_ymin) - (old_ymax - old_ymin),
}
```

This is useful because the reference category can contain multiple
bodies.

The system therefore measures the category's actual global change rather
than relying only on one body's theoretical growth.

------------------------------------------------------------------------

# 26. Compound Reference Shape

The scaled reference bodies are combined using:

``` python
reference_shape = make_compound(reference_shapes)
```

`make_compound()` creates a `TopoDS_Compound`.

It does **not** fuse the solids together.

This allows the category to be treated as one geometric reference while
retaining the individual bodies.

------------------------------------------------------------------------

# 27. Positioning Concept

Scaling geometry alone does not move other bodies.

Example before length scaling:

``` text
seat:
-800 to +800

left armrest:
+806 to +1029

right armrest:
-1029 to -806
```

If the seat shrinks to approximately:

``` text
-270.6 to +270.6
```

the armrests must move inward.

If the seat expands, they must move outward.

Therefore:

``` text
SCALING
changes the reference geometry

POSITIONING
moves dependent/external geometry
```

These must remain conceptually separate.

------------------------------------------------------------------------

# 28. Current Attachment Classification

`get_global_attachment()` currently compares OBB centers.

It calculates:

``` python
dx = body_center.X() - reference_center.X()
dy = body_center.Y() - reference_center.Y()
dz = body_center.Z() - reference_center.Z()
```

Then maps:

``` python
values = {
    "length": dx,
    "width": dz,
    "height": dy,
}
```

The dimension with the largest absolute value is selected.

The sign becomes `+` or `-`.

Examples from the current sofa:

``` text
left armrests  -> +length
right armrests -> -length
backrest       -> -width
```

This works for the current test model.

------------------------------------------------------------------------

# 29. Current Attachment Map Observed

When using the seat as reference:

``` text
backrest_front        -> -width
backrest_top          -> +height
backrest_back         -> -width

left_armrest top      -> +length
right_armrest_top     -> -length
left_armrest_front    -> +length
left_armrest_back     -> +length
right_armrest_front   -> -length
right_armrest_back    -> -length
left_armrest_top (1)  -> +length
left_armrest_base     -> +length
right_armrest_top (1) -> -length
right_armrest_base    -> -length
```

The armrest side classification is useful for the current model.

------------------------------------------------------------------------

# 30. Current Positioning Movement

`get_attachment_movement()` currently accepts:

``` python
old_reference_bounds
new_reference_bounds
attached_bounds
attachment
```

The current implementation does not actually use `attached_bounds`.

For `+X`:

``` python
return gp_Vec(1, 0, 0), new_xmax - old_xmax
```

For `-X`:

``` python
return gp_Vec(1, 0, 0), new_xmin - old_xmin
```

For `+Y`:

``` python
return gp_Vec(0, 1, 0), new_ymax - old_ymax
```

For `-Y`:

``` python
return gp_Vec(0, 1, 0), new_ymin - old_ymin
```

For `+Z`:

``` python
return gp_Vec(0, 0, 1), new_zmax - old_zmax
```

For `-Z`:

``` python
return gp_Vec(0, 0, 1), new_zmin - old_zmin
```

This uses the movement of the relevant reference face.

------------------------------------------------------------------------

# 31. Body Translation

`move_body()` calculates:

``` python
dx = direction.X() * distance
dy = direction.Y() * distance
dz = direction.Z() * distance
```

and applies a `gp_Trsf` translation:

``` python
trsf.SetTranslation(
    gp_Vec(dx, dy, dz)
)
```

using:

``` python
BRepBuilderAPI_Transform
```

It returns the translated shape.

------------------------------------------------------------------------

# 32. Important Current Positioning Limitation

The current positioning architecture is **not fully generic**.

The current `process_dimension()` loops through all non-reference bodies
and classifies them relative to the current reference category.

That means when the reference category changes, unrelated bodies can
accidentally be treated as attached to that category.

For example:

``` text
reference = seat
```

makes sense for:

``` text
armrest -> ±length
backrest -> -width
```

But:

``` text
reference = armrest
```

should not automatically cause every seat and backrest body to be
treated as an attachment to the armrest.

This is an architectural issue that the next positioning implementation
must solve.

------------------------------------------------------------------------

# 33. Why Current Center-Based Positioning Is Not Fully Generic

Center-to-center dominant-axis classification works for this test sofa
but can fail for arbitrary CAD geometry.

Examples of problematic cases:

-   overlapping bodies
-   bodies whose centers are close but attach on different faces
-   bodies extending through the reference center
-   irregular/curved bodies
-   multiple bodies attached to one face
-   bodies that are nearby but not physically attached
-   slightly rotated models

A more generic system should determine actual attachment/contact
relationships using geometry/bounds/face proximity rather than only
center displacement.

------------------------------------------------------------------------

# 34. Existing Positioning Utilities

`position_engine.py` already contains useful infrastructure:

``` python
get_obb(shape)
get_center(shape)
vector_between(shape1, shape2)
projection_on_axis(vector, axis)
classify_attachment(px, py, pz)
get_bbox(shape)
get_bounds(shape)
get_attachment_movement(...)
move_body(...)
make_compound(shapes)
```

These can be reused when developing the generic positioning algorithm.

------------------------------------------------------------------------

# 35. Processing Order

The main pipeline processes:

``` python
for logical_dimension in [
    "length",
    "width",
    "height",
]:
```

For each dimension, it processes the configured categories.

Current conceptual order:

``` text
1. length -> seat
2. width  -> seat
3. width  -> armrest
4. height -> backrest
```

The result of each call becomes the input to the next:

``` text
original solids
    |
    v
length result
    |
    v
width result
    |
    v
height result
    |
    v
final solids
```

This sequential behavior is important.

------------------------------------------------------------------------

# 36. `processed_solids`

Initially:

``` python
processed_solids = solids
```

After every processing call:

``` python
processed_solids = process_dimension(...)
```

Therefore every later stage operates on the already-transformed
geometry.

------------------------------------------------------------------------

# 37. Replacing Shapes

Scaled reference bodies are stored in:

``` python
scaled_reference_bodies
```

External/moved bodies are stored in:

``` python
attachment_map
```

At the end of `process_dimension()`, `processed_solids` is rebuilt.

For reference bodies:

``` python
processed_solids[i] = scaled_reference_bodies[body_name]
```

For moved bodies:

``` python
processed_solids[i] = item["shape"]
```

The returned list therefore contains the latest geometry.

------------------------------------------------------------------------

# 38. Debugging Global Length

`print_global_length_bounds()` prints every body's X range.

Example original:

``` text
cusion: X = -800.00 to 800.00
seat_top: X = -800.00 to 800.00
...
left_armrest_base: X = 813.02 to 1029.40
right_armrest_base: X = -1029.40 to -813.02

GLOBAL X = -1029.40 to 1029.40
GLOBAL LENGTH = 2058.80
```

This is the main debugging method used so far to verify logical sofa
length.

------------------------------------------------------------------------

# 39. Successful Length-Expansion Test

Target:

``` text
3000 mm
```

The seat factor was approximately:

``` text
1.588
```

After scaling and positioning, global X was approximately:

``` text
-1500.04 to +1500.04
```

giving:

``` text
3000.08 mm
```

This is considered successful within numerical tolerance.

------------------------------------------------------------------------

# 40. Successful Length-Contraction Concept

Target:

``` text
800 mm
```

The seat became much shorter.

The armrests were moved inward rather than remaining around the original
±800 to ±1000 mm positions.

This demonstrated that the basic reference-boundary movement concept
works in both directions.

It does not prove the algorithm is generic.

------------------------------------------------------------------------

# 41. Backrest Length Behavior

During seat-length scaling, the backrest length remained approximately:

``` text
1610 mm
```

This is expected under the current rules because length scaling
currently targets:

``` python
"length": ["seat"]
```

Therefore the backrest is not geometrically length-scaled during the
seat-length operation.

The backrest may need repositioning to maintain the sofa relationship,
but its own length is not supposed to change in that stage.

------------------------------------------------------------------------

# 42. STEP Export

After processing:

``` python
export_step(
    processed_solids,
    OUTPUT_STEP,
)
```

The transformed solids are written as a new STEP file.

Observed result:

``` text
STEP exported successfully!
```

The input file is not intentionally overwritten.

------------------------------------------------------------------------

# 43. Numerical Tolerance

Small differences are expected.

For example:

``` text
target = 3000.00
result = 3000.08
```

or:

``` text
target = 3000.00
result = 2999.99
```

Possible sources include:

-   floating-point arithmetic
-   OpenCascade transformations
-   AABB calculations
-   OBB calculations
-   CAD geometry tolerances

A tiny difference should not automatically be treated as a logical
failure.

------------------------------------------------------------------------

# 44. What Is Complete

``` text
[YES] STEP loading
[YES] Solid extraction
[YES] Body-name extraction
[YES] Metadata grouping
[YES] OBB calculation
[YES] Logical OBB axis mapping
[YES] Body dimensions
[YES] Category dimensions
[YES] Assembly dimensions
[YES] OBB-local scaling
[YES] Scaling around OBB center
[YES] Seat length scaling
[YES] Seat width scaling infrastructure
[YES] Category growth calculation
[YES] Translation infrastructure
[YES] STEP export
```

# 45. What Is NOT Complete

``` text
[NOT FINAL] Generic attachment detection
[NOT FINAL] Generic positioning
[NOT FINAL] Armrest scaling
[NOT FINAL] Armrest positioning
[NOT FINAL] Backrest scaling
[NOT FINAL] Backrest positioning
[NOT FINAL] Final multi-category width strategy
[NOT FINAL] Final multi-category height strategy
[NOT FINAL] Robust arbitrary-sofa geometry handling
```

------------------------------------------------------------------------

# 46. Rules for Teammates Continuing the Work

1.  **Do not replace the seat-length formula casually.**

    It is intentionally based on overall sofa length:

    ``` text
    target seat length
    =
    original seat length
    +
    target overall length
    -
    original overall length
    ```

2.  **Do not assume OBB X/Y/Z means logical length/width/height.**

    Always use `get_body_axis_map()`.

3.  **Do not assume category dimensions equal one body's dimensions.**

    Category dimensions use an enclosing global AABB.

4.  **Do not confuse scaling with positioning.**

    Scaling changes geometry. Positioning moves geometry.

5.  **Do not hard-code the current sofa's armrest positions into the
    generic implementation.**

6.  **Do not assume `left` always means +X or `right` always means -X
    for arbitrary CAD models.**

    Those are observations from the current test model.

7.  **Do not classify every other body as attached to whichever category
    is currently being scaled.**

    The generic positioning architecture must determine actual
    relationships.

8.  **Do not add a Fusion API dependency.**

    The current approach is intentionally external to Fusion.

9.  **Preserve the sequential nature of the pipeline.**

10. **Verify global bounds after every major transformation.**

------------------------------------------------------------------------

# 47. Recommended Generic Positioning Architecture

The desired final architecture is:

``` text
reference category
        |
        v
old reference geometry/bounds
        |
        v
scale reference bodies
        |
        v
new reference geometry/bounds
        |
        v
determine actual attached bodies
        |
        v
determine attachment face/direction
        |
        v
calculate old/new attachment face movement
        |
        v
translate attached body
        |
        v
verify contact/overlap/clearance
```

The critical improvement is:

``` text
"Which bodies are actually attached to this reference?"
```

rather than:

``` text
"Which direction is every other body from this reference?"
```

------------------------------------------------------------------------

# 48. Mental Model

The intended relationship can be thought of as:

``` text
              SEAT
             /    \
            /      \
     left arm     right arm
            \
             \
            backrest
```

When the seat expands:

``` text
seat grows
   |
   +--> dependent bodies move outward/accordingly
```

When the seat contracts:

``` text
seat shrinks
   |
   +--> dependent bodies move inward/accordingly
```

The movement should be derived from the geometry, not hard-coded
distances.

------------------------------------------------------------------------

# 49. AI Coding-Assistant Context

If this document is pasted into an AI assistant, the assistant should
understand:

-   This is a Python/OCP/OpenCascade STEP-processing system.
-   Fusion 360 API is intentionally not used.
-   The input is a STEP assembly containing separate solids.
-   Body names are obtained separately and mapped to categories through
    JSON.
-   Current categories are `seat`, `backrest`, and `armrest`.
-   Global logical axes are X=length, Z=width, Y=height.
-   Individual bodies may have different OBB axis orientations.
-   OBB mapping is therefore required.
-   Category dimensions use global AABBs.
-   Individual scaling is done along the OBB axis corresponding to the
    requested logical dimension.
-   Scaling is performed around the OBB center.
-   Seat length scaling targets overall sofa length, not seat length.
-   The seat absorbs the difference between target overall length and
    original overall length.
-   External bodies must then be positioned relative to the changed
    reference geometry.
-   Current attachment detection is center-based and works on the test
    model but is not generic.
-   Current movement uses reference-boundary changes.
-   `attached_bounds` exists in the current movement API but is not
    currently used.
-   The current `process_dimension()` can classify unrelated bodies
    against a reference category; this must be fixed for truly generic
    positioning.
-   Armrest and backrest scaling are not complete.
-   Do not rewrite the completed seat-length mathematics without a
    specific reason.
-   Do not introduce Fusion dependencies.

------------------------------------------------------------------------

# 50. Final Technical Summary

The external STEP approach is fundamentally:

``` text
STEP file
   |
   v
load STEP
   |
   v
extract solids + names
   |
   v
metadata -> seat/backrest/armrest
   |
   v
OBB analysis
   |
   v
map local OBB axes -> global logical dimensions
   |
   v
calculate assembly/category bounds
   |
   v
read target dimensions
   |
   v
calculate scaling factors
   |
   v
scale reference geometry around OBB centers
   |
   v
calculate actual reference-category growth
   |
   v
determine dependent bodies
   |
   v
move dependent bodies
   |
   v
repeat configured stages
   |
   v
export new STEP
```

The most important completed behavior is the **overall-length-aware seat
scaling**:

``` text
target overall length
        |
        v
target overall - original overall
        |
        v
apply that difference to seat length
        |
        v
scale seat
        |
        v
reposition external bodies
        |
        v
overall result approximately equals target
```

The remaining major engineering problem is **generic geometric
attachment/positioning**, followed by the other team members' backrest
and armrest scaling work.
