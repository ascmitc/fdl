// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_constants.h
 * @brief Named constants replacing magic numbers throughout the FDL core library.
 *
 * Every numeric literal in the codebase (except 0 and 0.0) must be a named
 * constant defined here or in the public header (fdl_core.h). This ensures
 * readability-magic-numbers and cppcoreguidelines-avoid-magic-numbers pass
 * with no whitelist.
 */
#ifndef FDL_CONSTANTS_INTERNAL_H
#define FDL_CONSTANTS_INTERNAL_H

#include <cstddef>
#include <cstdint>

namespace fdl::constants {

/** @name Alignment factors
 *  Used by template application to position content within canvases.
 *  0.0 = left/top, 0.5 = center, 1.0 = right/bottom.
 *  @{ */
constexpr double kAlignStart = 0.0;  /**< Left or top alignment factor. */
constexpr double kAlignCenter = 0.5; /**< Center alignment factor. */
constexpr double kAlignEnd = 1.0;    /**< Right or bottom alignment factor. */
/** @} */

/** Divisor for centering content (span / 2 = center offset). */
constexpr double kCenterDivisor = 2.0;

/** @name Identity / default values
 *  @{ */
constexpr double kIdentitySqueeze = 1.0; /**< No anamorphic distortion (1:1 squeeze). */
/** @} */

/** @name Banker's rounding constants
 *  Used by fdl_round() for half-to-even rounding per the FDL spec.
 *  @{ */
constexpr double kHalfway = 0.5;               /**< Halfway value for rounding decisions. */
constexpr double kFpHalfwayTolerance = 1e-15;  /**< FP tolerance for detecting exact halfway values. */
constexpr int kEvenDivisor = 2;                /**< Divisor for even/odd detection (v % 2). */
constexpr int64_t kPositiveSign = 1;           /**< Positive sign multiplier. */
constexpr int64_t kNegativeSign = -1;          /**< Negative sign multiplier. */
constexpr int64_t kEvenRoundingAdjustment = 1; /**< Step for adjusting even-rounding results (v +/- 1). */
/** @} */

/** @name Protection factor
 *  Protection dimensions = framing_dims * (kProtectionBase - protection_fraction).
 *  @{ */
constexpr double kProtectionBase = 1.0; /**< Base factor for protection calculation (100%). */
/** @} */

/** @name Bit-packing shifts for handle deduplication keys
 *  @{ */
constexpr unsigned kPackKey2Shift = 32;     /**< Shift for packing two 32-bit indices into a 64-bit key. */
constexpr unsigned kPackKey3HighShift = 40; /**< High-index shift in three-value pack (bits [40..59]). */
constexpr unsigned kPackKey3MidShift = 20;  /**< Mid-index shift in three-value pack (bits [20..39]). */
/** @} */

/** @name FDL spec version defaults
 *  @{ */
constexpr int kDefaultVersionMajor = 2; /**< Default FDL specification version major. */
constexpr int kDefaultVersionMinor = 0; /**< Default FDL specification version minor. */
/** @} */

/** @name Buffer sizes
 *  @{ */
constexpr size_t kErrorBufferSize = 256; /**< Size of snprintf error message buffers. */
/** @} */

/** @name Geometry path return codes
 *  Used by geometry_get_dims_anchor_from_path and fdl_resolve_geometry_layer.
 *  @{ */
constexpr int kGeometryNotFound = 1;     /**< Requested geometry layer is not present. */
constexpr int kGeometryInvalidPath = -1; /**< Invalid geometry path enum value. */
/** @} */

/** @name Hash combination
 *  @{ */
constexpr size_t kHashCombineShift = 1; /**< Bit shift for XOR-based hash combination. */
/** @} */

/** @name Default framing intent aspect ratio (1:1)
 *  @{ */
constexpr int64_t kDefaultAspectRatio = 1; /**< 1:1 aspect ratio for generated framing intents. */
/** @} */

/** Default JSON serialization indent (spaces per level). */
constexpr int kDefaultJsonIndent = 2;

/** @name Custom attribute return codes and type values
 *  @{ */
constexpr int kCustomAttrSuccess = 0;           /**< Operation succeeded. */
constexpr int kCustomAttrError = -1;            /**< Operation failed (type mismatch, not found, etc.). */
constexpr uint32_t kCustomAttrTypeNone = 0;     /**< Attribute not found. */
constexpr uint32_t kCustomAttrTypeString = 1;   /**< String attribute. */
constexpr uint32_t kCustomAttrTypeInt = 2;      /**< Integer attribute. */
constexpr uint32_t kCustomAttrTypeFloat = 3;    /**< Floating-point attribute. */
constexpr uint32_t kCustomAttrTypeBool = 4;     /**< Boolean attribute. */
constexpr uint32_t kCustomAttrTypePointF64 = 5; /**< Point (x, y) attribute. */
constexpr uint32_t kCustomAttrTypeDimsF64 = 6;  /**< Dimensions (width, height) float attribute. */
constexpr uint32_t kCustomAttrTypeDimsI64 = 7;  /**< Dimensions (width, height) integer attribute. */
constexpr uint32_t kCustomAttrTypeOther = 8;    /**< Unsupported JSON type. */
/** @} */

/** Custom attribute key prefix character. */
constexpr char kCustomAttrPrefix = '_';

/** @name First-class custom attribute name constants
 *  Well-known attribute names set by template application.
 *  @{ */
constexpr const char* kAttrScaleFactor = "scale_factor";               /**< Template scale factor (float). */
constexpr const char* kAttrContentTranslation = "content_translation"; /**< Template content translation (point_f64). */
constexpr const char* kAttrScaledBoundingBox = "scaled_bounding_box";  /**< Template scaled bounding box (dims_f64). */
/** @} */

} // namespace fdl::constants

#endif // FDL_CONSTANTS_INTERNAL_H
