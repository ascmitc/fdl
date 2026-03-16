// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_pipeline.cpp
 * @brief Pipeline helper implementations: scale factor, output sizing, alignment shift, dimension clamping.
 */
#include "fdl_pipeline.h"

#include <algorithm>

#include "fdl_constants.h"

namespace fdl::detail {

double calculate_scale_factor(
    fdl_dimensions_f64_t fit_norm, fdl_dimensions_f64_t target_norm, fdl_fit_method_t fit_method) {

    double const w_ratio = target_norm.width / fit_norm.width;
    double const h_ratio = target_norm.height / fit_norm.height;

    switch (fit_method) {
    case FDL_FIT_METHOD_FIT_ALL:
        return std::min(w_ratio, h_ratio);
    case FDL_FIT_METHOD_FILL:
        return std::max(w_ratio, h_ratio);
    case FDL_FIT_METHOD_WIDTH:
        return w_ratio;
    case FDL_FIT_METHOD_HEIGHT:
        return h_ratio;
    default:
        return 0.0;
    }
}

double output_size_for_axis(double canvas_size, double max_size, bool has_max, bool pad_to_max) {

    if (has_max && pad_to_max) {
        return max_size;
    }
    if (has_max && canvas_size > max_size) {
        return max_size;
    }
    return canvas_size;
}

double alignment_shift(
    double fit_size,
    double fit_anchor,
    double output_size,
    double canvas_size,
    double target_size,
    bool is_center,
    double align_factor,
    bool pad_to_max) {

    double const overflow = canvas_size - output_size;

    // FIT: output matches canvas exactly, no padding requested.
    // Geometry is already in its correct position — no shift needed.
    if (overflow == 0 && !pad_to_max) {
        return 0.0;
    }

    // PAD / CROP (unified)
    // Step 1: where the target region sits in the output.
    bool const center_target = pad_to_max || is_center;
    double const target_offset = center_target ? (output_size - target_size) * fdl::constants::kAlignCenter : 0.0;

    // Step 2: where the fit sits within the target.
    double const gap = target_size - fit_size;
    double const alignment_offset = gap * align_factor;

    // Step 3: sum all offsets.
    double shift = target_offset + alignment_offset - fit_anchor;

    // Step 4: clamp for crop — content must fill the entire output.
    if (!pad_to_max && overflow > 0) {
        shift = std::max(std::min(shift, 0.0), -overflow);
    }

    return shift;
}

fdl_dimensions_f64_t dimensions_clamp_to_dims(
    fdl_dimensions_f64_t dims, fdl_dimensions_f64_t clamp_dims, fdl_point_f64_t* out_delta) {

    double const delta_w = std::min(0.0, clamp_dims.width - dims.width);
    double const delta_h = std::min(0.0, clamp_dims.height - dims.height);
    double const new_w = std::min(dims.width, clamp_dims.width);
    double const new_h = std::min(dims.height, clamp_dims.height);

    if (out_delta != nullptr) {
        out_delta->x = delta_w;
        out_delta->y = delta_h;
    }

    return {new_w, new_h};
}

} // namespace fdl::detail
