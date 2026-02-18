// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_handles.cpp
 * @brief Handle node() resolution -- lazy index-based lookup into the document ojson tree.
 */
#include "fdl_handles.h"
#include "fdl_doc.h"

using ojson = jsoncons::ojson;

ojson* fdl_framing_intent::node() const {
    if (owner == nullptr) {
        return nullptr;
    }
    auto& data = owner->doc.data();
    if (!data.contains("framing_intents")) {
        return nullptr;
    }
    auto& arr = data["framing_intents"];
    return fi_index < arr.size() ? &arr[fi_index] : nullptr;
}

ojson* fdl_context::node() const {
    if (owner == nullptr) {
        return nullptr;
    }
    auto& data = owner->doc.data();
    if (!data.contains("contexts")) {
        return nullptr;
    }
    auto& arr = data["contexts"];
    return ctx_index < arr.size() ? &arr[ctx_index] : nullptr;
}

ojson* fdl_canvas_template::node() const {
    if (owner == nullptr) {
        return nullptr;
    }
    auto& data = owner->doc.data();
    if (!data.contains("canvas_templates")) {
        return nullptr;
    }
    auto& arr = data["canvas_templates"];
    return ct_index < arr.size() ? &arr[ct_index] : nullptr;
}

ojson* fdl_canvas::node() const {
    if (owner == nullptr) {
        return nullptr;
    }
    auto& data = owner->doc.data();
    if (!data.contains("contexts")) {
        return nullptr;
    }
    auto& ctxs = data["contexts"];
    if (ctx_index >= ctxs.size()) {
        return nullptr;
    }
    auto& ctx = ctxs[ctx_index];
    if (!ctx.contains("canvases")) {
        return nullptr;
    }
    auto& arr = ctx["canvases"];
    return cvs_index < arr.size() ? &arr[cvs_index] : nullptr;
}

ojson* fdl_framing_decision::node() const {
    if (owner == nullptr) {
        return nullptr;
    }
    auto& data = owner->doc.data();
    if (!data.contains("contexts")) {
        return nullptr;
    }
    auto& ctxs = data["contexts"];
    if (ctx_index >= ctxs.size()) {
        return nullptr;
    }
    auto& ctx = ctxs[ctx_index];
    if (!ctx.contains("canvases")) {
        return nullptr;
    }
    auto& cvss = ctx["canvases"];
    if (cvs_index >= cvss.size()) {
        return nullptr;
    }
    auto& cvs = cvss[cvs_index];
    if (!cvs.contains("framing_decisions")) {
        return nullptr;
    }
    auto& arr = cvs["framing_decisions"];
    return fd_index < arr.size() ? &arr[fd_index] : nullptr;
}

ojson* fdl_clip_id::node() const {
    if (owner == nullptr) {
        return nullptr;
    }
    auto& data = owner->doc.data();
    if (!data.contains("contexts")) {
        return nullptr;
    }
    auto& ctxs = data["contexts"];
    if (ctx_index >= ctxs.size()) {
        return nullptr;
    }
    auto& ctx = ctxs[ctx_index];
    if (!ctx.contains("clip_id")) {
        return nullptr;
    }
    return &ctx["clip_id"];
}

ojson* fdl_file_sequence::node() const {
    if (owner == nullptr) {
        return nullptr;
    }
    auto& data = owner->doc.data();
    if (!data.contains("contexts")) {
        return nullptr;
    }
    auto& ctxs = data["contexts"];
    if (ctx_index >= ctxs.size()) {
        return nullptr;
    }
    auto& ctx = ctxs[ctx_index];
    if (!ctx.contains("clip_id")) {
        return nullptr;
    }
    auto& cid = ctx["clip_id"];
    if (!cid.contains("sequence")) {
        return nullptr;
    }
    return &cid["sequence"];
}
