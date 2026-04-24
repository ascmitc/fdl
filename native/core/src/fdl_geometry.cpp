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
    // canvas.effective_dimensions).  Inner dimensions (protection, framing)
    // and all anchors remain float per the "fractional pixels" model; they
    // are only clamped down if they would exceed the rounded canvas.
    //
    // Called once at the end of the template pipeline (post-crop).  Every
    // anchor at this point already encodes the template's intent (scale,
    // alignment, padding, crop); rounding deltas are distributed
    // symmetrically (delta/2) so there is no directional bias.
    //
    // Steps:
    //   1. Ceil effective_dims; absorb the ceil delta into effective_anchor
    //      (delta/2).  Pure ceil — strategy.even / strategy.mode do NOT
    //      apply to effective (inner dims are <= effective_float by
    //      construction, so ceil preserves the hierarchy automatically).
    //   2. Round canvas_dims per strategy.even / strategy.mode.
    //   3. Clamp effective / protection / framing against the rounded
    //      canvas.  std::min(0, canvas) = 0 preserves the "unset" sentinel
    //      for optional protection.
    //   4. Shift ALL anchors by +canvas_delta/2 so content stays centered
    //      within the rounded canvas.
    //   5. Clamp anchors to [0, canvas - dim] so every layer stays inside
    //      the canvas.  Upper bound is still required — the symmetric
    //      shift only absorbs half of the canvas delta, so at canvas edges
    //      anchors can still overflow by up to |canvas_delta|/2.
    fdl_dimensions_f64_t const float_canvas = geo.canvas_dims;
    fdl_dimensions_f64_t const float_eff = geo.effective_dims;

    // 1) Ceil effective; absorb ceil delta symmetrically into effective_anchor.
    geo.effective_dims.width = std::ceil(float_eff.width);
    geo.effective_dims.height = std::ceil(float_eff.height);
    double const eff_dw = geo.effective_dims.width - float_eff.width;
    double const eff_dh = geo.effective_dims.height - float_eff.height;
    geo.effective_anchor.x -= eff_dw / 2.0;
    geo.effective_anchor.y -= eff_dh / 2.0;

    // 2) Round canvas per strategy.
    geo.canvas_dims = fdl_round_dimensions(float_canvas, strategy.even, strategy.mode);

    // 3) Clamp effective / protection / framing against rounded canvas.
    geo.effective_dims.width = std::min(geo.effective_dims.width, geo.canvas_dims.width);
    geo.effective_dims.height = std::min(geo.effective_dims.height, geo.canvas_dims.height);
    geo.protection_dims.width = std::min(geo.protection_dims.width, geo.canvas_dims.width);
    geo.protection_dims.height = std::min(geo.protection_dims.height, geo.canvas_dims.height);
    geo.framing_dims.width = std::min(geo.framing_dims.width, geo.canvas_dims.width);
    geo.framing_dims.height = std::min(geo.framing_dims.height, geo.canvas_dims.height);

    // 4) Shift all anchors by +canvas_delta/2.
    double const canvas_dw = geo.canvas_dims.width - float_canvas.width;
    double const canvas_dh = geo.canvas_dims.height - float_canvas.height;
    geo.effective_anchor.x += canvas_dw / 2.0;
    geo.effective_anchor.y += canvas_dh / 2.0;
    geo.protection_anchor.x += canvas_dw / 2.0;
    geo.protection_anchor.y += canvas_dh / 2.0;
    geo.framing_anchor.x += canvas_dw / 2.0;
    geo.framing_anchor.y += canvas_dh / 2.0;

    // 5a) Lower bound: clamp negative anchors to 0.  When rounding/shift
    // nudges an anchor below zero, pull it back to the canvas origin.
    auto clamp_anchor_lower = [](double& anchor) {
        if (anchor < 0.0) anchor = 0.0;
    };
    clamp_anchor_lower(geo.effective_anchor.x);
    clamp_anchor_lower(geo.effective_anchor.y);
    clamp_anchor_lower(geo.protection_anchor.x);
    clamp_anchor_lower(geo.protection_anchor.y);
    clamp_anchor_lower(geo.framing_anchor.x);
    clamp_anchor_lower(geo.framing_anchor.y);

    // 5b) Upper bound: if anchor + dim overflows the right/bottom canvas
    // edge, preserve the anchor and shrink the dim.  Effective is an
    // integer schema field so we floor the available space (anchor +
    // floor(canvas - anchor) <= canvas always holds).  Inner dims
    // (protection, framing) stay float per the "fractional pixels" model.
    {
        double const max_w = std::max(0.0, geo.canvas_dims.width - geo.effective_anchor.x);
        double const max_h = std::max(0.0, geo.canvas_dims.height - geo.effective_anchor.y);
        geo.effective_dims.width = std::min(geo.effective_dims.width, std::floor(max_w));
        geo.effective_dims.height = std::min(geo.effective_dims.height, std::floor(max_h));
    }
    geo.protection_dims.width = std::min(
        geo.protection_dims.width, std::max(0.0, geo.canvas_dims.width - geo.protection_anchor.x));
    geo.protection_dims.height = std::min(
        geo.protection_dims.height, std::max(0.0, geo.canvas_dims.height - geo.protection_anchor.y));
    geo.framing_dims.width = std::min(
        geo.framing_dims.width, std::max(0.0, geo.canvas_dims.width - geo.framing_anchor.x));
    geo.framing_dims.height = std::min(
        geo.framing_dims.height, std::max(0.0, geo.canvas_dims.height - geo.framing_anchor.y));

    // 5c) Re-establish hierarchy: floor on effective in 5b can drop it
    // below inner float dims that were valid before.  Clamp protection /
    // framing down to effective if they now exceed it.  Only clamp on
    // exceedance so that 0 (unset protection) stays 0.
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
