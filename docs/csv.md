# CSV Outputs

## 1. `component_dataset.csv`

**One row = One CAD body/component**

| Column                | Description                           |
| --------------------- | ------------------------------------- |
| Body                  | Unique body name                      |
| Category              | Seat, Backrest, Armrest, Spring, etc. |
| Appearance            | CAD appearance/material               |
| Visibility            | Internal / External                   |
| Measurement_Type      | Continuous / Discrete                 |
| Length, Width, Height | Bounding box dimensions               |
| Volume                | Component volume                      |
| Min/Max Coordinates   | Bounding box limits                   |
| Center Coordinates    | Component center position             |

---

## 2. `sofa_metadata.csv`

**One row = One sofa template**

| Column                  | Description                     |
| ----------------------- | ------------------------------- |
| Template_ID             | Unique sofa template ID         |
| Template_Name           | Template name                   |
| Sofa_Type               | Straight, L-shape, Chaise, etc. |
| Seat_Count              | Number of seats                 |
| Overall_Length          | Sofa length                     |
| Overall_Depth           | Sofa depth                      |
| Overall_Height          | Sofa height                     |
| Seat_Width              | Overall seat width              |
| Seat_Depth              | Seat depth                      |
| Seat_Height             | Seat height                     |
| Backrest_Height         | Backrest height                 |
| Armrest_Height          | Armrest height                  |
| Seat_Configuration      | Jointed / Separate              |
| Armrest_Frame_Material  | Wood / Metal                    |
| Backrest_Frame_Material | Wood / Metal                    |
| Fabric_Material         | Fabric type                     |
| Leg_Count               | Number of legs                  |
| Leg_Material            | Wood / Metal / Plastic          |

Here's a concise documentation table for your **`sofa_metadata.csv`**.

| Attribute                         | Description                                                                    | Derived From                                                                 |
| --------------------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| **Template_ID**                   | Unique identifier of the sofa template.                                        | Assigned manually.                                                           |
| **Template_Name**                 | Name of the CAD template.                                                      | CAD model / Fusion project name.                                             |
| **Sofa_Type**                     | Overall sofa category (Straight, L-shape, U-shape, etc.).                      | Manual classification or image processing.                                   |
| **Seat_Count**                    | Number of seating positions.                                                   | Manual / Image Processing (Module 2).                                        |
| **Overall_Length_mm**             | Total sofa length.                                                             | `fabric cover` → **L_mm** (bounding box).                                    |
| **Overall_Depth_mm** *(or Width)* | Total sofa depth (front to back).                                              | `fabric cover` → **W_mm** (bounding box).                                    |
| **Overall_Height_mm**             | Maximum height of the sofa.                                                    | `fabric cover` → **H_mm** (bounding box).                                    |
| **Armrest_Height_mm**             | Height of the armrest (prototype rule).                                        | **max(H_mm of left/right_armrest_top*) + H_mm of left/right_armrest_base**.  |
| **Backrest_Height_mm**            | Height of the visible backrest front.                                          | `backrest_front` → **H_mm**.                                                 |
| **Seat_Height_mm**                | Height of the seat surface from the ground.                                    | `seat_top` → **max_y_mm**.                                                   |
| **Seat_Width_mm**                 | Thickness (vertical section) of the seat top component (prototype definition). | `seat_top` → **W_mm**.                                                       |
| **Seat_Depth_mm**                 | Front face thickness of the seat (prototype definition).                       | `seat_front` → **H_mm**.                                                     |
| **Seat_Configuration**            | Indicates whether cushions are Jointed or Separate.                            | Manual.                                                                      |
| **Armrest_Frame_Material**        | Structural material inside armrest.                                            | Manual / Manufacturer data.                                                  |
| **Backrest_Frame_Material**       | Structural material inside backrest.                                           | Manual / Manufacturer data.                                                  |
| **Fabric_Material**               | Upholstery material.                                                           | Manual / Manufacturer data.                                                  |
| **Leg_Count**                     | Number of legs.                                                                | Manual or CAD count.                                                         |
| **Leg_Material**                  | Material of sofa legs.                                                         | Manual / Manufacturer data.                                                  |
| **Notes**                         | Additional comments about the template.                                        | Manual.                                                                      |

### Note on prototype-derived attributes

The following values are **prototype-specific engineering definitions** and are not standard furniture measurements:

* **Armrest_Height_mm** = `max(armrest_top H_mm) + armrest_base H_mm`
* **Seat_Width_mm** = `seat_top W_mm`
* **Seat_Depth_mm** = `seat_front H_mm`

These were chosen as consistent rules for your MVP and can be refined later if you decide to use more accurate geometric measurements.


---
