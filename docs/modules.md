Input Image
      │
      ▼
Module 2
Image Processing
      │
      ▼
Extract Ratios
(back height ratio,
arm width ratio,
seat depth ratio,
etc.)
      │
      ▼
Module 3
Measurement Scaling
      │
      ▼
Scaled dimensions for every body
      │
      ▼
Module 4
Internal Component Prediction
      │
      ▼
Frame dimensions
Foam dimensions
Fabric dimensions
      │
      ▼
Module 5
BOM Generation
      │
      ▼
Cost Estimate

(Optional)
      │
      ▼
Module 6
Generate Fusion360 model


Here's a concise project summary you can send to your team.

---

# Sofa Cost Estimation System – Module Overview (Prototype v1)

## Objective

Given:

* A sofa image
* Overall sofa dimensions (Length, Depth, Height)

Estimate the internal components and generate a Bill of Materials (BOM) and cost using a CAD template.

---

# Module 1 – CAD Knowledge Extraction

### Purpose

Extract engineering information from a master CAD template (Fusion 360 for the prototype).

### Input

* CAD template (.f3z)

### Output

#### 1. `component_dataset.csv`

One row per body/component.

Contains:

* Body name
* Category
* Appearance
* Visibility (Internal/External)
* Measurement Type (Continuous/Discrete)
* Dimensions
* Volume
* Coordinates

#### 2. `sofa_metadata.csv`

One row per sofa template.

Contains:

* Template ID
* Sofa Type
* Seat Count
* Overall dimensions
* Seat Configuration
* Armrest Frame Material
* Backrest Frame Material
* Fabric Material
* Leg Count
* Leg Material

**Note:** Prototype uses the Fusion API. Later versions may use STEP files instead.

---

# Module 2 – Image Processing

### Purpose

Extract only the **visible external components** from a sofa image.

**Foam is considered visible** (fabric thickness ignored in Version 1).

### Input

* Sofa image
* Overall Length
* Overall Depth
* Overall Height

### Output (JSON)

Contains:

### Sofa Properties

* Sofa Type
* Seat Count
* Seat Configuration
* Leg Count
* Armrest Frame Material
* Backrest Frame Material
* Fabric Material
* (Optional) Leg Material

### Component Ratios

* Seat dimensions
* Backrest dimensions
* Armrest dimensions

Outputs are **dimension ratios**, not absolute measurements.

Example:

```json
{
  "seat": {
    "width_ratio": 0.78,
    "depth_ratio": 0.42,
    "height_ratio": 0.21
  }
}
```

---

# Module 3 – Measurement Scaling

### Purpose

Convert the ratios from Module 2 into real measurements using the user-provided sofa dimensions.

### Input

* JSON from Module 2
* component_dataset.csv
* Overall sofa dimensions

### Output

Scaled dimensions for every external component.

Example:

* Seat width
* Armrest height
* Backrest thickness

Future versions will also include rule-based scaling.

---

# Module 4 – Internal Component Prediction

### Purpose

Predict the internal structure based on the scaled external measurements.

Examples:

* Wood frame
* Springs
* Belts
* Clips
* Foam
* Internal support members

This module will use engineering rules such as:

* Add 2 clips every 50 mm
* Add 1 spring every 120 mm
* Stretch wood frame continuously
* Maintain fixed leg count

Outputs complete measurements and quantities of all internal components.

---

# Module 5 – BOM Generation

### Purpose

Generate the complete Bill of Materials.

Uses:

* Component dimensions
* Component quantities
* Material information

Outputs:

* Material list
* Quantities
* Volumes
* Estimated manufacturing cost

---

# Module 6 (Optional) – CAD Generation

### Purpose

Automatically generate a new CAD model using the scaled measurements.

Input:

* Predicted component dimensions

Output:

* New Fusion/STEP model of the scaled sofa

---

# Overall Pipeline

```text
CAD Template
      │
      ▼
Module 1
CAD Knowledge Extraction
      │
      ├── component_dataset.csv
      └── sofa_metadata.csv
                │
                ▼
         Sofa Image
      + User Dimensions
                │
                ▼
Module 2
Image Processing
(JSON Output)
                │
                ▼
Module 3
Measurement Scaling
                │
                ▼
Module 4
Internal Component Prediction
                │
                ▼
Module 5
BOM Generation
                │
                ▼
(Optional)
Module 6
CAD Model Generation
```

### Team Notes

* **Module 2 should be treated as a black box.** It can use any computer vision technique (YOLO, SAM, Detectron2, OpenCV, etc.), as long as it produces the agreed JSON output.
* **Module 3 onward should not depend on Fusion 360.** They should only consume the CSVs from Module 1 and the JSON from Module 2.
* The prototype uses **Fusion API** only to build the initial datasets. Later, Module 1 can be replaced with a **STEP-based extractor** without changing the rest of the pipeline.
