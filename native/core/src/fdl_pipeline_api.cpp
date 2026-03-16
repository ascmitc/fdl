// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_pipeline_api.cpp
 * @brief C ABI wrappers for pipeline helper functions.
 */
#include "fdl/fdl_core.h"
#include "fdl_pipeline.h"

extern "C" {

double fdl_calculate_scale_factor(
    fdl_dimensions_f64_t fit_norm, fdl_dimensions_f64_t target_norm, fdl_fit_method_t fit_method) {
    return fdl::detail::calculate_scale_factor(fit_norm, target_norm, fit_method);
}

double fdl_output_size_for_axis(double canvas_size, double max_size, int has_max, int pad_to_max) {
    return fdl::detail::output_size_for_axis(canvas_size, max_size, has_max != 0, pad_to_max != 0);
}

double fdl_alignment_shift(
    double fit_size,
    double fit_anchor,
    double output_size,
    double canvas_size,
    double target_size,
    int is_center,
    double align_factor,
    int pad_to_max) {
    return fdl::detail::alignment_shift(
        fit_size, fit_anchor, output_size, canvas_size, target_size, is_center != 0, align_factor, pad_to_max != 0);
}

fdl_dimensions_f64_t fdl_dimensions_clamp_to_dims(
    fdl_dimensions_f64_t dims, fdl_dimensions_f64_t clamp_dims, fdl_point_f64_t* out_delta) {
    return fdl::detail::dimensions_clamp_to_dims(dims, clamp_dims, out_delta);
}

} // extern "C"
