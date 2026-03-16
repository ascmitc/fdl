// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_geometry_api.cpp
 * @brief C ABI wrappers for geometry operations.
 */
#include "fdl/fdl_core.h"
#include "fdl_constants.h"
#include "fdl_geometry.h"

extern "C" {

fdl_geometry_t fdl_geometry_fill_hierarchy_gaps(fdl_geometry_t geo, fdl_point_f64_t anchor_offset) {
    return fdl::detail::geometry_fill_hierarchy_gaps(geo, anchor_offset);
}

fdl_geometry_t fdl_geometry_normalize_and_scale(
    fdl_geometry_t geo, double source_squeeze, double scale_factor, double target_squeeze) {
    return fdl::detail::geometry_normalize_and_scale(geo, source_squeeze, scale_factor, target_squeeze);
}

fdl_geometry_t fdl_geometry_round(fdl_geometry_t geo, fdl_round_strategy_t strategy) {
    return fdl::detail::geometry_round(geo, strategy);
}

fdl_geometry_t fdl_geometry_apply_offset(
    fdl_geometry_t geo,
    fdl_point_f64_t offset,
    fdl_point_f64_t* theo_eff,
    fdl_point_f64_t* theo_prot,
    fdl_point_f64_t* theo_fram) {
    return fdl::detail::geometry_apply_offset(geo, offset, theo_eff, theo_prot, theo_fram);
}

fdl_geometry_t fdl_geometry_crop(
    fdl_geometry_t geo, fdl_point_f64_t theo_eff, fdl_point_f64_t theo_prot, fdl_point_f64_t theo_fram) {
    return fdl::detail::geometry_crop(geo, theo_eff, theo_prot, theo_fram);
}

int fdl_geometry_get_dims_anchor_from_path(
    const fdl_geometry_t* geo, fdl_geometry_path_t path, fdl_dimensions_f64_t* out_dims, fdl_point_f64_t* out_anchor) {
    return fdl::detail::geometry_get_dims_anchor_from_path(geo, path, out_dims, out_anchor);
}

int fdl_resolve_geometry_layer(
    const fdl_canvas_t* canvas,
    const fdl_framing_decision_t* framing,
    fdl_geometry_path_t path,
    fdl_dimensions_f64_t* out_dims,
    fdl_point_f64_t* out_anchor) {

    *out_dims = {0.0, 0.0};
    *out_anchor = {0.0, 0.0};

    switch (path) {
    case FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS: {
        auto d = fdl_canvas_get_dimensions(canvas);
        *out_dims = {static_cast<double>(d.width), static_cast<double>(d.height)};
        return 0;
    }
    case FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS: {
        if (fdl_canvas_has_effective_dimensions(canvas) == 0) {
            return fdl::constants::kGeometryNotFound;
        }
        auto d = fdl_canvas_get_effective_dimensions(canvas);
        *out_dims = {static_cast<double>(d.width), static_cast<double>(d.height)};
        *out_anchor = fdl_canvas_get_effective_anchor_point(canvas);
        return 0;
    }
    case FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS: {
        if (fdl_framing_decision_has_protection(framing) == 0) {
            return fdl::constants::kGeometryNotFound;
        }
        *out_dims = fdl_framing_decision_get_protection_dimensions(framing);
        *out_anchor = fdl_framing_decision_get_protection_anchor_point(framing);
        return 0;
    }
    case FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS: {
        *out_dims = fdl_framing_decision_get_dimensions(framing);
        *out_anchor = fdl_framing_decision_get_anchor_point(framing);
        return 0;
    }
    default:
        return fdl::constants::kGeometryInvalidPath;
    }
}

// -----------------------------------------------------------------------
// Rect convenience — combine dims + anchor into (x, y, w, h)
// -----------------------------------------------------------------------

fdl_rect_t fdl_make_rect(double x, double y, double width, double height) {
    return {x, y, width, height};
}

fdl_rect_t fdl_canvas_get_rect(const fdl_canvas_t* canvas) {
    auto dims = fdl_canvas_get_dimensions(canvas);
    return fdl_make_rect(0.0, 0.0, static_cast<double>(dims.width), static_cast<double>(dims.height));
}

int fdl_canvas_get_effective_rect(const fdl_canvas_t* canvas, fdl_rect_t* out_rect) {
    if (fdl_canvas_has_effective_dimensions(canvas) == 0) {
        return 0;
    }
    auto dims = fdl_canvas_get_effective_dimensions(canvas);
    auto pt = fdl_canvas_get_effective_anchor_point(canvas);
    *out_rect = fdl_make_rect(pt.x, pt.y, static_cast<double>(dims.width), static_cast<double>(dims.height));
    return FDL_TRUE;
}

fdl_rect_t fdl_framing_decision_get_rect(const fdl_framing_decision_t* fd) {
    auto dims = fdl_framing_decision_get_dimensions(fd);
    auto pt = fdl_framing_decision_get_anchor_point(fd);
    return fdl_make_rect(pt.x, pt.y, dims.width, dims.height);
}

int fdl_framing_decision_get_protection_rect(const fdl_framing_decision_t* fd, fdl_rect_t* out_rect) {
    if (fdl_framing_decision_has_protection(fd) == 0) {
        return 0;
    }
    auto dims = fdl_framing_decision_get_protection_dimensions(fd);
    auto pt = fdl_framing_decision_get_protection_anchor_point(fd);
    *out_rect = fdl_make_rect(pt.x, pt.y, dims.width, dims.height);
    return FDL_TRUE;
}

} // extern "C"
