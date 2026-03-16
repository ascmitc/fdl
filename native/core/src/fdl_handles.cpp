// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_handles.cpp
 * @brief Handle node() resolution -- lazy index-based lookup into the document ojson tree.
 *
 * All handle types resolve to their JSON node via a shared path-walking helper,
 * reducing duplication across the 7 node() methods.
 */
#include "fdl_handles.h"
#include "fdl_doc.h"

#include <initializer_list>
#include <utility>

using ojson = jsoncons::ojson;

namespace {

/**
 * @brief Walk a chain of (array-key, index) steps from the document root.
 *
 * Each step looks up a named array in the current node, checks bounds,
 * and descends into the element at the given index.
 *
 * @param owner  Owning document (may be null).
 * @param steps  Sequence of (key, index) pairs to traverse.
 * @return Pointer to the final array element, or nullptr if any step fails.
 */
ojson* resolve_path(fdl_doc* owner, std::initializer_list<std::pair<const char*, uint32_t>> steps) {
    if (owner == nullptr) {
        return nullptr;
    }
    ojson* node = &owner->doc.data();
    for (const auto& [key, index] : steps) {
        if (!node->contains(key)) {
            return nullptr;
        }
        auto& arr = (*node)[key];
        if (index >= arr.size()) {
            return nullptr;
        }
        node = &arr[index];
    }
    return node;
}

/**
 * @brief Walk an array path then descend into a named (non-array) key.
 *
 * Combines resolve_path() with a final named-key lookup, used by handle
 * types that resolve to a named child object (e.g., clip_id, sequence).
 *
 * @param owner      Owning document (may be null).
 * @param steps      Array path to traverse first.
 * @param final_key  Named key to descend into after the array path.
 * @return Pointer to the named child, or nullptr if any step fails.
 */
ojson* resolve_path_then_key(
    fdl_doc* owner, std::initializer_list<std::pair<const char*, uint32_t>> steps, const char* final_key) {
    ojson* node = resolve_path(owner, steps);
    if (node == nullptr || !node->contains(final_key)) {
        return nullptr;
    }
    return &(*node)[final_key];
}

} // namespace

ojson* fdl_framing_intent::node() const {
    return resolve_path(owner, {{"framing_intents", fi_index}});
}

ojson* fdl_context::node() const {
    return resolve_path(owner, {{"contexts", ctx_index}});
}

ojson* fdl_canvas_template::node() const {
    return resolve_path(owner, {{"canvas_templates", ct_index}});
}

ojson* fdl_canvas::node() const {
    return resolve_path(owner, {{"contexts", ctx_index}, {"canvases", cvs_index}});
}

ojson* fdl_framing_decision::node() const {
    return resolve_path(owner, {{"contexts", ctx_index}, {"canvases", cvs_index}, {"framing_decisions", fd_index}});
}

ojson* fdl_clip_id::node() const {
    return resolve_path_then_key(owner, {{"contexts", ctx_index}}, "clip_id");
}

ojson* fdl_file_sequence::node() const {
    ojson* cid = resolve_path_then_key(owner, {{"contexts", ctx_index}}, "clip_id");
    if (cid == nullptr || !cid->contains("sequence")) {
        return nullptr;
    }
    return &(*cid)["sequence"];
}
