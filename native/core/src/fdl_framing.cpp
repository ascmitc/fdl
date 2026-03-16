// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_framing.cpp
 * @brief Framing-from-intent computation — aspect ratio fitting with protection.
 *
 * Algorithm:
 * 1. Compare intent aspect ratio with working (effective or canvas) aspect ratio.
 * 2. If intent is wider: letterbox (fit to width, shrink height).
 *    If intent is narrower: pillarbox (fit to height, shrink width).
 * 3. If protection > 0, round to get protection dimensions, then shrink by
 *    the protection factor to get final framing dimensions.
 * 4. Center both framing and protection anchors within the full canvas.
 */
#include "fdl_framing.h"
#include "fdl_constants.h"

namespace fdl::detail {

fdl_from_intent_result_t compute_framing_from_intent(
    fdl_dimensions_f64_t canvas_dims,
    fdl_dimensions_f64_t working_dims,
    double squeeze,
    fdl_dimensions_i64_t aspect_ratio,
    double protection,
    fdl_round_strategy_t rounding) {

    fdl_from_intent_result_t result = {};
    result.has_protection = FDL_FALSE;

    // Guard against division by zero in aspect ratio or working dimensions.
    if (aspect_ratio.height == 0 || working_dims.height == 0.0) {
        return result;
    }

    // Compare aspect ratios
    double const intent_aspect = static_cast<double>(aspect_ratio.width) / static_cast<double>(aspect_ratio.height);
    double const canvas_aspect = working_dims.width / working_dims.height;

    double width;
    double height;
    if (intent_aspect >= canvas_aspect) {
        // Letterbox: wider intent, height shrinks
        width = working_dims.width;
        height = (width * squeeze) / intent_aspect;
    } else {
        // Pillarbox: narrower intent, width shrinks
        width = working_dims.height * intent_aspect;
        height = working_dims.height;
    }

    // If protection > 0, round to get protection dimensions
    fdl_dimensions_f64_t prot_dims = {0.0, 0.0};
    if (protection > 0) {
        prot_dims = fdl_round_dimensions({width, height}, rounding.even, rounding.mode);
        result.has_protection = FDL_TRUE;
        result.protection_dimensions = prot_dims;
    }

    // If protection was set, base final dimensions on protection dims
    if (result.has_protection != 0) {
        width = prot_dims.width;
        height = prot_dims.height;
    }

    // Apply protection factor and round
    fdl_dimensions_f64_t const dims = {
        width * (fdl::constants::kProtectionBase - protection),
        height * (fdl::constants::kProtectionBase - protection)};
    result.dimensions = fdl_round_dimensions(dims, rounding.even, rounding.mode);

    // Center framing decision anchor within canvas
    // (always relative to full canvas dims, not effective)
    result.anchor_point.x = (canvas_dims.width - result.dimensions.width) / fdl::constants::kCenterDivisor;
    result.anchor_point.y = (canvas_dims.height - result.dimensions.height) / fdl::constants::kCenterDivisor;

    // Center protection anchor within canvas (if applicable)
    if (result.has_protection != 0) {
        result.protection_anchor_point.x =
            (canvas_dims.width - result.protection_dimensions.width) / fdl::constants::kCenterDivisor;
        result.protection_anchor_point.y =
            (canvas_dims.height - result.protection_dimensions.height) / fdl::constants::kCenterDivisor;
    }

    return result;
}

} // namespace fdl::detail
