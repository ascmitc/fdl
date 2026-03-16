// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_framing.h
 * @brief Internal implementation of framing-from-intent computation.
 *
 * Fits a framing intent's aspect ratio within working dimensions,
 * centers within canvas, and optionally computes a protection area.
 */
#ifndef FDL_FRAMING_INTERNAL_H
#define FDL_FRAMING_INTERNAL_H

#include "fdl/fdl_core.h"

namespace fdl::detail {

/**
 * Compute a framing decision from a framing intent.
 *
 * Returns a zeroed result if @p aspect_ratio.height or @p working_dims.height
 * is zero (guards against division by zero).
 *
 * @param canvas_dims   Full canvas dimensions (for anchor centering).
 * @param working_dims  Effective dimensions if available, else canvas dims.
 * @param squeeze       Anamorphic squeeze factor.
 * @param aspect_ratio  Target aspect ratio as integer width:height (height must be > 0).
 * @param protection    Protection factor (0.0 for no protection).
 * @param rounding      Rounding strategy.
 * @return Computed framing dimensions, anchors, and optional protection.
 */
fdl_from_intent_result_t compute_framing_from_intent(
    fdl_dimensions_f64_t canvas_dims,
    fdl_dimensions_f64_t working_dims,
    double squeeze,
    fdl_dimensions_i64_t aspect_ratio,
    double protection,
    fdl_round_strategy_t rounding);

} // namespace fdl::detail

#endif // FDL_FRAMING_INTERNAL_H
