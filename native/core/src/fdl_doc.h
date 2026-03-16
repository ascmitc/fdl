// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_doc.h
 * @brief Internal Document class and opaque fdl_doc handle definition.
 *
 * Wraps an ojson tree with parsing, serialization, and per-document mutex locking.
 * The fdl_doc struct is the concrete type behind the public opaque handle.
 */
#ifndef FDL_DOC_INTERNAL_H
#define FDL_DOC_INTERNAL_H

#include <jsoncons/json.hpp>
#include <mutex>
#include <string>

#include "fdl_handles.h"

namespace fdl::detail {

/** Use ojson (ordered JSON) to preserve key insertion order for canonical serialization. */
using ojson = jsoncons::ojson;

/** Internal document class wrapping the JSON data tree. */
class Document {
public:
    Document() = default;

    /**
     * @brief Construct from an existing JSON tree.
     * @param data  JSON data (moved into the document).
     */
    explicit Document(ojson data) : data_(std::move(data)) {}

    /**
     * @brief Parse JSON string. Throws jsoncons::ser_error on failure.
     * @param json_str  Pointer to JSON text.
     * @param json_len  Length of JSON text in bytes.
     * @return Parsed Document.
     */
    static Document parse(const char* json_str, size_t json_len);

    /**
     * @brief Access the internal JSON data (const).
     * @return Const reference to the ojson tree.
     */
    [[nodiscard]] const ojson& data() const { return data_; }
    /**
     * @brief Access the internal JSON data (mutable).
     * @return Mutable reference to the ojson tree.
     */
    [[nodiscard]] ojson& data() { return data_; }

    /**
     * @brief Get UUID from the document.
     * @return UUID string, or empty string if missing.
     */
    [[nodiscard]] std::string get_uuid() const;
    /**
     * @brief Get fdl_creator from the document.
     * @return Creator string, or empty string if missing.
     */
    [[nodiscard]] std::string get_fdl_creator() const;

    /**
     * @brief Canonical JSON serialization.
     *
     * Reorders keys per FDL type-specific tables and strips null values.
     *
     * @param indent  Spaces per indent level (default 2, 0 for compact).
     * @return Formatted JSON string.
     */
    [[nodiscard]] std::string to_canonical_json(int indent = constants::kDefaultJsonIndent) const;

private:
    ojson data_;
};

} // namespace fdl::detail

/** Opaque handle definition — shared across ABI translation units. */
struct fdl_doc {
    fdl::detail::Document doc; /**< Document data tree. */
    fdl_handle_cache handles;  /**< Cache of sub-object handles. */
    mutable std::mutex mtx;    /**< Per-document mutex for thread safety. */
};

/**
 * RAII lock helper for per-document synchronization.
 *
 * Acquires the document's mutex on construction, releases on destruction.
 * Safe with const handles because the mutex is mutable.
 */
struct doc_lock {
    std::unique_lock<std::mutex> lock_; /**< Held lock (empty if doc was null). */

    /**
     * @brief Acquire the document's mutex.
     * @param doc  Document to lock (may be NULL, in which case no lock is acquired).
     */
    explicit doc_lock(const fdl_doc* doc) {
        if (doc != nullptr) {
            lock_ = std::unique_lock<std::mutex>(doc->mtx);
        }
    }
};

#endif // FDL_DOC_INTERNAL_H
