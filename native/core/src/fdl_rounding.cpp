// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_rounding.cpp
 * @brief FDL rounding functions (round, round_dimensions, round_point) using banker's rounding.
 */
#include "fdl_rounding.h"
#include "fdl/fdl_core.h"

#include <cmath>
#include <cstdlib>

// Port of Python fdl_round() from rounding.py.
// Critical: Python round() uses banker's rounding (half-to-even),
// C++ std::lround() uses half-away-from-zero. We use our own
// bankers_round() implementation in fdl_rounding.h.

int64_t fdl_round(double value, fdl_rounding_even_t even, fdl_rounding_mode_t mode) {
    int64_t sign = fdl::constants::kPositiveSign;
    if (value < 0.0) {
        sign = fdl::constants::kNegativeSign;
        value = std::abs(value);
    }

    int64_t v;
    if (mode == FDL_ROUNDING_MODE_UP) {
        v = fdl::detail::safe_to_int64(std::ceil(value));
    } else if (mode == FDL_ROUNDING_MODE_DOWN) {
        v = fdl::detail::safe_to_int64(std::floor(value));
    } else {
        // ROUND — banker's rounding to match Python
        v = fdl::detail::bankers_round(value);
    }

    if (even == FDL_ROUNDING_EVEN_EVEN) {
        if (mode == FDL_ROUNDING_MODE_UP) {
            v = (v % fdl::constants::kEvenDivisor == 0) ? v : v + fdl::constants::kEvenRoundingAdjustment;
        } else if (mode == FDL_ROUNDING_MODE_DOWN) {
            v = (v % fdl::constants::kEvenDivisor == 0) ? v : v - fdl::constants::kEvenRoundingAdjustment;
        } else {
            if (v % fdl::constants::kEvenDivisor != 0) {
                int64_t const up = v + fdl::constants::kEvenRoundingAdjustment;
                int64_t const down = v - fdl::constants::kEvenRoundingAdjustment;
                v = (std::abs(static_cast<double>(up) - value) <= std::abs(static_cast<double>(down) - value)) ? up
                                                                                                               : down;
            }
        }
    }

    return sign * v;
}

fdl_dimensions_f64_t fdl_round_dimensions(
    fdl_dimensions_f64_t dims, fdl_rounding_even_t even, fdl_rounding_mode_t mode) {
    return {
        static_cast<double>(fdl_round(dims.width, even, mode)),
        static_cast<double>(fdl_round(dims.height, even, mode))};
}

fdl_point_f64_t fdl_round_point(fdl_point_f64_t point, fdl_rounding_even_t even, fdl_rounding_mode_t mode) {
    return {static_cast<double>(fdl_round(point.x, even, mode)), static_cast<double>(fdl_round(point.y, even, mode))};
}
