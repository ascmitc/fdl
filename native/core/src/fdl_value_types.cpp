// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_value_types.cpp
 * @brief Value-type operations: dimensions arithmetic, point arithmetic, floating-point comparison.
 */
#include "fdl/fdl_core.h"

#include <algorithm>
#include <cmath>
#include <cstdlib>

// ---------------------------------------------------------------------------
// Floating-point comparison constants
// ---------------------------------------------------------------------------

namespace {

/** @brief Relative tolerance for floating-point comparison (matches Python math.isclose). */
constexpr double kRelTol = 1e-9;
/** @brief Absolute tolerance for floating-point comparison (matches Python math.isclose). */
constexpr double kAbsTol = 1e-6;

/**
 * @brief Test whether two doubles are approximately equal.
 *
 * Matches Python math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6):
 *   abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
 *
 * @param a  First value.
 * @param b  Second value.
 * @return True if the values are within tolerance.
 */
bool fp_close(double a, double b) {
    double const diff = std::abs(a - b);
    double const tol = std::max(kRelTol * std::max(std::abs(a), std::abs(b)), kAbsTol);
    return diff <= tol;
}

} // namespace

double fdl_fp_rel_tol(void) {
    return kRelTol;
}
double fdl_fp_abs_tol(void) {
    return kAbsTol;
}

// ---------------------------------------------------------------------------
// Dimensions operations
// ---------------------------------------------------------------------------

fdl_dimensions_f64_t fdl_dimensions_normalize(fdl_dimensions_f64_t dims, double squeeze) {
    return {dims.width * squeeze, dims.height};
}

fdl_dimensions_f64_t fdl_dimensions_scale(fdl_dimensions_f64_t dims, double scale_factor, double target_squeeze) {
    return {(dims.width * scale_factor) / target_squeeze, dims.height * scale_factor};
}

fdl_dimensions_f64_t fdl_dimensions_normalize_and_scale(
    fdl_dimensions_f64_t dims, double input_squeeze, double scale_factor, double target_squeeze) {
    fdl_dimensions_f64_t const normalized = fdl_dimensions_normalize(dims, input_squeeze);
    return fdl_dimensions_scale(normalized, scale_factor, target_squeeze);
}

fdl_dimensions_f64_t fdl_dimensions_sub(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b) {
    return {a.width - b.width, a.height - b.height};
}

int fdl_dimensions_equal(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b) {
    return fp_close(a.width, b.width) && fp_close(a.height, b.height) ? FDL_TRUE : FDL_FALSE;
}

int fdl_dimensions_f64_gt(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b) {
    return (a.width > b.width || a.height > b.height) ? FDL_TRUE : FDL_FALSE;
}

int fdl_dimensions_f64_lt(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b) {
    return (a.width < b.width || a.height < b.height) ? FDL_TRUE : FDL_FALSE;
}

int fdl_dimensions_is_zero(fdl_dimensions_f64_t dims) {
    return (dims.width == 0.0 && dims.height == 0.0) ? FDL_TRUE : FDL_FALSE;
}

// ---------------------------------------------------------------------------
// Dimensions (integer) operations
// ---------------------------------------------------------------------------

int fdl_dimensions_i64_is_zero(fdl_dimensions_i64_t dims) {
    return (dims.width == 0 && dims.height == 0) ? FDL_TRUE : FDL_FALSE;
}

fdl_dimensions_f64_t fdl_dimensions_i64_normalize(fdl_dimensions_i64_t dims, double squeeze) {
    return {static_cast<double>(dims.width) * squeeze, static_cast<double>(dims.height)};
}

fdl_dimensions_i64_t fdl_dimensions_f64_to_i64(fdl_dimensions_f64_t dims) {
    return {static_cast<int64_t>(dims.width), static_cast<int64_t>(dims.height)};
}

int fdl_dimensions_i64_gt(fdl_dimensions_i64_t a, fdl_dimensions_i64_t b) {
    return (a.width > b.width || a.height > b.height) ? FDL_TRUE : FDL_FALSE;
}

int fdl_dimensions_i64_lt(fdl_dimensions_i64_t a, fdl_dimensions_i64_t b) {
    return (a.width < b.width || a.height < b.height) ? FDL_TRUE : FDL_FALSE;
}

// ---------------------------------------------------------------------------
// Point operations
// ---------------------------------------------------------------------------

fdl_point_f64_t fdl_point_normalize(fdl_point_f64_t point, double squeeze) {
    return {point.x * squeeze, point.y};
}

fdl_point_f64_t fdl_point_scale(fdl_point_f64_t point, double scale_factor, double target_squeeze) {
    return {(point.x * scale_factor) / target_squeeze, point.y * scale_factor};
}

fdl_point_f64_t fdl_point_add(fdl_point_f64_t a, fdl_point_f64_t b) {
    return {a.x + b.x, a.y + b.y};
}

fdl_point_f64_t fdl_point_sub(fdl_point_f64_t a, fdl_point_f64_t b) {
    return {a.x - b.x, a.y - b.y};
}

fdl_point_f64_t fdl_point_mul_scalar(fdl_point_f64_t a, double scalar) {
    return {a.x * scalar, a.y * scalar};
}

fdl_point_f64_t fdl_point_clamp(fdl_point_f64_t point, double min_val, double max_val, int has_min, int has_max) {
    double x = point.x;
    double y = point.y;
    if (has_min != 0) {
        x = std::max(x, min_val);
        y = std::max(y, min_val);
    }
    if (has_max != 0) {
        x = std::min(x, max_val);
        y = std::min(y, max_val);
    }
    return {x, y};
}

int fdl_point_is_zero(fdl_point_f64_t point) {
    return (point.x == 0.0 && point.y == 0.0) ? FDL_TRUE : FDL_FALSE;
}

fdl_point_f64_t fdl_point_normalize_and_scale(
    fdl_point_f64_t point, double input_squeeze, double scale_factor, double target_squeeze) {
    fdl_point_f64_t const normalized = fdl_point_normalize(point, input_squeeze);
    return fdl_point_scale(normalized, scale_factor, target_squeeze);
}

int fdl_point_equal(fdl_point_f64_t a, fdl_point_f64_t b) {
    return fp_close(a.x, b.x) && fp_close(a.y, b.y) ? FDL_TRUE : FDL_FALSE;
}

int fdl_point_f64_lt(fdl_point_f64_t a, fdl_point_f64_t b) {
    return (a.x < b.x || a.y < b.y) ? FDL_TRUE : FDL_FALSE;
}

int fdl_point_f64_gt(fdl_point_f64_t a, fdl_point_f64_t b) {
    return (a.x > b.x || a.y > b.y) ? FDL_TRUE : FDL_FALSE;
}

// ---------------------------------------------------------------------------
// Memory management
// ---------------------------------------------------------------------------

void fdl_free(void* ptr) {
    free(ptr); // NOLINT(cppcoreguidelines-no-malloc)
}
