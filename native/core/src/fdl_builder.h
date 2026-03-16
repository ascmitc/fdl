// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_builder.h
 * @brief Internal helpers for constructing FDL JSON objects with canonical key order.
 *
 * Each make_* function creates an ojson object with keys inserted in the
 * FDL specification's canonical order, ready for serialization.
 */
#ifndef FDL_BUILDER_INTERNAL_H
#define FDL_BUILDER_INTERNAL_H

#include "fdl/fdl_core.h"
#include "fdl_doc.h"
#include "fdl_handles.h"

#include <jsoncons/json.hpp>
#include <string>

namespace fdl::detail {

using ojson = jsoncons::ojson;

/** @name Primitive builders — canonical key order */
/** @{ */

/**
 * @brief Build a version object {"major":…,"minor":…}.
 * @param major  Major version number.
 * @param minor  Minor version number.
 * @return ojson version object.
 */
ojson make_version(int major, int minor);

/**
 * @brief Build an integer dimensions object {"width":…,"height":…}.
 * @param width   Width in pixels.
 * @param height  Height in pixels.
 * @return ojson dimensions object.
 */
ojson make_dimensions_int(int64_t width, int64_t height);

/**
 * @brief Build a floating-point dimensions object {"width":…,"height":…}.
 * @param width   Width.
 * @param height  Height.
 * @return ojson dimensions object.
 */
ojson make_dimensions_float(double width, double height);

/**
 * @brief Build a point object {"x":…,"y":…}.
 * @param x  X coordinate.
 * @param y  Y coordinate.
 * @return ojson point object.
 */
ojson make_point_float(double x, double y);

/**
 * @brief Build a round_strategy object {"even":…,"mode":…}.
 * @param even  Rounding even string ("even" or "whole").
 * @param mode  Rounding mode string ("up", "down", or "round").
 * @return ojson round_strategy object.
 */
ojson make_round_strategy(const char* even, const char* mode);
/** @} */

/**
 * @brief Build a minimal FDL root document object with canonical key order.
 * @param uuid                    Document UUID string.
 * @param version_major           FDL spec major version.
 * @param version_minor           FDL spec minor version.
 * @param fdl_creator             Creator identifier string.
 * @param default_framing_intent  ID of the default framing intent.
 * @return ojson root document object.
 */
ojson make_root(
    const char* uuid,
    int version_major,
    int version_minor,
    const char* fdl_creator,
    const char* default_framing_intent);

/** @name Sub-object builders — canonical key order */
/** @{ */

/**
 * @brief Build a framing_intent JSON object.
 * @param id          Intent identifier.
 * @param label       Human-readable label.
 * @param aspect_w    Aspect ratio width component.
 * @param aspect_h    Aspect ratio height component.
 * @param protection  Protection factor (0.0–1.0, 0 = no protection).
 * @return ojson framing_intent object.
 */
ojson make_framing_intent(const char* id, const char* label, int64_t aspect_w, int64_t aspect_h, double protection);

/**
 * @brief Build a context JSON object.
 * @param label            Context label.
 * @param context_creator  Creator identifier.
 * @return ojson context object.
 */
ojson make_context(const char* label, const char* context_creator);

/**
 * @brief Build a canvas JSON object.
 * @param id                Canvas identifier.
 * @param label             Human-readable label.
 * @param source_canvas_id  ID of the source canvas (may be same as id).
 * @param dim_w             Canvas width in pixels.
 * @param dim_h             Canvas height in pixels.
 * @param squeeze           Anamorphic squeeze ratio (1.0 for spherical).
 * @return ojson canvas object.
 */
ojson make_canvas(
    const char* id, const char* label, const char* source_canvas_id, int64_t dim_w, int64_t dim_h, double squeeze);

/**
 * @brief Build a framing_decision JSON object.
 * @param id                  Decision identifier.
 * @param label               Human-readable label.
 * @param framing_intent_id   ID of the referenced framing intent.
 * @param dim_w               Framing width.
 * @param dim_h               Framing height.
 * @param anchor_x            Anchor X offset within canvas.
 * @param anchor_y            Anchor Y offset within canvas.
 * @return ojson framing_decision object.
 */
ojson make_framing_decision(
    const char* id,
    const char* label,
    const char* framing_intent_id,
    double dim_w,
    double dim_h,
    double anchor_x,
    double anchor_y);

/**
 * @brief Build a canvas_template JSON object.
 * @param id              Template identifier.
 * @param label           Human-readable label.
 * @param target_w        Target canvas width in pixels.
 * @param target_h        Target canvas height in pixels.
 * @param target_squeeze  Target anamorphic squeeze.
 * @param fit_source      Geometry path for fit source layer.
 * @param fit_method      Fit method (width, height, fill, fit_all).
 * @param halign          Horizontal alignment.
 * @param valign          Vertical alignment.
 * @param rounding        Rounding strategy for dimensions.
 * @return ojson canvas_template object.
 */
ojson make_canvas_template(
    const char* id,
    const char* label,
    int64_t target_w,
    int64_t target_h,
    double target_squeeze,
    fdl_geometry_path_t fit_source,
    fdl_fit_method_t fit_method,
    fdl_halign_t halign,
    fdl_valign_t valign,
    fdl_round_strategy_t rounding);
/** @} */

} // namespace fdl::detail

#endif // FDL_BUILDER_INTERNAL_H
