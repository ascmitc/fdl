// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_canonical.h
 * @brief Canonical JSON serialization — key ordering, null stripping, formatting.
 *
 * The FDL specification requires JSON keys to appear in a defined order per
 * object type. This module provides the reordering and cleanup logic.
 */
#ifndef FDL_CANONICAL_INTERNAL_H
#define FDL_CANONICAL_INTERNAL_H

#include <jsoncons/json.hpp>
#include <string>

namespace fdl::detail {

using ojson = jsoncons::ojson;

/**
 * @brief Strip null values recursively; empty arrays are preserved as [].
 * @param val  JSON value to process.
 * @return Copy of @p val with all null members removed.
 */
ojson strip_nulls(const ojson& val);

/**
 * Reorder an object's keys according to the specified type's canonical order.
 *
 * @param obj        JSON object to reorder.
 * @param type_hint  Object type: "root", "context", "canvas", "framing_decision",
 *                   "framing_intent", "canvas_template", "version",
 *                   "dimensions", "point", "round_strategy", "clip_id".
 * @return New object with keys in canonical order.
 */
ojson reorder_object(const ojson& obj, const std::string& type_hint);

/**
 * Serialize an ojson node to canonical JSON: strip_nulls + reorder + format.
 *
 * @param node       JSON node to serialize (may be nullptr).
 * @param type_hint  Type hint for key ordering.
 * @param indent     Spaces per indent level (0 for compact).
 * @return Heap-allocated C string (caller owns, free with fdl_free / std::free).
 *         Returns nullptr if node is nullptr.
 */
char* node_to_canonical_json(const ojson* node, const std::string& type_hint, int indent);

} // namespace fdl::detail

#endif // FDL_CANONICAL_INTERNAL_H
