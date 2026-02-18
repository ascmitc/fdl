// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_core.h
 * @brief Public C ABI for the FDL (Framing Decision List) core library.
 *
 * Provides document parsing, serialization, validation, geometry operations,
 * template application, and a builder API for creating FDL documents.
 * All public symbols use the @c FDL_API export macro for shared-library visibility.
 *
 * Thread safety: per-document mutex locking. See @ref THREAD_SAFETY for details.
 */
#ifndef FDL_CORE_H
#define FDL_CORE_H

#include "fdl_export.h"
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* -----------------------------------------------------------------------
 * Boolean constants for C ABI int fields/returns
 * ----------------------------------------------------------------------- */

/** Boolean constants for C ABI @c int fields and return values. */
#define FDL_TRUE 1  /**< Boolean true. */
#define FDL_FALSE 0 /**< Boolean false. */

/** Default JSON serialization indent. */
#define FDL_DEFAULT_JSON_INDENT 2 /**< Spaces per indent level. */

/* -----------------------------------------------------------------------
 * Custom attribute type constants
 * ----------------------------------------------------------------------- */

/** @brief Type identifier for custom attributes. */
typedef uint32_t fdl_custom_attr_type_t;
#define FDL_CUSTOM_ATTR_TYPE_NONE 0      /**< Attribute not found. */
#define FDL_CUSTOM_ATTR_TYPE_STRING 1    /**< String attribute. */
#define FDL_CUSTOM_ATTR_TYPE_INT 2       /**< Integer attribute. */
#define FDL_CUSTOM_ATTR_TYPE_FLOAT 3     /**< Floating-point attribute. */
#define FDL_CUSTOM_ATTR_TYPE_BOOL 4      /**< Boolean attribute. */
#define FDL_CUSTOM_ATTR_TYPE_POINT_F64 5 /**< Point (x, y) attribute. */
#define FDL_CUSTOM_ATTR_TYPE_DIMS_F64 6  /**< Dimensions (width, height) float attribute. */
#define FDL_CUSTOM_ATTR_TYPE_DIMS_I64 7  /**< Dimensions (width, height) integer attribute. */
#define FDL_CUSTOM_ATTR_TYPE_OTHER 8     /**< Unsupported JSON type. */

/* -----------------------------------------------------------------------
 * First-class custom attribute name constants
 * ----------------------------------------------------------------------- */

/** @brief Custom attribute name for the template scale factor (float). */
#define FDL_ATTR_SCALE_FACTOR "scale_factor"
/** @brief Custom attribute name for the template content translation (point_f64). */
#define FDL_ATTR_CONTENT_TRANSLATION "content_translation"
/** @brief Custom attribute name for the template scaled bounding box (dims_f64). */
#define FDL_ATTR_SCALED_BOUNDING_BOX "scaled_bounding_box"

/* -----------------------------------------------------------------------
 * ABI version
 * ----------------------------------------------------------------------- */

/** ABI version triple for runtime compatibility checks. */
typedef struct fdl_abi_version_t {
    uint32_t major; /**< Breaking changes increment this. */
    uint32_t minor; /**< Backwards-compatible additions increment this. */
    uint32_t patch; /**< Bug-fix releases increment this. */
} fdl_abi_version_t;

/**
 * Return the ABI version of the loaded library.
 *
 * @return ABI version triple (major, minor, patch).
 */
FDL_API fdl_abi_version_t fdl_abi_version(void);

/* -----------------------------------------------------------------------
 * Value types (pass by value, no heap allocation)
 * ----------------------------------------------------------------------- */

/** Canvas dimensions in integer pixels. */
typedef struct fdl_dimensions_i64_t {
    int64_t width;  /**< Width in pixels. */
    int64_t height; /**< Height in pixels. */
} fdl_dimensions_i64_t;

/** Floating-point dimensions (used during computation). */
typedef struct fdl_dimensions_f64_t {
    double width;  /**< Width (may be fractional during intermediate calculations). */
    double height; /**< Height (may be fractional during intermediate calculations). */
} fdl_dimensions_f64_t;

/** 2D point in floating-point coordinates. */
typedef struct fdl_point_f64_t {
    double x; /**< Horizontal position (pixels from left edge). */
    double y; /**< Vertical position (pixels from top edge). */
} fdl_point_f64_t;

/** Axis-aligned rectangle (x, y origin + width, height). */
typedef struct fdl_rect_t {
    double x;      /**< Left edge x-coordinate. */
    double y;      /**< Top edge y-coordinate. */
    double width;  /**< Rectangle width. */
    double height; /**< Rectangle height. */
} fdl_rect_t;

/* Note: fdl_clip_id_t and fdl_file_sequence_t are opaque handle types,
 * declared alongside other sub-object handles in the Document Model section. */

/* -----------------------------------------------------------------------
 * Enums (as uint32_t constants)
 * ----------------------------------------------------------------------- */

/** Rounding mode — direction to round fractional pixel values. */
typedef uint32_t fdl_rounding_mode_t;
#define FDL_ROUNDING_MODE_UP 0    /**< Always round up (ceiling). */
#define FDL_ROUNDING_MODE_DOWN 1  /**< Always round down (floor). */
#define FDL_ROUNDING_MODE_ROUND 2 /**< Round to nearest (half-to-even). */

/** Rounding even — whether to snap results to even numbers. */
typedef uint32_t fdl_rounding_even_t;
#define FDL_ROUNDING_EVEN_WHOLE 0 /**< No even constraint (round to nearest integer). */
#define FDL_ROUNDING_EVEN_EVEN 1  /**< Snap to nearest even integer after rounding. */

/** Geometry path — selects a dimension layer within the FDL hierarchy. */
typedef uint32_t fdl_geometry_path_t;
#define FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS 0             /**< Full canvas dimensions. */
#define FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS 1   /**< Effective (active image) dimensions. */
#define FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS 2 /**< Protection area dimensions. */
#define FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS 3            /**< Framing decision dimensions. */

/** Fit method — how source content is scaled into the target canvas. */
typedef uint32_t fdl_fit_method_t;
#define FDL_FIT_METHOD_WIDTH 0   /**< Scale to match target width. */
#define FDL_FIT_METHOD_HEIGHT 1  /**< Scale to match target height. */
#define FDL_FIT_METHOD_FIT_ALL 2 /**< Scale to fit entirely within target (letterbox/pillarbox). */
#define FDL_FIT_METHOD_FILL 3    /**< Scale to fill target completely (may crop). */

/** Horizontal alignment — how content is positioned horizontally. */
typedef uint32_t fdl_halign_t;
#define FDL_HALIGN_LEFT 0   /**< Align to left edge. */
#define FDL_HALIGN_CENTER 1 /**< Center horizontally. */
#define FDL_HALIGN_RIGHT 2  /**< Align to right edge. */

/** Vertical alignment — how content is positioned vertically. */
typedef uint32_t fdl_valign_t;
#define FDL_VALIGN_TOP 0    /**< Align to top edge. */
#define FDL_VALIGN_CENTER 1 /**< Center vertically. */
#define FDL_VALIGN_BOTTOM 2 /**< Align to bottom edge. */

/* -----------------------------------------------------------------------
 * Composite types
 * ----------------------------------------------------------------------- */

/** Geometry container for FDL template transformation processing.
 *  Holds 4 dimension layers + 3 anchor points through the pipeline. */
typedef struct fdl_geometry_t {
    fdl_dimensions_f64_t canvas_dims;     /**< Full canvas dimensions. */
    fdl_dimensions_f64_t effective_dims;  /**< Effective (active image) dimensions. */
    fdl_dimensions_f64_t protection_dims; /**< Protection area dimensions. */
    fdl_dimensions_f64_t framing_dims;    /**< Framing decision dimensions. */
    fdl_point_f64_t effective_anchor;     /**< Anchor point for effective area. */
    fdl_point_f64_t protection_anchor;    /**< Anchor point for protection area. */
    fdl_point_f64_t framing_anchor;       /**< Anchor point for framing decision. */
} fdl_geometry_t;

/** Rounding strategy combining even-snap and direction mode. */
typedef struct fdl_round_strategy_t {
    fdl_rounding_even_t even; /**< Whether to snap to even integers. */
    fdl_rounding_mode_t mode; /**< Rounding direction (up, down, nearest). */
} fdl_round_strategy_t;

/** Result of computing a framing decision from a framing intent. */
typedef struct fdl_from_intent_result_t {
    fdl_dimensions_f64_t dimensions;            /**< Computed framing dimensions. */
    fdl_point_f64_t anchor_point;               /**< Computed anchor point. */
    int has_protection;                         /**< FDL_TRUE if protection was computed, FDL_FALSE otherwise. */
    fdl_dimensions_f64_t protection_dimensions; /**< Protection dimensions (valid if has_protection). */
    fdl_point_f64_t protection_anchor_point;    /**< Protection anchor (valid if has_protection). */
} fdl_from_intent_result_t;

/* -----------------------------------------------------------------------
 * Rounding functions
 * ----------------------------------------------------------------------- */

/**
 * Round a single value according to FDL rounding rules.
 *
 * @param value  The floating-point value to round.
 * @param even   Even constraint (FDL_ROUNDING_EVEN_WHOLE or _EVEN).
 * @param mode   Rounding direction (FDL_ROUNDING_MODE_UP, _DOWN, or _ROUND).
 * @return Rounded integer value.
 */
FDL_API int64_t fdl_round(double value, fdl_rounding_even_t even, fdl_rounding_mode_t mode);

/**
 * Round dimensions according to FDL rounding rules.
 *
 * @param dims  Dimensions to round.
 * @param even  Even constraint.
 * @param mode  Rounding direction.
 * @return Rounded dimensions (both width and height rounded independently).
 */
FDL_API fdl_dimensions_f64_t
fdl_round_dimensions(fdl_dimensions_f64_t dims, fdl_rounding_even_t even, fdl_rounding_mode_t mode);

/**
 * Round a point according to FDL rounding rules.
 *
 * @param point  Point to round.
 * @param even   Even constraint.
 * @param mode   Rounding direction.
 * @return Rounded point (both x and y rounded independently).
 */
FDL_API fdl_point_f64_t fdl_round_point(fdl_point_f64_t point, fdl_rounding_even_t even, fdl_rounding_mode_t mode);

/* -----------------------------------------------------------------------
 * Dimensions operations
 * ----------------------------------------------------------------------- */

/**
 * Normalize dimensions by applying anamorphic squeeze to width.
 *
 * Converts from squeezed (sensor) coordinates to unsqueezed (display) coordinates.
 * width *= squeeze; height unchanged.
 *
 * @param dims     Dimensions to normalize.
 * @param squeeze  Anamorphic squeeze factor (e.g. 2.0 for 2x anamorphic).
 * @return Normalized dimensions.
 */
FDL_API fdl_dimensions_f64_t fdl_dimensions_normalize(fdl_dimensions_f64_t dims, double squeeze);

/**
 * Scale normalized dimensions and apply target squeeze.
 *
 * width = (width * scale_factor) / target_squeeze;
 * height = height * scale_factor.
 *
 * @param dims           Normalized dimensions to scale.
 * @param scale_factor   Scale multiplier.
 * @param target_squeeze Target anamorphic squeeze to apply.
 * @return Scaled dimensions in target coordinate space.
 */
FDL_API fdl_dimensions_f64_t
fdl_dimensions_scale(fdl_dimensions_f64_t dims, double scale_factor, double target_squeeze);

/**
 * Normalize and scale in one step.
 *
 * Equivalent to fdl_dimensions_scale(fdl_dimensions_normalize(dims, input_squeeze), ...).
 *
 * @param dims            Dimensions to transform.
 * @param input_squeeze   Source anamorphic squeeze factor.
 * @param scale_factor    Scale multiplier.
 * @param target_squeeze  Target anamorphic squeeze factor.
 * @return Transformed dimensions.
 */
FDL_API fdl_dimensions_f64_t fdl_dimensions_normalize_and_scale(
    fdl_dimensions_f64_t dims, double input_squeeze, double scale_factor, double target_squeeze);

/**
 * Subtract two dimensions: result = a - b.
 *
 * @param a  Minuend dimensions.
 * @param b  Subtrahend dimensions.
 * @return Component-wise difference (a.width - b.width, a.height - b.height).
 */
FDL_API fdl_dimensions_f64_t fdl_dimensions_sub(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b);

/**
 * Check if dimensions are approximately equal within FDL tolerance.
 *
 * Uses relative tolerance of 1e-9 and absolute tolerance of 1e-6.
 *
 * @param a  First dimensions.
 * @param b  Second dimensions.
 * @return FDL_TRUE if approximately equal, FDL_FALSE otherwise.
 */
FDL_API int fdl_dimensions_equal(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b);

/**
 * Check if a > b using OR logic (either width or height is greater).
 *
 * @param a  First dimensions.
 * @param b  Second dimensions.
 * @return FDL_TRUE if a.width > b.width OR a.height > b.height, FDL_FALSE otherwise.
 */
FDL_API int fdl_dimensions_f64_gt(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b);

/**
 * Check if a < b using OR logic (either width or height is less).
 *
 * @param a  First dimensions.
 * @param b  Second dimensions.
 * @return FDL_TRUE if a.width < b.width OR a.height < b.height, FDL_FALSE otherwise.
 */
FDL_API int fdl_dimensions_f64_lt(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b);

/**
 * Check if both width and height are zero.
 *
 * @param dims  Dimensions to test.
 * @return FDL_TRUE if both components are zero, FDL_FALSE otherwise.
 */
FDL_API int fdl_dimensions_is_zero(fdl_dimensions_f64_t dims);

/* -----------------------------------------------------------------------
 * Dimensions (integer) operations
 * ----------------------------------------------------------------------- */

/**
 * Check if both width and height are zero (int64 variant).
 *
 * @param dims  Integer dimensions to test.
 * @return FDL_TRUE if both components are zero, FDL_FALSE otherwise.
 */
FDL_API int fdl_dimensions_i64_is_zero(fdl_dimensions_i64_t dims);

/**
 * Normalize int64 dimensions by applying anamorphic squeeze to width.
 *
 * @param dims     Integer dimensions to normalize.
 * @param squeeze  Anamorphic squeeze factor.
 * @return Float dimensions: width = width * squeeze, height unchanged.
 */
FDL_API fdl_dimensions_f64_t fdl_dimensions_i64_normalize(fdl_dimensions_i64_t dims, double squeeze);

/**
 * Convert float dimensions to int64 by truncation.
 *
 * @param dims  Float dimensions to convert.
 * @return Integer dimensions (truncated toward zero).
 */
FDL_API fdl_dimensions_i64_t fdl_dimensions_f64_to_i64(fdl_dimensions_f64_t dims);

/**
 * Check if a > b using OR logic (either width or height is greater).
 *
 * @param a  First dimensions.
 * @param b  Second dimensions.
 * @return FDL_TRUE if a.width > b.width OR a.height > b.height, FDL_FALSE otherwise.
 */
FDL_API int fdl_dimensions_i64_gt(fdl_dimensions_i64_t a, fdl_dimensions_i64_t b);

/**
 * Check if a < b using OR logic (either width or height is less).
 *
 * @param a  First dimensions.
 * @param b  Second dimensions.
 * @return FDL_TRUE if a.width < b.width OR a.height < b.height, FDL_FALSE otherwise.
 */
FDL_API int fdl_dimensions_i64_lt(fdl_dimensions_i64_t a, fdl_dimensions_i64_t b);

/* -----------------------------------------------------------------------
 * Point operations
 * ----------------------------------------------------------------------- */

/**
 * Normalize a point by applying anamorphic squeeze to x.
 *
 * @param point    Point to normalize.
 * @param squeeze  Anamorphic squeeze factor.
 * @return Normalized point: x *= squeeze, y unchanged.
 */
FDL_API fdl_point_f64_t fdl_point_normalize(fdl_point_f64_t point, double squeeze);

/**
 * Scale a normalized point and apply target squeeze.
 *
 * x = (x * scale_factor) / target_squeeze;
 * y = y * scale_factor.
 *
 * @param point          Normalized point to scale.
 * @param scale_factor   Scale multiplier.
 * @param target_squeeze Target anamorphic squeeze.
 * @return Scaled point in target coordinate space.
 */
FDL_API fdl_point_f64_t fdl_point_scale(fdl_point_f64_t point, double scale_factor, double target_squeeze);

/**
 * Add two points: result = a + b.
 *
 * @param a  First point.
 * @param b  Second point.
 * @return Component-wise sum.
 */
FDL_API fdl_point_f64_t fdl_point_add(fdl_point_f64_t a, fdl_point_f64_t b);

/**
 * Subtract two points: result = a - b.
 *
 * @param a  Minuend point.
 * @param b  Subtrahend point.
 * @return Component-wise difference.
 */
FDL_API fdl_point_f64_t fdl_point_sub(fdl_point_f64_t a, fdl_point_f64_t b);

/**
 * Multiply point by scalar.
 *
 * @param a       Point to scale.
 * @param scalar  Scalar multiplier applied to both x and y.
 * @return Scaled point.
 */
FDL_API fdl_point_f64_t fdl_point_mul_scalar(fdl_point_f64_t a, double scalar);

/**
 * Clamp point values to [min_val, max_val].
 *
 * Each bound is optional — set the corresponding has_* flag to enable it.
 *
 * @param point    Point to clamp.
 * @param min_val  Minimum bound (applied to both x and y).
 * @param max_val  Maximum bound (applied to both x and y).
 * @param has_min  FDL_TRUE to apply min_val, FDL_FALSE to skip.
 * @param has_max  FDL_TRUE to apply max_val, FDL_FALSE to skip.
 * @return Clamped point.
 */
FDL_API fdl_point_f64_t
fdl_point_clamp(fdl_point_f64_t point, double min_val, double max_val, int has_min, int has_max);

/**
 * Check if both x and y are zero.
 *
 * @param point  Point to test.
 * @return FDL_TRUE if both components are zero, FDL_FALSE otherwise.
 */
FDL_API int fdl_point_is_zero(fdl_point_f64_t point);

/**
 * Normalize and scale a point in one step.
 *
 * @param point          Point to transform.
 * @param input_squeeze  Source anamorphic squeeze factor.
 * @param scale_factor   Scale multiplier.
 * @param target_squeeze Target anamorphic squeeze factor.
 * @return Transformed point.
 */
FDL_API fdl_point_f64_t
fdl_point_normalize_and_scale(fdl_point_f64_t point, double input_squeeze, double scale_factor, double target_squeeze);

/**
 * Check approximate equality within FDL tolerances.
 *
 * @param a  First point.
 * @param b  Second point.
 * @return FDL_TRUE if approximately equal, FDL_FALSE otherwise.
 */
FDL_API int fdl_point_equal(fdl_point_f64_t a, fdl_point_f64_t b);

/**
 * Check if a < b using OR logic (either x or y is less).
 *
 * @param a  First point.
 * @param b  Second point.
 * @return FDL_TRUE if a.x < b.x OR a.y < b.y, FDL_FALSE otherwise.
 */
FDL_API int fdl_point_f64_lt(fdl_point_f64_t a, fdl_point_f64_t b);

/**
 * Check if a > b using OR logic (either x or y is greater).
 *
 * @param a  First point.
 * @param b  Second point.
 * @return FDL_TRUE if a.x > b.x OR a.y > b.y, FDL_FALSE otherwise.
 */
FDL_API int fdl_point_f64_gt(fdl_point_f64_t a, fdl_point_f64_t b);

/* -----------------------------------------------------------------------
 * Floating-point comparison constants
 * ----------------------------------------------------------------------- */

/**
 * Relative tolerance for floating-point comparison.
 *
 * @return 1e-9.
 */
FDL_API double fdl_fp_rel_tol(void);

/**
 * Absolute tolerance for floating-point comparison.
 *
 * @return 1e-6.
 */
FDL_API double fdl_fp_abs_tol(void);

/* -----------------------------------------------------------------------
 * Geometry operations
 * ----------------------------------------------------------------------- */

/**
 * Fill gaps in the geometry hierarchy by propagating populated dimensions upward.
 *
 * If a higher-level dimension is zero but a lower level is set, the gap is filled
 * by copying from the populated layer. Protection is NEVER filled from framing.
 * Anchor points are offset by anchor_offset and clamped to >= 0.
 *
 * @param geo            Geometry with potentially sparse dimension layers.
 * @param anchor_offset  Offset applied to anchors during gap-filling.
 * @return Geometry with gaps filled.
 */
FDL_API fdl_geometry_t fdl_geometry_fill_hierarchy_gaps(fdl_geometry_t geo, fdl_point_f64_t anchor_offset);

/**
 * Normalize and scale all 7 fields of the geometry.
 *
 * Applies anamorphic normalization and scaling to all dimension and anchor fields.
 *
 * @param geo             Geometry to transform.
 * @param source_squeeze  Source anamorphic squeeze factor.
 * @param scale_factor    Scale multiplier.
 * @param target_squeeze  Target anamorphic squeeze factor.
 * @return Transformed geometry.
 */
FDL_API fdl_geometry_t
fdl_geometry_normalize_and_scale(fdl_geometry_t geo, double source_squeeze, double scale_factor, double target_squeeze);

/**
 * Round all 7 fields of the geometry.
 *
 * @param geo       Geometry to round.
 * @param strategy  Rounding strategy (even + mode).
 * @return Rounded geometry.
 */
FDL_API fdl_geometry_t fdl_geometry_round(fdl_geometry_t geo, fdl_round_strategy_t strategy);

/**
 * Apply offset to all anchors, clamping to canvas bounds.
 *
 * The theoretical (unclamped) anchor values are written to the output
 * pointers for use in subsequent cropping.
 *
 * @param geo        Geometry to offset.
 * @param offset     Translation to apply to all anchor points.
 * @param theo_eff   [out] Unclamped effective anchor (may be NULL).
 * @param theo_prot  [out] Unclamped protection anchor (may be NULL).
 * @param theo_fram  [out] Unclamped framing anchor (may be NULL).
 * @return Geometry with clamped anchors.
 */
FDL_API fdl_geometry_t fdl_geometry_apply_offset(
    fdl_geometry_t geo,
    fdl_point_f64_t offset,
    fdl_point_f64_t* theo_eff,
    fdl_point_f64_t* theo_prot,
    fdl_point_f64_t* theo_fram);

/**
 * Crop all dimensions to visible portion within canvas.
 *
 * Enforces the hierarchy invariant: canvas >= effective >= protection >= framing.
 * Uses theoretical (unclamped) anchors to compute visible extents.
 *
 * @param geo        Geometry to crop.
 * @param theo_eff   Theoretical effective anchor (from fdl_geometry_apply_offset).
 * @param theo_prot  Theoretical protection anchor.
 * @param theo_fram  Theoretical framing anchor.
 * @return Cropped geometry.
 */
FDL_API fdl_geometry_t
fdl_geometry_crop(fdl_geometry_t geo, fdl_point_f64_t theo_eff, fdl_point_f64_t theo_prot, fdl_point_f64_t theo_fram);

/**
 * Extract dimensions and anchor from geometry by path.
 *
 * @param geo         Geometry to query.
 * @param path        Which dimension layer to extract (canvas, effective, protection, or framing).
 * @param out_dims    [out] Extracted dimensions.
 * @param out_anchor  [out] Extracted anchor point ({0,0} for canvas path).
 * @return 0 on success, -1 on invalid path.
 */
FDL_API int fdl_geometry_get_dims_anchor_from_path(
    const fdl_geometry_t* geo, fdl_geometry_path_t path, fdl_dimensions_f64_t* out_dims, fdl_point_f64_t* out_anchor);

/* -----------------------------------------------------------------------
 * Pipeline helper functions
 * ----------------------------------------------------------------------- */

/**
 * Calculate scale factor based on fit method.
 *
 * Computes the ratio needed to scale source (fit_norm) into target (target_norm)
 * using the specified fit method.
 *
 * @param fit_norm    Normalized source dimensions.
 * @param target_norm Normalized target dimensions.
 * @param fit_method  Fit method (WIDTH, HEIGHT, FIT_ALL, or FILL).
 * @return Scale factor (always > 0).
 */
FDL_API double fdl_calculate_scale_factor(
    fdl_dimensions_f64_t fit_norm, fdl_dimensions_f64_t target_norm, fdl_fit_method_t fit_method);

/**
 * Determine output canvas size for a single axis.
 *
 * Handles three regimes: PAD (pad_to_max -> max_size), CROP (canvas > max -> max_size),
 * FIT (canvas_size unchanged).
 *
 * @param canvas_size  Computed canvas size for this axis.
 * @param max_size     Maximum allowed size for this axis.
 * @param has_max      FDL_TRUE if max_size constraint is active, FDL_FALSE if unconstrained.
 * @param pad_to_max   FDL_TRUE to pad output to max_size, FDL_FALSE otherwise.
 * @return Final output size for this axis.
 */
FDL_API double fdl_output_size_for_axis(double canvas_size, double max_size, int has_max, int pad_to_max);

/**
 * Calculate content translation shift for a single axis.
 *
 * Handles three regimes: FIT (no shift), PAD (center/align content in padded area),
 * CROP (clip/align content that exceeds canvas).
 *
 * @param fit_size      Size of the content in this axis.
 * @param fit_anchor    Anchor position of the content.
 * @param output_size   Final output canvas size.
 * @param canvas_size   Computed canvas size before clamping.
 * @param target_size   Target template size.
 * @param is_center     FDL_TRUE if alignment is center, FDL_FALSE for edge alignment.
 * @param align_factor  Alignment factor (0.0 = left/top, 1.0 = right/bottom).
 * @param pad_to_max    FDL_TRUE if padding to maximum, FDL_FALSE otherwise.
 * @return Translation shift for this axis.
 */
FDL_API double fdl_alignment_shift(
    double fit_size,
    double fit_anchor,
    double output_size,
    double canvas_size,
    double target_size,
    int is_center,
    double align_factor,
    int pad_to_max);

/**
 * Clamp dimensions to maximum bounds.
 *
 * @param dims        Dimensions to clamp.
 * @param clamp_dims  Maximum allowed dimensions.
 * @param out_delta   [out] Amount clamped per axis (dims - result), as a point.
 * @return Clamped dimensions (each axis independently capped at clamp_dims).
 */
FDL_API fdl_dimensions_f64_t
fdl_dimensions_clamp_to_dims(fdl_dimensions_f64_t dims, fdl_dimensions_f64_t clamp_dims, fdl_point_f64_t* out_delta);

/* -----------------------------------------------------------------------
 * Framing from intent
 * ----------------------------------------------------------------------- */

/**
 * Compute a framing decision from a framing intent.
 *
 * Fits the intent's aspect ratio within the working dimensions, centers the
 * result within the canvas, and optionally computes a protection area.
 *
 * @param canvas_dims   Full canvas dimensions (used for anchor centering).
 * @param working_dims  Effective dimensions if available, else canvas dims (used for aspect ratio fitting).
 * @param squeeze       Anamorphic squeeze factor of the canvas.
 * @param aspect_ratio  Target aspect ratio as integer width:height (e.g. {16, 9}).
 * @param protection    Protection factor (0.0 for no protection, > 0.0 to enable).
 * @param rounding      Rounding strategy for the computed dimensions.
 * @return Result containing computed dimensions, anchors, and optional protection.
 */
FDL_API fdl_from_intent_result_t fdl_compute_framing_from_intent(
    fdl_dimensions_f64_t canvas_dims,
    fdl_dimensions_f64_t working_dims,
    double squeeze,
    fdl_dimensions_i64_t aspect_ratio,
    double protection,
    fdl_round_strategy_t rounding);

/* -----------------------------------------------------------------------
 * Document model (opaque handle)
 * ----------------------------------------------------------------------- */

/**
 * @anchor THREAD_SAFETY
 * @par Thread Safety
 *
 * libfdl_core provides per-document mutex locking:
 * - Different documents on different threads: **SAFE**
 * - Same document, concurrent reads: **SAFE** (serialized)
 * - Same document, concurrent read + write: **SAFE** (serialized)
 * - fdl_doc_free() during operations: **NOT SAFE** (caller must synchronize)
 *
 * String accessors return thread-local pointers keyed by field name.
 * Valid until the next call for the SAME field on the SAME thread.
 *
 * @par Handle Validity
 *
 * Handles use index-based resolution and remain valid after collection
 * mutations (push_back). Repeated access for the same index returns the
 * same handle (deduplication). A handle is valid until:
 * - The owning document is freed (fdl_doc_free)
 * - The element at the handle's index is removed (not currently supported)
 */

/** Opaque handle to an FDL document. */
typedef struct fdl_doc fdl_doc_t;

/** Opaque handles to FDL sub-objects (index-based, stable across mutations). */
typedef struct fdl_context fdl_context_t;
typedef struct fdl_canvas fdl_canvas_t;                     /**< Opaque handle to a canvas. */
typedef struct fdl_framing_decision fdl_framing_decision_t; /**< Opaque handle to a framing decision. */
typedef struct fdl_framing_intent fdl_framing_intent_t;     /**< Opaque handle to a framing intent. */
typedef struct fdl_canvas_template fdl_canvas_template_t;   /**< Opaque handle to a canvas template. */
typedef struct fdl_clip_id fdl_clip_id_t;                   /**< Opaque handle to a clip ID. */
typedef struct fdl_file_sequence fdl_file_sequence_t;       /**< Opaque handle to a file sequence. */

/** Result of parsing JSON into an FDL document. */
typedef struct fdl_parse_result_t {
    fdl_doc_t* doc;    /**< non-NULL on success */
    const char* error; /**< non-NULL on failure (free with fdl_free) */
} fdl_parse_result_t;

/**
 * Create an empty FDL document.
 *
 * @return New document handle, or NULL on allocation failure.
 *         Caller owns — free with fdl_doc_free().
 */
FDL_API fdl_doc_t* fdl_doc_create(void);

/**
 * Free an FDL document and all associated handles.
 *
 * After this call, all handles (contexts, canvases, framing decisions, etc.)
 * obtained from this document are invalid. Safe to call with NULL.
 *
 * @param doc  Document to free, or NULL (no-op).
 */
FDL_API void fdl_doc_free(fdl_doc_t* doc);

/**
 * Parse a JSON string into an FDL document.
 *
 * @param json_str  JSON string to parse (need not be null-terminated).
 * @param json_len  Length of json_str in bytes.
 * @return Parse result. On success, result.doc is non-NULL (caller owns, free
 *         with fdl_doc_free). On failure, result.error is non-NULL (caller owns,
 *         free with fdl_free).
 */
FDL_API fdl_parse_result_t fdl_doc_parse_json(const char* json_str, size_t json_len);

/**
 * Get the UUID from a parsed FDL document.
 *
 * @param doc  Document to query.
 * @return UUID string, or NULL if not present. Pointer valid until doc is freed.
 */
FDL_API const char* fdl_doc_get_uuid(const fdl_doc_t* doc);

/**
 * Get the fdl_creator from a parsed FDL document.
 *
 * @param doc  Document to query.
 * @return Creator string, or NULL if not present. Pointer valid until doc is freed.
 */
FDL_API const char* fdl_doc_get_fdl_creator(const fdl_doc_t* doc);

/**
 * Get the default_framing_intent from a parsed FDL document.
 *
 * @param doc  Document to query.
 * @return Default framing intent ID, or NULL if not present. Pointer valid until doc is freed.
 */
FDL_API const char* fdl_doc_get_default_framing_intent(const fdl_doc_t* doc);

/**
 * Get the FDL version major number.
 *
 * @param doc  Document to query.
 * @return Major version number, or 0 if not present.
 */
FDL_API int fdl_doc_get_version_major(const fdl_doc_t* doc);

/**
 * Get the FDL version minor number.
 *
 * @param doc  Document to query.
 * @return Minor version number, or 0 if not present.
 */
FDL_API int fdl_doc_get_version_minor(const fdl_doc_t* doc);

/**
 * Serialize document to canonical JSON string.
 *
 * Keys are ordered per the FDL specification; null values are excluded.
 *
 * @param doc     Document to serialize.
 * @param indent  Number of spaces per indent level (0 for compact JSON).
 * @return Heap-allocated JSON string. Caller owns — free with fdl_free().
 *         Returns NULL if doc is NULL.
 */
FDL_API char* fdl_doc_to_json(const fdl_doc_t* doc, int indent);

/**
 * Serialize a context sub-object to canonical JSON.
 *
 * @param ctx     Context handle.
 * @param indent  Number of spaces per indent level (0 for compact).
 * @return Heap-allocated JSON string. Caller owns — free with fdl_free().
 *         Returns NULL if ctx is NULL.
 */
FDL_API char* fdl_context_to_json(const fdl_context_t* ctx, int indent);

/**
 * Serialize a canvas sub-object to canonical JSON.
 *
 * @param canvas  Canvas handle.
 * @param indent  Number of spaces per indent level (0 for compact).
 * @return Heap-allocated JSON string. Caller owns — free with fdl_free().
 */
FDL_API char* fdl_canvas_to_json(const fdl_canvas_t* canvas, int indent);

/**
 * Serialize a framing decision to canonical JSON.
 *
 * @param fd      Framing decision handle.
 * @param indent  Number of spaces per indent level (0 for compact).
 * @return Heap-allocated JSON string. Caller owns — free with fdl_free().
 */
FDL_API char* fdl_framing_decision_to_json(const fdl_framing_decision_t* fd, int indent);

/**
 * Serialize a framing intent to canonical JSON.
 *
 * @param fi      Framing intent handle.
 * @param indent  Number of spaces per indent level (0 for compact).
 * @return Heap-allocated JSON string. Caller owns — free with fdl_free().
 */
FDL_API char* fdl_framing_intent_to_json(const fdl_framing_intent_t* fi, int indent);

/**
 * Serialize a canvas template to canonical JSON.
 *
 * @param ct      Canvas template handle.
 * @param indent  Number of spaces per indent level (0 for compact).
 * @return Heap-allocated JSON string. Caller owns — free with fdl_free().
 */
FDL_API char* fdl_canvas_template_to_json(const fdl_canvas_template_t* ct, int indent);

/* -----------------------------------------------------------------------
 * Collection traversal
 * ----------------------------------------------------------------------- */

/** @name Framing Intents — root-level collection
 * @{ */

/**
 * Get the number of framing intents in the document.
 * @param doc  Document handle.
 * @return Number of framing intents.
 */
FDL_API uint32_t fdl_doc_framing_intents_count(fdl_doc_t* doc);

/**
 * Get a framing intent by index.
 * @param doc    Document handle.
 * @param index  Zero-based index.
 * @return Framing intent handle (owned by doc), or NULL if index out of range.
 */
FDL_API fdl_framing_intent_t* fdl_doc_framing_intent_at(fdl_doc_t* doc, uint32_t index);

/**
 * Find a framing intent by its ID string.
 * @param doc  Document handle.
 * @param id   Framing intent ID to search for.
 * @return Framing intent handle (owned by doc), or NULL if not found.
 */
FDL_API fdl_framing_intent_t* fdl_doc_framing_intent_find_by_id(fdl_doc_t* doc, const char* id);

/** @} */

/** @name Contexts — root-level collection
 * @{ */

/**
 * Get the number of contexts in the document.
 * @param doc  Document handle.
 * @return Number of contexts.
 */
FDL_API uint32_t fdl_doc_contexts_count(fdl_doc_t* doc);

/**
 * Get a context by index.
 * @param doc    Document handle.
 * @param index  Zero-based index.
 * @return Context handle (owned by doc), or NULL if index out of range.
 */
FDL_API fdl_context_t* fdl_doc_context_at(fdl_doc_t* doc, uint32_t index);

/**
 * Find a context by its label string.
 * @param doc    Document handle.
 * @param label  Context label to search for.
 * @return Context handle (owned by doc), or NULL if not found.
 */
FDL_API fdl_context_t* fdl_doc_context_find_by_label(fdl_doc_t* doc, const char* label);

/** @} */

/** @name Canvas Templates — root-level collection
 * @{ */

/**
 * Get the number of canvas templates in the document.
 * @param doc  Document handle.
 * @return Number of canvas templates.
 */
FDL_API uint32_t fdl_doc_canvas_templates_count(fdl_doc_t* doc);

/**
 * Get a canvas template by index.
 * @param doc    Document handle.
 * @param index  Zero-based index.
 * @return Canvas template handle (owned by doc), or NULL if index out of range.
 */
FDL_API fdl_canvas_template_t* fdl_doc_canvas_template_at(fdl_doc_t* doc, uint32_t index);

/**
 * Find a canvas template by its ID string.
 * @param doc  Document handle.
 * @param id   Canvas template ID to search for.
 * @return Canvas template handle (owned by doc), or NULL if not found.
 */
FDL_API fdl_canvas_template_t* fdl_doc_canvas_template_find_by_id(fdl_doc_t* doc, const char* id);

/** @} */

/** @name Canvases — child collection of context
 * @{ */

/**
 * Get the number of canvases in a context.
 * @param ctx  Context handle.
 * @return Number of canvases.
 */
FDL_API uint32_t fdl_context_canvases_count(const fdl_context_t* ctx);

/**
 * Get a canvas by index within a context.
 * @param ctx    Context handle.
 * @param index  Zero-based index.
 * @return Canvas handle (owned by doc), or NULL if index out of range.
 */
FDL_API fdl_canvas_t* fdl_context_canvas_at(fdl_context_t* ctx, uint32_t index);

/**
 * Find a canvas by its ID within a context.
 * @param ctx  Context handle.
 * @param id   Canvas ID to search for.
 * @return Canvas handle (owned by doc), or NULL if not found.
 */
FDL_API fdl_canvas_t* fdl_context_find_canvas_by_id(fdl_context_t* ctx, const char* id);

/** @} */

/** @name Framing Decisions — child collection of canvas
 * @{ */

/**
 * Get the number of framing decisions in a canvas.
 * @param canvas  Canvas handle.
 * @return Number of framing decisions.
 */
FDL_API uint32_t fdl_canvas_framing_decisions_count(const fdl_canvas_t* canvas);

/**
 * Get a framing decision by index within a canvas.
 * @param canvas  Canvas handle.
 * @param index   Zero-based index.
 * @return Framing decision handle (owned by doc), or NULL if index out of range.
 */
FDL_API fdl_framing_decision_t* fdl_canvas_framing_decision_at(fdl_canvas_t* canvas, uint32_t index);

/**
 * Find a framing decision by its ID within a canvas.
 * @param canvas  Canvas handle.
 * @param id      Framing decision ID to search for.
 * @return Framing decision handle (owned by doc), or NULL if not found.
 */
FDL_API fdl_framing_decision_t* fdl_canvas_find_framing_decision_by_id(fdl_canvas_t* canvas, const char* id);

/** @} */

/* -----------------------------------------------------------------------
 * Field accessors — Context
 * ----------------------------------------------------------------------- */

/**
 * Get the label of a context.
 * @param ctx  Context handle.
 * @return Label string. Thread-local pointer, valid until next call for same field on same thread.
 */
FDL_API const char* fdl_context_get_label(const fdl_context_t* ctx);

/**
 * Get the context_creator of a context.
 * @param ctx  Context handle.
 * @return Creator string. Thread-local pointer, valid until next call for same field on same thread.
 */
FDL_API const char* fdl_context_get_context_creator(const fdl_context_t* ctx);

/**
 * Check if a context has a clip_id.
 * @param ctx  Context handle.
 * @return FDL_TRUE if clip_id is present, FDL_FALSE otherwise.
 */
FDL_API int fdl_context_has_clip_id(const fdl_context_t* ctx);

/**
 * Get clip_id as a JSON string.
 *
 * @param ctx  Context handle.
 * @return Heap-allocated JSON string, or NULL if not present.
 *         Caller owns — free with fdl_free().
 */
FDL_API const char* fdl_context_get_clip_id(const fdl_context_t* ctx);

/**
 * Get the clip_id handle from a context.
 *
 * @param ctx  Context handle.
 * @return Clip ID handle (owned by doc), or NULL if clip_id is not present.
 */
FDL_API fdl_clip_id_t* fdl_context_clip_id(fdl_context_t* ctx);

/**
 * Get the clip_name from a clip_id.
 *
 * @param cid  Clip ID handle.
 * @return Clip name string. Thread-local pointer, valid until next call for same field on same thread.
 */
FDL_API const char* fdl_clip_id_get_clip_name(const fdl_clip_id_t* cid);

/**
 * Check if a clip_id has a file path.
 *
 * @param cid  Clip ID handle.
 * @return FDL_TRUE if file is present, FDL_FALSE otherwise.
 */
FDL_API int fdl_clip_id_has_file(const fdl_clip_id_t* cid);

/**
 * Get the file path from a clip_id.
 *
 * @param cid  Clip ID handle.
 * @return File path string, or NULL if not present. Thread-local pointer.
 */
FDL_API const char* fdl_clip_id_get_file(const fdl_clip_id_t* cid);

/**
 * Check if a clip_id has a file sequence.
 *
 * @param cid  Clip ID handle.
 * @return FDL_TRUE if sequence is present, FDL_FALSE otherwise.
 */
FDL_API int fdl_clip_id_has_sequence(const fdl_clip_id_t* cid);

/**
 * Get the file sequence handle from a clip_id.
 *
 * @param cid  Clip ID handle.
 * @return File sequence handle (owned by doc), or NULL if sequence is not present.
 */
FDL_API fdl_file_sequence_t* fdl_clip_id_sequence(fdl_clip_id_t* cid);

/**
 * Serialize a clip_id to canonical JSON.
 *
 * @param cid     Clip ID handle.
 * @param indent  Number of spaces per indent level (0 for compact).
 * @return Heap-allocated JSON string. Caller owns — free with fdl_free().
 */
FDL_API char* fdl_clip_id_to_json(const fdl_clip_id_t* cid, int indent);

/**
 * Get the sequence pattern value string.
 *
 * @param seq  File sequence handle.
 * @return Sequence pattern string. Thread-local pointer.
 */
FDL_API const char* fdl_file_sequence_get_value(const fdl_file_sequence_t* seq);

/**
 * Get the index variable name.
 *
 * @param seq  File sequence handle.
 * @return Index variable string. Thread-local pointer.
 */
FDL_API const char* fdl_file_sequence_get_idx(const fdl_file_sequence_t* seq);

/**
 * Get the minimum (first) frame number.
 *
 * @param seq  File sequence handle.
 * @return First frame number.
 */
FDL_API int64_t fdl_file_sequence_get_min(const fdl_file_sequence_t* seq);

/**
 * Get the maximum (last) frame number.
 *
 * @param seq  File sequence handle.
 * @return Last frame number.
 */
FDL_API int64_t fdl_file_sequence_get_max(const fdl_file_sequence_t* seq);

/* -----------------------------------------------------------------------
 * Field accessors — Canvas
 * ----------------------------------------------------------------------- */

/** Get the label of a canvas.
 * @param canvas  Canvas handle.
 * @return Label string. Thread-local pointer. */
FDL_API const char* fdl_canvas_get_label(const fdl_canvas_t* canvas);

/** Get the ID of a canvas.
 * @param canvas  Canvas handle.
 * @return ID string. Thread-local pointer. */
FDL_API const char* fdl_canvas_get_id(const fdl_canvas_t* canvas);

/** Get the source_canvas_id of a canvas (the canvas this was derived from).
 * @param canvas  Canvas handle.
 * @return Source canvas ID string. Thread-local pointer. */
FDL_API const char* fdl_canvas_get_source_canvas_id(const fdl_canvas_t* canvas);

/** Get the canvas dimensions in pixels.
 * @param canvas  Canvas handle.
 * @return Canvas dimensions. */
FDL_API fdl_dimensions_i64_t fdl_canvas_get_dimensions(const fdl_canvas_t* canvas);

/** Check if the canvas has effective dimensions set.
 * @param canvas  Canvas handle.
 * @return FDL_TRUE if effective dimensions are present, FDL_FALSE otherwise. */
FDL_API int fdl_canvas_has_effective_dimensions(const fdl_canvas_t* canvas);

/** Get effective (active image area) dimensions.
 * @param canvas  Canvas handle.
 * @return Effective dimensions. Only valid if fdl_canvas_has_effective_dimensions() returns FDL_TRUE. */
FDL_API fdl_dimensions_i64_t fdl_canvas_get_effective_dimensions(const fdl_canvas_t* canvas);

/** Get the effective anchor point (offset from canvas origin).
 * @param canvas  Canvas handle.
 * @return Effective anchor point. Returns {0,0} if no effective dimensions. */
FDL_API fdl_point_f64_t fdl_canvas_get_effective_anchor_point(const fdl_canvas_t* canvas);

/** Get the anamorphic squeeze factor.
 * @param canvas  Canvas handle.
 * @return Squeeze factor (1.0 for non-anamorphic). */
FDL_API double fdl_canvas_get_anamorphic_squeeze(const fdl_canvas_t* canvas);

/** Check if the canvas has photosite dimensions set.
 * @param canvas  Canvas handle.
 * @return FDL_TRUE if photosite dimensions are present, FDL_FALSE otherwise. */
FDL_API int fdl_canvas_has_photosite_dimensions(const fdl_canvas_t* canvas);

/** Get photosite (sensor) dimensions.
 * @param canvas  Canvas handle.
 * @return Photosite dimensions. Only valid if fdl_canvas_has_photosite_dimensions() returns FDL_TRUE. */
FDL_API fdl_dimensions_i64_t fdl_canvas_get_photosite_dimensions(const fdl_canvas_t* canvas);

/** Check if the canvas has physical dimensions set.
 * @param canvas  Canvas handle.
 * @return FDL_TRUE if physical dimensions are present, FDL_FALSE otherwise. */
FDL_API int fdl_canvas_has_physical_dimensions(const fdl_canvas_t* canvas);

/** Get physical dimensions (e.g. millimeters on sensor).
 * @param canvas  Canvas handle.
 * @return Physical dimensions. Only valid if fdl_canvas_has_physical_dimensions() returns FDL_TRUE. */
FDL_API fdl_dimensions_f64_t fdl_canvas_get_physical_dimensions(const fdl_canvas_t* canvas);
/* -----------------------------------------------------------------------
 * Field accessors — Framing Decision
 * ----------------------------------------------------------------------- */

/** Get the label of a framing decision.
 * @param fd  Framing decision handle.
 * @return Label string. Thread-local pointer. */
FDL_API const char* fdl_framing_decision_get_label(const fdl_framing_decision_t* fd);

/** Get the ID of a framing decision.
 * @param fd  Framing decision handle.
 * @return ID string. Thread-local pointer. */
FDL_API const char* fdl_framing_decision_get_id(const fdl_framing_decision_t* fd);

/** Get the framing_intent_id that this framing decision references.
 * @param fd  Framing decision handle.
 * @return Framing intent ID string. Thread-local pointer. */
FDL_API const char* fdl_framing_decision_get_framing_intent_id(const fdl_framing_decision_t* fd);

/** Get the framing decision dimensions (floating-point sub-pixel).
 * @param fd  Framing decision handle.
 * @return Framing dimensions. */
FDL_API fdl_dimensions_f64_t fdl_framing_decision_get_dimensions(const fdl_framing_decision_t* fd);

/** Get the anchor point of a framing decision.
 * @param fd  Framing decision handle.
 * @return Anchor point (offset from canvas origin). */
FDL_API fdl_point_f64_t fdl_framing_decision_get_anchor_point(const fdl_framing_decision_t* fd);

/** Check if a framing decision has protection area set.
 * @param fd  Framing decision handle.
 * @return FDL_TRUE if protection is present, FDL_FALSE otherwise. */
FDL_API int fdl_framing_decision_has_protection(const fdl_framing_decision_t* fd);

/** Get the protection area dimensions.
 * @param fd  Framing decision handle.
 * @return Protection dimensions. Only valid if fdl_framing_decision_has_protection() returns FDL_TRUE. */
FDL_API fdl_dimensions_f64_t fdl_framing_decision_get_protection_dimensions(const fdl_framing_decision_t* fd);

/** Get the protection anchor point.
 * @param fd  Framing decision handle.
 * @return Protection anchor point. Only valid if fdl_framing_decision_has_protection() returns FDL_TRUE. */
FDL_API fdl_point_f64_t fdl_framing_decision_get_protection_anchor_point(const fdl_framing_decision_t* fd);

/* -----------------------------------------------------------------------
 * Field accessors — Framing Intent
 * ----------------------------------------------------------------------- */

/** Get the label of a framing intent.
 * @param fi  Framing intent handle.
 * @return Label string. Thread-local pointer. */
FDL_API const char* fdl_framing_intent_get_label(const fdl_framing_intent_t* fi);

/** Get the ID of a framing intent.
 * @param fi  Framing intent handle.
 * @return ID string. Thread-local pointer. */
FDL_API const char* fdl_framing_intent_get_id(const fdl_framing_intent_t* fi);

/** Get the target aspect ratio of a framing intent.
 * @param fi  Framing intent handle.
 * @return Aspect ratio as integer width:height (e.g. {16, 9}). */
FDL_API fdl_dimensions_i64_t fdl_framing_intent_get_aspect_ratio(const fdl_framing_intent_t* fi);

/** Get the protection factor of a framing intent.
 * @param fi  Framing intent handle.
 * @return Protection factor (0.0 = no protection). */
FDL_API double fdl_framing_intent_get_protection(const fdl_framing_intent_t* fi);

/* -----------------------------------------------------------------------
 * Field accessors — Canvas Template
 * ----------------------------------------------------------------------- */

/** Get the label of a canvas template.
 * @param ct  Canvas template handle.
 * @return Label string. Thread-local pointer. */
FDL_API const char* fdl_canvas_template_get_label(const fdl_canvas_template_t* ct);

/** Get the ID of a canvas template.
 * @param ct  Canvas template handle.
 * @return ID string. Thread-local pointer. */
FDL_API const char* fdl_canvas_template_get_id(const fdl_canvas_template_t* ct);

/** Get the target dimensions of a canvas template.
 * @param ct  Canvas template handle.
 * @return Target output dimensions in pixels. */
FDL_API fdl_dimensions_i64_t fdl_canvas_template_get_target_dimensions(const fdl_canvas_template_t* ct);

/** Get the target anamorphic squeeze factor.
 * @param ct  Canvas template handle.
 * @return Target squeeze factor (1.0 for non-anamorphic). */
FDL_API double fdl_canvas_template_get_target_anamorphic_squeeze(const fdl_canvas_template_t* ct);

/** Get the fit source — which dimension layer to scale from.
 * @param ct  Canvas template handle.
 * @return Geometry path (canvas, effective, protection, or framing). */
FDL_API fdl_geometry_path_t fdl_canvas_template_get_fit_source(const fdl_canvas_template_t* ct);

/** Get the fit method — how source is scaled into target.
 * @param ct  Canvas template handle.
 * @return Fit method (WIDTH, HEIGHT, FIT_ALL, or FILL). */
FDL_API fdl_fit_method_t fdl_canvas_template_get_fit_method(const fdl_canvas_template_t* ct);

/** Get the horizontal alignment method.
 * @param ct  Canvas template handle.
 * @return Horizontal alignment (LEFT, CENTER, or RIGHT). */
FDL_API fdl_halign_t fdl_canvas_template_get_alignment_method_horizontal(const fdl_canvas_template_t* ct);

/** Get the vertical alignment method.
 * @param ct  Canvas template handle.
 * @return Vertical alignment (TOP, CENTER, or BOTTOM). */
FDL_API fdl_valign_t fdl_canvas_template_get_alignment_method_vertical(const fdl_canvas_template_t* ct);

/** Check if preserve_from_source_canvas is set.
 * @param ct  Canvas template handle.
 * @return FDL_TRUE if present, FDL_FALSE otherwise. */
FDL_API int fdl_canvas_template_has_preserve_from_source_canvas(const fdl_canvas_template_t* ct);

/** Get the preserve_from_source_canvas geometry path.
 * @param ct  Canvas template handle.
 * @return Geometry path to preserve. Only valid if has_preserve returns FDL_TRUE. */
FDL_API fdl_geometry_path_t fdl_canvas_template_get_preserve_from_source_canvas(const fdl_canvas_template_t* ct);

/** Check if maximum_dimensions constraint is set.
 * @param ct  Canvas template handle.
 * @return FDL_TRUE if maximum dimensions are set, FDL_FALSE otherwise. */
FDL_API int fdl_canvas_template_has_maximum_dimensions(const fdl_canvas_template_t* ct);

/** Get the maximum_dimensions constraint.
 * @param ct  Canvas template handle.
 * @return Maximum dimensions. Only valid if has_maximum_dimensions returns FDL_TRUE. */
FDL_API fdl_dimensions_i64_t fdl_canvas_template_get_maximum_dimensions(const fdl_canvas_template_t* ct);

/** Get the pad_to_maximum flag.
 * @param ct  Canvas template handle.
 * @return FDL_TRUE if output should be padded to maximum dimensions, FDL_FALSE otherwise. */
FDL_API int fdl_canvas_template_get_pad_to_maximum(const fdl_canvas_template_t* ct);

/** Get the rounding strategy.
 * @param ct  Canvas template handle.
 * @return Rounding strategy (even + mode). */
FDL_API fdl_round_strategy_t fdl_canvas_template_get_round(const fdl_canvas_template_t* ct);

/* -----------------------------------------------------------------------
 * Geometry layer resolution (from handle types)
 * ----------------------------------------------------------------------- */

/**
 * Resolve dimensions and anchor directly from canvas/framing handles for a path.
 *
 * @param canvas      Canvas handle.
 * @param framing     Framing decision handle.
 * @param path        Geometry path to resolve.
 * @param out_dims    [out] Resolved dimensions.
 * @param out_anchor  [out] Resolved anchor point.
 * @return 0 on success, 1 if path is valid but data absent (optional field not set,
 *         out_dims/out_anchor zero-initialized), -1 on invalid path.
 */
FDL_API int fdl_resolve_geometry_layer(
    const fdl_canvas_t* canvas,
    const fdl_framing_decision_t* framing,
    fdl_geometry_path_t path,
    fdl_dimensions_f64_t* out_dims,
    fdl_point_f64_t* out_anchor);

/* -----------------------------------------------------------------------
 * Rect convenience — combine dims + anchor into (x, y, w, h)
 * ----------------------------------------------------------------------- */

/**
 * Construct a rect from raw coordinates.
 *
 * @param x       Left edge x-coordinate.
 * @param y       Top edge y-coordinate.
 * @param width   Rectangle width.
 * @param height  Rectangle height.
 * @return Constructed rect.
 */
FDL_API fdl_rect_t fdl_make_rect(double x, double y, double width, double height);

/**
 * Get the full canvas rect: (0, 0, dims.width, dims.height).
 *
 * @param canvas  Canvas handle.
 * @return Canvas rect with origin at (0, 0).
 */
FDL_API fdl_rect_t fdl_canvas_get_rect(const fdl_canvas_t* canvas);

/**
 * Get the effective (active image) rect of a canvas.
 *
 * @param canvas    Canvas handle.
 * @param out_rect  [out] Effective rect if present.
 * @return FDL_TRUE if effective dimensions exist and out_rect was written, FDL_FALSE if absent.
 */
FDL_API int fdl_canvas_get_effective_rect(const fdl_canvas_t* canvas, fdl_rect_t* out_rect);

/**
 * Get the framing decision rect: (anchor.x, anchor.y, dims.width, dims.height).
 *
 * @param fd  Framing decision handle.
 * @return Framing rect.
 */
FDL_API fdl_rect_t fdl_framing_decision_get_rect(const fdl_framing_decision_t* fd);

/**
 * Get the framing decision protection rect.
 *
 * @param fd        Framing decision handle.
 * @param out_rect  [out] Protection rect if present.
 * @return FDL_TRUE if protection exists and out_rect was written, FDL_FALSE if absent.
 */
FDL_API int fdl_framing_decision_get_protection_rect(const fdl_framing_decision_t* fd, fdl_rect_t* out_rect);

/* -----------------------------------------------------------------------
 * Template pipeline — full CanvasTemplate.apply()
 * ----------------------------------------------------------------------- */

/** Result of applying a canvas template. */
typedef struct fdl_template_result_t {
    fdl_doc_t* output_fdl;     /**< Output FDL (caller owns, free with fdl_doc_free or fdl_template_result_free) */
    const char* context_label; /**< Label of the new context (caller frees with fdl_free) */
    const char* canvas_id;     /**< ID of the new canvas (caller frees with fdl_free) */
    const char* framing_decision_id; /**< ID of the new framing decision (caller frees with fdl_free) */
    const char* error;               /**< Error message on failure (free with fdl_free) */
} fdl_template_result_t;

/**
 * Apply a canvas template to a source canvas/framing.
 *
 * Runs the full template pipeline: normalize, scale, round, offset, crop.
 * Produces a new FDL document with the transformed canvas and framing decision.
 *
 * @param tmpl                  Canvas template to apply.
 * @param source_canvas         Source canvas to transform.
 * @param source_framing        Source framing decision to transform.
 * @param new_canvas_id         ID for the output canvas (caller provides).
 * @param new_fd_name           Name/label for the output framing decision.
 * @param source_context_label  Label from source context (for label generation, may be NULL).
 * @param context_creator       Creator string for the output context.
 * @return Result with output_fdl on success, error on failure.
 *         Caller must free with fdl_template_result_free().
 */
FDL_API fdl_template_result_t fdl_apply_canvas_template(
    const fdl_canvas_template_t* tmpl,
    const fdl_canvas_t* source_canvas,
    const fdl_framing_decision_t* source_framing,
    const char* new_canvas_id,
    const char* new_fd_name,
    const char* source_context_label,
    const char* context_creator);

/**
 * Free a template result (doc + all allocated strings).
 *
 * Safe to call with NULL.
 *
 * @param result  Template result to free.
 */
FDL_API void fdl_template_result_free(fdl_template_result_t* result);

/* -----------------------------------------------------------------------
 * Canvas resolution — find matching canvas for input dimensions
 * ----------------------------------------------------------------------- */

/** Result of resolving a canvas for given input dimensions. */
typedef struct fdl_resolve_canvas_result_t {
    fdl_canvas_t* canvas;                     /**< Resolved canvas (non-owning, do NOT free). */
    fdl_framing_decision_t* framing_decision; /**< Resolved framing decision (non-owning, do NOT free). */
    int was_resolved;  /**< FDL_TRUE if a different canvas was found, FDL_FALSE if original matched. */
    const char* error; /**< Error message on failure (caller frees with fdl_free). */
} fdl_resolve_canvas_result_t;

/**
 * Resolve canvas for given input dimensions.
 *
 * If input_dims match the canvas dimensions, returns the original canvas/framing
 * with was_resolved=0. If they don't match and the canvas is derived
 * (id != source_canvas_id), searches sibling canvases for one with matching
 * dimensions and a framing decision with the same label.
 *
 * @param ctx         Context containing the canvases to search.
 * @param input_dims  Input dimensions to match against.
 * @param canvas      Starting canvas (may be returned if dimensions match).
 * @param framing     Starting framing decision (label used for matching).
 * @return Result with resolved canvas/framing on success, error if no match found.
 *         Handles in result are non-owning (owned by doc). Error string, if set,
 *         must be freed with fdl_free().
 */
FDL_API fdl_resolve_canvas_result_t fdl_context_resolve_canvas_for_dimensions(
    fdl_context_t* ctx, fdl_dimensions_f64_t input_dims, fdl_canvas_t* canvas, fdl_framing_decision_t* framing);

/* -----------------------------------------------------------------------
 * Document builder — create and mutate FDL documents
 * ----------------------------------------------------------------------- */

/**
 * Create a new FDL document with header fields and empty collections.
 *
 * @param uuid                     Document UUID.
 * @param version_major            FDL version major number.
 * @param version_minor            FDL version minor number.
 * @param fdl_creator              Creator identifier string.
 * @param default_framing_intent   Default framing intent ID, or NULL.
 * @return New document handle. Caller owns — free with fdl_doc_free().
 */
FDL_API fdl_doc_t* fdl_doc_create_with_header(
    const char* uuid,
    int version_major,
    int version_minor,
    const char* fdl_creator,
    const char* default_framing_intent);

/** Set the UUID on a document.
 * @param doc   Document handle.
 * @param uuid  New UUID string. */
FDL_API void fdl_doc_set_uuid(fdl_doc_t* doc, const char* uuid);

/** Set the fdl_creator on a document.
 * @param doc      Document handle.
 * @param creator  New creator string. */
FDL_API void fdl_doc_set_fdl_creator(fdl_doc_t* doc, const char* creator);

/** Set the default_framing_intent on a document.
 * @param doc    Document handle.
 * @param fi_id  Framing intent ID, or NULL to clear. */
FDL_API void fdl_doc_set_default_framing_intent(fdl_doc_t* doc, const char* fi_id);

/** Set the FDL version on a document.
 * @param doc    Document handle.
 * @param major  Version major number.
 * @param minor  Version minor number. */
FDL_API void fdl_doc_set_version(fdl_doc_t* doc, int major, int minor);

/**
 * Add a framing intent to the document.
 *
 * @param doc         Document handle.
 * @param id          Framing intent ID.
 * @param label       Display label.
 * @param aspect_w    Aspect ratio width component.
 * @param aspect_h    Aspect ratio height component.
 * @param protection  Protection factor (0.0 for no protection).
 * @return Handle to the new framing intent (owned by doc).
 */
FDL_API fdl_framing_intent_t* fdl_doc_add_framing_intent(
    fdl_doc_t* doc, const char* id, const char* label, int64_t aspect_w, int64_t aspect_h, double protection);

/**
 * Add a context to the document.
 *
 * @param doc              Document handle.
 * @param label            Context label.
 * @param context_creator  Creator identifier string.
 * @return Handle to the new context (owned by doc).
 */
FDL_API fdl_context_t* fdl_doc_add_context(fdl_doc_t* doc, const char* label, const char* context_creator);

/**
 * Add a canvas to a context.
 *
 * @param ctx              Context handle.
 * @param id               Canvas ID.
 * @param label            Display label.
 * @param source_canvas_id Source canvas ID (for derived canvases; equals id for originals).
 * @param dim_w            Canvas width in pixels.
 * @param dim_h            Canvas height in pixels.
 * @param squeeze          Anamorphic squeeze factor (1.0 for non-anamorphic).
 * @return Handle to the new canvas (owned by doc).
 */
FDL_API fdl_canvas_t* fdl_context_add_canvas(
    fdl_context_t* ctx,
    const char* id,
    const char* label,
    const char* source_canvas_id,
    int64_t dim_w,
    int64_t dim_h,
    double squeeze);

/**
 * Set effective dimensions and anchor on a canvas.
 *
 * @param canvas  Canvas handle.
 * @param dims    Effective dimensions.
 * @param anchor  Effective anchor point.
 */
FDL_API void fdl_canvas_set_effective_dimensions(
    fdl_canvas_t* canvas, fdl_dimensions_i64_t dims, fdl_point_f64_t anchor);

/**
 * Set photosite dimensions on a canvas.
 *
 * @param canvas  Canvas handle.
 * @param dims    Photosite (sensor) dimensions.
 */
FDL_API void fdl_canvas_set_photosite_dimensions(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims);

/**
 * Set physical dimensions on a canvas.
 *
 * @param canvas  Canvas handle.
 * @param dims    Physical dimensions (e.g. millimeters on sensor).
 */
FDL_API void fdl_canvas_set_physical_dimensions(fdl_canvas_t* canvas, fdl_dimensions_f64_t dims);

/**
 * Add a framing decision to a canvas.
 *
 * @param canvas            Canvas handle.
 * @param id                Framing decision ID.
 * @param label             Display label.
 * @param framing_intent_id ID of the framing intent this decision implements.
 * @param dim_w             Framing width.
 * @param dim_h             Framing height.
 * @param anchor_x          Anchor x-coordinate.
 * @param anchor_y          Anchor y-coordinate.
 * @return Handle to the new framing decision (owned by doc).
 */
FDL_API fdl_framing_decision_t* fdl_canvas_add_framing_decision(
    fdl_canvas_t* canvas,
    const char* id,
    const char* label,
    const char* framing_intent_id,
    double dim_w,
    double dim_h,
    double anchor_x,
    double anchor_y);

/**
 * Add a canvas template to the document.
 *
 * @param doc             Document handle.
 * @param id              Canvas template ID.
 * @param label           Display label.
 * @param target_w        Target width in pixels.
 * @param target_h        Target height in pixels.
 * @param target_squeeze  Target anamorphic squeeze factor.
 * @param fit_source      Geometry path to scale from.
 * @param fit_method      How source is scaled into target.
 * @param halign          Horizontal alignment.
 * @param valign          Vertical alignment.
 * @param rounding        Rounding strategy.
 * @return Handle to the new canvas template (owned by doc).
 */
FDL_API fdl_canvas_template_t* fdl_doc_add_canvas_template(
    fdl_doc_t* doc,
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

/**
 * Set preserve_from_source_canvas on a canvas template.
 *
 * @param ct    Canvas template handle.
 * @param path  Geometry path to preserve from the source canvas.
 */
FDL_API void fdl_canvas_template_set_preserve_from_source_canvas(fdl_canvas_template_t* ct, fdl_geometry_path_t path);

/**
 * Set maximum_dimensions on a canvas template.
 *
 * @param ct    Canvas template handle.
 * @param dims  Maximum allowed output dimensions.
 */
FDL_API void fdl_canvas_template_set_maximum_dimensions(fdl_canvas_template_t* ct, fdl_dimensions_i64_t dims);

/**
 * Set pad_to_maximum flag on a canvas template.
 *
 * @param ct   Canvas template handle.
 * @param pad  FDL_TRUE to pad output to maximum dimensions, FDL_FALSE otherwise.
 */
FDL_API void fdl_canvas_template_set_pad_to_maximum(fdl_canvas_template_t* ct, int pad);

/**
 * Set protection dimensions and anchor on a framing decision.
 *
 * @param fd      Framing decision handle.
 * @param dims    Protection dimensions.
 * @param anchor  Protection anchor point.
 */
FDL_API void fdl_framing_decision_set_protection(
    fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims, fdl_point_f64_t anchor);

/**
 * Set aspect ratio on a framing intent.
 *
 * @param fi    Framing intent handle.
 * @param dims  Aspect ratio as integer width:height (e.g. {16, 9}).
 */
FDL_API void fdl_framing_intent_set_aspect_ratio(fdl_framing_intent_t* fi, fdl_dimensions_i64_t dims);

/**
 * Set protection factor on a framing intent.
 *
 * @param fi          Framing intent handle.
 * @param protection  Protection factor (0.0 for no protection).
 */
FDL_API void fdl_framing_intent_set_protection(fdl_framing_intent_t* fi, double protection);

/**
 * Set dimensions on a canvas.
 *
 * @param canvas  Canvas handle.
 * @param dims    New canvas dimensions.
 */
FDL_API void fdl_canvas_set_dimensions(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims);

/**
 * Set anamorphic squeeze on a canvas.
 *
 * @param canvas   Canvas handle.
 * @param squeeze  New anamorphic squeeze factor.
 */
FDL_API void fdl_canvas_set_anamorphic_squeeze(fdl_canvas_t* canvas, double squeeze);

/**
 * Set effective dimensions on a canvas.
 *
 * Creates anchor at {0, 0} if effective anchor is not already set.
 *
 * @param canvas  Canvas handle.
 * @param dims    Effective dimensions.
 */
FDL_API void fdl_canvas_set_effective_dims_only(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims);

/**
 * Remove effective dimensions and anchor from a canvas.
 *
 * @param canvas  Canvas handle.
 */
FDL_API void fdl_canvas_remove_effective(fdl_canvas_t* canvas);

/**
 * Set dimensions on a framing decision.
 *
 * @param fd    Framing decision handle.
 * @param dims  New framing dimensions.
 */
FDL_API void fdl_framing_decision_set_dimensions(fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims);

/**
 * Set anchor point on a framing decision.
 *
 * @param fd     Framing decision handle.
 * @param point  New anchor point.
 */
FDL_API void fdl_framing_decision_set_anchor_point(fdl_framing_decision_t* fd, fdl_point_f64_t point);

/**
 * Set protection dimensions on a framing decision (without changing anchor).
 *
 * @param fd    Framing decision handle.
 * @param dims  New protection dimensions.
 */
FDL_API void fdl_framing_decision_set_protection_dimensions(fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims);

/**
 * Set protection anchor point on a framing decision (without changing dimensions).
 *
 * @param fd     Framing decision handle.
 * @param point  New protection anchor point.
 */
FDL_API void fdl_framing_decision_set_protection_anchor_point(fdl_framing_decision_t* fd, fdl_point_f64_t point);

/**
 * Remove protection dimensions and anchor from a framing decision.
 *
 * @param fd  Framing decision handle.
 */
FDL_API void fdl_framing_decision_remove_protection(fdl_framing_decision_t* fd);

/* -----------------------------------------------------------------------
 * Framing decision business logic (handle-based)
 * ----------------------------------------------------------------------- */

/**
 * Adjust anchor_point on a framing decision based on alignment within canvas.
 *
 * Reads canvas dimensions and framing dimensions, then computes the aligned
 * anchor position according to the specified alignment.
 *
 * @param fd       Framing decision to modify.
 * @param canvas   Canvas providing the bounding dimensions.
 * @param h_align  Horizontal alignment (LEFT, CENTER, or RIGHT).
 * @param v_align  Vertical alignment (TOP, CENTER, or BOTTOM).
 */
FDL_API void fdl_framing_decision_adjust_anchor(
    fdl_framing_decision_t* fd, const fdl_canvas_t* canvas, fdl_halign_t h_align, fdl_valign_t v_align);

/**
 * Adjust protection_anchor_point on a framing decision based on alignment within canvas.
 *
 * Reads canvas dimensions and protection_dimensions, then computes the aligned
 * protection anchor position.
 *
 * @param fd       Framing decision to modify.
 * @param canvas   Canvas providing the bounding dimensions.
 * @param h_align  Horizontal alignment.
 * @param v_align  Vertical alignment.
 */
FDL_API void fdl_framing_decision_adjust_protection_anchor(
    fdl_framing_decision_t* fd, const fdl_canvas_t* canvas, fdl_halign_t h_align, fdl_valign_t v_align);

/**
 * Populate a framing decision from a canvas and framing intent.
 *
 * Extracts values from canvas/intent handles, calls the framing computation,
 * and writes dimensions, anchor_point, and optionally protection to the framing decision.
 *
 * @param fd        Framing decision to populate.
 * @param canvas    Source canvas (provides dimensions and squeeze).
 * @param intent    Framing intent (provides aspect ratio and protection).
 * @param rounding  Rounding strategy for the computed values.
 */
FDL_API void fdl_framing_decision_populate_from_intent(
    fdl_framing_decision_t* fd,
    const fdl_canvas_t* canvas,
    const fdl_framing_intent_t* intent,
    fdl_round_strategy_t rounding);

/**
 * Set clip_id on a context from a JSON string.
 *
 * Validates mutual exclusion (file vs sequence) before setting.
 *
 * @param ctx       Context handle.
 * @param json_str  JSON string representing the clip_id object.
 * @param json_len  Length of json_str in bytes.
 * @return NULL on success, or heap-allocated error string on failure.
 *         Caller frees error with fdl_free().
 */
FDL_API const char* fdl_context_set_clip_id_json(fdl_context_t* ctx, const char* json_str, size_t json_len);

/**
 * Remove clip_id from a context. Safe to call if not present.
 *
 * @param ctx  Context handle.
 */
FDL_API void fdl_context_remove_clip_id(fdl_context_t* ctx);

/**
 * Validate clip_id JSON for mutual exclusion (file vs sequence).
 *
 * @param json_str  JSON string to validate.
 * @param json_len  Length of json_str in bytes.
 * @return NULL if valid, or heap-allocated error string on failure.
 *         Caller frees error with fdl_free().
 */
FDL_API const char* fdl_clip_id_validate_json(const char* json_str, size_t json_len);

/* -----------------------------------------------------------------------
 * Validation (schema + semantic)
 * ----------------------------------------------------------------------- */

/** Opaque handle to a validation result. */
typedef struct fdl_validation_result fdl_validation_result_t;

/**
 * Run schema and semantic validators on the document.
 *
 * Schema validation (JSON Schema Draft 2020-12) runs first; semantic validators
 * (referential integrity, value range checks) run only if the document is
 * structurally valid.
 *
 * @param doc  Document to validate.
 * @return Validation result handle. Caller owns — free with fdl_validation_result_free().
 */
FDL_API fdl_validation_result_t* fdl_doc_validate(const fdl_doc_t* doc);

/**
 * Get the number of validation errors.
 *
 * @param result  Validation result handle.
 * @return Number of errors (0 means the document is valid).
 */
FDL_API uint32_t fdl_validation_result_error_count(const fdl_validation_result_t* result);

/**
 * Get a specific error message by index.
 *
 * @param result  Validation result handle.
 * @param index   Zero-based error index.
 * @return Error message string, or NULL if index is out of range.
 *         Pointer valid until result is freed.
 */
FDL_API const char* fdl_validation_result_error_at(const fdl_validation_result_t* result, uint32_t index);

/**
 * Free a validation result. Safe to call with NULL.
 *
 * @param result  Validation result to free, or NULL (no-op).
 */
FDL_API void fdl_validation_result_free(fdl_validation_result_t* result);

/* -----------------------------------------------------------------------
 * Memory management
 * ----------------------------------------------------------------------- */

/**
 * Free memory allocated by fdl_core functions.
 *
 * Use this for strings returned by serialization, error messages, and
 * other heap-allocated values. Safe to call with NULL.
 *
 * @param ptr  Pointer to free, or NULL (no-op).
 */
FDL_API void fdl_free(void* ptr);

/* -----------------------------------------------------------------------
 * Custom attribute API (19 functions x 8 handle types = 152 functions)
 *
 * Names are passed WITHOUT the '_' prefix; the library prepends it internally.
 * Type-safe: setting an attribute with a different type than its current value
 * returns -1. Remove the attribute first, then set with the new type.
 * ----------------------------------------------------------------------- */

/** @brief Macro to declare all 19 custom attribute functions for a handle type.
 *  @param PREFIX      Function name prefix (e.g., fdl_doc_).
 *  @param HANDLE_TYPE C handle type (e.g., fdl_doc_t). */
#define FDL_CUSTOM_ATTR_DECL(PREFIX, HANDLE_TYPE)                                                                    \
    /** @brief Set a string custom attribute. @return 0 on success, -1 on type mismatch. */                          \
    FDL_API int PREFIX##set_custom_attr_string(HANDLE_TYPE* h, const char* name, const char* value);                 \
    /** @brief Set an integer custom attribute. @return 0 on success, -1 on type mismatch. */                        \
    FDL_API int PREFIX##set_custom_attr_int(HANDLE_TYPE* h, const char* name, int64_t value);                        \
    /** @brief Set a float custom attribute. @return 0 on success, -1 on type mismatch. */                           \
    FDL_API int PREFIX##set_custom_attr_float(HANDLE_TYPE* h, const char* name, double value);                       \
    /** @brief Set a boolean custom attribute. @return 0 on success, -1 on type mismatch. */                         \
    FDL_API int PREFIX##set_custom_attr_bool(HANDLE_TYPE* h, const char* name, int value);                           \
    /** @brief Get a string custom attribute. @return Thread-local pointer, or NULL. */                              \
    FDL_API const char* PREFIX##get_custom_attr_string(const HANDLE_TYPE* h, const char* name);                      \
    /** @brief Get an integer custom attribute. @return 0 on success, -1 if absent/wrong type. */                    \
    FDL_API int PREFIX##get_custom_attr_int(const HANDLE_TYPE* h, const char* name, int64_t* out);                   \
    /** @brief Get a float custom attribute. @return 0 on success, -1 if absent/wrong type. */                       \
    FDL_API int PREFIX##get_custom_attr_float(const HANDLE_TYPE* h, const char* name, double* out);                  \
    /** @brief Get a boolean custom attribute. @return 0 on success, -1 if absent/wrong type. */                     \
    FDL_API int PREFIX##get_custom_attr_bool(const HANDLE_TYPE* h, const char* name, int* out);                      \
    /** @brief Check if a custom attribute exists. @return FDL_TRUE or FDL_FALSE. */                                 \
    FDL_API int PREFIX##has_custom_attr(const HANDLE_TYPE* h, const char* name);                                     \
    /** @brief Get the type of a custom attribute. @return FDL_CUSTOM_ATTR_TYPE_* constant. */                       \
    FDL_API fdl_custom_attr_type_t PREFIX##get_custom_attr_type(const HANDLE_TYPE* h, const char* name);             \
    /** @brief Remove a custom attribute. @return 0 if removed, -1 if not found. */                                  \
    FDL_API int PREFIX##remove_custom_attr(HANDLE_TYPE* h, const char* name);                                        \
    /** @brief Count custom attributes on this object. */                                                            \
    FDL_API uint32_t PREFIX##custom_attrs_count(const HANDLE_TYPE* h);                                               \
    /** @brief Get name of custom attribute at index (without '_' prefix). @return Thread-local pointer, or NULL. */ \
    FDL_API const char* PREFIX##custom_attr_name_at(const HANDLE_TYPE* h, uint32_t index);                           \
    /** @brief Set a point_f64 custom attribute. @return 0 on success, -1 on type mismatch. */                       \
    FDL_API int PREFIX##set_custom_attr_point_f64(HANDLE_TYPE* h, const char* name, fdl_point_f64_t value);          \
    /** @brief Get a point_f64 custom attribute. @return 0 on success, -1 if absent/wrong type. */                   \
    FDL_API int PREFIX##get_custom_attr_point_f64(const HANDLE_TYPE* h, const char* name, fdl_point_f64_t* out);     \
    /** @brief Set a dims_f64 custom attribute. @return 0 on success, -1 on type mismatch. */                        \
    FDL_API int PREFIX##set_custom_attr_dims_f64(HANDLE_TYPE* h, const char* name, fdl_dimensions_f64_t value);      \
    /** @brief Get a dims_f64 custom attribute. @return 0 on success, -1 if absent/wrong type. */                    \
    FDL_API int PREFIX##get_custom_attr_dims_f64(const HANDLE_TYPE* h, const char* name, fdl_dimensions_f64_t* out); \
    /** @brief Set a dims_i64 custom attribute. @return 0 on success, -1 on type mismatch. */                        \
    FDL_API int PREFIX##set_custom_attr_dims_i64(HANDLE_TYPE* h, const char* name, fdl_dimensions_i64_t value);      \
    /** @brief Get a dims_i64 custom attribute. @return 0 on success, -1 if absent/wrong type. */                    \
    FDL_API int PREFIX##get_custom_attr_dims_i64(const HANDLE_TYPE* h, const char* name, fdl_dimensions_i64_t* out);

FDL_CUSTOM_ATTR_DECL(fdl_doc_, fdl_doc_t)
FDL_CUSTOM_ATTR_DECL(fdl_context_, fdl_context_t)
FDL_CUSTOM_ATTR_DECL(fdl_canvas_, fdl_canvas_t)
FDL_CUSTOM_ATTR_DECL(fdl_framing_decision_, fdl_framing_decision_t)
FDL_CUSTOM_ATTR_DECL(fdl_framing_intent_, fdl_framing_intent_t)
FDL_CUSTOM_ATTR_DECL(fdl_canvas_template_, fdl_canvas_template_t)
FDL_CUSTOM_ATTR_DECL(fdl_clip_id_, fdl_clip_id_t)
FDL_CUSTOM_ATTR_DECL(fdl_file_sequence_, fdl_file_sequence_t)

#undef FDL_CUSTOM_ATTR_DECL

#ifdef __cplusplus
}
#endif

#endif /* FDL_CORE_H */
