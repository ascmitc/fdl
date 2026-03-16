// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_custom_attr.h
 * @brief Internal helpers for custom attribute operations on ojson nodes.
 *
 * Custom attributes are user-defined keys prefixed with '_' in the FDL JSON.
 * Users pass attribute names without the prefix; the library prepends it
 * internally. All functions operate on a single ojson node (the target
 * object) and are called from the C ABI wrappers with the document mutex held.
 */
#ifndef FDL_CUSTOM_ATTR_INTERNAL_H
#define FDL_CUSTOM_ATTR_INTERNAL_H

#include <jsoncons/json.hpp>
#include <string>

#include "fdl/fdl_core.h"
#include "fdl_constants.h"

namespace fdl::detail::custom_attr {

/** @brief Alias for ordered JSON type. */
using ojson = jsoncons::ojson;

/**
 * @brief Build the internal key by prepending '_' to the user-visible name.
 * @param name  User-visible attribute name (without '_' prefix).
 * @return Internal key string (e.g., "_vendor" for "vendor").
 */
std::string make_key(const char* name);

/**
 * @brief Check if a custom attribute exists on a node.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @return True if the '_'-prefixed key exists.
 */
bool has(const ojson* node, const char* name);

/**
 * @brief Get the type of a custom attribute.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @return One of FDL_CUSTOM_ATTR_TYPE_* constants.
 */
fdl_custom_attr_type_t get_type(const ojson* node, const char* name);

/**
 * @brief Set a string custom attribute. Fails if the key exists with a different type.
 * @param node   Target JSON node.
 * @param name   User-visible attribute name.
 * @param value  String value to set.
 * @return 0 on success, -1 on type mismatch.
 */
int set_string(ojson* node, const char* name, const char* value);

/**
 * @brief Set an integer custom attribute. Fails if the key exists with a different type.
 * @param node   Target JSON node.
 * @param name   User-visible attribute name.
 * @param value  Integer value to set.
 * @return 0 on success, -1 on type mismatch.
 */
int set_int(ojson* node, const char* name, int64_t value);

/**
 * @brief Set a floating-point custom attribute. Fails if the key exists with a different type.
 * @param node   Target JSON node.
 * @param name   User-visible attribute name.
 * @param value  Double value to set.
 * @return 0 on success, -1 on type mismatch.
 */
int set_float(ojson* node, const char* name, double value);

/**
 * @brief Set a boolean custom attribute. Fails if the key exists with a different type.
 * @param node   Target JSON node.
 * @param name   User-visible attribute name.
 * @param value  Boolean value (non-zero = true, zero = false).
 * @return 0 on success, -1 on type mismatch.
 */
int set_bool(ojson* node, const char* name, int value);

/**
 * @brief Get a string custom attribute.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @return Thread-local C string pointer, or nullptr if absent or wrong type.
 */
const char* get_string(const ojson* node, const char* name);

/**
 * @brief Get an integer custom attribute.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @param out   Output pointer for the integer value.
 * @return 0 on success, -1 if absent or wrong type.
 */
int get_int(const ojson* node, const char* name, int64_t* out);

/**
 * @brief Get a floating-point custom attribute.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @param out   Output pointer for the double value.
 * @return 0 on success, -1 if absent or wrong type.
 */
int get_float(const ojson* node, const char* name, double* out);

/**
 * @brief Get a boolean custom attribute.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @param out   Output pointer for the boolean value (FDL_TRUE or FDL_FALSE).
 * @return 0 on success, -1 if absent or wrong type.
 */
int get_bool(const ojson* node, const char* name, int* out);

/**
 * @brief Set a point_f64 custom attribute. Fails if the key exists with a different type.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @param x     X coordinate.
 * @param y     Y coordinate.
 * @return 0 on success, -1 on type mismatch.
 */
int set_point_f64(ojson* node, const char* name, double x, double y);

/**
 * @brief Get a point_f64 custom attribute.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @param x     Output pointer for X coordinate.
 * @param y     Output pointer for Y coordinate.
 * @return 0 on success, -1 if absent or wrong type.
 */
int get_point_f64(const ojson* node, const char* name, double* x, double* y);

/**
 * @brief Set a dims_f64 custom attribute. Fails if the key exists with a different type.
 * @param node    Target JSON node.
 * @param name    User-visible attribute name.
 * @param width   Width value.
 * @param height  Height value.
 * @return 0 on success, -1 on type mismatch.
 */
int set_dims_f64(ojson* node, const char* name, double width, double height);

/**
 * @brief Get a dims_f64 custom attribute.
 * @param node    Target JSON node.
 * @param name    User-visible attribute name.
 * @param width   Output pointer for width.
 * @param height  Output pointer for height.
 * @return 0 on success, -1 if absent or wrong type.
 */
int get_dims_f64(const ojson* node, const char* name, double* width, double* height);

/**
 * @brief Set a dims_i64 custom attribute. Fails if the key exists with a different type.
 * @param node    Target JSON node.
 * @param name    User-visible attribute name.
 * @param width   Width value.
 * @param height  Height value.
 * @return 0 on success, -1 on type mismatch.
 */
int set_dims_i64(ojson* node, const char* name, int64_t width, int64_t height);

/**
 * @brief Get a dims_i64 custom attribute.
 * @param node    Target JSON node.
 * @param name    User-visible attribute name.
 * @param width   Output pointer for width.
 * @param height  Output pointer for height.
 * @return 0 on success, -1 if absent or wrong type.
 */
int get_dims_i64(const ojson* node, const char* name, int64_t* width, int64_t* height);

/**
 * @brief Remove a custom attribute.
 * @param node  Target JSON node.
 * @param name  User-visible attribute name.
 * @return 0 if removed, -1 if not found.
 */
int remove(ojson* node, const char* name);

/**
 * @brief Count the number of custom attributes on a node.
 * @param node  Target JSON node.
 * @return Number of '_'-prefixed keys.
 */
uint32_t count(const ojson* node);

/**
 * @brief Get the name of a custom attribute by index.
 *
 * Returns names without the '_' prefix. The index refers to the order
 * among custom attributes only (not all keys).
 *
 * @param node   Target JSON node.
 * @param index  Zero-based index among custom attributes.
 * @return Thread-local C string pointer, or nullptr if index is out of range.
 */
const char* name_at(const ojson* node, uint32_t index);

} // namespace fdl::detail::custom_attr

#endif // FDL_CUSTOM_ATTR_INTERNAL_H
