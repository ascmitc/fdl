// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_canonical.cpp
 * @brief Canonical JSON serialization -- null stripping, key reordering per FDL spec, formatting.
 */
#include "fdl_canonical.h"
#include "fdl_compat.h"

#include <cstring>

namespace fdl::detail {

// -----------------------------------------------------------------------
// Key ordering tables matching FDL canonical field order
// -----------------------------------------------------------------------

namespace {

/** @brief Canonical key order for the FDL root object. */
const std::vector<std::string> ROOT_KEYS = {
    "uuid", "version", "fdl_creator", "default_framing_intent", "framing_intents", "contexts", "canvas_templates"};

/** @brief Canonical key order for the version object. */
const std::vector<std::string> VERSION_KEYS = {"major", "minor"};

/** @brief Canonical key order for context objects. */
const std::vector<std::string> CONTEXT_KEYS = {"label", "context_creator", "clip_id", "canvases"};

/** @brief Canonical key order for clip_id objects. */
const std::vector<std::string> CLIP_ID_KEYS = {"clip_name", "file", "sequence"};

/** @brief Canonical key order for canvas objects. */
const std::vector<std::string> CANVAS_KEYS = {
    "label",
    "id",
    "source_canvas_id",
    "dimensions",
    "effective_dimensions",
    "effective_anchor_point",
    "photosite_dimensions",
    "physical_dimensions",
    "anamorphic_squeeze",
    "framing_decisions"};

/** @brief Canonical key order for framing decision objects. */
const std::vector<std::string> FRAMING_DECISION_KEYS = {
    "label",
    "id",
    "framing_intent_id",
    "dimensions",
    "anchor_point",
    "protection_dimensions",
    "protection_anchor_point"};

/** @brief Canonical key order for framing intent objects. */
const std::vector<std::string> FRAMING_INTENT_KEYS = {"label", "id", "aspect_ratio", "protection"};

/** @brief Canonical key order for canvas template objects. */
const std::vector<std::string> CANVAS_TEMPLATE_KEYS = {
    "label",
    "id",
    "target_dimensions",
    "target_anamorphic_squeeze",
    "fit_source",
    "fit_method",
    "alignment_method_vertical",
    "alignment_method_horizontal",
    "preserve_from_source_canvas",
    "maximum_dimensions",
    "pad_to_maximum",
    "round"};

/** @brief Canonical key order for dimensions objects. */
const std::vector<std::string> DIMENSIONS_KEYS = {"width", "height"};
/** @brief Canonical key order for point objects. */
const std::vector<std::string> POINT_KEYS = {"x", "y"};
/** @brief Canonical key order for round strategy objects. */
const std::vector<std::string> ROUND_STRATEGY_KEYS = {"even", "mode"};

// -----------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------

/**
 * @brief Determine type hint for a child object based on key name.
 * @param key          Key name of the child field.
 * @return Type hint string for the child, or empty if unknown.
 */
std::string child_type_hint(const std::string& /*parent_type*/, const std::string& key) {
    if (key == "version") {
        return "version";
    }
    if (key == "clip_id") {
        return "clip_id";
    }
    if (key == "dimensions" || key == "effective_dimensions" || key == "photosite_dimensions" ||
        key == "physical_dimensions" || key == "target_dimensions" || key == "maximum_dimensions" ||
        key == "protection_dimensions" || key == "aspect_ratio") {
        return "dimensions";
    }
    if (key == "anchor_point" || key == "effective_anchor_point" || key == "protection_anchor_point") {
        return "point";
    }
    if (key == "round") {
        return "round_strategy";
    }
    if (key == "framing_intents") {
        return "framing_intent_array";
    }
    if (key == "contexts") {
        return "context_array";
    }
    if (key == "canvas_templates") {
        return "canvas_template_array";
    }
    if (key == "canvases") {
        return "canvas_array";
    }
    if (key == "framing_decisions") {
        return "framing_decision_array";
    }
    return "";
}

} // namespace

// -----------------------------------------------------------------------
// Public API
// -----------------------------------------------------------------------

ojson strip_nulls(const ojson& val) {
    if (val.is_object()) {
        ojson result(jsoncons::json_object_arg);
        for (const auto& m : val.object_range()) {
            if (!m.value().is_null()) {
                result.insert_or_assign(m.key(), strip_nulls(m.value()));
            }
        }
        return result;
    }
    if (val.is_array()) {
        ojson result(jsoncons::json_array_arg);
        for (const auto& elem : val.array_range()) {
            result.push_back(strip_nulls(elem));
        }
        return result;
    }
    return val;
}

ojson reorder_object(const ojson& obj, const std::string& type_hint) {
    if (!obj.is_object()) {
        return obj;
    }

    // Select key order based on type
    const std::vector<std::string>* key_order = nullptr;
    if (type_hint == "root") {
        key_order = &ROOT_KEYS;
    } else if (type_hint == "version") {
        key_order = &VERSION_KEYS;
    } else if (type_hint == "context") {
        key_order = &CONTEXT_KEYS;
    } else if (type_hint == "clip_id") {
        key_order = &CLIP_ID_KEYS;
    } else if (type_hint == "canvas") {
        key_order = &CANVAS_KEYS;
    } else if (type_hint == "framing_decision") {
        key_order = &FRAMING_DECISION_KEYS;
    } else if (type_hint == "framing_intent") {
        key_order = &FRAMING_INTENT_KEYS;
    } else if (type_hint == "canvas_template") {
        key_order = &CANVAS_TEMPLATE_KEYS;
    } else if (type_hint == "dimensions") {
        key_order = &DIMENSIONS_KEYS;
    } else if (type_hint == "point") {
        key_order = &POINT_KEYS;
    } else if (type_hint == "round_strategy") {
        key_order = &ROUND_STRATEGY_KEYS;
    }

    ojson result(jsoncons::json_object_arg);

    if (key_order != nullptr) {
        // Insert keys in canonical order
        for (const auto& key : *key_order) {
            if (obj.contains(key)) {
                const auto& val = obj[key];
                const std::string c_hint = child_type_hint(type_hint, key);

                if (val.is_object() && !c_hint.empty()) {
                    result.insert_or_assign(key, reorder_object(val, c_hint));
                } else if (val.is_array()) {
                    // Determine element type from array type hint
                    std::string elem_type;
                    if (c_hint == "framing_intent_array") {
                        elem_type = "framing_intent";
                    } else if (c_hint == "context_array") {
                        elem_type = "context";
                    } else if (c_hint == "canvas_template_array") {
                        elem_type = "canvas_template";
                    } else if (c_hint == "canvas_array") {
                        elem_type = "canvas";
                    } else if (c_hint == "framing_decision_array") {
                        elem_type = "framing_decision";
                    }

                    ojson arr(jsoncons::json_array_arg);
                    for (const auto& elem : val.array_range()) {
                        if (elem.is_object() && !elem_type.empty()) {
                            arr.push_back(reorder_object(elem, elem_type));
                        } else {
                            arr.push_back(elem);
                        }
                    }
                    result.insert_or_assign(key, std::move(arr));
                } else {
                    result.insert_or_assign(key, val);
                }
            }
        }
        // Append any keys not in the canonical order (preserves extensibility)
        for (const auto& m : obj.object_range()) {
            if (!result.contains(m.key())) {
                result.insert_or_assign(m.key(), m.value());
            }
        }
    } else {
        // No known type — pass through
        result = obj;
    }

    return result;
}

char* node_to_canonical_json(const ojson* node, const std::string& type_hint, int indent) {
    if (node == nullptr) {
        return nullptr;
    }
    const ojson cleaned = strip_nulls(*node);
    const ojson ordered = reorder_object(cleaned, type_hint);
    std::string buffer;
    if (indent > 0) {
        jsoncons::json_options options;
        options.indent_size(static_cast<uint8_t>(indent));
        ordered.dump_pretty(buffer, options);
    } else {
        ordered.dump(buffer);
    }
    return fdl_strdup(buffer.c_str());
}

} // namespace fdl::detail
