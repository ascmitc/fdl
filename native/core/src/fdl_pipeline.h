// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_pipeline.h
 * @brief Internal pipeline helper functions for template application.
 *
 * Scale factor calculation, output sizing, alignment shift, and dimension clamping
 * — the building blocks of the canvas template application pipeline.
 */
#ifndef FDL_PIPELINE_INTERNAL_H
#define FDL_PIPELINE_INTERNAL_H

#include "fdl/fdl_core.h"

namespace fdl::detail {

/**
 * @brief Calculate scale factor based on fit method.
 * @param fit_norm    Normalized fit-source dimensions.
 * @param target_norm Normalized target dimensions.
 * @param fit_method  Fit method (width, height, fill, fit_all).
 * @return Scale factor (always > 0).
 */
double calculate_scale_factor(
    fdl_dimensions_f64_t fit_norm, fdl_dimensions_f64_t target_norm, fdl_fit_method_t fit_method);

/**
 * @brief Determine output canvas size for a single axis.
 * @param canvas_size  Scaled canvas size along this axis.
 * @param max_size     Maximum allowed size (from target dimensions).
 * @param has_max      Whether a maximum constraint exists.
 * @param pad_to_max   Whether to pad to maximum size.
 * @return Output size for this axis.
 */
double output_size_for_axis(double canvas_size, double max_size, bool has_max, bool pad_to_max);

/**
 * @brief Calculate content translation shift for a single axis.
 * @param fit_size      Fit-source size along this axis.
 * @param fit_anchor    Fit-source anchor along this axis.
 * @param output_size   Output canvas size along this axis.
 * @param canvas_size   Scaled canvas size along this axis.
 * @param target_size   Target size along this axis.
 * @param is_center     Whether alignment is centered.
 * @param align_factor  Alignment factor (0.0 = start, 0.5 = center, 1.0 = end).
 * @param pad_to_max    Whether padding is applied.
 * @return Shift amount in pixels.
 */
double alignment_shift(
    double fit_size,
    double fit_anchor,
    double output_size,
    double canvas_size,
    double target_size,
    bool is_center,
    double align_factor,
    bool pad_to_max);

/**
 * @brief Clamp dimensions to maximum bounds.
 * @param dims        Input dimensions.
 * @param clamp_dims  Maximum allowed dimensions.
 * @param out_delta   [out] Reduction applied to each axis (dims - result).
 * @return Clamped dimensions.
 */
fdl_dimensions_f64_t dimensions_clamp_to_dims(
    fdl_dimensions_f64_t dims, fdl_dimensions_f64_t clamp_dims, fdl_point_f64_t* out_delta);

} // namespace fdl::detail

#endif // FDL_PIPELINE_INTERNAL_H
