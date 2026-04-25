// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_geometry.cpp
 * @brief Geometry operations on the 4-layer FDL dimension hierarchy.
 *
 * The FDL hierarchy is: canvas >= effective >= protection >= framing.
 * This module provides the transformations applied during template application:
 *
 * - **Gap-filling**: Propagates populated dimensions upward to fill missing layers.
 *   Protection is never auto-filled from framing (by spec).
 * - **Normalize+scale**: Applies anamorphic correction and uniform scaling using
 *   ratio-based arithmetic (multiply before divide) to preserve precision for
 *   scale factors that are not exactly representable in IEEE 754.
 * - **Round**: Rounds all 7 fields (4 dimensions + 3 anchors) per strategy.
 * - **Offset**: Translates anchors for alignment, tracking theoretical positions.
 * - **Crop**: Clips dimensions to visible portion within canvas bounds,
 *   enforcing the hierarchy invariant.
 */
#include "fdl_geometry.h"

#include "fdl_constants.h"

#include <algorithm>
#include <cmath>

namespace fdl::detail {

namespace {

/**
 * @brief Normalize and scale dimensions using ratio (num/den) for precision.
 */
fdl_dimensions_f64_t dims_normalize_and_scale_ratio(
    fdl_dimensions_f64_t dims, double input_squeeze, double num, double den, double target_squeeze) {
    return {(dims.width * input_squeeze * num) / (den * target_squeeze), (dims.height * num) / den};
}

/**
 * @brief Normalize and scale a point using ratio (num/den) for precision.
 */
fdl_point_f64_t point_normalize_and_scale_ratio(
    fdl_point_f64_t pt, double squeeze, double num, double den, double target_squeeze) {
    fdl_point_f64_t const normalized = fdl_point_normalize(pt, squeeze);
    return {(normalized.x * num) / (den * target_squeeze), (normalized.y * num) / den};
}

/**
 * @brief Clamp dimensions to not exceed given bounds.
 * @param dims        Dimensions to clamp.
 * @param clamp_dims  Maximum allowed dimensions.
 * @return Dimensions with each axis clamped to the corresponding bound.
 */
fdl_dimensions_f64_t dims_clamp_to_dims(fdl_dimensions_f64_t dims, fdl_dimensions_f64_t clamp_dims) {
    return {
        std::min(dims.width, clamp_dims.width),
        std::min(dims.height, clamp_dims.height),
    };
}

} // namespace

fdl_geometry_t geometry_fill_hierarchy_gaps(fdl_geometry_t geo, fdl_point_f64_t anchor_offset) {

    auto canvas = geo.canvas_dims;
    auto effective = geo.effective_dims;
    auto protection = geo.protection_dims;
    auto framing = geo.framing_dims;

    auto effective_anchor = geo.effective_anchor;
    auto protection_anchor = geo.protection_anchor;
    auto framing_anchor = geo.framing_anchor;

    // Determine the reference dimension and anchor for propagation.
    // Go from outermost to innermost to find the first populated layer.
    fdl_dimensions_f64_t reference_dims;
    fdl_point_f64_t reference_anchor;

    if (fdl_dimensions_is_zero(canvas) == 0) {
        reference_dims = canvas;
        reference_anchor = {0.0, 0.0};
    } else if (fdl_dimensions_is_zero(effective) == 0) {
        reference_dims = effective;
        reference_anchor = effective_anchor;
    } else if (fdl_dimensions_is_zero(protection) == 0) {
        reference_dims = protection;
        reference_anchor = protection_anchor;
    } else {
        // Only framing populated. Protection is NEVER filled from framing.
        reference_dims = framing;
        reference_anchor = framing_anchor;
    }

    // Fill canvas if zero
    if (fdl_dimensions_is_zero(canvas) != 0) {
        canvas = reference_dims;
    }

    // Fill effective if zero
    if (fdl_dimensions_is_zero(effective) != 0) {
        effective = reference_dims;
        effective_anchor = reference_anchor;
    }

    // Protection is NEVER filled from framing — stays zero if not provided.

    // Subtract anchor_offset and clamp >= 0
    effective_anchor = fdl_point_sub(effective_anchor, anchor_offset);
    protection_anchor = fdl_point_sub(protection_anchor, anchor_offset);
    framing_anchor = fdl_point_sub(framing_anchor, anchor_offset);

    effective_anchor = fdl_point_clamp(effective_anchor, 0.0, 0.0, FDL_TRUE, FDL_FALSE);
    protection_anchor = fdl_point_clamp(protection_anchor, 0.0, 0.0, FDL_TRUE, FDL_FALSE);
    framing_anchor = fdl_point_clamp(framing_anchor, 0.0, 0.0, FDL_TRUE, FDL_FALSE);

    return {
        canvas,
        effective,
        protection,
        framing,
        effective_anchor,
        protection_anchor,
        framing_anchor,
    };
}

fdl_geometry_t geometry_normalize_and_scale_ratio(
    fdl_geometry_t geo,
    double source_squeeze,
    double scale_numerator,
    double scale_denominator,
    double target_squeeze) {

    return {
        dims_normalize_and_scale_ratio(
            geo.canvas_dims, source_squeeze, scale_numerator, scale_denominator, target_squeeze),
        dims_normalize_and_scale_ratio(
            geo.effective_dims, source_squeeze, scale_numerator, scale_denominator, target_squeeze),
        dims_normalize_and_scale_ratio(
            geo.protection_dims, source_squeeze, scale_numerator, scale_denominator, target_squeeze),
        dims_normalize_and_scale_ratio(
            geo.framing_dims, source_squeeze, scale_numerator, scale_denominator, target_squeeze),
        point_normalize_and_scale_ratio(
            geo.effective_anchor, source_squeeze, scale_numerator, scale_denominator, target_squeeze),
        point_normalize_and_scale_ratio(
            geo.protection_anchor, source_squeeze, scale_numerator, scale_denominator, target_squeeze),
        point_normalize_and_scale_ratio(
            geo.framing_anchor, source_squeeze, scale_numerator, scale_denominator, target_squeeze),
    };
}

fdl_geometry_t geometry_round(fdl_geometry_t geo, fdl_round_strategy_t strategy) {
    // Rounds integer-typed schema fields (canvas.dimensions,
    // canvas.effective_dimensions) and clamps every layer inside the rounded
    // canvas.  Inner dimensions (protection, framing) and all anchors remain
    // float per the "fractional pixels" model; they are only clamped down if
    // they would exceed the rounded canvas.
    //
    // Called once at the end of the template pipeline (post-crop).  Every
    // anchor at this point already encodes the template's intent (scale,
    // alignment, padding, crop); rounding deltas are distributed
    // symmetrically (delta/2) so there is no directional bias.
    //
    // Each dimension is rounded at most once: effective by `ceil(float_eff)`
    // in step 3, inner layers not at all.  When effective's ceil would
    // overflow the canvas at its anchor, the ANCHOR is pulled back (step 4)
    // rather than the dim being shrunk — a sub-pixel slide is cheaper than
    // losing a full integer pixel.  For inner layers (float) the DIM is
    // shrunk (step 5) to preserve the anchor position.
    //
    // Steps:
    //   1. Round canvas per strategy.even / strategy.mode.
    //   2. Absorb rounding deltas into anchors (symmetric distribution):
    //        - all anchors shift by +canvas_delta/2 so content stays centered;
    //        - effective anchor additionally shifts by -eff_ceil_delta/2 so
    //          the effective rectangle stays centered on its pre-ceil float
    //          position.
    //   3. Integerize effective: `min(ceil(float_eff), canvas)`.  This is
    //      the sole integer round for effective.
    //   4. Clamp anchors.  Effective anchor clamps to [0, canvas - dim]
    //      (preserves the integer dim from step 3).  Inner anchors clamp
    //      to [0, canvas] so step 5 can shrink the dim at a valid anchor.
    //   5. Shrink inner dims to fit at their anchors: protection / framing
    //      = min(float_dim, canvas - anchor).  Float, no rounding.
    //   6. Re-establish hierarchy: clamp protection / framing down to
    //      effective only when they exceed it (preserves 0 = "unset").
    fdl_dimensions_f64_t const float_canvas = geo.canvas_dims;
    fdl_dimensions_f64_t const float_eff = geo.effective_dims;

    // 1) Round canvas per strategy.
    geo.canvas_dims = fdl_round_dimensions(float_canvas, strategy.even, strategy.mode);

    // 2) Symmetric anchor absorption.
    //    2a) Canvas delta shifts every anchor by +canvas_delta/2.
    double const canvas_dw = geo.canvas_dims.width - float_canvas.width;
    double const canvas_dh = geo.canvas_dims.height - float_canvas.height;
    geo.effective_anchor.x += canvas_dw / 2.0;
    geo.effective_anchor.y += canvas_dh / 2.0;
    geo.protection_anchor.x += canvas_dw / 2.0;
    geo.protection_anchor.y += canvas_dh / 2.0;
    geo.framing_anchor.x += canvas_dw / 2.0;
    geo.framing_anchor.y += canvas_dh / 2.0;
    //    2b) Effective ceil grows the box by up to 1 px; shift its anchor by
    //        -ceil_delta/2 so the rectangle stays centered on the original
    //        float center.  ceil_delta ≥ 0 always, so this pulls the anchor
    //        toward the origin.
    double const eff_ceil_dw = std::ceil(float_eff.width) - float_eff.width;
    double const eff_ceil_dh = std::ceil(float_eff.height) - float_eff.height;
    geo.effective_anchor.x -= eff_ceil_dw / 2.0;
    geo.effective_anchor.y -= eff_ceil_dh / 2.0;

    // 3) Set effective dims.  Integerized once by ceil(float_eff); then
    //    clamped to canvas.  If the ceil'd value would overflow
    //    (effective_anchor + effective_dims > canvas), the anchor is pulled
    //    back to canvas - dim in step 4 instead of the dim being reduced
    //    (dim-shrink would lose a whole integer pixel to sub-pixel anchor
    //    noise; effective's ceil delta is already committed to the dim).
    geo.effective_dims.width = std::min(std::ceil(float_eff.width), geo.canvas_dims.width);
    geo.effective_dims.height = std::min(std::ceil(float_eff.height), geo.canvas_dims.height);

    // 4) Clamp anchors inside the canvas.
    //    For effective (integer-typed): clamp anchor to [0, canvas - dim]
    //      so the ceil'd dim stays intact; sub-pixel slide inward is cheap.
    //    For protection / framing (float): clamp anchor to [0, canvas]
    //      and let step 5 shrink the dim (float, no round — preserves
    //      the spatial anchor position).
    auto clamp_range = [](double a, double lo, double hi) {
        if (a < lo) return lo;
        if (a > hi) return hi;
        return a;
    };
    double const eff_max_ax = std::max(0.0, geo.canvas_dims.width - geo.effective_dims.width);
    double const eff_max_ay = std::max(0.0, geo.canvas_dims.height - geo.effective_dims.height);
    geo.effective_anchor.x = clamp_range(geo.effective_anchor.x, 0.0, eff_max_ax);
    geo.effective_anchor.y = clamp_range(geo.effective_anchor.y, 0.0, eff_max_ay);
    geo.protection_anchor.x = clamp_range(geo.protection_anchor.x, 0.0, geo.canvas_dims.width);
    geo.protection_anchor.y = clamp_range(geo.protection_anchor.y, 0.0, geo.canvas_dims.height);
    geo.framing_anchor.x = clamp_range(geo.framing_anchor.x, 0.0, geo.canvas_dims.width);
    geo.framing_anchor.y = clamp_range(geo.framing_anchor.y, 0.0, geo.canvas_dims.height);

    // 5) Shrink protection / framing dims so they fit at their anchors
    //    inside the canvas.  Float so no rounding; preserves the anchor.
    geo.protection_dims.width = std::min(
        geo.protection_dims.width, geo.canvas_dims.width - geo.protection_anchor.x);
    geo.protection_dims.height = std::min(
        geo.protection_dims.height, geo.canvas_dims.height - geo.protection_anchor.y);
    geo.framing_dims.width =
        std::min(geo.framing_dims.width, geo.canvas_dims.width - geo.framing_anchor.x);
    geo.framing_dims.height =
        std::min(geo.framing_dims.height, geo.canvas_dims.height - geo.framing_anchor.y);

    // 6) Re-establish hierarchy: protection / framing cannot exceed the
    //    (already integer, already canvas-clamped) effective.  Only clamp
    //    on exceedance so that 0 (unset protection) stays 0.
    if (geo.protection_dims.width > geo.effective_dims.width)
        geo.protection_dims.width = geo.effective_dims.width;
    if (geo.protection_dims.height > geo.effective_dims.height)
        geo.protection_dims.height = geo.effective_dims.height;
    if (geo.framing_dims.width > geo.effective_dims.width)
        geo.framing_dims.width = geo.effective_dims.width;
    if (geo.framing_dims.height > geo.effective_dims.height)
        geo.framing_dims.height = geo.effective_dims.height;

    return geo;
}

fdl_geometry_t geometry_apply_offset(
    fdl_geometry_t geo,
    fdl_point_f64_t offset,
    fdl_point_f64_t* theo_eff,
    fdl_point_f64_t* theo_prot,
    fdl_point_f64_t* theo_fram) {

    // All output pointers are required — return geometry unmodified if any is null.
    if (theo_eff == nullptr || theo_prot == nullptr || theo_fram == nullptr) {
        return geo;
    }

    // Calculate theoretical anchor positions (may be negative)
    *theo_eff = fdl_point_add(geo.effective_anchor, offset);
    *theo_prot = fdl_point_add(geo.protection_anchor, offset);
    *theo_fram = fdl_point_add(geo.framing_anchor, offset);

    return {
        geo.canvas_dims,
        geo.effective_dims,
        geo.protection_dims,
        geo.framing_dims,
        fdl_point_clamp(*theo_eff, 0.0, 0.0, FDL_TRUE, FDL_FALSE),
        fdl_point_clamp(*theo_prot, 0.0, 0.0, FDL_TRUE, FDL_FALSE),
        fdl_point_clamp(*theo_fram, 0.0, 0.0, FDL_TRUE, FDL_FALSE),
    };
}

namespace {

/**
 * @brief Clip a dimension to the visible portion within canvas bounds.
 *
 * Uses the theoretical (unclamped) anchor to compute how much of the
 * dimension extends beyond the canvas edges, then clips accordingly.
 *
 * @param dims            Dimensions to clip.
 * @param theo_anchor     Theoretical (unclamped) anchor position.
 * @param clamped_anchor  Clamped anchor position (>= 0).
 * @param canvas_dims     Canvas bounds used for clipping.
 * @return Visible portion of @p dims within the canvas.
 */
fdl_dimensions_f64_t crop_dim(
    fdl_dimensions_f64_t dims,
    fdl_point_f64_t theo_anchor,
    fdl_point_f64_t clamped_anchor,
    fdl_dimensions_f64_t canvas_dims) {

    if (fdl_dimensions_is_zero(dims) != 0) {
        return dims;
    }

    // Calculate how much is clipped from left/top edge (negative anchor)
    double const clip_left = std::max(0.0, -theo_anchor.x);
    double const clip_top = std::max(0.0, -theo_anchor.y);
    // Reduce dimensions by clipped amount
    double visible_w = dims.width - clip_left;
    double visible_h = dims.height - clip_top;
    // Ensure doesn't extend beyond canvas right/bottom edge
    visible_w = std::min(visible_w, canvas_dims.width - clamped_anchor.x);
    visible_h = std::min(visible_h, canvas_dims.height - clamped_anchor.y);

    return {std::max(0.0, visible_w), std::max(0.0, visible_h)};
}

} // namespace

fdl_geometry_t geometry_crop(
    fdl_geometry_t geo, fdl_point_f64_t theo_eff, fdl_point_f64_t theo_prot, fdl_point_f64_t theo_fram) {

    auto canvas_dims = geo.canvas_dims;

    // Clip all dimensions based on their theoretical anchors
    auto visible_effective = crop_dim(geo.effective_dims, theo_eff, geo.effective_anchor, canvas_dims);
    auto visible_protection = crop_dim(geo.protection_dims, theo_prot, geo.protection_anchor, canvas_dims);
    auto visible_framing = crop_dim(geo.framing_dims, theo_fram, geo.framing_anchor, canvas_dims);

    // Enforce hierarchy: each layer <= parent
    // effective must fit within canvas
    visible_effective =
        dims_clamp_to_dims(visible_effective, canvas_dims); // NOLINT(readability-suspicious-call-argument)
    // Protection must fit within effective (if protection exists)
    if (fdl_dimensions_is_zero(visible_protection) == 0) {
        visible_protection = dims_clamp_to_dims(visible_protection, visible_effective);
    }
    // Framing must fit within protection (or effective if no protection)
    auto parent_dims = (fdl_dimensions_is_zero(visible_protection) != 0) ? visible_effective : visible_protection;
    visible_framing = dims_clamp_to_dims(visible_framing, parent_dims); // NOLINT(readability-suspicious-call-argument)

    return {
        canvas_dims,
        visible_effective,
        visible_protection,
        visible_framing,
        geo.effective_anchor,
        geo.protection_anchor,
        geo.framing_anchor,
    };
}

int geometry_get_dims_anchor_from_path(
    const fdl_geometry_t* geo, fdl_geometry_path_t path, fdl_dimensions_f64_t* out_dims, fdl_point_f64_t* out_anchor) {

    switch (path) {
    case FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS:
        *out_dims = geo->canvas_dims;
        *out_anchor = {0.0, 0.0};
        return 0;
    case FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS:
        *out_dims = geo->effective_dims;
        *out_anchor = geo->effective_anchor;
        return 0;
    case FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS:
        *out_dims = geo->protection_dims;
        *out_anchor = geo->protection_anchor;
        return 0;
    case FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS:
        *out_dims = geo->framing_dims;
        *out_anchor = geo->framing_anchor;
        return 0;
    default:
        return fdl::constants::kGeometryInvalidPath;
    }
}

} // namespace fdl::detail
