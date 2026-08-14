# External Scaling Proposal (Phase 4A)

## Objective

Improve the external component scaling algorithm so that it preserves realistic sofa proportions by using logical furniture measurements instead of uniformly scaling every body with the overall sofa dimensions.

---

# CSV Inputs

## 1. `renamed_sofa_component.csv`

**One row = One CAD body/component**

| Column             | Description                           |
| ------------------ | ------------------------------------- |
| Body               | Unique body name                      |
| Category           | Seat, Backrest, Armrest, Spring, etc. |
| Appearance         | CAD appearance/material               |
| Visibility         | Internal / External                   |
| Measurement_Type   | Continuous / Discrete                 |
| Length             | Bounding box length                   |
| Width              | Bounding box width                    |
| Height             | Bounding box height                   |
| Volume             | Component volume                      |
| Min Coordinates    | Bounding box minimum coordinates      |
| Max Coordinates    | Bounding box maximum coordinates      |
| Center Coordinates | Component center position             |

---

## 2. `sofa_metadata.csv`

**One row = One sofa template**

| Column                  | Description                     |
| ----------------------- | ------------------------------- |
| Template_ID             | Unique sofa template ID         |
| Template_Name           | Template name                   |
| Sofa_Type               | Straight, L-shape, Chaise, etc. |
| Seat_Count              | Number of seating positions     |
| Overall_Length_mm       | Sofa length                     |
| Overall_Depth_mm        | Sofa depth                      |
| Overall_Height_mm       | Sofa height                     |
| Seat_Width_mm           | Overall seat width              |
| Seat_Depth_mm           | Seat depth                      |
| Seat_Height_mm          | Seat height                     |
| Backrest_Height_mm      | Backrest height                 |
| Armrest_Height_mm       | Armrest height                  |
| Seat_Configuration      | Jointed / Separate              |
| Armrest_Frame_Material  | Armrest frame material          |
| Backrest_Frame_Material | Backrest frame material         |
| Fabric_Material         | Upholstery material             |
| Leg_Count               | Number of legs                  |
| Leg_Material            | Material of sofa legs           |
| Notes                   | Additional template notes       |

---

# Proposed Scaling Rules

| **Body**                                                         | **Scaling Rules**                                                                                                                                                                                                    | **Data Used**                                                                                                            |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **seat_top**                                                     | **X:** Scale normally using template body length.<br>**Y:** Keep constant.<br>**Z:** Scale normally using template body width.                                                                                       | **X, Z:** `Length`, `Width` → `component_dataset.csv`                                                                    |
| **seat_front**                                                   | **X:** Scale normally using template body length.<br>**Y:** Scale using target **Seat_Height**.<br>**Z:** Keep constant.                                                                                             | **Y:** `Seat_Height_mm` → `sofa_metadata.csv`<br>Template body dimensions → `component_dataset.csv`                      |
| **backrest_back**                                                | **X:** Scale normally.<br>**Y:** Scale using **Overall_Height** .<br>**Z:** Keep constant.                                                                                                                           | **Y:** `Overall_Height_mm`, `Seat_Height_mm` → `sofa_metadata.csv`<br>Template body dimensions → `component_dataset.csv` |
| **backrest_front**                                               | **X:** Scale normally.<br>**Y:** Scale using **Overall_Height − Seat_Height**.<br>**Z:** Keep constant.                                                                                                              | **Y:** `Overall_Height_mm`, `Seat_Height_mm` → `sofa_metadata.csv`<br>Template body dimensions → `component_dataset.csv` |
| **armrest_base + armrest_front** _(treated as one logical body)_ | **Logical Y:** Scale total armrest height using **Armrest_Height**. Distribute the scaled height between base and front proportionally.<br>**X, Z:** Scale normally.<br>**armrest_top:** Not considered for scaling. | **Y:** `Armrest_Height_mm` → `sofa_metadata.csv`<br>Template body dimensions → `component_dataset.csv`                   |

**Note**

- In the table above, **X = logical length**, **Y = logical height**, and **Z = logical width** only for describing the scaling rules.
- These do **not** necessarily correspond to Fusion's local X/Y/Z axes. Some bodies have different local axis mappings, so the implementation must apply the rules according to each body's verified axis mapping from the CAD model.

---

# Detailed Explanation of the Rules

## Seat Top

The seat top behaves like the horizontal cushion of the sofa. Its thickness remains unchanged, while its logical length (X) and logical width (Z) scale normally using the template body dimensions.

## Seat Front

The seat front represents the visible front panel beneath the cushion.

- X scales normally using the template body length.
- Y scales using `Seat_Height_mm` from `sofa_metadata.csv`.
- Z remains unchanged.

This allows the seat front and seat top to continue behaving like a cuboid while maintaining realistic proportions.

## Backrest (Front and Back)

The visible backrest height is calculated as:

`Overall_Height_mm - Seat_Height_mm`

Both `backrest_front` and `backrest_back` use this value for logical Y scaling.

- X scales normally.
- Y scales using the calculated backrest height.
- Z remains unchanged.

## Armrest

`armrest_base` and `armrest_front` are treated as one logical component.

The combined logical height is obtained from:

`Armrest_Height_mm`

The total height is then distributed between the two bodies while preserving their original proportions.

`armrest_top` is excluded from scaling in the current MVP.

---

# Body Placement rules:

| Component                  | Anchor / Placement Rule                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Backrest Back**          | Start from the **overall sofa max Y** (user-entered overall height). Build downward.                                            |
| **Backrest Front**         | Also start from the **overall sofa max Y**. Its bottom is determined by the seat height and backrest thickness. Build downward. |
| **Seat Front**             | Positioned using the **seat height** from the sofa metadata. Build downward from the seat height.                               |
| **Seat Top**               | Its Y position is exactly the **seat height** stored in the sofa metadata.                                                      |
| **Armrests**               | Positioned beside the seat and backrest, not independently from template coordinates.                                           |
| **Seat & Backrest Length** | Assume they are equal unless a specific sofa template overrides this.                                                           |

---

| **Body**                | **Placement Rule**                                                                                                                           |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **seat_top**            | Center of sofa. Bottom face touches the top face of `seat_front`.                                                                            |
| **seat_front**          | Centered along X. Front face defines the front of the sofa (minimum Y). Top face touches the bottom of `seat_top`.                           |
| **backrest_back**       | Bottom face sits on top of `seat_top`. Front face touches the back face (maximum Y) of `seat_top`. Centered along X.                         |
| **backrest_front**      | Bottom face sits on top of `seat_top`. Back face touches the front face of `backrest_back`. Centered along X.                                |
| **left_armrest_base**   | Left face aligned with sofa minimum X. Inner face touches the left face of `seat_top`. Bottom aligned with ground.                           |
| **right_armrest_base**  | Right face aligned with sofa maximum X. Inner face touches the right face of `seat_top`. Bottom aligned with ground.                         |
| **left_armrest_front**  | Bottom face sits on top of `left_armrest_base`. Outer face flush with left side of `left_armrest_base`. Front face flush with sofa front.    |
| **right_armrest_front** | Bottom face sits on top of `right_armrest_base`. Outer face flush with right side of `right_armrest_base`. Front face flush with sofa front. |

# Current Scope

This proposal only defines body scaling rules.

Body placement, coordinate updates, local axis mapping, and Fusion reconstruction will be addressed in a later phase.
