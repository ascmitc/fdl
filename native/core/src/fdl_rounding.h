// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_rounding.h
 * @brief Banker's rounding (half-to-even) implementation.
 *
 * Provides the core rounding primitive that matches Python's built-in round()
 * behavior, ensuring consistent results across the C++ and Python implementations.
 */
#ifndef FDL_ROUNDING_INTERNAL_H
#define FDL_ROUNDING_INTERNAL_H

#include <cmath>
#include <cstdint>
#include <limits>

#include "fdl_constants.h"

namespace fdl::detail {

/**
 * @brief Safely cast a double to int64_t, clamping to [INT64_MIN, INT64_MAX].
 *
 * Prevents undefined behavior from casting doubles that exceed the
 * representable range of int64_t.
 *
 * @param value  The floating-point value to convert.
 * @return The integer value, clamped to int64_t bounds.
 */
inline int64_t safe_to_int64(double value) {
    // Doubles beyond int64_t range would cause UB in static_cast.
    constexpr auto kMax = static_cast<double>(std::numeric_limits<int64_t>::max());
    constexpr auto kMin = static_cast<double>(std::numeric_limits<int64_t>::min());
    if (value >= kMax) {
        return std::numeric_limits<int64_t>::max();
    }
    if (value <= kMin) {
        return std::numeric_limits<int64_t>::min();
    }
    return static_cast<int64_t>(value);
}

/**
 * Banker's rounding (half-to-even), matching Python's built-in round().
 *
 * At exact halfway points (e.g. 0.5, 1.5), rounds to the nearest even integer.
 * This avoids systematic rounding bias.
 *
 * @param value  The floating-point value to round.
 * @return Rounded integer value.
 */
inline int64_t bankers_round(double value) {
    double rounded = std::round(value);
    // Check if we're exactly at the halfway point
    double const remainder = value - std::floor(value);
    if (std::abs(remainder - constants::kHalfway) < constants::kFpHalfwayTolerance) {
        // Halfway case: round to even
        auto r = safe_to_int64(rounded);
        if (r % constants::kEvenDivisor != 0) {
            // rounded is odd, go the other way
            rounded = std::floor(value + constants::kHalfway);
            if (safe_to_int64(rounded) % constants::kEvenDivisor != 0) {
                rounded = std::ceil(value - constants::kHalfway);
            }
        }
    }
    return safe_to_int64(rounded);
}

} // namespace fdl::detail

#endif // FDL_ROUNDING_INTERNAL_H
