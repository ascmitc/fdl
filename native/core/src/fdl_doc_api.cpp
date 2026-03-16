// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_doc_api.cpp
 * @brief C ABI wrappers for document creation, parsing, serialization, and memory management.
 */
#include "fdl/fdl_core.h"
#include "fdl_compat.h"
#include "fdl_constants.h"
#include "fdl_doc.h"

#include <cstring>
#include <functional>
#include <new>
#include <string>
#include <unordered_map>

#include "fdl_tl_cache.h"

namespace {

/** @brief Thread-local buffer cache key for document-level strings.
 *
 * This ensures that reading the same field from different documents returns
 * independent buffers.
 */
struct DocStringBufKey {
    uintptr_t doc_addr; /**< Address of the owning document. */
    std::string field;  /**< Field name within the document. */
    /**
     * @brief Equality comparison for hash-map lookup.
     * @param o  The other key to compare against.
     * @return True if both document address and field name match.
     */
    bool operator==(const DocStringBufKey& o) const { return doc_addr == o.doc_addr && field == o.field; }
};

/** @brief Hash functor for DocStringBufKey. */
struct DocStringBufKeyHash {
    /**
     * @brief Compute hash by combining document address and field name hashes.
     * @param k  The key to hash.
     * @return Combined hash value.
     */
    size_t operator()(const DocStringBufKey& k) const {
        return std::hash<uintptr_t>{}(k.doc_addr) ^
               (std::hash<std::string>{}(k.field) << fdl::constants::kHashCombineShift);
    }
};

/**
 * @brief Get a top-level string field from the document.
 *
 * Per-(doc, key) thread-local buffer for doc-level string accessors.
 * Pointers are valid until the next call for the SAME doc AND SAME key
 * on the SAME thread.
 *
 * @param doc  Pointer to the document handle.
 * @param key  Top-level field name to look up.
 * @return Pointer to a thread-local C string, or nullptr if absent/empty.
 */
const char* get_doc_string(const fdl_doc_t* doc, const char* key) {
    if (doc == nullptr) {
        return nullptr;
    }
    const auto& data = doc->doc.data();
    if (!data.contains(key) || !data[key].is_string()) {
        return nullptr;
    }
    static thread_local fdl::detail::TlStringCache<DocStringBufKey, DocStringBufKeyHash> cache; // NOLINT
    DocStringBufKey const bk{reinterpret_cast<uintptr_t>(doc), key};
    auto& buf = cache.get(bk);
    buf = data[key].as<std::string>();
    return buf.empty() ? nullptr : buf.c_str();
}

} // namespace

extern "C" {

fdl_doc_t* fdl_doc_create(void) {
    return new (std::nothrow) fdl_doc{};
}

void fdl_doc_free(fdl_doc_t* doc) {
    delete doc;
}

fdl_parse_result_t fdl_doc_parse_json(const char* json_str, size_t json_len) {
    fdl_parse_result_t result = {nullptr, nullptr};
    try {
        auto document = fdl::detail::Document::parse(json_str, json_len);
        auto* handle = new (std::nothrow) fdl_doc{std::move(document), {}, {}};
        if (handle == nullptr) {
            auto msg = std::string("Out of memory");
            result.error = fdl_strdup(msg.c_str());
            return result;
        }
        result.doc = handle;
    } catch (const jsoncons::ser_error& e) {
        result.error = fdl_strdup(e.what());
    } catch (const std::exception& e) {
        result.error = fdl_strdup(e.what());
    }
    return result;
}

const char* fdl_doc_get_uuid(const fdl_doc_t* doc) {
    if (doc == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return get_doc_string(doc, "uuid");
}

const char* fdl_doc_get_fdl_creator(const fdl_doc_t* doc) {
    if (doc == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return get_doc_string(doc, "fdl_creator");
}

const char* fdl_doc_get_default_framing_intent(const fdl_doc_t* doc) {
    if (doc == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return get_doc_string(doc, "default_framing_intent");
}

char* fdl_doc_to_json(const fdl_doc_t* doc, int indent) {
    if (doc == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    auto json_str = doc->doc.to_canonical_json(indent);
    return fdl_strdup(json_str.c_str());
}

} // extern "C"
