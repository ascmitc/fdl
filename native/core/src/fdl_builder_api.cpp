// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_builder_api.cpp
 * @brief C ABI wrappers for the document builder (create, add, set, remove operations).
 */
#include "fdl/fdl_core.h"
#include "fdl_builder.h"
#include "fdl_compat.h"
#include "fdl_doc.h"
#include "fdl_enum_map.h"

#include <cstring>
#include <new>
#include <string>

using ojson = jsoncons::ojson;

extern "C" {

// -----------------------------------------------------------------------
// Document-level setters
// -----------------------------------------------------------------------

void fdl_doc_set_uuid(fdl_doc_t* doc, const char* uuid) {
    if (doc == nullptr || uuid == nullptr) {
        return;
    }
    const doc_lock lock(doc);
    doc->doc.data().insert_or_assign("uuid", uuid);
}

void fdl_doc_set_fdl_creator(fdl_doc_t* doc, const char* creator) {
    if (doc == nullptr || creator == nullptr) {
        return;
    }
    const doc_lock lock(doc);
    doc->doc.data().insert_or_assign("fdl_creator", creator);
}

void fdl_doc_set_default_framing_intent(fdl_doc_t* doc, const char* fi_id) {
    if (doc == nullptr) {
        return;
    }
    const doc_lock lock(doc);
    if (fi_id != nullptr) {
        doc->doc.data().insert_or_assign("default_framing_intent", fi_id);
    }
}

void fdl_doc_set_version(fdl_doc_t* doc, int major, int minor) {
    if (doc == nullptr) {
        return;
    }
    const doc_lock lock(doc);
    doc->doc.data().insert_or_assign("version", fdl::detail::make_version(major, minor));
}

// -----------------------------------------------------------------------
// Initialize a new document with canonical structure
// -----------------------------------------------------------------------

fdl_doc_t* fdl_doc_create_with_header(
    const char* uuid,
    int version_major,
    int version_minor,
    const char* fdl_creator,
    const char* default_framing_intent) {
    if (uuid == nullptr || fdl_creator == nullptr) {
        return nullptr;
    }

    auto* doc = new (std::nothrow) fdl_doc{};
    if (doc == nullptr) {
        return nullptr;
    }

    doc->doc = fdl::detail::Document(
        fdl::detail::make_root(uuid, version_major, version_minor, fdl_creator, default_framing_intent));
    return doc;
}

// -----------------------------------------------------------------------
// Adding sub-objects
// -----------------------------------------------------------------------

fdl_framing_intent_t* fdl_doc_add_framing_intent(
    fdl_doc_t* doc, const char* id, const char* label, int64_t aspect_w, int64_t aspect_h, double protection) {
    if (doc == nullptr || id == nullptr) {
        return nullptr;
    }

    const doc_lock lock(doc);
    auto& data = doc->doc.data();
    if (!data.contains("framing_intents")) {
        data.insert_or_assign("framing_intents", ojson(jsoncons::json_array_arg));
    }

    auto fi = fdl::detail::make_framing_intent(id, label, aspect_w, aspect_h, protection);
    auto& fi_arr = data["framing_intents"];
    auto index = static_cast<uint32_t>(fi_arr.size());
    fi_arr.push_back(std::move(fi));
    auto handle = std::make_unique<fdl_framing_intent>();
    handle->owner = doc;
    handle->fi_index = index;
    auto* ptr = handle.get();
    doc->handles.framing_intents.push_back(std::move(handle));
    doc->handles.fi_by_index[index] = ptr;
    return ptr;
}

fdl_context_t* fdl_doc_add_context(fdl_doc_t* doc, const char* label, const char* context_creator) {
    if (doc == nullptr) {
        return nullptr;
    }

    const doc_lock lock(doc);
    auto& data = doc->doc.data();
    if (!data.contains("contexts")) {
        data.insert_or_assign("contexts", ojson(jsoncons::json_array_arg));
    }

    auto ctx = fdl::detail::make_context(label, context_creator);
    auto& ctx_arr = data["contexts"];
    auto index = static_cast<uint32_t>(ctx_arr.size());
    ctx_arr.push_back(std::move(ctx));
    auto handle = std::make_unique<fdl_context>();
    handle->owner = doc;
    handle->ctx_index = index;
    auto* ptr = handle.get();
    doc->handles.contexts.push_back(std::move(handle));
    doc->handles.ctx_by_index[index] = ptr;
    return ptr;
}

fdl_canvas_t* fdl_context_add_canvas(
    fdl_context_t* ctx,
    const char* id,
    const char* label,
    const char* source_canvas_id,
    int64_t dim_w,
    int64_t dim_h,
    double squeeze) {
    if (ctx == nullptr || id == nullptr || source_canvas_id == nullptr) {
        return nullptr;
    }

    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr) {
        return nullptr;
    }

    if (!n->contains("canvases")) {
        n->insert_or_assign("canvases", ojson(jsoncons::json_array_arg));
    }

    auto canvas = fdl::detail::make_canvas(id, label, source_canvas_id, dim_w, dim_h, squeeze);
    auto& cvs_arr = (*n)["canvases"];
    auto cvs_index = static_cast<uint32_t>(cvs_arr.size());
    cvs_arr.push_back(std::move(canvas));
    auto handle = std::make_unique<fdl_canvas>();
    handle->owner = ctx->owner;
    handle->ctx_index = ctx->ctx_index;
    handle->cvs_index = cvs_index;
    auto* ptr = handle.get();
    ctx->owner->handles.canvases.push_back(std::move(handle));
    ctx->owner->handles.cvs_by_key[pack_key(ctx->ctx_index, cvs_index)] = ptr;
    return ptr;
}

void fdl_canvas_set_effective_dimensions(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims, fdl_point_f64_t anchor) {
    if (canvas == nullptr) {
        return;
    }

    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("effective_dimensions", fdl::detail::make_dimensions_int(dims.width, dims.height));
    n->insert_or_assign("effective_anchor_point", fdl::detail::make_point_float(anchor.x, anchor.y));
}

void fdl_canvas_set_photosite_dimensions(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims) {
    if (canvas == nullptr) {
        return;
    }

    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("photosite_dimensions", fdl::detail::make_dimensions_int(dims.width, dims.height));
}

void fdl_canvas_set_physical_dimensions(fdl_canvas_t* canvas, fdl_dimensions_f64_t dims) {
    if (canvas == nullptr) {
        return;
    }

    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("physical_dimensions", fdl::detail::make_dimensions_float(dims.width, dims.height));
}

fdl_framing_decision_t* fdl_canvas_add_framing_decision(
    fdl_canvas_t* canvas,
    const char* id,
    const char* label,
    const char* framing_intent_id,
    double dim_w,
    double dim_h,
    double anchor_x,
    double anchor_y) {
    if (canvas == nullptr || id == nullptr || framing_intent_id == nullptr) {
        return nullptr;
    }

    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return nullptr;
    }

    if (!n->contains("framing_decisions")) {
        n->insert_or_assign("framing_decisions", ojson(jsoncons::json_array_arg));
    }

    auto fd = fdl::detail::make_framing_decision(id, label, framing_intent_id, dim_w, dim_h, anchor_x, anchor_y);
    auto& fd_arr = (*n)["framing_decisions"];
    auto fd_index = static_cast<uint32_t>(fd_arr.size());
    fd_arr.push_back(std::move(fd));
    auto handle = std::make_unique<fdl_framing_decision>();
    handle->owner = canvas->owner;
    handle->ctx_index = canvas->ctx_index;
    handle->cvs_index = canvas->cvs_index;
    handle->fd_index = fd_index;
    auto* ptr = handle.get();
    canvas->owner->handles.framing_decisions.push_back(std::move(handle));
    canvas->owner->handles.fd_by_key[pack_key3(canvas->ctx_index, canvas->cvs_index, fd_index)] = ptr;
    return ptr;
}

void fdl_framing_decision_set_protection(
    fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims, fdl_point_f64_t anchor) {
    if (fd == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("protection_dimensions", fdl::detail::make_dimensions_float(dims.width, dims.height));
    n->insert_or_assign("protection_anchor_point", fdl::detail::make_point_float(anchor.x, anchor.y));
}

// -----------------------------------------------------------------------
// Canvas template builder + setters
// -----------------------------------------------------------------------

fdl_canvas_template_t* fdl_doc_add_canvas_template(
    fdl_doc_t* doc,
    const char* id,
    const char* label,
    int64_t target_w,
    int64_t target_h,
    double target_squeeze,
    fdl_geometry_path_t fit_source,
    fdl_fit_method_t fit_method,
    fdl_halign_t halign,
    fdl_valign_t valign,
    fdl_round_strategy_t rounding) {
    if (doc == nullptr || id == nullptr) {
        return nullptr;
    }

    const doc_lock lock(doc);
    auto& data = doc->doc.data();
    if (!data.contains("canvas_templates")) {
        data.insert_or_assign("canvas_templates", ojson(jsoncons::json_array_arg));
    }

    auto ct = fdl::detail::make_canvas_template(
        id, label, target_w, target_h, target_squeeze, fit_source, fit_method, halign, valign, rounding);
    auto& ct_arr = data["canvas_templates"];
    auto index = static_cast<uint32_t>(ct_arr.size());
    ct_arr.push_back(std::move(ct));
    auto handle = std::make_unique<fdl_canvas_template>();
    handle->owner = doc;
    handle->ct_index = index;
    auto* ptr = handle.get();
    doc->handles.canvas_templates.push_back(std::move(handle));
    doc->handles.ct_by_index[index] = ptr;
    return ptr;
}

void fdl_canvas_template_set_preserve_from_source_canvas(fdl_canvas_template_t* ct, fdl_geometry_path_t path) {
    if (ct == nullptr) {
        return;
    }

    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("preserve_from_source_canvas", fdl::detail::geometry_path_to_string(path));
}

void fdl_canvas_template_set_maximum_dimensions(fdl_canvas_template_t* ct, fdl_dimensions_i64_t dims) {
    if (ct == nullptr) {
        return;
    }

    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("maximum_dimensions", fdl::detail::make_dimensions_int(dims.width, dims.height));
}

void fdl_canvas_template_set_pad_to_maximum(fdl_canvas_template_t* ct, int pad) {
    if (ct == nullptr) {
        return;
    }

    const doc_lock lock(ct->owner);
    auto* n = ct->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("pad_to_maximum", pad != 0);
}

// -----------------------------------------------------------------------
// FramingIntent setters
// -----------------------------------------------------------------------

void fdl_framing_intent_set_aspect_ratio(fdl_framing_intent_t* fi, fdl_dimensions_i64_t dims) {
    if (fi == nullptr) {
        return;
    }

    const doc_lock lock(fi->owner);
    auto* n = fi->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("aspect_ratio", fdl::detail::make_dimensions_int(dims.width, dims.height));
}

void fdl_framing_intent_set_protection(fdl_framing_intent_t* fi, double protection) {
    if (fi == nullptr) {
        return;
    }

    const doc_lock lock(fi->owner);
    auto* n = fi->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("protection", protection);
}

// -----------------------------------------------------------------------
// Canvas setters
// -----------------------------------------------------------------------

void fdl_canvas_set_dimensions(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims) {
    if (canvas == nullptr) {
        return;
    }

    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("dimensions", fdl::detail::make_dimensions_int(dims.width, dims.height));
}

void fdl_canvas_set_anamorphic_squeeze(fdl_canvas_t* canvas, double squeeze) {
    if (canvas == nullptr) {
        return;
    }

    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("anamorphic_squeeze", squeeze);
}

void fdl_canvas_set_effective_dims_only(fdl_canvas_t* canvas, fdl_dimensions_i64_t dims) {
    if (canvas == nullptr) {
        return;
    }

    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("effective_dimensions", fdl::detail::make_dimensions_int(dims.width, dims.height));
    if (!n->contains("effective_anchor_point")) {
        n->insert_or_assign("effective_anchor_point", fdl::detail::make_point_float(0.0, 0.0));
    }
}

void fdl_canvas_remove_effective(fdl_canvas_t* canvas) {
    if (canvas == nullptr) {
        return;
    }

    const doc_lock lock(canvas->owner);
    auto* n = canvas->node();
    if (n == nullptr) {
        return;
    }

    n->erase("effective_dimensions");
    n->erase("effective_anchor_point");
}

// -----------------------------------------------------------------------
// FramingDecision individual setters
// -----------------------------------------------------------------------

void fdl_framing_decision_set_dimensions(fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims) {
    if (fd == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("dimensions", fdl::detail::make_dimensions_float(dims.width, dims.height));
}

void fdl_framing_decision_set_anchor_point(fdl_framing_decision_t* fd, fdl_point_f64_t point) {
    if (fd == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("anchor_point", fdl::detail::make_point_float(point.x, point.y));
}

void fdl_framing_decision_set_protection_dimensions(fdl_framing_decision_t* fd, fdl_dimensions_f64_t dims) {
    if (fd == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("protection_dimensions", fdl::detail::make_dimensions_float(dims.width, dims.height));
}

void fdl_framing_decision_set_protection_anchor_point(fdl_framing_decision_t* fd, fdl_point_f64_t point) {
    if (fd == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return;
    }

    n->insert_or_assign("protection_anchor_point", fdl::detail::make_point_float(point.x, point.y));
}

void fdl_framing_decision_remove_protection(fdl_framing_decision_t* fd) {
    if (fd == nullptr) {
        return;
    }

    const doc_lock lock(fd->owner);
    auto* n = fd->node();
    if (n == nullptr) {
        return;
    }

    n->erase("protection_dimensions");
    n->erase("protection_anchor_point");
}

// -----------------------------------------------------------------------
// clip_id validation and setter
// -----------------------------------------------------------------------

const char* fdl_clip_id_validate_json(const char* json_str, size_t json_len) {
    if (json_str == nullptr) {
        return fdl_strdup("json_str is NULL");
    }

    ojson obj;
    try {
        obj = ojson::parse(jsoncons::string_view(json_str, json_len));
    } catch (const std::exception& e) {
        return fdl_strdup((std::string("Invalid JSON: ") + e.what()).c_str());
    }

    if (!obj.is_object()) {
        return fdl_strdup("clip_id must be a JSON object");
    }

    if (obj.contains("file") && obj.contains("sequence")) {
        return fdl_strdup("Both file and sequence attributes are provided, only one is allowed.");
    }

    return nullptr;
}

const char* fdl_context_set_clip_id_json(fdl_context_t* ctx, const char* json_str, size_t json_len) {
    if (ctx == nullptr) {
        return fdl_strdup("context handle is NULL");
    }

    const char* err = fdl_clip_id_validate_json(json_str, json_len);
    if (err != nullptr) {
        return err;
    }

    ojson obj;
    try {
        obj = ojson::parse(jsoncons::string_view(json_str, json_len));
    } catch (const std::exception& e) {
        return fdl_strdup((std::string("Invalid JSON: ") + e.what()).c_str());
    }

    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr) {
        return fdl_strdup("context handle is invalid");
    }

    n->insert_or_assign("clip_id", std::move(obj));
    return nullptr;
}

void fdl_context_remove_clip_id(fdl_context_t* ctx) {
    if (ctx == nullptr) {
        return;
    }

    const doc_lock lock(ctx->owner);
    auto* n = ctx->node();
    if (n == nullptr) {
        return;
    }

    n->erase("clip_id");
}

} // extern "C"
