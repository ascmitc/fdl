# FDL Apply Template Logic

> Step-by-step description of the `CanvasTemplate.apply()` pipeline.
>
> **Implementation**: `native/core/src/fdl_template.cpp` (C++ core),
> exposed via `fdl_apply_canvas_template()` in `native/core/include/fdl/fdl_core.h`.
> Python and C++ RAII bindings call through to this C library.
>
> **FDL Spec Reference**: Section 7.4 -- Template Application Algorithm

---

## Overview

The template application algorithm takes a **source canvas** (with its framing decision)
and a **canvas template**, and produces a new output canvas with transformed geometry.
The algorithm processes all geometry layers through a linear pipeline:

```
Source Canvas + Template
        |
        v
  +----------------------+
  |  1. Derive Config     |
  |  2. Populate          |
  |  3. Hierarchy         |
  |  4. Scale Factor      |
  |  5. Scale & Round     |
  |  6. Output Size       |
  |  7. Alignment Shift   |
  |  8. Apply Offsets     |
  |  9. Crop to Visible   |
  | 10. Create Output     |
  +----------------------+
        |
        v
  Output Canvas + FDL
```

---

## Geometry Layers

FDL defines four nested layers from outermost to innermost. Each layer has
dimensions (width x height) and an anchor point (x, y) that positions it
relative to the canvas origin.

```
+--------------------------------------------------+
|  Canvas                                          |
|  +------------------------------------------+    |
|  |  Effective                               |    |
|  |  +----------------------------------+    |    |
|  |  |  Protection                      |    |    |
|  |  |  +--------------------------+    |    |    |
|  |  |  |  Framing                 |    |    |    |
|  |  |  +--------------------------+    |    |    |
|  |  +----------------------------------+    |    |
|  +------------------------------------------+    |
+--------------------------------------------------+
```

| Layer       | FDL Path                                | Anchor    | Description                                    |
|-------------|-----------------------------------------|-----------|------------------------------------------------|
| Canvas      | `canvas.dimensions`                     | (0, 0)    | Outermost -- the full sensor/image area         |
| Effective   | `canvas.effective_dimensions`           | yes       | Active image area within the canvas            |
| Protection  | `framing_decision.protection_dimensions`| yes       | Region with safety margin for cropping         |
| Framing     | `framing_decision.dimensions`           | yes       | Innermost -- the intended framing               |

The hierarchy must always satisfy: `canvas >= effective >= protection >= framing`.

---

## Pipeline Steps

### Step 1 -- Derive Configuration

**C++ implementation**: `fdl_template.cpp`, `apply_canvas_template()` lines 153-179

Read all template parameters and derive working values as local variables.
There is no separate context object -- values are computed once at the start
and threaded through helper functions via arguments.

Key derived values:

| Variable                  | Source                                    |
|---------------------------|-------------------------------------------|
| `fit_method`              | `template.fit_method` -- `fit_all`, `fill`, `width`, or `height` |
| `preserve_path`           | `template.preserve_from_source_canvas` -- outermost layer to keep |
| `target_dims`             | `template.target_dimensions` (as float) |
| `max_dims`, `has_max_dims`| `template.maximum_dimensions`                 |
| `pad_to_maximum`          | `template.pad_to_maximum` -- expand output to max dims |
| `h_align`, `v_align`      | `template.alignment_method_horizontal/vertical` |
| `input_squeeze`           | `source_canvas.anamorphic_squeeze` (default 1.0) |
| `target_squeeze`          | `template.target_anamorphic_squeeze` (default 1.0) |

---

### Step 2 -- Populate Source Geometry

**C++ implementation**: `fdl_template.cpp`, `populate_from_path()` + `populate_layer()`

Build a `fdl_geometry_t` by reading dimensions and anchors from the source
canvas and framing decision. Two template paths control what is read:

1. **`preserve_from_source_canvas`** -- the outermost layer to keep (e.g.
   `canvas.effective_dimensions`). Populates this level and all layers
   below it in the hierarchy.
2. **`fit_source`** -- the layer that will be fitted to the target (e.g.
   `framing_decision.dimensions`). Populates this level and all layers
   below it, overwriting any overlap with preserve.

Both paths are validated against the source FDL using
`fdl_resolve_geometry_layer()` -- if the source does not have the referenced
layer, an error is raised.

After population, the geometry is **validated**: framing dimensions must
not be zero, and effective must not be smaller than protection.

---

### Step 3 -- Fill Hierarchy Gaps

**C API**: `fdl_geometry_fill_hierarchy_gaps()`
**C++ implementation**: `fdl_geometry.cpp`, `geometry_fill_hierarchy_gaps()`

After population, some layers may be zero (not present in the source). The
hierarchy is completed by propagating the outermost populated layer upward:

- If only **framing** is populated: canvas and effective become framing.
- If **protection** is populated: canvas and effective become protection.
- If **effective** is populated: canvas becomes effective.
- If **canvas** is populated: everything stays.

**Special rule**: Protection is **never** filled from framing. If protection
was not explicitly provided, it stays zero (absent).

**Anchor offset**: All anchors are made relative to the outermost reference
anchor. If `preserve_from_source_canvas` is specified, its anchor is the
reference; otherwise the `fit_source` anchor is used. This offset is
subtracted from all anchors so they represent positions relative to the
new canvas origin.

The function also returns the `fit_dims` (dimensions of the fit_source
layer before scaling) for use in the next step.

---

### Step 4 -- Compute Scale Factor

**C API**: `fdl_calculate_scale_factor()`
**C++ implementation**: `fdl_pipeline.cpp`, `calculate_scale_factor()`

Calculate the single uniform scale factor that transforms the fit_source
dimensions to match the template's target dimensions.

Both fit and target dimensions are first **normalized** by their respective
anamorphic squeeze factors to produce square-pixel equivalents (via
`fdl_dimensions_normalize()`):

```
normalized_width = width * anamorphic_squeeze
```

The scale factor is then determined by the `fit_method`:

| Method    | Formula                                        | Behaviour                          |
|-----------|------------------------------------------------|------------------------------------|
| `fit_all` | `min(target_w / fit_w, target_h / fit_h)`      | Fits entirely within target        |
| `fill`    | `max(target_w / fit_w, target_h / fit_h)`      | Fills target completely (may crop) |
| `width`   | `target_w / fit_w`                              | Fits width exactly                 |
| `height`  | `target_h / fit_h`                              | Fits height exactly                |

---

### Step 5 -- Scale and Round

**C API**: `fdl_geometry_normalize_and_scale()` + `fdl_geometry_round()`
**C++ implementation**: `fdl_geometry.cpp`

Apply the scale factor to **all** dimensions and anchors uniformly.

**Normalize and scale** (per value):

```
scaled_value = (source_value * source_squeeze * scale_factor) / target_squeeze
```

This converts from source pixel space through square-pixel space to target
pixel space in one operation.

**Round** all dimensions and anchors according to the template's `RoundStrategy`:

| Setting | Behaviour                                    |
|---------|----------------------------------------------|
| `even`  | Round to the nearest even integer             |
| `whole` | Round to the nearest integer                  |
| `up`    | Always round up (ceiling)                     |
| `down`  | Always round down (floor)                     |
| `round` | Standard rounding (half-up)                   |

After rounding, all dimensions and anchors are clean integers (stored as
float for pipeline consistency).

**Extract scaled values** for use in later steps:

- `scaled_fit` -- fit_source dimensions after scale+round
- `scaled_fit_anchor` -- fit_source anchor after scale+round
- `scaled_bounding_box` -- canvas dimensions (the full bounding box)

---

### Step 6 -- Determine Output Size (per axis)

**C API**: `fdl_output_size_for_axis()`
**C++ implementation**: `fdl_pipeline.cpp`, `output_size_for_axis()`

For each axis independently, determine the final output canvas size. Three
modes exist:

| Mode   | Condition                         | Output size   | Description                        |
|--------|-----------------------------------|---------------|------------------------------------|
| **PAD**  | `has_max_dims` and `pad_to_maximum` | `max_dims`    | Expand to maximum dimensions       |
| **CROP** | `has_max_dims` and `canvas > max`   | `max_dims`    | Clamp canvas to maximum            |
| **FIT**  | No max constraint                   | `canvas`      | Use canvas as-is                   |

Note: each axis is evaluated independently -- one axis may PAD while the
other CROPs.

---

### Step 7 -- Calculate Alignment Shift (per axis)

**C API**: `fdl_alignment_shift()`
**C++ implementation**: `fdl_pipeline.cpp`, `alignment_shift()`

Alignment factors: `left/top = 0.0`, `center = 0.5`, `right/bottom = 1.0`.

Calculate the content translation (how many pixels to shift the entire
scaled content) for each axis. This is where PAD, CROP, and alignment
are unified into a single formula.

#### FIT regime

If `output == canvas` and `pad_to_maximum` is off: no shift is needed.
The geometry is already correctly positioned from the hierarchy and scaling
steps. **Return 0.**

#### PAD / CROP regime (unified)

The shift is the sum of three independent offsets:

```
shift = target_offset + alignment_offset - fit_anchor
```

**1. Target offset** -- where the target region starts in the output:

```
center_target = pad_to_maximum OR is_center
target_offset = (output_size - target_size) * 0.5   if center_target
              = 0                                    otherwise
```

When padding (`pad_to_maximum`), the target region is always centred in the
larger output canvas. When using centre alignment, centring in the output is
mathematically equivalent. When neither applies, the target sits at the
output origin.

**2. Alignment offset** -- where the fit sits within the target:

```
gap = target_size - fit_size
alignment_offset = gap * align_factor
```

| Alignment    | `align_factor` | Fit position within target     |
|--------------|----------------|--------------------------------|
| left / top   | 0.0            | Snapped to left/top edge       |
| center       | 0.5            | Centred                        |
| right / bottom | 1.0          | Snapped to right/bottom edge   |

When `gap > 0`, the fit is smaller than the target and there is room.
When `gap < 0`, the fit is larger (overflow), and alignment determines
which part is visible.

**3. Fit anchor compensation** -- `-fit_anchor`:

The fit_source may not start at position (0, 0) within the bounding box.
The fit_anchor is the offset from the canvas origin to the fit_source
origin. This is subtracted to align the fit_source itself (not the
bounding box).

#### Clamp for crop

When cropping without padding (`pad_to_maximum` is off and `overflow > 0`),
the content must fill the entire output -- no empty space allowed. The shift
is clamped:

```
shift = max(min(shift, 0.0), -overflow)
```

This ensures:
- `shift <= 0` : content starts at or before the output origin (no left gap)
- `shift >= -overflow` : content extends to or beyond the output end (no right gap)

---

### Step 8 -- Apply Offsets to Anchors

**C API**: `fdl_geometry_apply_offset()`
**C++ implementation**: `fdl_geometry.cpp`, `geometry_apply_offset()`

The content translation calculated in step 7 is applied to **all** anchor
points (effective, protection, framing):

```
new_anchor = original_anchor + content_translation
```

This produces two versions of each anchor:

- **Clamped anchors** (stored in the geometry): `max(new_anchor, 0)` -- used
  in the output FDL where anchors cannot be negative.
- **Theoretical anchors** (returned separately): the raw unclamped values --
  used in the next step to calculate how much of each layer is visible.

Theoretical anchors can be **negative** when content extends off the left/top
edge of the output canvas (e.g. right-aligned crop).

---

### Step 9 -- Crop to Visible

**C API**: `fdl_geometry_crop()`
**C++ implementation**: `fdl_geometry.cpp`, `geometry_crop()`

Calculate the **visible portion** of each layer within the output canvas.
This is not a destructive pixel crop -- it computes what part of each
geometry layer falls within the canvas boundaries.

For each layer, the visible dimensions are:

```
clip_left    = max(0, -theoretical_anchor.x)
clip_top     = max(0, -theoretical_anchor.y)
visible_w    = dims.width - clip_left
visible_h    = dims.height - clip_top
visible_w    = min(visible_w, canvas.width - clamped_anchor.x)
visible_h    = min(visible_h, canvas.height - clamped_anchor.y)
```

After individual clipping, the **hierarchy is enforced**:

```
effective  = min(effective, canvas)
protection = min(protection, effective)     (if protection exists)
framing    = min(framing, protection or effective)
```

This ensures inner layers never exceed their parent boundaries.

**Example** -- right-aligned crop with 400px overflow:

```
                    Output Canvas (3840px)
        +-------------------------------------------+
        |                                           |
    +---+   visible portion of content              |
    |   |                                           |
    +---+                                           |
        |                                           |
        +-------------------------------------------+
    ^
    400px clipped (theoretical_anchor.x = -400)
```

---

### Step 10 -- Create Output FDL

**C++ implementation**: `fdl_template.cpp`, lines 298-473

Assemble the final output objects from the processed geometry:

1. **New Canvas**: dimensions from geometry, effective dimensions and anchor,
   anamorphic squeeze from the target, linked to the source canvas via
   `source_canvas_id`.

2. **New Framing Decision**: framing dimensions and anchor from geometry,
   protection dimensions and anchor (if present), linked to the source
   framing intent.

3. **Custom Attributes**: `_scale_factor`, `_scaled_bounding_box`, and
   `_content_translation` are stored on the output canvas for use by
   image processing pipelines.

4. **New Context**: contains both the source canvas (for reference) and the
   new output canvas.

5. **New FDL**: wraps the context, a default framing intent, and the
   applied template.

The C API returns a `fdl_template_result_t` containing the output FDL
document and IDs for resolving the created context, canvas, and framing
decision. Python wraps this as `TemplateResult` with convenience properties.

---

## Complete Formula Reference

For a single axis, the full content translation calculation is:

```
# Inputs
canvas_size  = scaled bounding box on this axis
target_size  = template target dimensions on this axis
fit_size     = scaled fit_source dimensions on this axis
fit_anchor   = scaled fit_source anchor on this axis
output_size  = final output canvas size (from step 6)
align_factor = 0.0 (left/top), 0.5 (center), 1.0 (right/bottom)

# Output size (step 6)
if has_max and pad_to_max:   output_size = max_size
elif has_max and canvas > max: output_size = max_size
else:                          output_size = canvas_size

# Content translation (step 7)
overflow = canvas_size - output_size

if overflow == 0 and not pad_to_max:
    shift = 0                                           # FIT

else:
    center_target = pad_to_max or is_center
    target_offset = (output - target) * 0.5  if center_target  else 0
    gap             = target_size - fit_size
    alignment       = gap * align_factor
    shift           = target_offset + alignment - fit_anchor

    if not pad_to_max and overflow > 0:                 # Clamp for crop
        shift = max(min(shift, 0), -overflow)
```
