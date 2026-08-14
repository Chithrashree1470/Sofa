# Module 4 – Internal Component Prediction & Scaling (Prototype v1)

## Purpose

Module 4 predicts the dimensions and quantities of the **internal components** of a sofa using the scaled external dimensions produced by Module 3.

The scaling is based on the **selected CAD template**. Currently, only one CAD template exists, so no template selection is performed. In future versions, the most similar CAD template will be selected before this module executes.

---

# Inputs

Module 4 receives the following inputs:

1. `scaled_external.json` (Output of Module 3)
2. `component_dataset.csv`
3. `sofa_metadata.csv`
4. Selected CAD Template

---

# Output

Return a JSON named:

```text
scaled_internal.json
```

The JSON should contain the predicted dimensions and quantities of all internal components.

---

# General Assumptions

1. The engineering relationships in the selected CAD template are assumed to be correct.

2. Internal components are inferred from the scaled external components.

3. Two types of scaling exist:

- Continuous Scaling
- Discrete Scaling

4. Continuous components change their dimensions.

5. Discrete components usually change their quantity.

6. Every component should preserve the engineering proportions of the selected CAD template.

---

# Continuous Components

## 1. Wood Frame

### Related External Components

- Seat
- Backrest
- Left Armrest
- Right Armrest

### Scaling Rule

The wood frame scales continuously with its corresponding external component.

Examples:

- Seat frame ← Seat
- Backrest frame ← Backrest
- Left arm frame ← Left armrest
- Right arm frame ← Right armrest

The proportions from the selected CAD template should be preserved.

---

## 2. Cushion (Foam)

### Related External Component

Seat

### Scaling Rule

The cushion dimensions are inferred from the scaled seat dimensions.

For Prototype v1:

> Foam dimensions are assumed to be equal to the visible upholstered seat dimensions.

Fabric thickness is ignored.

### Future Improvement

Estimate fabric thickness and subtract it from the external dimensions before computing foam dimensions.

---

## 3. Left Handle Frame

### Related External Component

Left Armrest

### Scaling Rule

Scale proportionally with the Left Armrest.

---

## 4. Right Handle Frame

### Related External Component

Right Armrest

### Scaling Rule

Scale proportionally with the Right Armrest.

---

# Discrete Components

## 1. Clips

### Related External Component

Seat

### Scaling Rule

The number of clips depends on the seat length.

Determine the clip density from the selected CAD template.

```
clip_density =

(number of clips in template)

/

(template seat length)
```

Then estimate

```
Estimated Clip Count =

round(

clip_density × scaled seat length

)
```

The clips should remain approximately equally spaced.

### Future Improvement

Replace the density rule with manufacturer specifications if available.

---

## 2. Springs

### Related External Component

Seat

### Scaling Rule

The number of springs depends on the seat length.

Determine the spring density from the selected CAD template.

```
spring_density =

(number of springs in template)

/

(template seat length)
```

Estimate

```
Estimated Spring Count =

round(

spring_density × scaled seat length

)
```

Maintain approximately uniform spacing.

---

# Components Requiring Validation

These rules are assumptions and should be verified with the manufacturer.

---

## Seat Belts

### Related External Component

Seat

Seat belts are elastic support belts.

Possible dependencies include:

- Seat width
- Cushion weight
- Number of springs

### Current Prototype Rule

Scale according to seat width only.

### To Be Verified

Determine whether:

- only the belt length changes

or

- both belt quantity and length change.

---

## Backrest Belts

### Related External Component

Backrest

Backrest belts are elastic support belts.

Possible dependencies include:

- Backrest width
- Backrest height

### Current Prototype Rule

Scale according to backrest dimensions.

### To Be Verified

Determine whether:

- only belt length changes

or

- belt quantity also changes.

---

# General Constraints

The implementation should satisfy the following constraints:

- Preserve left/right symmetry.
- Preserve component orientation.
- Preserve the proportions of the selected CAD template.
- Never generate negative dimensions.
- Never generate zero dimensions.
- Quantities must always be positive integers.
- Do not create component types that are not present in the selected CAD template.

---

# Future Improvements

The following features are outside the scope of Prototype v1.

- Similar CAD template retrieval before scaling.
- Manufacturer-provided engineering rules.
- Weight-based cushion estimation.
- Fabric thickness compensation.
- Material-specific scaling rules.
- Constraint-based optimization between neighbouring components.
- Support for asymmetric sofa templates.

---

# Implementation Notes

The implementation should **not** hardcode engineering constants.

Instead, engineering rules such as clip density, spring density, belt spacing and future material-specific rules should be stored separately (for example in a JSON/YAML configuration file). Module 4 should behave as a rule engine that reads these rules rather than embedding them directly in code. This will make the system easier to maintain and easier to extend when additional sofa templates are added.