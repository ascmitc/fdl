// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_collection_helpers.h
 * @brief Template helpers for collection traversal (count, at, find_by_field).
 *
 * These templates eliminate duplication across the 5 collection types
 * (framing_intents, contexts, canvas_templates, canvases, framing_decisions).
 * Each template is parameterized by:
 * - HandleT: the handle struct type
 * - MakeHandleFn: callable(doc, index) -> unique_ptr<HandleT>
 * - GetCacheFn: callable(doc) -> pair<ownership_vec&, dedup_map&>
 *
 * The doc_lock must already be held by the caller.
 */
#ifndef FDL_COLLECTION_HELPERS_H
#define FDL_COLLECTION_HELPERS_H

#include "fdl_doc.h"

#include <cstdint>
#include <memory>
#include <string_view>

namespace fdl::detail {

/**
 * @brief Count elements in a root-level collection array.
 *
 * Caller must hold the document lock.
 *
 * @param doc  Document handle.
 * @param key  JSON key for the root-level array (e.g., "contexts").
 * @return Number of elements, or 0 if absent.
 */
inline uint32_t root_collection_count(fdl_doc_t* doc, const char* key) {
    auto& data = doc->doc.data();
    if (!data.contains(key) || !data[key].is_array()) {
        return 0;
    }
    return static_cast<uint32_t>(data[key].size());
}

/**
 * @brief Access an element by index in a root-level collection, with handle deduplication.
 *
 * Caller must hold the document lock.
 *
 * @tparam HandleT      Handle struct type.
 * @tparam MakeHandleFn Callable: (fdl_doc_t*, uint32_t) -> std::unique_ptr<HandleT>.
 * @tparam GetCacheFn   Callable: (fdl_doc_t*) -> std::pair<vector<unique_ptr<HandleT>>&, map<KeyT,HandleT*>&>.
 * @param doc          Document handle.
 * @param key          JSON key for the root-level array.
 * @param index        Element index.
 * @param make_handle  Factory for creating new handles.
 * @param get_cache    Accessor for ownership vector and dedup map.
 * @return Handle pointer, or nullptr if out of bounds.
 */
template<typename HandleT, typename MakeHandleFn, typename GetCacheFn>
HandleT* root_collection_at(
    fdl_doc_t* doc, const char* key, uint32_t index, MakeHandleFn make_handle, GetCacheFn get_cache) {
    auto& data = doc->doc.data();
    if (!data.contains(key) || !data[key].is_array()) {
        return nullptr;
    }
    if (index >= data[key].size()) {
        return nullptr;
    }

    auto [vec, map] = get_cache(doc);
    auto it = map.find(index);
    if (it != map.end()) {
        return it->second;
    }

    auto handle = make_handle(doc, index);
    auto* ptr = handle.get();
    vec.push_back(std::move(handle));
    map[index] = ptr;
    return ptr;
}

/**
 * @brief Find an element by a string field in a root-level collection.
 *
 * Performs a linear scan of the array, matching on the given field.
 * Caller must hold the document lock.
 *
 * @tparam HandleT      Handle struct type.
 * @tparam MakeHandleFn Callable: (fdl_doc_t*, uint32_t) -> std::unique_ptr<HandleT>.
 * @tparam GetCacheFn   Callable: (fdl_doc_t*) -> std::pair<vector<unique_ptr<HandleT>>&, map<KeyT,HandleT*>&>.
 * @param doc          Document handle.
 * @param array_key    JSON key for the root-level array.
 * @param field_key    JSON key within each element to match against.
 * @param target       Value to search for.
 * @param make_handle  Factory for creating new handles.
 * @param get_cache    Accessor for ownership vector and dedup map.
 * @return Handle pointer, or nullptr if not found.
 */
template<typename HandleT, typename MakeHandleFn, typename GetCacheFn>
HandleT* root_collection_find(
    fdl_doc_t* doc,
    const char* array_key,
    const char* field_key,
    const char* target,
    MakeHandleFn make_handle,
    GetCacheFn get_cache) {
    auto& data = doc->doc.data();
    if (!data.contains(array_key) || !data[array_key].is_array()) {
        return nullptr;
    }

    const std::string_view sv(target);
    auto& arr = data[array_key];
    for (size_t i = 0; i < arr.size(); ++i) {
        auto& elem = arr[i];
        if (elem.contains(field_key) && elem[field_key].is_string() && elem[field_key].as<std::string_view>() == sv) {
            auto index = static_cast<uint32_t>(i);
            auto [vec, map] = get_cache(doc);
            auto it = map.find(index);
            if (it != map.end()) {
                return it->second;
            }
            auto handle = make_handle(doc, index);
            auto* ptr = handle.get();
            vec.push_back(std::move(handle));
            map[index] = ptr;
            return ptr;
        }
    }
    return nullptr;
}

/**
 * @brief Count elements in a child collection accessed via a parent node.
 *
 * Caller must hold the document lock.
 *
 * @param parent_node  Resolved parent JSON node (e.g., context node).
 * @param key          JSON key for the child array (e.g., "canvases").
 * @return Number of elements, or 0 if absent.
 */
inline uint32_t child_collection_count(const jsoncons::ojson* parent_node, const char* key) {
    if (parent_node == nullptr || !parent_node->contains(key) || !(*parent_node)[key].is_array()) {
        return 0;
    }
    return static_cast<uint32_t>((*parent_node)[key].size());
}

/**
 * @brief Access an element by index in a child collection, with handle deduplication.
 *
 * Caller must hold the document lock.
 *
 * @tparam HandleT      Handle struct type.
 * @tparam KeyT         Dedup map key type (uint64_t for packed keys).
 * @tparam MakeHandleFn Callable: (uint32_t) -> std::unique_ptr<HandleT>.
 * @tparam GetCacheFn   Callable: () -> std::pair<vector<unique_ptr<HandleT>>&, map<KeyT,HandleT*>&>.
 * @param parent_node  Resolved parent JSON node.
 * @param key          JSON key for the child array.
 * @param index        Element index.
 * @param dedup_key    Packed key for dedup map lookup.
 * @param make_handle  Factory for creating new handles.
 * @param get_cache    Accessor for ownership vector and dedup map.
 * @return Handle pointer, or nullptr if out of bounds.
 */
template<typename HandleT, typename KeyT, typename MakeHandleFn, typename GetCacheFn>
HandleT* child_collection_at(
    const jsoncons::ojson* parent_node,
    const char* key,
    uint32_t index,
    KeyT dedup_key,
    MakeHandleFn make_handle,
    GetCacheFn get_cache) {
    if (parent_node == nullptr || !parent_node->contains(key) || !(*parent_node)[key].is_array()) {
        return nullptr;
    }
    if (index >= (*parent_node)[key].size()) {
        return nullptr;
    }

    auto [vec, map] = get_cache();
    auto it = map.find(dedup_key);
    if (it != map.end()) {
        return it->second;
    }

    auto handle = make_handle(index);
    auto* ptr = handle.get();
    vec.push_back(std::move(handle));
    map[dedup_key] = ptr;
    return ptr;
}

/**
 * @brief Find an element by a string field in a child collection.
 *
 * Caller must hold the document lock.
 *
 * @tparam HandleT      Handle struct type.
 * @tparam MakeKeyFn    Callable: (uint32_t) -> KeyT. Computes dedup key from index.
 * @tparam MakeHandleFn Callable: (uint32_t) -> std::unique_ptr<HandleT>.
 * @tparam GetCacheFn   Callable: () -> std::pair<vector<unique_ptr<HandleT>>&, map<KeyT,HandleT*>&>.
 * @param parent_node  Resolved parent JSON node.
 * @param array_key    JSON key for the child array.
 * @param field_key    JSON key within each element to match against.
 * @param target       Value to search for.
 * @param make_key     Key factory for dedup map.
 * @param make_handle  Handle factory.
 * @param get_cache    Accessor for ownership vector and dedup map.
 * @return Handle pointer, or nullptr if not found.
 */
template<typename HandleT, typename MakeKeyFn, typename MakeHandleFn, typename GetCacheFn>
HandleT* child_collection_find(
    const jsoncons::ojson* parent_node,
    const char* array_key,
    const char* field_key,
    const char* target,
    MakeKeyFn make_key,
    MakeHandleFn make_handle,
    GetCacheFn get_cache) {
    if (parent_node == nullptr || !parent_node->contains(array_key) || !(*parent_node)[array_key].is_array()) {
        return nullptr;
    }

    const std::string_view sv(target);
    const auto& arr = (*parent_node)[array_key];
    for (size_t i = 0; i < arr.size(); ++i) {
        const auto& elem = arr[i];
        if (elem.contains(field_key) && elem[field_key].is_string() && elem[field_key].as<std::string_view>() == sv) {
            auto index = static_cast<uint32_t>(i);
            auto dedup_key = make_key(index);
            auto [vec, map] = get_cache();
            auto it = map.find(dedup_key);
            if (it != map.end()) {
                return it->second;
            }
            auto handle = make_handle(index);
            auto* ptr = handle.get();
            vec.push_back(std::move(handle));
            map[dedup_key] = ptr;
            return ptr;
        }
    }
    return nullptr;
}

} // namespace fdl::detail

#endif // FDL_COLLECTION_HELPERS_H
