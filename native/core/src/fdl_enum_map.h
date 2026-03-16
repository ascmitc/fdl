// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_enum_map.h
 * @brief Bidirectional string<->enum conversions for FDL enumerated types.
 *
 * Each enum type has a from_string (for parsing) and to_string (for serialization)
 * function. Unrecognized inputs return a sensible default.
 */
#ifndef FDL_ENUM_MAP_H
#define FDL_ENUM_MAP_H

#include "fdl/fdl_core.h"

#include <string>
#include <string_view>

namespace fdl::detail {

/**
 * @brief Convert fit method string to enum. Default: FDL_FIT_METHOD_WIDTH.
 * @param s  String to convert ("width", "height", "fit_all", "fill").
 * @return Corresponding enum value.
 */
inline fdl_fit_method_t fit_method_from_string(std::string_view s) {
    if (s == "width") {
        return FDL_FIT_METHOD_WIDTH;
    }
    if (s == "height") {
        return FDL_FIT_METHOD_HEIGHT;
    }
    if (s == "fit_all") {
        return FDL_FIT_METHOD_FIT_ALL;
    }
    if (s == "fill") {
        return FDL_FIT_METHOD_FILL;
    }
    return FDL_FIT_METHOD_WIDTH; // default
}

/**
 * @brief Convert geometry path string to enum. Default: FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS.
 * @param s  String to convert (e.g. "canvas.dimensions").
 * @return Corresponding enum value.
 */
inline fdl_geometry_path_t geometry_path_from_string(std::string_view s) {
    if (s == "canvas.dimensions") {
        return FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS;
    }
    if (s == "canvas.effective_dimensions") {
        return FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS;
    }
    if (s == "framing_decision.protection_dimensions") {
        return FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS;
    }
    if (s == "framing_decision.dimensions") {
        return FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS;
    }
    return FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS; // default
}

/**
 * @brief Convert horizontal alignment string to enum. Default: FDL_HALIGN_CENTER.
 * @param s  String to convert ("left", "center", "right").
 * @return Corresponding enum value.
 */
inline fdl_halign_t halign_from_string(std::string_view s) {
    if (s == "left") {
        return FDL_HALIGN_LEFT;
    }
    if (s == "center") {
        return FDL_HALIGN_CENTER;
    }
    if (s == "right") {
        return FDL_HALIGN_RIGHT;
    }
    return FDL_HALIGN_CENTER; // default
}

/**
 * @brief Convert vertical alignment string to enum. Default: FDL_VALIGN_CENTER.
 * @param s  String to convert ("top", "center", "bottom").
 * @return Corresponding enum value.
 */
inline fdl_valign_t valign_from_string(std::string_view s) {
    if (s == "top") {
        return FDL_VALIGN_TOP;
    }
    if (s == "center") {
        return FDL_VALIGN_CENTER;
    }
    if (s == "bottom") {
        return FDL_VALIGN_BOTTOM;
    }
    return FDL_VALIGN_CENTER; // default
}

/**
 * @brief Convert rounding even string to enum. Default: FDL_ROUNDING_EVEN_WHOLE.
 * @param s  String to convert ("even" or "whole").
 * @return Corresponding enum value.
 */
inline fdl_rounding_even_t rounding_even_from_string(std::string_view s) {
    if (s == "even") {
        return FDL_ROUNDING_EVEN_EVEN;
    }
    if (s == "whole") {
        return FDL_ROUNDING_EVEN_WHOLE;
    }
    return FDL_ROUNDING_EVEN_WHOLE; // default
}

/**
 * @brief Convert rounding mode string to enum. Default: FDL_ROUNDING_MODE_ROUND.
 * @param s  String to convert ("up", "down", "round").
 * @return Corresponding enum value.
 */
inline fdl_rounding_mode_t rounding_mode_from_string(std::string_view s) {
    if (s == "up") {
        return FDL_ROUNDING_MODE_UP;
    }
    if (s == "down") {
        return FDL_ROUNDING_MODE_DOWN;
    }
    if (s == "round") {
        return FDL_ROUNDING_MODE_ROUND;
    }
    return FDL_ROUNDING_MODE_ROUND; // default
}

/** @name Enum-to-string (reverse mappings for builder/serialization) */
/** @{ */

/**
 * @brief Convert fit method enum to canonical JSON string.
 * @param m  Fit method enum value.
 * @return Static string literal.
 */
inline const char* fit_method_to_string(fdl_fit_method_t m) {
    switch (m) {
    case FDL_FIT_METHOD_WIDTH:
        return "width";
    case FDL_FIT_METHOD_HEIGHT:
        return "height";
    case FDL_FIT_METHOD_FIT_ALL:
        return "fit_all";
    case FDL_FIT_METHOD_FILL:
        return "fill";
    default:
        return "width";
    }
}

/**
 * @brief Convert geometry path enum to canonical JSON string.
 * @param p  Geometry path enum value.
 * @return Static string literal.
 */
inline const char* geometry_path_to_string(fdl_geometry_path_t p) {
    switch (p) {
    case FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS:
        return "canvas.dimensions";
    case FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS:
        return "canvas.effective_dimensions";
    case FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS:
        return "framing_decision.protection_dimensions";
    default:
        return "framing_decision.dimensions";
    }
}

/**
 * @brief Convert horizontal alignment enum to canonical JSON string.
 * @param h  Horizontal alignment enum value.
 * @return Static string literal.
 */
inline const char* halign_to_string(fdl_halign_t h) {
    switch (h) {
    case FDL_HALIGN_LEFT:
        return "left";
    case FDL_HALIGN_CENTER:
        return "center";
    case FDL_HALIGN_RIGHT:
        return "right";
    default:
        return "center";
    }
}

/**
 * @brief Convert vertical alignment enum to canonical JSON string.
 * @param v  Vertical alignment enum value.
 * @return Static string literal.
 */
inline const char* valign_to_string(fdl_valign_t v) {
    switch (v) {
    case FDL_VALIGN_TOP:
        return "top";
    case FDL_VALIGN_CENTER:
        return "center";
    case FDL_VALIGN_BOTTOM:
        return "bottom";
    default:
        return "center";
    }
}

/**
 * @brief Convert rounding even enum to canonical JSON string.
 * @param e  Rounding even enum value.
 * @return Static string literal.
 */
inline const char* rounding_even_to_string(fdl_rounding_even_t e) {
    switch (e) {
    case FDL_ROUNDING_EVEN_WHOLE:
        return "whole";
    case FDL_ROUNDING_EVEN_EVEN:
        return "even";
    default:
        return "whole";
    }
}

/**
 * @brief Convert rounding mode enum to canonical JSON string.
 * @param m  Rounding mode enum value.
 * @return Static string literal.
 */
inline const char* rounding_mode_to_string(fdl_rounding_mode_t m) {
    switch (m) {
    case FDL_ROUNDING_MODE_UP:
        return "up";
    case FDL_ROUNDING_MODE_DOWN:
        return "down";
    default:
        return "round";
    }
}

/** @} */

} // namespace fdl::detail

#endif // FDL_ENUM_MAP_H
