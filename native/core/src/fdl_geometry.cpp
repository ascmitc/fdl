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
 * - **Normalize+scale**: Applies anamorphic correction and uniform scaling.
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
 * @brief Normalize a point for squeeze then apply uniform scale.
 * @param pt              Input point.
 * @param squeeze         Source anamorphic squeeze factor.
 * @param scale           Uniform scale factor.
 * @param target_squeeze  Target anamorphic squeeze factor.
 * @return The normalized and scaled point.
 */
fdl_point_f64_t point_normalize_and_scale(fdl_point_f64_t pt, double squeeze, double scale, double target_squeeze) {
    fdl_point_f64_t const normalized = fdl_point_normalize(pt, squeeze);
    return fdl_point_scale(normalized, scale, target_squeeze);
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

fdl_geometry_t geometry_normalize_and_scale(
    fdl_geometry_t geo, double source_squeeze, double scale_factor, double target_squeeze) {

    return {
        fdl_dimensions_normalize_and_scale(geo.canvas_dims, source_squeeze, scale_factor, target_squeeze),
        fdl_dimensions_normalize_and_scale(geo.effective_dims, source_squeeze, scale_factor, target_squeeze),
        fdl_dimensions_normalize_and_scale(geo.protection_dims, source_squeeze, scale_factor, target_squeeze),
        fdl_dimensions_normalize_and_scale(geo.framing_dims, source_squeeze, scale_factor, target_squeeze),
        point_normalize_and_scale(geo.effective_anchor, source_squeeze, scale_factor, target_squeeze),
        point_normalize_and_scale(geo.protection_anchor, source_squeeze, scale_factor, target_squeeze),
        point_normalize_and_scale(geo.framing_anchor, source_squeeze, scale_factor, target_squeeze),
    };
}

fdl_geometry_t geometry_round(fdl_geometry_t geo, fdl_round_strategy_t strategy) {

    return {
        fdl_round_dimensions(geo.canvas_dims, strategy.even, strategy.mode),
        fdl_round_dimensions(geo.effective_dims, strategy.even, strategy.mode),
        fdl_round_dimensions(geo.protection_dims, strategy.even, strategy.mode),
        fdl_round_dimensions(geo.framing_dims, strategy.even, strategy.mode),
        fdl_round_point(geo.effective_anchor, strategy.even, strategy.mode),
        fdl_round_point(geo.protection_anchor, strategy.even, strategy.mode),
        fdl_round_point(geo.framing_anchor, strategy.even, strategy.mode),
    };
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
