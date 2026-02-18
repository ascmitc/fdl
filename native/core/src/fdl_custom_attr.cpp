// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_custom_attr.cpp
 * @brief Shared implementation of custom attribute operations on ojson nodes.
 *
 * All functions expect the caller to hold the document mutex. String returns
 * use thread-local buffers keyed by (node address, attribute name) to avoid
 * heap allocation per call, following the pattern in fdl_accessors_api.cpp.
 */
#include "fdl_custom_attr.h"

#include <functional>
#include <string>
#include <unordered_map>

namespace fdl::detail::custom_attr {

// -----------------------------------------------------------------------
// Thread-local string buffer cache (same pattern as fdl_accessors_api.cpp)
// -----------------------------------------------------------------------

namespace {

/** @brief Cache key for thread-local string buffers: node address + field name. */
struct AttrBufKey {
    uintptr_t node_addr; /**< Address of the JSON node. */
    std::string field;   /**< Internal key (with '_' prefix). */
    /** @brief Equality comparison. */
    bool operator==(const AttrBufKey& o) const { return node_addr == o.node_addr && field == o.field; }
};

/** @brief Hash functor for AttrBufKey. */
struct AttrBufKeyHash {
    /** @brief Compute hash by combining node address and field name. */
    size_t operator()(const AttrBufKey& k) const {
        return std::hash<uintptr_t>{}(k.node_addr) ^
               (std::hash<std::string>{}(k.field) << fdl::constants::kHashCombineShift);
    }
};

/** @brief Thread-local string buffer map for custom attribute string returns. */
thread_local std::unordered_map<AttrBufKey, std::string, AttrBufKeyHash> tl_bufs; // NOLINT

} // namespace

// -----------------------------------------------------------------------
// Key construction
// -----------------------------------------------------------------------

std::string make_key(const char* name) {
    // NOLINTNEXTLINE(readability-magic-numbers,cppcoreguidelines-avoid-magic-numbers)
    std::string key(1, fdl::constants::kCustomAttrPrefix);
    key += name;
    return key;
}

// -----------------------------------------------------------------------
// Query
// -----------------------------------------------------------------------

bool has(const ojson* node, const char* name) {
    if (node == nullptr || name == nullptr) {
        return false;
    }
    return node->contains(make_key(name));
}

fdl_custom_attr_type_t get_type(const ojson* node, const char* name) {
    if (node == nullptr || name == nullptr) {
        return FDL_CUSTOM_ATTR_TYPE_NONE;
    }
    auto key = make_key(name);
    if (!node->contains(key)) {
        return FDL_CUSTOM_ATTR_TYPE_NONE;
    }
    const auto& val = (*node)[key];
    if (val.is_string()) {
        return FDL_CUSTOM_ATTR_TYPE_STRING;
    }
    if (val.is_bool()) {
        return FDL_CUSTOM_ATTR_TYPE_BOOL;
    }
    if (val.is_int64() || val.is_uint64()) {
        return FDL_CUSTOM_ATTR_TYPE_INT;
    }
    if (val.is_double()) {
        return FDL_CUSTOM_ATTR_TYPE_FLOAT;
    }
    if (val.is_object()) {
        if (val.contains("x") && val.contains("y")) {
            return FDL_CUSTOM_ATTR_TYPE_POINT_F64;
        }
        if (val.contains("width") && val.contains("height")) {
            const auto& w = val["width"];
            if (w.is_double()) {
                return FDL_CUSTOM_ATTR_TYPE_DIMS_F64;
            }
            return FDL_CUSTOM_ATTR_TYPE_DIMS_I64;
        }
        return FDL_CUSTOM_ATTR_TYPE_OTHER;
    }
    return FDL_CUSTOM_ATTR_TYPE_OTHER;
}

// -----------------------------------------------------------------------
// Setters (type-safe: fail on type mismatch)
// -----------------------------------------------------------------------

int set_string(ojson* node, const char* name, const char* value) {
    if (node == nullptr || name == nullptr || value == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (node->contains(key)) {
        const auto& existing = (*node)[key];
        if (!existing.is_string()) {
            return fdl::constants::kCustomAttrError;
        }
    }
    node->insert_or_assign(key, ojson(value));
    return fdl::constants::kCustomAttrSuccess;
}

int set_int(ojson* node, const char* name, int64_t value) {
    if (node == nullptr || name == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (node->contains(key)) {
        const auto& existing = (*node)[key];
        if (!existing.is_int64() && !existing.is_uint64()) {
            return fdl::constants::kCustomAttrError;
        }
    }
    node->insert_or_assign(key, ojson(value));
    return fdl::constants::kCustomAttrSuccess;
}

int set_float(ojson* node, const char* name, double value) {
    if (node == nullptr || name == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (node->contains(key)) {
        const auto& existing = (*node)[key];
        if (!existing.is_double()) {
            return fdl::constants::kCustomAttrError;
        }
    }
    node->insert_or_assign(key, ojson(value));
    return fdl::constants::kCustomAttrSuccess;
}

int set_bool(ojson* node, const char* name, int value) {
    if (node == nullptr || name == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (node->contains(key)) {
        const auto& existing = (*node)[key];
        if (!existing.is_bool()) {
            return fdl::constants::kCustomAttrError;
        }
    }
    node->insert_or_assign(key, ojson(value != 0));
    return fdl::constants::kCustomAttrSuccess;
}

// -----------------------------------------------------------------------
// Composite setters
// -----------------------------------------------------------------------

int set_point_f64(ojson* node, const char* name, double x, double y) {
    if (node == nullptr || name == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (node->contains(key)) {
        auto existing_type = get_type(node, name);
        if (existing_type != FDL_CUSTOM_ATTR_TYPE_POINT_F64) {
            return fdl::constants::kCustomAttrError;
        }
    }
    ojson obj(jsoncons::json_object_arg);
    obj.insert_or_assign("x", ojson(x));
    obj.insert_or_assign("y", ojson(y));
    node->insert_or_assign(key, std::move(obj));
    return fdl::constants::kCustomAttrSuccess;
}

int set_dims_f64(ojson* node, const char* name, double width, double height) {
    if (node == nullptr || name == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (node->contains(key)) {
        auto existing_type = get_type(node, name);
        if (existing_type != FDL_CUSTOM_ATTR_TYPE_DIMS_F64) {
            return fdl::constants::kCustomAttrError;
        }
    }
    ojson obj(jsoncons::json_object_arg);
    obj.insert_or_assign("width", ojson(width));
    obj.insert_or_assign("height", ojson(height));
    node->insert_or_assign(key, std::move(obj));
    return fdl::constants::kCustomAttrSuccess;
}

int set_dims_i64(ojson* node, const char* name, int64_t width, int64_t height) {
    if (node == nullptr || name == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (node->contains(key)) {
        auto existing_type = get_type(node, name);
        if (existing_type != FDL_CUSTOM_ATTR_TYPE_DIMS_I64) {
            return fdl::constants::kCustomAttrError;
        }
    }
    ojson obj(jsoncons::json_object_arg);
    obj.insert_or_assign("width", ojson(width));
    obj.insert_or_assign("height", ojson(height));
    node->insert_or_assign(key, std::move(obj));
    return fdl::constants::kCustomAttrSuccess;
}

// -----------------------------------------------------------------------
// Getters
// -----------------------------------------------------------------------

const char* get_string(const ojson* node, const char* name) {
    if (node == nullptr || name == nullptr) {
        return nullptr;
    }
    auto key = make_key(name);
    if (!node->contains(key) || !(*node)[key].is_string()) {
        return nullptr;
    }
    const AttrBufKey bk{reinterpret_cast<uintptr_t>(node), key};
    auto& buf = tl_bufs[bk];
    buf = (*node)[key].as<std::string>();
    return buf.c_str();
}

int get_int(const ojson* node, const char* name, int64_t* out) {
    if (node == nullptr || name == nullptr || out == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (!node->contains(key)) {
        return fdl::constants::kCustomAttrError;
    }
    const auto& val = (*node)[key];
    if (!val.is_int64() && !val.is_uint64()) {
        return fdl::constants::kCustomAttrError;
    }
    *out = val.as<int64_t>();
    return fdl::constants::kCustomAttrSuccess;
}

int get_float(const ojson* node, const char* name, double* out) {
    if (node == nullptr || name == nullptr || out == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (!node->contains(key)) {
        return fdl::constants::kCustomAttrError;
    }
    const auto& val = (*node)[key];
    if (!val.is_double()) {
        return fdl::constants::kCustomAttrError;
    }
    *out = val.as<double>();
    return fdl::constants::kCustomAttrSuccess;
}

int get_bool(const ojson* node, const char* name, int* out) {
    if (node == nullptr || name == nullptr || out == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (!node->contains(key)) {
        return fdl::constants::kCustomAttrError;
    }
    const auto& val = (*node)[key];
    if (!val.is_bool()) {
        return fdl::constants::kCustomAttrError;
    }
    *out = val.as_bool() ? FDL_TRUE : FDL_FALSE;
    return fdl::constants::kCustomAttrSuccess;
}

// -----------------------------------------------------------------------
// Composite getters
// -----------------------------------------------------------------------

int get_point_f64(const ojson* node, const char* name, double* x, double* y) {
    if (node == nullptr || name == nullptr || x == nullptr || y == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (!node->contains(key)) {
        return fdl::constants::kCustomAttrError;
    }
    const auto& val = (*node)[key];
    if (!val.is_object() || !val.contains("x") || !val.contains("y")) {
        return fdl::constants::kCustomAttrError;
    }
    *x = val["x"].as<double>();
    *y = val["y"].as<double>();
    return fdl::constants::kCustomAttrSuccess;
}

int get_dims_f64(const ojson* node, const char* name, double* width, double* height) {
    if (node == nullptr || name == nullptr || width == nullptr || height == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (!node->contains(key)) {
        return fdl::constants::kCustomAttrError;
    }
    const auto& val = (*node)[key];
    if (!val.is_object() || !val.contains("width") || !val.contains("height")) {
        return fdl::constants::kCustomAttrError;
    }
    const auto& w = val["width"];
    if (!w.is_double()) {
        return fdl::constants::kCustomAttrError;
    }
    *width = w.as<double>();
    *height = val["height"].as<double>();
    return fdl::constants::kCustomAttrSuccess;
}

int get_dims_i64(const ojson* node, const char* name, int64_t* width, int64_t* height) {
    if (node == nullptr || name == nullptr || width == nullptr || height == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (!node->contains(key)) {
        return fdl::constants::kCustomAttrError;
    }
    const auto& val = (*node)[key];
    if (!val.is_object() || !val.contains("width") || !val.contains("height")) {
        return fdl::constants::kCustomAttrError;
    }
    const auto& w = val["width"];
    if (w.is_double()) {
        return fdl::constants::kCustomAttrError;
    }
    if (!w.is_int64() && !w.is_uint64()) {
        return fdl::constants::kCustomAttrError;
    }
    *width = w.as<int64_t>();
    *height = val["height"].as<int64_t>();
    return fdl::constants::kCustomAttrSuccess;
}

// -----------------------------------------------------------------------
// Remove
// -----------------------------------------------------------------------

int remove(ojson* node, const char* name) {
    if (node == nullptr || name == nullptr) {
        return fdl::constants::kCustomAttrError;
    }
    auto key = make_key(name);
    if (!node->contains(key)) {
        return fdl::constants::kCustomAttrError;
    }
    node->erase(key);
    return fdl::constants::kCustomAttrSuccess;
}

// -----------------------------------------------------------------------
// Enumeration
// -----------------------------------------------------------------------

uint32_t count(const ojson* node) {
    if (node == nullptr || !node->is_object()) {
        return 0;
    }
    uint32_t n = 0;
    for (const auto& m : node->object_range()) {
        if (!m.key().empty() && m.key()[0] == fdl::constants::kCustomAttrPrefix) {
            ++n;
        }
    }
    return n;
}

const char* name_at(const ojson* node, uint32_t index) {
    if (node == nullptr || !node->is_object()) {
        return nullptr;
    }
    uint32_t cur = 0;
    for (const auto& m : node->object_range()) {
        if (!m.key().empty() && m.key()[0] == fdl::constants::kCustomAttrPrefix) {
            if (cur == index) {
                // Return the name without the '_' prefix
                const AttrBufKey bk{reinterpret_cast<uintptr_t>(node), m.key()};
                auto& buf = tl_bufs[bk];
                // NOLINTNEXTLINE(readability-magic-numbers,cppcoreguidelines-avoid-magic-numbers)
                buf = m.key().substr(1);
                return buf.c_str();
            }
            ++cur;
        }
    }
    return nullptr;
}

} // namespace fdl::detail::custom_attr
