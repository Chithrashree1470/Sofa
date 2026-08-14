# Scale factors

Suppose user enters

```
Overall Length = 2400

Overall Depth = 900

Overall Height = 900
```

Phase 3

```
armrest.width_ratio = 0.12
armrest.depth_ratio = 0.43
armrest.height_ratio = 0.61
```

Target

```
Length

=
0.12 × 2400

=
288 mm
```

```
Depth

=
0.43 × 900

=
387 mm
```

```
Height

=
0.61 × 900

=
549 mm
```

Now compare against template

Template logical

```
Length

=
179.77+38.4

=
218.17
```

Depth

```
332.1
```

Height

```
821+12

=
833
```

Scale factors

```
ScaleX

=
288/218.17
```

```
ScaleY

=
387/332.1
```

```
ScaleZ

=
549/833
```

Every armrest body gets these three numbers.

---

# How should coordinates scale?

Don't scale center.

Don't scale min and max independently.

Scale relative to an origin.

Example

Current

```
base

minX = 813

maxX =1029
```

Length

```
216
```

After scaling

```
newLength

=
216×ScaleX
```

Keep

```
minX
```

fixed (or whichever reference you choose)

then

```
newMaxX

=
minX+newLength
```

Then

```
center

=
(min+max)/2
```

This avoids floating-point drift.

---

# How to verify your scaling

I would perform these checks after every scaling.

### ✔ Check 1

```
newL

≈

oldL×ScaleX
```

for every body.

---

### ✔ Check 2

```
newW

≈

oldW×ScaleY
```

---

### ✔ Check 3

```
newH

≈

oldH×ScaleZ
```

---

### ✔ Check 4

Bounding box

```
maxX-minX

==

newL
```

---

### ✔ Check 5

```
maxY-minY

==

newW
```

---

### ✔ Check 6

```
maxZ-minZ

==

newH
```

---

### ✔ Check 7

Center

```
centerX

=

(minX+maxX)/2
```

---

### ✔ Check 8

Merged armrest

```
top.L

+

top(1).L

≈

base.L
```

should still approximately hold after scaling.

---

# One suggestion

I would **not** update coordinates by simply multiplying them by the scale factor. That only works if the origin `(0,0,0)` is the scaling pivot.

Instead:

1. Choose a reference point for the armrest (for example, the `min_x`, `min_y`, `min_z` of the `armrest_base`).
2. Convert every coordinate to a local offset from that reference.
3. Scale the offsets with `ScaleX`, `ScaleY`, and `ScaleZ`.
4. Add the reference point back.

This preserves the relative arrangement of all five bodies and is how CAD systems typically handle grouped scaling. It's much more robust than scaling absolute coordinates directly.
