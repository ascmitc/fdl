// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_geometry.h
 * @brief Internal geometry operations on the 4-layer FDL dimension hierarchy.
 *
 * Provides gap-filling, ratio-based normalize+scale, rounding, offset, and
 * cropping operations used by the template application pipeline.
 */
#ifndef FDL_GEOMETRY_INTERNAL_H
#define FDL_GEOMETRY_INTERNAL_H

#include "fdl/fdl_core.h"

namespace fdl::detail {

/**
 * @brief Fill gaps in the geometry hierarchy by propagating populated dimensions upward.
 *
 * Protection is NEVER filled from framing (special case).
 * Anchors are adjusted by subtracting anchor_offset, then clamped >= 0.
 *
 * @param geo            Input geometry with possibly-zero layers.
 * @param anchor_offset  Offset to subtract from all anchors.
 * @return Geometry with gaps filled and anchors adjusted.
 */
fdl_geometry_t geometry_fill_hierarchy_gaps(fdl_geometry_t geo, fdl_point_f64_t anchor_offset);

/**
 * @brief Normalize and scale using a ratio (numerator/denominator) for precision.
 *
 * Computes (value * numerator) / denominator instead of value * (num/den) to
 * preserve precision for integer inputs.
 *
 * @param geo              Input geometry.
 * @param source_squeeze   Source anamorphic squeeze.
 * @param scale_numerator  Numerator of the scale ratio.
 * @param scale_denominator Denominator of the scale ratio.
 * @param target_squeeze   Target anamorphic squeeze.
 * @return Normalized and scaled geometry.
 */
fdl_geometry_t geometry_normalize_and_scale_ratio(
    fdl_geometry_t geo, double source_squeeze, double scale_numerator, double scale_denominator, double target_squeeze);

/**
 * @brief Round canvas_dims and effective_dims; absorb deltas symmetrically.
 *
 * Per spec 7.4.12 "round" applies to canvas.dimensions.  The schema also
 * types canvas.effective_dimensions as integer, so both are rounded here.
 * Inner geometry (protection, framing dims and all anchors) remains float
 * per the fractional-pixels model.
 *
 * Intended to run once at the end of the template pipeline (post-crop).
 * The anchors at that point already encode all template intent (scale,
 * alignment, padding, crop); the rounding deltas are pure schema-integer
 * artifacts.  This function distributes those deltas symmetrically so no
 * directional bias is introduced:
 *
 *   - canvas delta is absorbed by shifting ALL anchors by +delta/2
 *     (content stays centered in the rounded canvas).
 *   - effective delta is absorbed by shifting effective_anchor by -delta/2
 *     (rounded effective rectangle stays centered on its pre-round extent).
 *
 * Effective is rounded once (ceil); if it would overflow the canvas at its
 * anchor, the effective anchor is pulled back to `canvas - dim` — we trade
 * a sub-pixel anchor slide for a preserved integer dim, because the ceil
 * delta is already committed to the pixel budget.  Inner layers
 * (protection, framing) instead have their float dims shrunk to
 * `canvas - anchor`, which preserves the anchor position since the dims
 * carry no integer commitment.  The rounded canvas is the absolute
 * container: no layer may extend beyond it on either edge.  Hierarchy is
 * re-established post-shrink so protection/framing do not exceed effective.
 *
 * @param geo       Input geometry (typically post-crop with float fields).
 * @param strategy  Rounding strategy (even + mode).
 * @return Geometry with canvas/effective rounded and anchors compensated.
 */
fdl_geometry_t geometry_round(fdl_geometry_t geo, fdl_round_strategy_t strategy);

/**
 * @brief Apply offset to all anchors, clamping to canvas bounds.
 *
 * Returns clamped geometry; theoretical (unclamped) anchors written to output pointers.
 * If any output pointer is null, returns the geometry unmodified.
 *
 * @param geo        Input geometry.
 * @param offset     Offset to add to all anchors.
 * @param theo_eff   [out] Theoretical effective anchor (may be negative). Must not be null.
 * @param theo_prot  [out] Theoretical protection anchor. Must not be null.
 * @param theo_fram  [out] Theoretical framing anchor. Must not be null.
 * @return Geometry with clamped anchors, or unmodified @p geo if any output pointer is null.
 */
fdl_geometry_t geometry_apply_offset(
    fdl_geometry_t geo,
    fdl_point_f64_t offset,
    fdl_point_f64_t* theo_eff,
    fdl_point_f64_t* theo_prot,
    fdl_point_f64_t* theo_fram);

/**
 * @brief Crop all dimensions to visible portion within canvas.
 *
 * Enforces hierarchy: canvas >= effective >= protection >= framing.
 *
 * @param geo        Input geometry (anchors must already be clamped).
 * @param theo_eff   Theoretical effective anchor (unclamped).
 * @param theo_prot  Theoretical protection anchor (unclamped).
 * @param theo_fram  Theoretical framing anchor (unclamped).
 * @return Geometry with dimensions cropped to visible area.
 */
fdl_geometry_t geometry_crop(
    fdl_geometry_t geo, fdl_point_f64_t theo_eff, fdl_point_f64_t theo_prot, fdl_point_f64_t theo_fram);

/**
 * @brief Extract dimensions and anchor from geometry by path.
 * @param geo         Geometry to query.
 * @param path        Which layer to extract.
 * @param out_dims    [out] Extracted dimensions.
 * @param out_anchor  [out] Extracted anchor point.
 * @return 0 on success, -1 on invalid path.
 */
int geometry_get_dims_anchor_from_path(
    const fdl_geometry_t* geo, fdl_geometry_path_t path, fdl_dimensions_f64_t* out_dims, fdl_point_f64_t* out_anchor);

} // namespace fdl::detail

#endif // FDL_GEOMETRY_INTERNAL_H
