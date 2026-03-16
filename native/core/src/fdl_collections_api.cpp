// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_collections_api.cpp
 * @brief C ABI for collection traversal (count, at, find_by_id/label) and handle allocation.
 *
 * Uses template helpers from fdl_collection_helpers.h to eliminate duplication
 * across the 5 collection types. Each C ABI function is a thin wrapper that
 * acquires the document lock and delegates to the appropriate template.
 */
#include "fdl/fdl_core.h"
#include "fdl_collection_helpers.h"
#include "fdl_compat.h"
#include "fdl_constants.h"
#include "fdl_doc.h"

#include <cinttypes>
#include <cstring>
#include <string_view>
#include <tuple>

using ojson = jsoncons::ojson;

// -----------------------------------------------------------------------
// Handle factory and cache accessor helpers (anonymous namespace)
// -----------------------------------------------------------------------

namespace {

/** @brief Create a framing intent handle. */
auto make_fi(fdl_doc_t* doc, uint32_t index) {
    auto h = std::make_unique<fdl_framing_intent>();
    h->owner = doc;
    h->fi_index = index;
    return h;
}

/** @brief Access framing intent ownership vector and dedup map. */
auto get_fi_cache(fdl_doc_t* doc)
    -> std::pair<decltype(doc->handles.framing_intents)&, decltype(doc->handles.fi_by_index)&> {
    return {doc->handles.framing_intents, doc->handles.fi_by_index};
}

/** @brief Create a context handle. */
auto make_ctx(fdl_doc_t* doc, uint32_t index) {
    auto h = std::make_unique<fdl_context>();
    h->owner = doc;
    h->ctx_index = index;
    return h;
}

/** @brief Access context ownership vector and dedup map. */
auto get_ctx_cache(fdl_doc_t* doc)
    -> std::pair<decltype(doc->handles.contexts)&, decltype(doc->handles.ctx_by_index)&> {
    return {doc->handles.contexts, doc->handles.ctx_by_index};
}

/** @brief Create a canvas template handle. */
auto make_ct(fdl_doc_t* doc, uint32_t index) {
    auto h = std::make_unique<fdl_canvas_template>();
    h->owner = doc;
    h->ct_index = index;
    return h;
}

/** @brief Access canvas template ownership vector and dedup map. */
auto get_ct_cache(fdl_doc_t* doc)
    -> std::pair<decltype(doc->handles.canvas_templates)&, decltype(doc->handles.ct_by_index)&> {
    return {doc->handles.canvas_templates, doc->handles.ct_by_index};
}

} // namespace

extern "C" {

// -----------------------------------------------------------------------
// Framing intents (root-level collection)
// -----------------------------------------------------------------------

uint32_t fdl_doc_framing_intents_count(fdl_doc_t* doc) {
    if (doc == nullptr) {
        return 0;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_count(doc, "framing_intents");
}

fdl_framing_intent_t* fdl_doc_framing_intent_at(fdl_doc_t* doc, uint32_t index) {
    if (doc == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_at<fdl_framing_intent>(doc, "framing_intents", index, make_fi, get_fi_cache);
}

fdl_framing_intent_t* fdl_doc_framing_intent_find_by_id(fdl_doc_t* doc, const char* id) {
    if (doc == nullptr || id == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_find<fdl_framing_intent>(
        doc, "framing_intents", "id", id, make_fi, get_fi_cache);
}

// -----------------------------------------------------------------------
// Contexts (root-level collection)
// -----------------------------------------------------------------------

uint32_t fdl_doc_contexts_count(fdl_doc_t* doc) {
    if (doc == nullptr) {
        return 0;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_count(doc, "contexts");
}

fdl_context_t* fdl_doc_context_at(fdl_doc_t* doc, uint32_t index) {
    if (doc == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_at<fdl_context>(doc, "contexts", index, make_ctx, get_ctx_cache);
}

fdl_context_t* fdl_doc_context_find_by_label(fdl_doc_t* doc, const char* label) {
    if (doc == nullptr || label == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_find<fdl_context>(doc, "contexts", "label", label, make_ctx, get_ctx_cache);
}

// -----------------------------------------------------------------------
// Canvas templates (root-level collection)
// -----------------------------------------------------------------------

uint32_t fdl_doc_canvas_templates_count(fdl_doc_t* doc) {
    if (doc == nullptr) {
        return 0;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_count(doc, "canvas_templates");
}

fdl_canvas_template_t* fdl_doc_canvas_template_at(fdl_doc_t* doc, uint32_t index) {
    if (doc == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_at<fdl_canvas_template>(doc, "canvas_templates", index, make_ct, get_ct_cache);
}

fdl_canvas_template_t* fdl_doc_canvas_template_find_by_id(fdl_doc_t* doc, const char* id) {
    if (doc == nullptr || id == nullptr) {
        return nullptr;
    }
    const doc_lock lock(doc);
    return fdl::detail::root_collection_find<fdl_canvas_template>(
        doc, "canvas_templates", "id", id, make_ct, get_ct_cache);
}

// -----------------------------------------------------------------------
// Canvases (child of context)
// -----------------------------------------------------------------------

uint32_t fdl_context_canvases_count(const fdl_context_t* ctx) {
    if (ctx == nullptr) {
        return 0;
    }
    const doc_lock lock(ctx->owner);
    return fdl::detail::child_collection_count(ctx->node(), "canvases");
}

fdl_canvas_t* fdl_context_canvas_at(fdl_context_t* ctx, uint32_t index) {
    if (ctx == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ctx->owner);
    return fdl::detail::child_collection_at<fdl_canvas>(
        ctx->node(),
        "canvases",
        index,
        pack_key(ctx->ctx_index, index),
        [ctx](uint32_t idx) {
            auto h = std::make_unique<fdl_canvas>();
            h->owner = ctx->owner;
            h->ctx_index = ctx->ctx_index;
            h->cvs_index = idx;
            return h;
        },
        [ctx]() -> std::pair<decltype(ctx->owner->handles.canvases)&, decltype(ctx->owner->handles.cvs_by_key)&> {
            return {ctx->owner->handles.canvases, ctx->owner->handles.cvs_by_key};
        });
}

fdl_canvas_t* fdl_context_find_canvas_by_id(fdl_context_t* ctx, const char* id) {
    if (ctx == nullptr || id == nullptr) {
        return nullptr;
    }
    const doc_lock lock(ctx->owner);
    return fdl::detail::child_collection_find<fdl_canvas>(
        ctx->node(),
        "canvases",
        "id",
        id,
        [ctx](uint32_t idx) { return pack_key(ctx->ctx_index, idx); },
        [ctx](uint32_t idx) {
            auto h = std::make_unique<fdl_canvas>();
            h->owner = ctx->owner;
            h->ctx_index = ctx->ctx_index;
            h->cvs_index = idx;
            return h;
        },
        [ctx]() -> std::pair<decltype(ctx->owner->handles.canvases)&, decltype(ctx->owner->handles.cvs_by_key)&> {
            return {ctx->owner->handles.canvases, ctx->owner->handles.cvs_by_key};
        });
}

// -----------------------------------------------------------------------
// Framing decisions (child of canvas)
// -----------------------------------------------------------------------

uint32_t fdl_canvas_framing_decisions_count(const fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return 0;
    }
    const doc_lock lock(canvas->owner);
    return fdl::detail::child_collection_count(canvas->node(), "framing_decisions");
}

fdl_framing_decision_t* fdl_canvas_framing_decision_at(fdl_canvas_t* canvas, uint32_t index) {
    if (canvas == nullptr) {
        return nullptr;
    }
    const doc_lock lock(canvas->owner);
    return fdl::detail::child_collection_at<fdl_framing_decision>(
        canvas->node(),
        "framing_decisions",
        index,
        pack_key3(canvas->ctx_index, canvas->cvs_index, index),
        [canvas](uint32_t idx) {
            auto h = std::make_unique<fdl_framing_decision>();
            h->owner = canvas->owner;
            h->ctx_index = canvas->ctx_index;
            h->cvs_index = canvas->cvs_index;
            h->fd_index = idx;
            return h;
        },
        [canvas]()
            -> std::
                pair<decltype(canvas->owner->handles.framing_decisions)&, decltype(canvas->owner->handles.fd_by_key)&> {
                    return {canvas->owner->handles.framing_decisions, canvas->owner->handles.fd_by_key};
                });
}

fdl_framing_decision_t* fdl_canvas_find_framing_decision_by_id(fdl_canvas_t* canvas, const char* id) {
    if (canvas == nullptr || id == nullptr) {
        return nullptr;
    }
    const doc_lock lock(canvas->owner);
    return fdl::detail::child_collection_find<fdl_framing_decision>(
        canvas->node(),
        "framing_decisions",
        "id",
        id,
        [canvas](uint32_t idx) { return pack_key3(canvas->ctx_index, canvas->cvs_index, idx); },
        [canvas](uint32_t idx) {
            auto h = std::make_unique<fdl_framing_decision>();
            h->owner = canvas->owner;
            h->ctx_index = canvas->ctx_index;
            h->cvs_index = canvas->cvs_index;
            h->fd_index = idx;
            return h;
        },
        [canvas]()
            -> std::
                pair<decltype(canvas->owner->handles.framing_decisions)&, decltype(canvas->owner->handles.fd_by_key)&> {
                    return {canvas->owner->handles.framing_decisions, canvas->owner->handles.fd_by_key};
                });
}

// -----------------------------------------------------------------------
// Canvas resolution
// -----------------------------------------------------------------------

fdl_resolve_canvas_result_t fdl_context_resolve_canvas_for_dimensions(
    fdl_context_t* ctx, fdl_dimensions_f64_t input_dims, fdl_canvas_t* canvas, fdl_framing_decision_t* framing) {

    fdl_resolve_canvas_result_t result = {};

    if (ctx == nullptr || canvas == nullptr || framing == nullptr) {
        result.error = fdl_strdup("NULL argument to fdl_context_resolve_canvas_for_dimensions");
        return result;
    }

    const doc_lock lock(ctx->owner);

    // Get canvas dimensions
    auto* cvs_node = canvas->node();
    if (cvs_node == nullptr || !cvs_node->contains("dimensions")) {
        result.error = fdl_strdup("Canvas has no dimensions");
        return result;
    }
    auto& dims = (*cvs_node)["dimensions"];
    const int64_t cvs_w = dims["width"].as<int64_t>();
    const int64_t cvs_h = dims["height"].as<int64_t>();

    auto input_w = static_cast<int64_t>(input_dims.width);
    auto input_h = static_cast<int64_t>(input_dims.height);

    // Fast path: dimensions already match
    if (cvs_w == input_w && cvs_h == input_h) {
        result.canvas = canvas;
        result.framing_decision = framing;
        result.was_resolved = FDL_FALSE;
        return result;
    }

    // Check if this is a derived canvas (id != source_canvas_id)
    const std::string canvas_id = cvs_node->contains("id") ? (*cvs_node)["id"].as<std::string>() : "";
    const std::string source_id =
        cvs_node->contains("source_canvas_id") ? (*cvs_node)["source_canvas_id"].as<std::string>() : "";

    if (canvas_id != source_id) {
        // Get framing label for matching
        auto* fd_node = framing->node();
        const std::string fd_label =
            (fd_node != nullptr && fd_node->contains("label")) ? (*fd_node)["label"].as<std::string>() : "";

        // Search sibling canvases in this context
        auto* ctx_node = ctx->node();
        if (ctx_node != nullptr && ctx_node->contains("canvases") && (*ctx_node)["canvases"].is_array()) {
            auto& canvases = (*ctx_node)["canvases"];
            auto n = static_cast<uint32_t>(canvases.size());

            for (uint32_t i = 0; i < n; ++i) {
                auto& other = canvases[i];
                if (!other.contains("dimensions")) {
                    continue;
                }

                auto& other_dims = other["dimensions"];
                const int64_t ow = other_dims["width"].as<int64_t>();
                const int64_t oh = other_dims["height"].as<int64_t>();

                if (ow == input_w && oh == input_h) {
                    // Found matching dimensions — search framing decisions by label
                    if (other.contains("framing_decisions") && other["framing_decisions"].is_array()) {
                        auto& fds = other["framing_decisions"];
                        for (uint32_t j = 0; j < fds.size(); ++j) {
                            const std::string other_label =
                                fds[j].contains("label") ? fds[j]["label"].as<std::string>() : "";
                            if (other_label == fd_label) {
                                // Get or create deduped canvas handle
                                const uint64_t cvs_key = pack_key(ctx->ctx_index, i);
                                fdl_canvas_t* matched_cvs;
                                auto cvs_it = ctx->owner->handles.cvs_by_key.find(cvs_key);
                                if (cvs_it != ctx->owner->handles.cvs_by_key.end()) {
                                    matched_cvs = cvs_it->second;
                                } else {
                                    auto h = std::make_unique<fdl_canvas>();
                                    h->owner = ctx->owner;
                                    h->ctx_index = ctx->ctx_index;
                                    h->cvs_index = i;
                                    matched_cvs = h.get();
                                    ctx->owner->handles.canvases.push_back(std::move(h));
                                    ctx->owner->handles.cvs_by_key[cvs_key] = matched_cvs;
                                }

                                // Get or create deduped framing decision handle
                                const uint64_t fd_key = pack_key3(ctx->ctx_index, i, j);
                                fdl_framing_decision_t* matched_fd;
                                auto fd_it = ctx->owner->handles.fd_by_key.find(fd_key);
                                if (fd_it != ctx->owner->handles.fd_by_key.end()) {
                                    matched_fd = fd_it->second;
                                } else {
                                    auto h = std::make_unique<fdl_framing_decision>();
                                    h->owner = ctx->owner;
                                    h->ctx_index = ctx->ctx_index;
                                    h->cvs_index = i;
                                    h->fd_index = j;
                                    matched_fd = h.get();
                                    ctx->owner->handles.framing_decisions.push_back(std::move(h));
                                    ctx->owner->handles.fd_by_key[fd_key] = matched_fd;
                                }

                                result.canvas = matched_cvs;
                                result.framing_decision = matched_fd;
                                result.was_resolved = FDL_TRUE;
                                return result;
                            }
                        }
                    }
                }
            }
        }
    }

    // No match found
    char buf[fdl::constants::kErrorBufferSize];
    snprintf(
        buf,
        sizeof(buf),
        "Canvas dimensions (%" PRId64 "x%" PRId64 ") do not match input dimensions (%" PRId64 "x%" PRId64 ")",
        cvs_w,
        cvs_h,
        input_w,
        input_h);
    result.error = fdl_strdup(buf);
    return result;
}

} // extern "C"
