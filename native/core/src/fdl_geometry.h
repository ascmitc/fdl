// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_geometry.h
 * @brief Internal geometry operations on the 4-layer FDL dimension hierarchy.
 *
 * Provides gap-filling, normalize+scale, rounding, offset, and cropping
 * operations used by the template application pipeline.
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
 * @brief Normalize and scale all 7 fields (4 dimensions + 3 anchors) of the geometry.
 * @param geo             Input geometry.
 * @param source_squeeze  Source anamorphic squeeze.
 * @param scale_factor    Uniform scale factor to apply.
 * @param target_squeeze  Target anamorphic squeeze.
 * @return Normalized and scaled geometry.
 */
fdl_geometry_t geometry_normalize_and_scale(
    fdl_geometry_t geo, double source_squeeze, double scale_factor, double target_squeeze);

/**
 * @brief Round all 7 fields of the geometry using the given strategy.
 * @param geo       Input geometry.
 * @param strategy  Rounding strategy (even + mode).
 * @return Geometry with all fields rounded.
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
