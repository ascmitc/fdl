// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_accessors_api.cpp
 * @brief C ABI field accessors with thread-local string buffering and per-document mutex locking.
 */
#include "fdl/fdl_core.h"
#include "fdl_canonical.h"
#include "fdl_compat.h"
#include "fdl_constants.h"
#include "fdl_doc.h"
#include "fdl_enum_map.h"

#include <cstdlib>
#include <cstring>
#include <functional>
#include <string>
#include <unordered_map>

/** @brief Alias for ordered JSON type. */
using ojson = jsoncons::ojson;

// -----------------------------------------------------------------------
// Helpers for reading typed fields from ojson nodes
// -----------------------------------------------------------------------

namespace {

/** @brief Thread-local buffer cache key: node address + field name.
 *
 * This ensures that reading the same field from different nodes (e.g.,
 * canvas.label vs context.label) returns independent buffers.
 */
struct StringBufKey {
    uintptr_t node_addr; /**< Address of the owning JSON node. */
    std::string field;   /**< Field name within the node. */
    /**
     * @brief Equality comparison for hash-map lookup.
     * @param o  The other key to compare against.
     * @return True if both node address and field name match.
     */
    bool operator==(const StringBufKey& o) const { return node_addr == o.node_addr && field == o.field; }
};

/** @brief Hash functor for StringBufKey. */
struct StringBufKeyHash {
    /**
     * @brief Compute hash by combining node address and field name hashes.
     * @param k  The key to hash.
     * @return Combined hash value.
     */
    size_t operator()(const StringBufKey& k) const {
        return std::hash<uintptr_t>{}(k.node_addr) ^
               (std::hash<std::string>{}(k.field) << fdl::constants::kHashCombineShift);
    }
};

/**
 * @brief Get a string field from a JSON node, or return nullptr.
 *
 * Per-(node, key) thread-local buffer. Pointers are valid until the next
 * call for the SAME node AND SAME key on the SAME thread.
 *
 * @param node  Pointer to the JSON node to read from.
 * @param key   Field name to look up.
 * @return Pointer to a thread-local C string, or nullptr if absent/non-string.
 */
const char* get_string(const ojson* node, const char* key) {
    if (node == nullptr || !node->contains(key) || !(*node)[key].is_string()) {
        return nullptr;
    }
    static thread_local std::unordered_map<StringBufKey, std::string, StringBufKeyHash> bufs;
    const StringBufKey bk{reinterpret_cast<uintptr_t>(node), key};
    auto& buf = bufs[bk];
    buf = (*node)[key].as<std::string>();
    return buf.c_str();
}

/**
 * @brief Get a double field from a JSON node, with fallback default.
 * @param node         Pointer to the JSON node to read from.
 * @param key          Field name to look up.
 * @param default_val  Value returned when the field is absent.
 * @return The field value, or @p default_val if not present.
 */
double get_double(const ojson* node, const char* key, double default_val) {
    if (node == nullptr || !node->contains(key)) {
        return default_val;
    }
    return (*node)[key].as<double>();
}

/**
 * @brief Get floating-point dimensions from a JSON node.
 * @param node  Pointer to the JSON node to read from.
 * @param key   Field name of the dimensions object.
 * @return Dimensions with width/height, or {0,0} if absent.
 */
fdl_dimensions_f64_t get_dims_f64(const ojson* node, const char* key) {
    fdl_dimensions_f64_t result = {0.0, 0.0};
    if (node == nullptr || !node->contains(key) || !(*node)[key].is_object()) {
        return result;
    }
    const auto& obj = (*node)[key];
    if (obj.contains("width")) {
        result.width = obj["width"].as<double>();
    }
    if (obj.contains("height")) {
        result.height = obj["height"].as<double>();
    }
    return result;
}

/**
 * @brief Get integer dimensions from a JSON node.
 * @param node  Pointer to the JSON node to read from.
 * @param key   Field name of the dimensions object.
 * @return Dimensions with width/height, or {0,0} if absent.
 */
fdl_dimensions_i64_t get_dims_i64(const ojson* node, const char* key) {
    fdl_dimensions_i64_t result = {0, 0};
    if (node == nullptr || !node->contains(key) || !(*node)[key].is_object()) {
        return result;
    }
    const auto& obj = (*node)[key];
    if (obj.contains("width")) {
        result.width = obj["width"].as<int64_t>();
    }
    if (obj.contains("height")) {
        result.height = obj["height"].as<int64_t>();
    }
    return result;
}

/**
 * @brief Get a floating-point point from a JSON node.
 * @param node  Pointer to the JSON node to read from.
 * @param key   Field name of the point object.
 * @return Point with x/y, or {0,0} if absent.
 */
fdl_point_f64_t get_point_f64(const ojson* node, const char* key) {
    fdl_point_f64_t result = {0.0, 0.0};
    if (node == nullptr || !node->contains(key) || !(*node)[key].is_object()) {
        return result;
    }
    const auto& obj = (*node)[key];
    if (obj.contains("x")) {
        result.x = obj["x"].as<double>();
    }
    if (obj.contains("y")) {
        result.y = obj["y"].as<double>();
    }
    return result;
}

} // namespace

extern "C" {

// -----------------------------------------------------------------------
// Context accessors
// -----------------------------------------------------------------------

const char* fdl_context_get_label(const fdl_context_t* ctx) {
    if (ctx == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "label");
}

const char* fdl_context_get_context_creator(const fdl_context_t* ctx) {
    if (ctx == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "context_creator");
}

// -----------------------------------------------------------------------
// Canvas accessors
// -----------------------------------------------------------------------

const char* fdl_canvas_get_label(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return nullptr;
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "label");
}

const char* fdl_canvas_get_id(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return nullptr;
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "id");
}

const char* fdl_canvas_get_source_canvas_id(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return nullptr;
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "source_canvas_id");
}

fdl_dimensions_i64_t fdl_canvas_get_dimensions(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return {0, 0};
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return {0, 0};
    }
    return get_dims_i64(n, "dimensions");
}

int fdl_canvas_has_effective_dimensions(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return 0;
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("effective_dimensions") ? FDL_TRUE : FDL_FALSE;
}

fdl_dimensions_i64_t fdl_canvas_get_effective_dimensions(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return {0, 0};
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return {0, 0};
    }
    return get_dims_i64(n, "effective_dimensions");
}

fdl_point_f64_t fdl_canvas_get_effective_anchor_point(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return {0.0, 0.0};
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return {0.0, 0.0};
    }
    return get_point_f64(n, "effective_anchor_point");
}

double fdl_canvas_get_anamorphic_squeeze(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return fdl::constants::kIdentitySqueeze;
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return fdl::constants::kIdentitySqueeze;
    }
    return get_double(n, "anamorphic_squeeze", fdl::constants::kIdentitySqueeze);
}

int fdl_canvas_has_photosite_dimensions(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return 0;
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("photosite_dimensions") ? FDL_TRUE : FDL_FALSE;
}

fdl_dimensions_i64_t fdl_canvas_get_photosite_dimensions(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return {0, 0};
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return {0, 0};
    }
    return get_dims_i64(n, "photosite_dimensions");
}

int fdl_canvas_has_physical_dimensions(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return 0;
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("physical_dimensions") ? FDL_TRUE : FDL_FALSE;
}

fdl_dimensions_f64_t fdl_canvas_get_physical_dimensions(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return {0.0, 0.0};
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return {0.0, 0.0};
    }
    return get_dims_f64(n, "physical_dimensions");
}

int fdl_context_has_clip_id(const fdl_context_t* ctx) {
    if (ctx == nullptr) {
        return 0;
    }
    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("clip_id") ? FDL_TRUE : FDL_FALSE;
}

const char* fdl_context_get_clip_id(const fdl_context_t* ctx) {
    if (ctx == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr || !n->contains("clip_id")) {
        return nullptr;
    }
    const auto& val = (*n)["clip_id"];
    if (val.is_string()) {
        return fdl_strdup(val.as<std::string>().c_str());
    }
    if (val.is_object()) {
        return fdl::detail::node_to_canonical_json(&val, "clip_id", 0);
    }
    return nullptr;
}

fdl_clip_id_t* fdl_context_clip_id(fdl_context_t* ctx) {
    if (ctx == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr || !n->contains("clip_id")) {
        return nullptr;
    }
    auto& cache = ctx->owner->handles;
    auto it = cache.cid_by_ctx.find(ctx->ctx_index);
    if (it != cache.cid_by_ctx.end()) {
        return it->second;
    }
    auto h = std::make_unique<fdl_clip_id>();
    h->owner = ctx->owner;
    h->ctx_index = ctx->ctx_index;
    auto* raw = h.get();
    cache.clip_ids.push_back(std::move(h));
    cache.cid_by_ctx[ctx->ctx_index] = raw;
    return raw;
}

const char* fdl_clip_id_get_clip_name(const fdl_clip_id_t* cid) {
    if (cid == nullptr) {
        return nullptr;
    }
    const doc_lock lock(cid->owner);
    auto* n = cid->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "clip_name");
}

int fdl_clip_id_has_file(const fdl_clip_id_t* cid) {
    if (cid == nullptr) {
        return 0;
    }
    const doc_lock lock(cid->owner);
    auto* n = cid->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("file") ? FDL_TRUE : FDL_FALSE;
}

const char* fdl_clip_id_get_file(const fdl_clip_id_t* cid) {
    if (cid == nullptr) {
        return nullptr;
    }
    const doc_lock lock(cid->owner);
    auto* n = cid->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "file");
}

int fdl_clip_id_has_sequence(const fdl_clip_id_t* cid) {
    if (cid == nullptr) {
        return 0;
    }
    const doc_lock lock(cid->owner);
    auto* n = cid->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("sequence") ? FDL_TRUE : FDL_FALSE;
}

fdl_file_sequence_t* fdl_clip_id_sequence(fdl_clip_id_t* cid) {
    if (cid == nullptr) {
        return nullptr;
    }
    const doc_lock lock(cid->owner);
    auto* n = cid->node();
    if (n == nullptr || !n->contains("sequence")) {
        return nullptr;
    }
    auto& cache = cid->owner->handles;
    auto it = cache.seq_by_ctx.find(cid->ctx_index);
    if (it != cache.seq_by_ctx.end()) {
        return it->second;
    }
    auto h = std::make_unique<fdl_file_sequence>();
    h->owner = cid->owner;
    h->ctx_index = cid->ctx_index;
    auto* raw = h.get();
    cache.file_sequences.push_back(std::move(h));
    cache.seq_by_ctx[cid->ctx_index] = raw;
    return raw;
}

char* fdl_clip_id_to_json(const fdl_clip_id_t* cid, int indent) {
    if (cid == nullptr) {
        return nullptr;
    }
    const doc_lock lock(cid->owner);
    auto* n = cid->node();
    if (n == nullptr) {
        return nullptr;
    }
    return fdl::detail::node_to_canonical_json(n, "clip_id", indent);
}

const char* fdl_file_sequence_get_value(const fdl_file_sequence_t* seq) {
    if (seq == nullptr) {
        return nullptr;
    }
    const doc_lock lock(seq->owner);
    auto* n = seq->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "value");
}

const char* fdl_file_sequence_get_idx(const fdl_file_sequence_t* seq) {
    if (seq == nullptr) {
        return nullptr;
    }
    const doc_lock lock(seq->owner);
    auto* n = seq->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "idx");
}

int64_t fdl_file_sequence_get_min(const fdl_file_sequence_t* seq) {
    if (seq == nullptr) {
        return 0;
    }
    const doc_lock lock(seq->owner);
    auto* n = seq->node();
    if (n == nullptr || !n->contains("min")) {
        return 0;
    }
    return (*n)["min"].as<int64_t>();
}

int64_t fdl_file_sequence_get_max(const fdl_file_sequence_t* seq) {
    if (seq == nullptr) {
        return 0;
    }
    const doc_lock lock(seq->owner);
    auto* n = seq->node();
    if (n == nullptr || !n->contains("max")) {
        return 0;
    }
    return (*n)["max"].as<int64_t>();
}

// -----------------------------------------------------------------------
// Framing decision accessors
// -----------------------------------------------------------------------

const char* fdl_framing_decision_get_label(const fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return nullptr;
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "label");
}

const char* fdl_framing_decision_get_id(const fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return nullptr;
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "id");
}

const char* fdl_framing_decision_get_framing_intent_id(const fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return nullptr;
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "framing_intent_id");
}

fdl_dimensions_f64_t fdl_framing_decision_get_dimensions(const fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return {0.0, 0.0};
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return {0.0, 0.0};
    }
    return get_dims_f64(n, "dimensions");
}

fdl_point_f64_t fdl_framing_decision_get_anchor_point(const fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return {0.0, 0.0};
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return {0.0, 0.0};
    }
    return get_point_f64(n, "anchor_point");
}

int fdl_framing_decision_has_protection(const fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return 0;
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("protection_dimensions") ? FDL_TRUE : FDL_FALSE;
}

fdl_dimensions_f64_t fdl_framing_decision_get_protection_dimensions(const fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return {0.0, 0.0};
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return {0.0, 0.0};
    }
    return get_dims_f64(n, "protection_dimensions");
}

fdl_point_f64_t fdl_framing_decision_get_protection_anchor_point(const fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return {0.0, 0.0};
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return {0.0, 0.0};
    }
    return get_point_f64(n, "protection_anchor_point");
}

// -----------------------------------------------------------------------
// Framing intent accessors
// -----------------------------------------------------------------------

const char* fdl_framing_intent_get_label(const fdl_framing_intent_t* fi) {
    if (fi == nullptr) {
        return nullptr;
    }
    const doc_lock lock(fi->owner);
    auto* n = fi->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "label");
}

const char* fdl_framing_intent_get_id(const fdl_framing_intent_t* fi) {
    if (fi == nullptr) {
        return nullptr;
    }
    const doc_lock lock(fi->owner);
    auto* n = fi->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "id");
}

fdl_dimensions_i64_t fdl_framing_intent_get_aspect_ratio(const fdl_framing_intent_t* fi) {
    if (fi == nullptr) {
        return {0, 0};
    }
    const doc_lock lock(fi->owner);
    auto* n = fi->node();
    if (n == nullptr) {
        return {0, 0};
    }
    return get_dims_i64(n, "aspect_ratio");
}

double fdl_framing_intent_get_protection(const fdl_framing_intent_t* fi) {
    if (fi == nullptr) {
        return 0.0;
    }
    const doc_lock lock(fi->owner);
    auto* n = fi->node();
    if (n == nullptr) {
        return 0.0;
    }
    return get_double(n, "protection", 0.0);
}

// -----------------------------------------------------------------------
// Canvas template accessors
// -----------------------------------------------------------------------

const char* fdl_canvas_template_get_label(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "label");
}

const char* fdl_canvas_template_get_id(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return nullptr;
    }
    return get_string(n, "id");
}

fdl_dimensions_i64_t fdl_canvas_template_get_target_dimensions(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return {0, 0};
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return {0, 0};
    }
    return get_dims_i64(n, "target_dimensions");
}

double fdl_canvas_template_get_target_anamorphic_squeeze(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return fdl::constants::kIdentitySqueeze;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return fdl::constants::kIdentitySqueeze;
    }
    return get_double(n, "target_anamorphic_squeeze", fdl::constants::kIdentitySqueeze);
}

fdl_geometry_path_t fdl_canvas_template_get_fit_source(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr || !n->contains("fit_source")) {
        return FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS;
    }
    return fdl::detail::geometry_path_from_string((*n)["fit_source"].as<std::string_view>());
}

fdl_fit_method_t fdl_canvas_template_get_fit_method(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return FDL_FIT_METHOD_WIDTH;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr || !n->contains("fit_method")) {
        return FDL_FIT_METHOD_WIDTH;
    }
    return fdl::detail::fit_method_from_string((*n)["fit_method"].as<std::string_view>());
}

fdl_halign_t fdl_canvas_template_get_alignment_method_horizontal(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return FDL_HALIGN_CENTER;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr || !n->contains("alignment_method_horizontal")) {
        return FDL_HALIGN_CENTER;
    }
    return fdl::detail::halign_from_string((*n)["alignment_method_horizontal"].as<std::string_view>());
}

fdl_valign_t fdl_canvas_template_get_alignment_method_vertical(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return FDL_VALIGN_CENTER;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr || !n->contains("alignment_method_vertical")) {
        return FDL_VALIGN_CENTER;
    }
    return fdl::detail::valign_from_string((*n)["alignment_method_vertical"].as<std::string_view>());
}

int fdl_canvas_template_has_preserve_from_source_canvas(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return 0;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("preserve_from_source_canvas") ? FDL_TRUE : FDL_FALSE;
}

fdl_geometry_path_t fdl_canvas_template_get_preserve_from_source_canvas(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr || !n->contains("preserve_from_source_canvas")) {
        return FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS;
    }
    return fdl::detail::geometry_path_from_string((*n)["preserve_from_source_canvas"].as<std::string_view>());
}

int fdl_canvas_template_has_maximum_dimensions(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return 0;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return 0;
    }
    return n->contains("maximum_dimensions") ? FDL_TRUE : FDL_FALSE;
}

fdl_dimensions_i64_t fdl_canvas_template_get_maximum_dimensions(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return {0, 0};
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return {0, 0};
    }
    return get_dims_i64(n, "maximum_dimensions");
}

int fdl_canvas_template_get_pad_to_maximum(const fdl_canvas_template_t* ct) {
    if (ct == nullptr) {
        return 0;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr || !n->contains("pad_to_maximum")) {
        return 0;
    }
    return (*n)["pad_to_maximum"].as<bool>() ? FDL_TRUE : FDL_FALSE;
}

fdl_round_strategy_t fdl_canvas_template_get_round(const fdl_canvas_template_t* ct) {
    fdl_round_strategy_t result = {FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND};
    if (ct == nullptr) {
        return result;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr || !n->contains("round") || !(*n)["round"].is_object()) {
        return result;
    }

    const auto& rnd = (*n)["round"];
    if (rnd.contains("even") && rnd["even"].is_string()) {
        result.even = fdl::detail::rounding_even_from_string(rnd["even"].as<std::string_view>());
    }
    if (rnd.contains("mode") && rnd["mode"].is_string()) {
        result.mode = fdl::detail::rounding_mode_from_string(rnd["mode"].as<std::string_view>());
    }
    return result;
}

// -----------------------------------------------------------------------
// Document header accessors (version)
// -----------------------------------------------------------------------

int fdl_doc_get_version_major(const fdl_doc_t* doc) {
    if (doc == nullptr) {
        return 0;
    }
    const doc_lock lock(doc);
    const auto& data = doc->doc.data();
    if (!data.contains("version") || !data["version"].is_object()) {
        return 0;
    }
    const auto& ver = data["version"];
    if (!ver.contains("major")) {
        return 0;
    }
    return ver["major"].as<int>();
}

int fdl_doc_get_version_minor(const fdl_doc_t* doc) {
    if (doc == nullptr) {
        return 0;
    }
    const doc_lock lock(doc);
    const auto& data = doc->doc.data();
    if (!data.contains("version") || !data["version"].is_object()) {
        return 0;
    }
    const auto& ver = data["version"];
    if (!ver.contains("minor")) {
        return 0;
    }
    return ver["minor"].as<int>();
}

// -----------------------------------------------------------------------
// Sub-object serialization
// -----------------------------------------------------------------------

char* fdl_context_to_json(const fdl_context_t* ctx, int indent) {
    if (ctx == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr) {
        return nullptr;
    }
    return fdl::detail::node_to_canonical_json(n, "context", indent);
}

char* fdl_canvas_to_json(const fdl_canvas_t* canvas, int indent) {
    if (canvas == nullptr) {
        return nullptr;
    }
    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return nullptr;
    }
    return fdl::detail::node_to_canonical_json(n, "canvas", indent);
}

char* fdl_framing_decision_to_json(const fdl_framing_decision_t* fd, int indent) {
    if (fd == nullptr) {
        return nullptr;
    }
    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return nullptr;
    }
    return fdl::detail::node_to_canonical_json(n, "framing_decision", indent);
}

char* fdl_framing_intent_to_json(const fdl_framing_intent_t* fi, int indent) {
    if (fi == nullptr) {
        return nullptr;
    }
    const doc_lock lock(fi->owner);
    auto* n = fi->node();
    if (n == nullptr) {
        return nullptr;
    }
    return fdl::detail::node_to_canonical_json(n, "framing_intent", indent);
}

char* fdl_canvas_template_to_json(const fdl_canvas_template_t* ct, int indent) {
    if (ct == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return nullptr;
    }
    return fdl::detail::node_to_canonical_json(n, "canvas_template", indent);
}

} // extern "C"
