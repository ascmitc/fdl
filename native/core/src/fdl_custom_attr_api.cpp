// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_custom_attr_api.cpp
 * @brief C ABI wrappers for custom attribute operations on all handle types.
 *
 * Uses a macro to generate 13 extern "C" functions per handle type (8 types = 104 functions).
 * Each wrapper null-checks the handle, acquires the document mutex, resolves the
 * target JSON node, and delegates to the shared implementation in fdl_custom_attr.h.
 */
#include "fdl/fdl_core.h"
#include "fdl_custom_attr.h"
#include "fdl_doc.h"

namespace ca = fdl::detail::custom_attr;

// clang-format off

/**
 * @brief Macro to generate all 19 custom attribute C ABI functions for a handle type.
 *
 * @param PREFIX      Function name prefix (e.g., fdl_doc_).
 * @param HANDLE_TYPE C handle type (e.g., fdl_doc_t).
 * @param GET_OWNER   Expression to get the owning fdl_doc from handle pointer 'h'.
 * @param GET_NODE    Expression to get the ojson* from handle pointer 'h'.
 */
#define FDL_CUSTOM_ATTR_IMPL(PREFIX, HANDLE_TYPE, GET_OWNER, GET_NODE)                                            \
    int PREFIX##set_custom_attr_string(HANDLE_TYPE* h, const char* name, const char* value) {                     \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        auto* node = GET_NODE;                                                                                    \
        return ca::set_string(node, name, value);                                                                 \
    }                                                                                                             \
    int PREFIX##set_custom_attr_int(HANDLE_TYPE* h, const char* name, int64_t value) {                            \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        auto* node = GET_NODE;                                                                                    \
        return ca::set_int(node, name, value);                                                                    \
    }                                                                                                             \
    int PREFIX##set_custom_attr_float(HANDLE_TYPE* h, const char* name, double value) {                           \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        auto* node = GET_NODE;                                                                                    \
        return ca::set_float(node, name, value);                                                                  \
    }                                                                                                             \
    int PREFIX##set_custom_attr_bool(HANDLE_TYPE* h, const char* name, int value) {                               \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        auto* node = GET_NODE;                                                                                    \
        return ca::set_bool(node, name, value);                                                                   \
    }                                                                                                             \
    const char* PREFIX##get_custom_attr_string(const HANDLE_TYPE* h, const char* name) {                          \
        if (h == nullptr) return nullptr;                                                                         \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::get_string(node, name);                                                                        \
    }                                                                                                             \
    int PREFIX##get_custom_attr_int(const HANDLE_TYPE* h, const char* name, int64_t* out) {                       \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::get_int(node, name, out);                                                                      \
    }                                                                                                             \
    int PREFIX##get_custom_attr_float(const HANDLE_TYPE* h, const char* name, double* out) {                      \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::get_float(node, name, out);                                                                    \
    }                                                                                                             \
    int PREFIX##get_custom_attr_bool(const HANDLE_TYPE* h, const char* name, int* out) {                          \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::get_bool(node, name, out);                                                                     \
    }                                                                                                             \
    int PREFIX##has_custom_attr(const HANDLE_TYPE* h, const char* name) {                                         \
        if (h == nullptr) return 0;                                                                               \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::has(node, name) ? FDL_TRUE : FDL_FALSE;                                                        \
    }                                                                                                             \
    fdl_custom_attr_type_t PREFIX##get_custom_attr_type(const HANDLE_TYPE* h, const char* name) {                 \
        if (h == nullptr) return FDL_CUSTOM_ATTR_TYPE_NONE;                                                       \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::get_type(node, name);                                                                          \
    }                                                                                                             \
    int PREFIX##remove_custom_attr(HANDLE_TYPE* h, const char* name) {                                            \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        auto* node = GET_NODE;                                                                                    \
        return ca::remove(node, name);                                                                            \
    }                                                                                                             \
    uint32_t PREFIX##custom_attrs_count(const HANDLE_TYPE* h) {                                                   \
        if (h == nullptr) return 0;                                                                               \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::count(node);                                                                                   \
    }                                                                                                             \
    const char* PREFIX##custom_attr_name_at(const HANDLE_TYPE* h, uint32_t index) {                               \
        if (h == nullptr) return nullptr;                                                                         \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::name_at(node, index);                                                                          \
    }                                                                                                             \
    int PREFIX##set_custom_attr_point_f64(HANDLE_TYPE* h, const char* name, fdl_point_f64_t value) {              \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        auto* node = GET_NODE;                                                                                    \
        return ca::set_point_f64(node, name, value.x, value.y);                                                   \
    }                                                                                                             \
    int PREFIX##get_custom_attr_point_f64(const HANDLE_TYPE* h, const char* name, fdl_point_f64_t* out) {         \
        if (h == nullptr || out == nullptr) return fdl::constants::kCustomAttrError;                               \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::get_point_f64(node, name, &out->x, &out->y);                                                   \
    }                                                                                                             \
    int PREFIX##set_custom_attr_dims_f64(HANDLE_TYPE* h, const char* name, fdl_dimensions_f64_t value) {          \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        auto* node = GET_NODE;                                                                                    \
        return ca::set_dims_f64(node, name, value.width, value.height);                                            \
    }                                                                                                             \
    int PREFIX##get_custom_attr_dims_f64(const HANDLE_TYPE* h, const char* name, fdl_dimensions_f64_t* out) {     \
        if (h == nullptr || out == nullptr) return fdl::constants::kCustomAttrError;                               \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::get_dims_f64(node, name, &out->width, &out->height);                                            \
    }                                                                                                             \
    int PREFIX##set_custom_attr_dims_i64(HANDLE_TYPE* h, const char* name, fdl_dimensions_i64_t value) {          \
        if (h == nullptr) return fdl::constants::kCustomAttrError;                                                \
        const doc_lock lock(GET_OWNER);                                                                           \
        auto* node = GET_NODE;                                                                                    \
        return ca::set_dims_i64(node, name, value.width, value.height);                                            \
    }                                                                                                             \
    int PREFIX##get_custom_attr_dims_i64(const HANDLE_TYPE* h, const char* name, fdl_dimensions_i64_t* out) {     \
        if (h == nullptr || out == nullptr) return fdl::constants::kCustomAttrError;                               \
        const doc_lock lock(GET_OWNER);                                                                           \
        const auto* node = GET_NODE;                                                                              \
        return ca::get_dims_i64(node, name, &out->width, &out->height);                                            \
    }

// clang-format on

extern "C" {

// Document (root-level) — owner IS the handle, node is the data tree root
FDL_CUSTOM_ATTR_IMPL(fdl_doc_, fdl_doc_t, h, &h->doc.data())

// Sub-object handles — owner is h->owner, node is h->node()
FDL_CUSTOM_ATTR_IMPL(fdl_context_, fdl_context_t, h->owner, h->node())
FDL_CUSTOM_ATTR_IMPL(fdl_canvas_, fdl_canvas_t, h->owner, h->node())
FDL_CUSTOM_ATTR_IMPL(fdl_framing_decision_, fdl_framing_decision_t, h->owner, h->node())
FDL_CUSTOM_ATTR_IMPL(fdl_framing_intent_, fdl_framing_intent_t, h->owner, h->node())
FDL_CUSTOM_ATTR_IMPL(fdl_canvas_template_, fdl_canvas_template_t, h->owner, h->node())
FDL_CUSTOM_ATTR_IMPL(fdl_clip_id_, fdl_clip_id_t, h->owner, h->node())
FDL_CUSTOM_ATTR_IMPL(fdl_file_sequence_, fdl_file_sequence_t, h->owner, h->node())

} // extern "C"
