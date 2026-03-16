// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_handles.h
 * @brief Internal handle types and handle cache for opaque FDL sub-objects.
 *
 * Each handle stores path indices into the document's ojson tree and resolves
 * its node lazily via node(). Handles are stable across array reallocations
 * (e.g., push_back). Lifetime is managed by the owning fdl_doc through the
 * fdl_handle_cache. Deduplication maps ensure at most one handle per index path.
 */
#ifndef FDL_HANDLES_INTERNAL_H
#define FDL_HANDLES_INTERNAL_H

#include <jsoncons/json.hpp>
#include <memory>
#include <unordered_map>
#include <vector>

#include "fdl_constants.h"

struct fdl_doc;

/** @name Handle types — index-based paths into the document ojson tree */
/** @{ */

/** Handle to a framing intent (root-level, single index). */
struct fdl_framing_intent {
    fdl_doc* owner;    /**< Owning document. */
    uint32_t fi_index; /**< Index into root "framing_intents" array. */
    /** @brief Resolve handle to its JSON node. @return Pointer to ojson node. */
    [[nodiscard]] jsoncons::ojson* node() const;
};

/** Handle to a context (root-level, single index). */
struct fdl_context {
    fdl_doc* owner;     /**< Owning document. */
    uint32_t ctx_index; /**< Index into root "contexts" array. */
    /** @brief Resolve handle to its JSON node. @return Pointer to ojson node. */
    [[nodiscard]] jsoncons::ojson* node() const;
};

/** Handle to a canvas template (root-level, single index). */
struct fdl_canvas_template {
    fdl_doc* owner;    /**< Owning document. */
    uint32_t ct_index; /**< Index into root "canvas_templates" array. */
    /** @brief Resolve handle to its JSON node. @return Pointer to ojson node. */
    [[nodiscard]] jsoncons::ojson* node() const;
};

/** Handle to a canvas (child of context, two-level index). */
struct fdl_canvas {
    fdl_doc* owner;     /**< Owning document. */
    uint32_t ctx_index; /**< Index into "contexts" array. */
    uint32_t cvs_index; /**< Index into context's "canvases" array. */
    /** @brief Resolve handle to its JSON node. @return Pointer to ojson node. */
    [[nodiscard]] jsoncons::ojson* node() const;
};

/** Handle to a framing decision (child of canvas, three-level index). */
struct fdl_framing_decision {
    fdl_doc* owner;     /**< Owning document. */
    uint32_t ctx_index; /**< Index into "contexts" array. */
    uint32_t cvs_index; /**< Index into context's "canvases" array. */
    uint32_t fd_index;  /**< Index into canvas's "framing_decisions" array. */
    /** @brief Resolve handle to its JSON node. @return Pointer to ojson node. */
    [[nodiscard]] jsoncons::ojson* node() const;
};

/** Handle to a clip ID (child of context, one-level index). */
struct fdl_clip_id {
    fdl_doc* owner;     /**< Owning document. */
    uint32_t ctx_index; /**< Index into "contexts" array. */
    /** @brief Resolve handle to its JSON node (context's "clip_id" object). @return Pointer to ojson node. */
    [[nodiscard]] jsoncons::ojson* node() const;
};

/** Handle to a file sequence (grandchild of context, via clip_id, one-level index). */
struct fdl_file_sequence {
    fdl_doc* owner;     /**< Owning document. */
    uint32_t ctx_index; /**< Index into "contexts" array. */
    /** @brief Resolve handle to its JSON node (clip_id's "sequence" object). @return Pointer to ojson node. */
    [[nodiscard]] jsoncons::ojson* node() const;
};

/** @} */

/** @name Index packing helpers for deduplication map keys */
/** @{ */

/**
 * @brief Pack two 32-bit indices into a 64-bit map key.
 * @param a  High 32 bits.
 * @param b  Low 32 bits.
 * @return Packed key.
 */
inline uint64_t pack_key(uint32_t a, uint32_t b) {
    return (static_cast<uint64_t>(a) << fdl::constants::kPackKey2Shift) | b;
}

/**
 * @brief Pack three indices into a 64-bit map key (20 bits each, a in high bits).
 * @param a  Bits [40..59].
 * @param b  Bits [20..39].
 * @param c  Bits [0..19].
 * @return Packed key.
 */
inline uint64_t pack_key3(uint32_t a, uint32_t b, uint32_t c) {
    return (static_cast<uint64_t>(a) << fdl::constants::kPackKey3HighShift) |
           (static_cast<uint64_t>(b) << fdl::constants::kPackKey3MidShift) | c;
}

/** @} */

/**
 * Cache container for all handle types — lives on fdl_doc.
 *
 * Ownership vectors store unique_ptrs; deduplication maps provide
 * O(1) lookup to avoid creating duplicate handles for the same index.
 */
struct fdl_handle_cache {
    /** @name Ownership vectors — unique_ptrs own the handle memory */
    /** @{ */
    std::vector<std::unique_ptr<fdl_context>> contexts;                   /**< Context handles. */
    std::vector<std::unique_ptr<fdl_canvas>> canvases;                    /**< Canvas handles. */
    std::vector<std::unique_ptr<fdl_framing_decision>> framing_decisions; /**< Framing decision handles. */
    std::vector<std::unique_ptr<fdl_framing_intent>> framing_intents;     /**< Framing intent handles. */
    std::vector<std::unique_ptr<fdl_canvas_template>> canvas_templates;   /**< Canvas template handles. */
    std::vector<std::unique_ptr<fdl_clip_id>> clip_ids;                   /**< Clip ID handles. */
    std::vector<std::unique_ptr<fdl_file_sequence>> file_sequences;       /**< File sequence handles. */
    /** @} */

    /** @name Deduplication maps — index path to raw pointer into ownership vectors */
    /** @{ */
    std::unordered_map<uint32_t, fdl_context*> ctx_by_index;        /**< Context dedup map. */
    std::unordered_map<uint32_t, fdl_framing_intent*> fi_by_index;  /**< Framing intent dedup map. */
    std::unordered_map<uint32_t, fdl_canvas_template*> ct_by_index; /**< Canvas template dedup map. */
    std::unordered_map<uint64_t, fdl_canvas*> cvs_by_key;           /**< Canvas dedup map (packed ctx+cvs key). */
    std::unordered_map<uint64_t, fdl_framing_decision*> fd_by_key;  /**< Framing decision dedup map (packed key). */
    std::unordered_map<uint32_t, fdl_clip_id*> cid_by_ctx;          /**< Clip ID dedup map (by context index). */
    std::unordered_map<uint32_t, fdl_file_sequence*> seq_by_ctx;    /**< File sequence dedup map (by context index). */
    /** @} */

    /** @brief Clear all handles and deduplication maps. */
    void clear() {
        contexts.clear();
        canvases.clear();
        framing_decisions.clear();
        framing_intents.clear();
        canvas_templates.clear();
        clip_ids.clear();
        file_sequences.clear();
        ctx_by_index.clear();
        fi_by_index.clear();
        ct_by_index.clear();
        cvs_by_key.clear();
        fd_by_key.clear();
        cid_by_ctx.clear();
        seq_by_ctx.clear();
    }
};

#endif // FDL_HANDLES_INTERNAL_H
