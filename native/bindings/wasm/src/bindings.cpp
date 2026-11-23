// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file bindings.cpp
 * @brief Emscripten Embind bindings exposing the fdl_core C ABI to JavaScript.
 *
 * Each registered function carries the same name as the underlying C function
 * (e.g. fdl_doc_create), so JavaScript can call the WASM module the same way
 * it calls the N-API addon.  Opaque handles are passed as plain JS objects
 * { __ptr: <number> }; value-type structs are plain JS objects whose property
 * names match the N-API path produced by structs.h.
 */

#include "fdl/fdl_core.h"
#include <cstdint>
#include <emscripten.h>
#include <emscripten/bind.h>
#include <emscripten/val.h>
#include <string>

using emscripten::val;

// Throw a real JS Error from C++ so non-nullable NULL returns surface the same
// way as the N-API addon (a catchable Error with a message), rather than an
// opaque value. Defined via EM_JS so it works under -sDYNAMIC_EXECUTION=0.
EM_JS(void, fdl_throw_js_error, (const char* msg), { throw new Error(UTF8ToString(msg)); });

// ----------------------------------------------------------------------------
// Handle wrap / unwrap
// ----------------------------------------------------------------------------

template<typename T> static T* unwrap_handle(const val& v) {
    if (v.isNull() || v.isUndefined()) {
        return nullptr;
    }
    return reinterpret_cast<T*>(v["__ptr"].as<uintptr_t>());
}

template<typename T> static val wrap_handle(T* p) {
    if (!p) {
        return val::null();
    }
    auto o = val::object();
    o.set("__ptr", static_cast<uintptr_t>(reinterpret_cast<uintptr_t>(p)));
    return o;
}

static const char* val_to_cstr_or_null(const val& v, std::string& buf) {
    if (v.isNull() || v.isUndefined()) {
        return nullptr;
    }
    buf = v.as<std::string>();
    return buf.c_str();
}

// ----------------------------------------------------------------------------
// Struct <-> val helpers
// ----------------------------------------------------------------------------

static val to_val_AbiVersion(const fdl_abi_version_t& d) {
    auto o = val::object();
    o.set("major", emscripten::val(static_cast<double>(d.major)));
    o.set("minor", emscripten::val(static_cast<double>(d.minor)));
    o.set("patch", emscripten::val(static_cast<double>(d.patch)));
    return o;
}

static val to_val_DimensionsI64(const fdl_dimensions_i64_t& d) {
    auto o = val::object();
    o.set("width", emscripten::val(static_cast<double>(d.width)));
    o.set("height", emscripten::val(static_cast<double>(d.height)));
    return o;
}

static fdl_dimensions_i64_t from_val_DimensionsI64(const val& v) {
    fdl_dimensions_i64_t d{};
    d.width = static_cast<int64_t>(v["width"].as<double>());
    d.height = static_cast<int64_t>(v["height"].as<double>());
    return d;
}

static val to_val_DimensionsF64(const fdl_dimensions_f64_t& d) {
    auto o = val::object();
    o.set("width", emscripten::val(d.width));
    o.set("height", emscripten::val(d.height));
    return o;
}

static fdl_dimensions_f64_t from_val_DimensionsF64(const val& v) {
    fdl_dimensions_f64_t d{};
    d.width = v["width"].as<double>();
    d.height = v["height"].as<double>();
    return d;
}

static val to_val_PointF64(const fdl_point_f64_t& d) {
    auto o = val::object();
    o.set("x", emscripten::val(d.x));
    o.set("y", emscripten::val(d.y));
    return o;
}

static fdl_point_f64_t from_val_PointF64(const val& v) {
    fdl_point_f64_t d{};
    d.x = v["x"].as<double>();
    d.y = v["y"].as<double>();
    return d;
}

static val to_val_Rect(const fdl_rect_t& d) {
    auto o = val::object();
    o.set("x", emscripten::val(d.x));
    o.set("y", emscripten::val(d.y));
    o.set("width", emscripten::val(d.width));
    o.set("height", emscripten::val(d.height));
    return o;
}

static val to_val_RoundStrategy(const fdl_round_strategy_t& d) {
    auto o = val::object();
    o.set("even", emscripten::val(static_cast<unsigned>(d.even)));
    o.set("mode", emscripten::val(static_cast<unsigned>(d.mode)));
    return o;
}

static fdl_round_strategy_t from_val_RoundStrategy(const val& v) {
    fdl_round_strategy_t d{};
    d.even = static_cast<fdl_rounding_even_t>(v["even"].as<unsigned>());
    d.mode = static_cast<fdl_rounding_mode_t>(v["mode"].as<unsigned>());
    return d;
}

static val to_val_ParseResult(const fdl_parse_result_t& d) {
    auto o = val::object();
    o.set("doc", wrap_handle(d.doc));
    o.set("error", (d.error ? emscripten::val(std::string(d.error)) : emscripten::val::null()));
    return o;
}

static val to_val_TemplateResult(const fdl_template_result_t& d) {
    auto o = val::object();
    o.set("output_fdl", wrap_handle(d.output_fdl));
    o.set("context_label", (d.context_label ? emscripten::val(std::string(d.context_label)) : emscripten::val::null()));
    o.set("canvas_id", (d.canvas_id ? emscripten::val(std::string(d.canvas_id)) : emscripten::val::null()));
    o.set(
        "framing_decision_id",
        (d.framing_decision_id ? emscripten::val(std::string(d.framing_decision_id)) : emscripten::val::null()));
    o.set("error", (d.error ? emscripten::val(std::string(d.error)) : emscripten::val::null()));
    return o;
}

static val to_val_ResolveCanvasResult(const fdl_resolve_canvas_result_t& d) {
    auto o = val::object();
    o.set("canvas", wrap_handle(d.canvas));
    o.set("framing_decision", wrap_handle(d.framing_decision));
    o.set("was_resolved", emscripten::val(static_cast<double>(d.was_resolved)));
    o.set("error", (d.error ? emscripten::val(std::string(d.error)) : emscripten::val::null()));
    return o;
}

static val to_val_Geometry(const fdl_geometry_t& d) {
    auto o = val::object();
    o.set("canvas_dims", to_val_DimensionsF64(d.canvas_dims));
    o.set("effective_dims", to_val_DimensionsF64(d.effective_dims));
    o.set("protection_dims", to_val_DimensionsF64(d.protection_dims));
    o.set("framing_dims", to_val_DimensionsF64(d.framing_dims));
    o.set("effective_anchor", to_val_PointF64(d.effective_anchor));
    o.set("protection_anchor", to_val_PointF64(d.protection_anchor));
    o.set("framing_anchor", to_val_PointF64(d.framing_anchor));
    return o;
}

static fdl_geometry_t from_val_Geometry(const val& v) {
    fdl_geometry_t d{};
    d.canvas_dims = from_val_DimensionsF64(v["canvas_dims"]);
    d.effective_dims = from_val_DimensionsF64(v["effective_dims"]);
    d.protection_dims = from_val_DimensionsF64(v["protection_dims"]);
    d.framing_dims = from_val_DimensionsF64(v["framing_dims"]);
    d.effective_anchor = from_val_PointF64(v["effective_anchor"]);
    d.protection_anchor = from_val_PointF64(v["protection_anchor"]);
    d.framing_anchor = from_val_PointF64(v["framing_anchor"]);
    return d;
}

static val to_val_FromIntentResult(const fdl_from_intent_result_t& d) {
    auto o = val::object();
    o.set("dimensions", to_val_DimensionsF64(d.dimensions));
    o.set("anchor_point", to_val_PointF64(d.anchor_point));
    o.set("has_protection", emscripten::val(static_cast<double>(d.has_protection)));
    o.set("protection_dimensions", to_val_DimensionsF64(d.protection_dimensions));
    o.set("protection_anchor_point", to_val_PointF64(d.protection_anchor_point));
    return o;
}

// ----------------------------------------------------------------------------
// Function bindings
// ----------------------------------------------------------------------------

EMSCRIPTEN_BINDINGS(fdl_core_bindings) {
    // fdl_abi_version — Return the ABI version of the loaded library.
    emscripten::function("fdl_abi_version", emscripten::optional_override([]() -> val {
                             fdl_abi_version_t _r = fdl_abi_version();
                             auto _out = to_val_AbiVersion(_r);
                             return _out;
                         }));

    // fdl_alignment_shift — Calculate content translation shift for a single axis.
    emscripten::function(
        "fdl_alignment_shift",
        emscripten::optional_override(
            [](double fit_size,
               double fit_anchor,
               double output_size,
               double canvas_size,
               double target_size,
               int is_center,
               double align_factor,
               int pad_to_max) -> val {
                auto _r = fdl_alignment_shift(
                    fit_size, fit_anchor, output_size, canvas_size, target_size, is_center, align_factor, pad_to_max);
                return val(static_cast<double>(_r));
            }));

    // fdl_apply_canvas_template — Apply a canvas template to a source canvas/framing.
    emscripten::function(
        "fdl_apply_canvas_template",
        emscripten::optional_override(
            [](emscripten::val tmpl_v,
               emscripten::val source_canvas_v,
               emscripten::val source_framing_v,
               std::string new_canvas_id_str,
               std::string new_fd_name_str,
               emscripten::val source_context_label_v,
               emscripten::val context_creator_v) -> val {
                auto* tmpl = unwrap_handle<fdl_canvas_template_t>(tmpl_v);
                auto* source_canvas = unwrap_handle<fdl_canvas_t>(source_canvas_v);
                auto* source_framing = unwrap_handle<fdl_framing_decision_t>(source_framing_v);
                std::string source_context_label_buf;
                const char* source_context_label =
                    val_to_cstr_or_null(source_context_label_v, source_context_label_buf);
                std::string context_creator_buf;
                const char* context_creator = val_to_cstr_or_null(context_creator_v, context_creator_buf);
                fdl_template_result_t _r = fdl_apply_canvas_template(
                    tmpl,
                    source_canvas,
                    source_framing,
                    new_canvas_id_str.c_str(),
                    new_fd_name_str.c_str(),
                    source_context_label,
                    context_creator);
                auto _out = to_val_TemplateResult(_r);
                if (_r.context_label) {
                    fdl_free(const_cast<char*>(_r.context_label));
                }
                if (_r.canvas_id) {
                    fdl_free(const_cast<char*>(_r.canvas_id));
                }
                if (_r.framing_decision_id) {
                    fdl_free(const_cast<char*>(_r.framing_decision_id));
                }
                if (_r.error) {
                    fdl_free(const_cast<char*>(_r.error));
                }
                return _out;
            }));

    // fdl_calculate_scale_factor — Calculate scale factor based on fit method.
    emscripten::function(
        "fdl_calculate_scale_factor",
        emscripten::optional_override(
            [](emscripten::val fit_norm_v, emscripten::val target_norm_v, unsigned fit_method_i) -> val {
                fdl_dimensions_f64_t fit_norm = from_val_DimensionsF64(fit_norm_v);
                fdl_dimensions_f64_t target_norm = from_val_DimensionsF64(target_norm_v);
                fdl_fit_method_t fit_method = static_cast<fdl_fit_method_t>(fit_method_i);
                auto _r = fdl_calculate_scale_factor(fit_norm, target_norm, fit_method);
                return val(static_cast<double>(_r));
            }));

    // fdl_canvas_add_framing_decision — Add a framing decision to a canvas.
    emscripten::function(
        "fdl_canvas_add_framing_decision",
        emscripten::optional_override(
            [](emscripten::val canvas_v,
               std::string id_str,
               std::string label_str,
               std::string framing_intent_id_str,
               double dim_w,
               double dim_h,
               double anchor_x,
               double anchor_y) -> val {
                auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                auto* _r = fdl_canvas_add_framing_decision(
                    canvas,
                    id_str.c_str(),
                    label_str.c_str(),
                    framing_intent_id_str.c_str(),
                    dim_w,
                    dim_h,
                    anchor_x,
                    anchor_y);
                return wrap_handle(_r);
            }));

    // fdl_canvas_find_framing_decision_by_id — Find a framing decision by its ID within a canvas.
    emscripten::function(
        "fdl_canvas_find_framing_decision_by_id",
        emscripten::optional_override([](emscripten::val canvas_v, std::string id_str) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto* _r = fdl_canvas_find_framing_decision_by_id(canvas, id_str.c_str());
            return wrap_handle(_r);
        }));

    // fdl_canvas_framing_decision_at — Get a framing decision by index within a canvas.
    emscripten::function(
        "fdl_canvas_framing_decision_at",
        emscripten::optional_override([](emscripten::val canvas_v, uint32_t index) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto* _r = fdl_canvas_framing_decision_at(canvas, index);
            return wrap_handle(_r);
        }));

    // fdl_canvas_framing_decisions_count — Get the number of framing decisions in a canvas.
    emscripten::function(
        "fdl_canvas_framing_decisions_count", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto _r = fdl_canvas_framing_decisions_count(canvas);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_get_anamorphic_squeeze — Get the anamorphic squeeze factor.
    emscripten::function(
        "fdl_canvas_get_anamorphic_squeeze", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto _r = fdl_canvas_get_anamorphic_squeeze(canvas);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_get_dimensions — Get the canvas dimensions in pixels.
    emscripten::function(
        "fdl_canvas_get_dimensions", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_dimensions_i64_t _r = fdl_canvas_get_dimensions(canvas);
            auto _out = to_val_DimensionsI64(_r);
            return _out;
        }));

    // fdl_canvas_get_effective_anchor_point — Get the effective anchor point (offset from canvas origin).
    emscripten::function(
        "fdl_canvas_get_effective_anchor_point", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_point_f64_t _r = fdl_canvas_get_effective_anchor_point(canvas);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_canvas_get_effective_dimensions — Get effective (active image area) dimensions.
    emscripten::function(
        "fdl_canvas_get_effective_dimensions", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_dimensions_i64_t _r = fdl_canvas_get_effective_dimensions(canvas);
            auto _out = to_val_DimensionsI64(_r);
            return _out;
        }));

    // fdl_canvas_get_effective_rect — Get the effective (active image) rect of a canvas.
    emscripten::function(
        "fdl_canvas_get_effective_rect", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_rect_t out_rect{};
            auto _r = fdl_canvas_get_effective_rect(canvas, &out_rect);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("rect", to_val_Rect(out_rect));
            return _out;
        }));

    // fdl_canvas_get_id — Get the ID of a canvas.
    emscripten::function("fdl_canvas_get_id", emscripten::optional_override([](emscripten::val canvas_v) -> val {
                             auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                             const char* _r = fdl_canvas_get_id(canvas);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_canvas_get_label — Get the label of a canvas.
    emscripten::function("fdl_canvas_get_label", emscripten::optional_override([](emscripten::val canvas_v) -> val {
                             auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                             const char* _r = fdl_canvas_get_label(canvas);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_canvas_get_photosite_dimensions — Get photosite (sensor) dimensions.
    emscripten::function(
        "fdl_canvas_get_photosite_dimensions", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_dimensions_i64_t _r = fdl_canvas_get_photosite_dimensions(canvas);
            auto _out = to_val_DimensionsI64(_r);
            return _out;
        }));

    // fdl_canvas_get_physical_dimensions — Get physical dimensions (e.g. millimeters on sensor).
    emscripten::function(
        "fdl_canvas_get_physical_dimensions", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_dimensions_f64_t _r = fdl_canvas_get_physical_dimensions(canvas);
            auto _out = to_val_DimensionsF64(_r);
            return _out;
        }));

    // fdl_canvas_get_rect — Get the full canvas rect: (0, 0, dims.width, dims.height).
    emscripten::function("fdl_canvas_get_rect", emscripten::optional_override([](emscripten::val canvas_v) -> val {
                             auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                             fdl_rect_t _r = fdl_canvas_get_rect(canvas);
                             auto _out = to_val_Rect(_r);
                             return _out;
                         }));

    // fdl_canvas_get_source_canvas_id — Get the source_canvas_id of a canvas (the canvas this was derived from).
    emscripten::function(
        "fdl_canvas_get_source_canvas_id", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            const char* _r = fdl_canvas_get_source_canvas_id(canvas);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_canvas_has_effective_dimensions — Check if the canvas has effective dimensions set.
    emscripten::function(
        "fdl_canvas_has_effective_dimensions", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto _r = fdl_canvas_has_effective_dimensions(canvas);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_has_photosite_dimensions — Check if the canvas has photosite dimensions set.
    emscripten::function(
        "fdl_canvas_has_photosite_dimensions", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto _r = fdl_canvas_has_photosite_dimensions(canvas);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_has_physical_dimensions — Check if the canvas has physical dimensions set.
    emscripten::function(
        "fdl_canvas_has_physical_dimensions", emscripten::optional_override([](emscripten::val canvas_v) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto _r = fdl_canvas_has_physical_dimensions(canvas);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_remove_effective — Remove effective dimensions and anchor from a canvas.
    emscripten::function(
        "fdl_canvas_remove_effective", emscripten::optional_override([](emscripten::val canvas_v) -> void {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_canvas_remove_effective(canvas);
            return;
        }));

    // fdl_canvas_set_anamorphic_squeeze — Set anamorphic squeeze on a canvas.
    emscripten::function(
        "fdl_canvas_set_anamorphic_squeeze",
        emscripten::optional_override([](emscripten::val canvas_v, double squeeze) -> void {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_canvas_set_anamorphic_squeeze(canvas, squeeze);
            return;
        }));

    // fdl_canvas_set_dimensions — Set dimensions on a canvas.
    emscripten::function(
        "fdl_canvas_set_dimensions",
        emscripten::optional_override([](emscripten::val canvas_v, emscripten::val dims_v) -> void {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_dimensions_i64_t dims = from_val_DimensionsI64(dims_v);
            fdl_canvas_set_dimensions(canvas, dims);
            return;
        }));

    // fdl_canvas_set_effective_dimensions — Set effective dimensions and anchor on a canvas.
    emscripten::function(
        "fdl_canvas_set_effective_dimensions",
        emscripten::optional_override(
            [](emscripten::val canvas_v, emscripten::val dims_v, emscripten::val anchor_v) -> void {
                auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                fdl_dimensions_i64_t dims = from_val_DimensionsI64(dims_v);
                fdl_point_f64_t anchor = from_val_PointF64(anchor_v);
                fdl_canvas_set_effective_dimensions(canvas, dims, anchor);
                return;
            }));

    // fdl_canvas_set_effective_dims_only — Set effective dimensions on a canvas.
    emscripten::function(
        "fdl_canvas_set_effective_dims_only",
        emscripten::optional_override([](emscripten::val canvas_v, emscripten::val dims_v) -> void {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_dimensions_i64_t dims = from_val_DimensionsI64(dims_v);
            fdl_canvas_set_effective_dims_only(canvas, dims);
            return;
        }));

    // fdl_canvas_set_photosite_dimensions — Set photosite dimensions on a canvas.
    emscripten::function(
        "fdl_canvas_set_photosite_dimensions",
        emscripten::optional_override([](emscripten::val canvas_v, emscripten::val dims_v) -> void {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_dimensions_i64_t dims = from_val_DimensionsI64(dims_v);
            fdl_canvas_set_photosite_dimensions(canvas, dims);
            return;
        }));

    // fdl_canvas_set_physical_dimensions — Set physical dimensions on a canvas.
    emscripten::function(
        "fdl_canvas_set_physical_dimensions",
        emscripten::optional_override([](emscripten::val canvas_v, emscripten::val dims_v) -> void {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
            fdl_canvas_set_physical_dimensions(canvas, dims);
            return;
        }));

    // fdl_canvas_template_get_alignment_method_horizontal — Get the horizontal alignment method.
    emscripten::function(
        "fdl_canvas_template_get_alignment_method_horizontal",
        emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_get_alignment_method_horizontal(ct);
            return val(static_cast<unsigned>(_r));
        }));

    // fdl_canvas_template_get_alignment_method_vertical — Get the vertical alignment method.
    emscripten::function(
        "fdl_canvas_template_get_alignment_method_vertical",
        emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_get_alignment_method_vertical(ct);
            return val(static_cast<unsigned>(_r));
        }));

    // fdl_canvas_template_get_fit_method — Get the fit method — how source is scaled into target.
    emscripten::function(
        "fdl_canvas_template_get_fit_method", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_get_fit_method(ct);
            return val(static_cast<unsigned>(_r));
        }));

    // fdl_canvas_template_get_fit_source — Get the fit source — which dimension layer to scale from.
    emscripten::function(
        "fdl_canvas_template_get_fit_source", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_get_fit_source(ct);
            return val(static_cast<unsigned>(_r));
        }));

    // fdl_canvas_template_get_id — Get the ID of a canvas template.
    emscripten::function("fdl_canvas_template_get_id", emscripten::optional_override([](emscripten::val ct_v) -> val {
                             auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
                             const char* _r = fdl_canvas_template_get_id(ct);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_canvas_template_get_label — Get the label of a canvas template.
    emscripten::function(
        "fdl_canvas_template_get_label", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            const char* _r = fdl_canvas_template_get_label(ct);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_canvas_template_get_maximum_dimensions — Get the maximum_dimensions constraint.
    emscripten::function(
        "fdl_canvas_template_get_maximum_dimensions", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            fdl_dimensions_i64_t _r = fdl_canvas_template_get_maximum_dimensions(ct);
            auto _out = to_val_DimensionsI64(_r);
            return _out;
        }));

    // fdl_canvas_template_get_pad_to_maximum — Get the pad_to_maximum flag.
    emscripten::function(
        "fdl_canvas_template_get_pad_to_maximum", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_get_pad_to_maximum(ct);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_get_preserve_from_source_canvas — Get the preserve_from_source_canvas geometry path.
    emscripten::function(
        "fdl_canvas_template_get_preserve_from_source_canvas",
        emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_get_preserve_from_source_canvas(ct);
            return val(static_cast<unsigned>(_r));
        }));

    // fdl_canvas_template_get_round — Get the rounding strategy. Returns the spec-default {FDL_ROUNDING_EVEN_EVEN,
    // FDL_ROUNDING_MODE_UP} when no "round" field is present (FDL spec §7.4.12).
    emscripten::function(
        "fdl_canvas_template_get_round", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            fdl_round_strategy_t _r = fdl_canvas_template_get_round(ct);
            auto _out = to_val_RoundStrategy(_r);
            return _out;
        }));

    // fdl_canvas_template_get_target_anamorphic_squeeze — Get the target anamorphic squeeze factor.
    emscripten::function(
        "fdl_canvas_template_get_target_anamorphic_squeeze",
        emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_get_target_anamorphic_squeeze(ct);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_get_target_dimensions — Get the target dimensions of a canvas template.
    emscripten::function(
        "fdl_canvas_template_get_target_dimensions", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            fdl_dimensions_i64_t _r = fdl_canvas_template_get_target_dimensions(ct);
            auto _out = to_val_DimensionsI64(_r);
            return _out;
        }));

    // fdl_canvas_template_has_maximum_dimensions — Check if maximum_dimensions constraint is set.
    emscripten::function(
        "fdl_canvas_template_has_maximum_dimensions", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_has_maximum_dimensions(ct);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_has_preserve_from_source_canvas — Check if preserve_from_source_canvas is set.
    emscripten::function(
        "fdl_canvas_template_has_preserve_from_source_canvas",
        emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_has_preserve_from_source_canvas(ct);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_has_round — Check whether the template has an explicit rounding strategy.
    emscripten::function(
        "fdl_canvas_template_has_round", emscripten::optional_override([](emscripten::val ct_v) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto _r = fdl_canvas_template_has_round(ct);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_set_maximum_dimensions — Set maximum_dimensions on a canvas template.
    emscripten::function(
        "fdl_canvas_template_set_maximum_dimensions",
        emscripten::optional_override([](emscripten::val ct_v, emscripten::val dims_v) -> void {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            fdl_dimensions_i64_t dims = from_val_DimensionsI64(dims_v);
            fdl_canvas_template_set_maximum_dimensions(ct, dims);
            return;
        }));

    // fdl_canvas_template_set_pad_to_maximum — Set pad_to_maximum flag on a canvas template.
    emscripten::function(
        "fdl_canvas_template_set_pad_to_maximum",
        emscripten::optional_override([](emscripten::val ct_v, int pad) -> void {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            fdl_canvas_template_set_pad_to_maximum(ct, pad);
            return;
        }));

    // fdl_canvas_template_set_preserve_from_source_canvas — Set preserve_from_source_canvas on a canvas template.
    emscripten::function(
        "fdl_canvas_template_set_preserve_from_source_canvas",
        emscripten::optional_override([](emscripten::val ct_v, unsigned path_i) -> void {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            fdl_geometry_path_t path = static_cast<fdl_geometry_path_t>(path_i);
            fdl_canvas_template_set_preserve_from_source_canvas(ct, path);
            return;
        }));

    // fdl_canvas_template_to_json — Serialize a canvas template to canonical JSON.
    emscripten::function(
        "fdl_canvas_template_to_json", emscripten::optional_override([](emscripten::val ct_v, int indent) -> val {
            auto* ct = unwrap_handle<fdl_canvas_template_t>(ct_v);
            auto* _r = fdl_canvas_template_to_json(ct, indent);
            if (!_r) {
                fdl_throw_js_error("fdl_canvas_template_to_json returned NULL");
                return val::null(); // unreachable: the line above throws
            }
            std::string _s(_r);
            fdl_free(const_cast<char*>(_r));
            return val(_s);
        }));

    // fdl_canvas_to_json — Serialize a canvas sub-object to canonical JSON.
    emscripten::function(
        "fdl_canvas_to_json", emscripten::optional_override([](emscripten::val canvas_v, int indent) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto* _r = fdl_canvas_to_json(canvas, indent);
            if (!_r) {
                fdl_throw_js_error("fdl_canvas_to_json returned NULL");
                return val::null(); // unreachable: the line above throws
            }
            std::string _s(_r);
            fdl_free(const_cast<char*>(_r));
            return val(_s);
        }));

    // fdl_clip_id_get_clip_name — Get the clip_name from a clip_id.
    emscripten::function("fdl_clip_id_get_clip_name", emscripten::optional_override([](emscripten::val cid_v) -> val {
                             auto* cid = unwrap_handle<fdl_clip_id_t>(cid_v);
                             const char* _r = fdl_clip_id_get_clip_name(cid);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_clip_id_get_file — Get the file path from a clip_id.
    emscripten::function("fdl_clip_id_get_file", emscripten::optional_override([](emscripten::val cid_v) -> val {
                             auto* cid = unwrap_handle<fdl_clip_id_t>(cid_v);
                             const char* _r = fdl_clip_id_get_file(cid);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_clip_id_has_file — Check if a clip_id has a file path.
    emscripten::function("fdl_clip_id_has_file", emscripten::optional_override([](emscripten::val cid_v) -> val {
                             auto* cid = unwrap_handle<fdl_clip_id_t>(cid_v);
                             auto _r = fdl_clip_id_has_file(cid);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_clip_id_has_sequence — Check if a clip_id has a file sequence.
    emscripten::function("fdl_clip_id_has_sequence", emscripten::optional_override([](emscripten::val cid_v) -> val {
                             auto* cid = unwrap_handle<fdl_clip_id_t>(cid_v);
                             auto _r = fdl_clip_id_has_sequence(cid);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_clip_id_sequence — Get the file sequence handle from a clip_id.
    emscripten::function("fdl_clip_id_sequence", emscripten::optional_override([](emscripten::val cid_v) -> val {
                             auto* cid = unwrap_handle<fdl_clip_id_t>(cid_v);
                             auto* _r = fdl_clip_id_sequence(cid);
                             return wrap_handle(_r);
                         }));

    // fdl_clip_id_to_json — Serialize a clip_id to canonical JSON.
    emscripten::function(
        "fdl_clip_id_to_json", emscripten::optional_override([](emscripten::val cid_v, int indent) -> val {
            auto* cid = unwrap_handle<fdl_clip_id_t>(cid_v);
            auto* _r = fdl_clip_id_to_json(cid, indent);
            if (!_r) {
                fdl_throw_js_error("fdl_clip_id_to_json returned NULL");
                return val::null(); // unreachable: the line above throws
            }
            std::string _s(_r);
            fdl_free(const_cast<char*>(_r));
            return val(_s);
        }));

    // fdl_clip_id_validate_json — Validate clip_id JSON for mutual exclusion (file vs sequence).
    emscripten::function(
        "fdl_clip_id_validate_json",
        emscripten::optional_override([](std::string json_str_str, double json_len_d) -> val {
            size_t json_len = static_cast<size_t>(json_len_d);
            auto* _r = fdl_clip_id_validate_json(json_str_str.c_str(), json_len);
            if (!_r) {
                return val::null();
            }
            std::string _s(_r);
            fdl_free(const_cast<char*>(_r));
            return val(_s);
        }));

    // fdl_compute_framing_from_intent — Compute a framing decision from a framing intent.
    emscripten::function(
        "fdl_compute_framing_from_intent",
        emscripten::optional_override(
            [](emscripten::val canvas_dims_v,
               emscripten::val working_dims_v,
               double squeeze,
               emscripten::val aspect_ratio_v,
               double protection,
               emscripten::val rounding_v) -> val {
                fdl_dimensions_f64_t canvas_dims = from_val_DimensionsF64(canvas_dims_v);
                fdl_dimensions_f64_t working_dims = from_val_DimensionsF64(working_dims_v);
                fdl_dimensions_i64_t aspect_ratio = from_val_DimensionsI64(aspect_ratio_v);
                fdl_round_strategy_t rounding = from_val_RoundStrategy(rounding_v);
                fdl_from_intent_result_t _r = fdl_compute_framing_from_intent(
                    canvas_dims, working_dims, squeeze, aspect_ratio, protection, rounding);
                auto _out = to_val_FromIntentResult(_r);
                return _out;
            }));

    // fdl_context_add_canvas — Add a canvas to a context.
    emscripten::function(
        "fdl_context_add_canvas",
        emscripten::optional_override(
            [](emscripten::val ctx_v,
               std::string id_str,
               std::string label_str,
               std::string source_canvas_id_str,
               double dim_w_d,
               double dim_h_d,
               double squeeze) -> val {
                auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
                int64_t dim_w = static_cast<int64_t>(dim_w_d);
                int64_t dim_h = static_cast<int64_t>(dim_h_d);
                auto* _r = fdl_context_add_canvas(
                    ctx, id_str.c_str(), label_str.c_str(), source_canvas_id_str.c_str(), dim_w, dim_h, squeeze);
                return wrap_handle(_r);
            }));

    // fdl_context_canvas_at — Get a canvas by index within a context.
    emscripten::function(
        "fdl_context_canvas_at", emscripten::optional_override([](emscripten::val ctx_v, uint32_t index) -> val {
            auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
            auto* _r = fdl_context_canvas_at(ctx, index);
            return wrap_handle(_r);
        }));

    // fdl_context_canvases_count — Get the number of canvases in a context.
    emscripten::function("fdl_context_canvases_count", emscripten::optional_override([](emscripten::val ctx_v) -> val {
                             auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
                             auto _r = fdl_context_canvases_count(ctx);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_context_clip_id — Get the clip_id handle from a context.
    emscripten::function("fdl_context_clip_id", emscripten::optional_override([](emscripten::val ctx_v) -> val {
                             auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
                             auto* _r = fdl_context_clip_id(ctx);
                             return wrap_handle(_r);
                         }));

    // fdl_context_find_canvas_by_id — Find a canvas by its ID within a context.
    emscripten::function(
        "fdl_context_find_canvas_by_id",
        emscripten::optional_override([](emscripten::val ctx_v, std::string id_str) -> val {
            auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
            auto* _r = fdl_context_find_canvas_by_id(ctx, id_str.c_str());
            return wrap_handle(_r);
        }));

    // fdl_context_get_clip_id — Get clip_id as a JSON string.
    emscripten::function("fdl_context_get_clip_id", emscripten::optional_override([](emscripten::val ctx_v) -> val {
                             auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
                             auto* _r = fdl_context_get_clip_id(ctx);
                             if (!_r) {
                                 return val::null();
                             }
                             std::string _s(_r);
                             fdl_free(const_cast<char*>(_r));
                             return val(_s);
                         }));

    // fdl_context_get_context_creator — Get the context_creator of a context.
    emscripten::function(
        "fdl_context_get_context_creator", emscripten::optional_override([](emscripten::val ctx_v) -> val {
            auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
            const char* _r = fdl_context_get_context_creator(ctx);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_context_get_label — Get the label of a context.
    emscripten::function("fdl_context_get_label", emscripten::optional_override([](emscripten::val ctx_v) -> val {
                             auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
                             const char* _r = fdl_context_get_label(ctx);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_context_has_clip_id — Check if a context has a clip_id.
    emscripten::function("fdl_context_has_clip_id", emscripten::optional_override([](emscripten::val ctx_v) -> val {
                             auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
                             auto _r = fdl_context_has_clip_id(ctx);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_context_remove_clip_id — Remove clip_id from a context. Safe to call if not present.
    emscripten::function("fdl_context_remove_clip_id", emscripten::optional_override([](emscripten::val ctx_v) -> void {
                             auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
                             fdl_context_remove_clip_id(ctx);
                             return;
                         }));

    // fdl_context_resolve_canvas_for_dimensions — Resolve canvas for given input dimensions.
    emscripten::function(
        "fdl_context_resolve_canvas_for_dimensions",
        emscripten::optional_override(
            [](emscripten::val ctx_v, emscripten::val input_dims_v, emscripten::val canvas_v, emscripten::val framing_v)
                -> val {
                auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
                fdl_dimensions_f64_t input_dims = from_val_DimensionsF64(input_dims_v);
                auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                auto* framing = unwrap_handle<fdl_framing_decision_t>(framing_v);
                fdl_resolve_canvas_result_t _r =
                    fdl_context_resolve_canvas_for_dimensions(ctx, input_dims, canvas, framing);
                auto _out = to_val_ResolveCanvasResult(_r);
                if (_r.error) {
                    fdl_free(const_cast<char*>(_r.error));
                }
                return _out;
            }));

    // fdl_context_set_clip_id_json — Set clip_id on a context from a JSON string.
    emscripten::function(
        "fdl_context_set_clip_id_json",
        emscripten::optional_override([](emscripten::val ctx_v, std::string json_str_str, double json_len_d) -> val {
            auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
            size_t json_len = static_cast<size_t>(json_len_d);
            auto* _r = fdl_context_set_clip_id_json(ctx, json_str_str.c_str(), json_len);
            if (!_r) {
                return val::null();
            }
            std::string _s(_r);
            fdl_free(const_cast<char*>(_r));
            return val(_s);
        }));

    // fdl_context_to_json — Serialize a context sub-object to canonical JSON.
    emscripten::function(
        "fdl_context_to_json", emscripten::optional_override([](emscripten::val ctx_v, int indent) -> val {
            auto* ctx = unwrap_handle<fdl_context_t>(ctx_v);
            auto* _r = fdl_context_to_json(ctx, indent);
            if (!_r) {
                fdl_throw_js_error("fdl_context_to_json returned NULL");
                return val::null(); // unreachable: the line above throws
            }
            std::string _s(_r);
            fdl_free(const_cast<char*>(_r));
            return val(_s);
        }));

    // fdl_dimensions_clamp_to_dims — Clamp dimensions to maximum bounds.
    emscripten::function(
        "fdl_dimensions_clamp_to_dims",
        emscripten::optional_override([](emscripten::val dims_v, emscripten::val clamp_dims_v) -> val {
            fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
            fdl_dimensions_f64_t clamp_dims = from_val_DimensionsF64(clamp_dims_v);
            fdl_point_f64_t out_delta{};
            fdl_dimensions_f64_t _r = fdl_dimensions_clamp_to_dims(dims, clamp_dims, &out_delta);
            auto _out = val::object();
            _out.set("_return", to_val_DimensionsF64(_r));
            _out.set("delta", to_val_PointF64(out_delta));
            return _out;
        }));

    // fdl_dimensions_equal — Check if dimensions are approximately equal within FDL tolerance.
    emscripten::function(
        "fdl_dimensions_equal", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_dimensions_f64_t a = from_val_DimensionsF64(a_v);
            fdl_dimensions_f64_t b = from_val_DimensionsF64(b_v);
            auto _r = fdl_dimensions_equal(a, b);
            return val(static_cast<double>(_r));
        }));

    // fdl_dimensions_f64_gt — Check if a > b using OR logic (either width or height is greater).
    emscripten::function(
        "fdl_dimensions_f64_gt", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_dimensions_f64_t a = from_val_DimensionsF64(a_v);
            fdl_dimensions_f64_t b = from_val_DimensionsF64(b_v);
            auto _r = fdl_dimensions_f64_gt(a, b);
            return val(static_cast<double>(_r));
        }));

    // fdl_dimensions_f64_lt — Check if a < b using OR logic (either width or height is less).
    emscripten::function(
        "fdl_dimensions_f64_lt", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_dimensions_f64_t a = from_val_DimensionsF64(a_v);
            fdl_dimensions_f64_t b = from_val_DimensionsF64(b_v);
            auto _r = fdl_dimensions_f64_lt(a, b);
            return val(static_cast<double>(_r));
        }));

    // fdl_dimensions_f64_to_i64 — Convert float dimensions to int64 by truncation.
    emscripten::function("fdl_dimensions_f64_to_i64", emscripten::optional_override([](emscripten::val dims_v) -> val {
                             fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
                             fdl_dimensions_i64_t _r = fdl_dimensions_f64_to_i64(dims);
                             auto _out = to_val_DimensionsI64(_r);
                             return _out;
                         }));

    // fdl_dimensions_i64_gt — Check if a > b using OR logic (either width or height is greater).
    emscripten::function(
        "fdl_dimensions_i64_gt", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_dimensions_i64_t a = from_val_DimensionsI64(a_v);
            fdl_dimensions_i64_t b = from_val_DimensionsI64(b_v);
            auto _r = fdl_dimensions_i64_gt(a, b);
            return val(static_cast<double>(_r));
        }));

    // fdl_dimensions_i64_is_zero — Check if both width and height are zero (int64 variant).
    emscripten::function("fdl_dimensions_i64_is_zero", emscripten::optional_override([](emscripten::val dims_v) -> val {
                             fdl_dimensions_i64_t dims = from_val_DimensionsI64(dims_v);
                             auto _r = fdl_dimensions_i64_is_zero(dims);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_dimensions_i64_lt — Check if a < b using OR logic (either width or height is less).
    emscripten::function(
        "fdl_dimensions_i64_lt", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_dimensions_i64_t a = from_val_DimensionsI64(a_v);
            fdl_dimensions_i64_t b = from_val_DimensionsI64(b_v);
            auto _r = fdl_dimensions_i64_lt(a, b);
            return val(static_cast<double>(_r));
        }));

    // fdl_dimensions_i64_normalize — Normalize int64 dimensions by applying anamorphic squeeze to width.
    emscripten::function(
        "fdl_dimensions_i64_normalize",
        emscripten::optional_override([](emscripten::val dims_v, double squeeze) -> val {
            fdl_dimensions_i64_t dims = from_val_DimensionsI64(dims_v);
            fdl_dimensions_f64_t _r = fdl_dimensions_i64_normalize(dims, squeeze);
            auto _out = to_val_DimensionsF64(_r);
            return _out;
        }));

    // fdl_dimensions_is_zero — Check if both width and height are zero.
    emscripten::function("fdl_dimensions_is_zero", emscripten::optional_override([](emscripten::val dims_v) -> val {
                             fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
                             auto _r = fdl_dimensions_is_zero(dims);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_dimensions_normalize — Normalize dimensions by applying anamorphic squeeze to width.
    emscripten::function(
        "fdl_dimensions_normalize", emscripten::optional_override([](emscripten::val dims_v, double squeeze) -> val {
            fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
            fdl_dimensions_f64_t _r = fdl_dimensions_normalize(dims, squeeze);
            auto _out = to_val_DimensionsF64(_r);
            return _out;
        }));

    // fdl_dimensions_normalize_and_scale — Normalize and scale in one step.
    emscripten::function(
        "fdl_dimensions_normalize_and_scale",
        emscripten::optional_override(
            [](emscripten::val dims_v, double input_squeeze, double scale_factor, double target_squeeze) -> val {
                fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
                fdl_dimensions_f64_t _r =
                    fdl_dimensions_normalize_and_scale(dims, input_squeeze, scale_factor, target_squeeze);
                auto _out = to_val_DimensionsF64(_r);
                return _out;
            }));

    // fdl_dimensions_scale — Scale normalized dimensions and apply target squeeze.
    emscripten::function(
        "fdl_dimensions_scale",
        emscripten::optional_override([](emscripten::val dims_v, double scale_factor, double target_squeeze) -> val {
            fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
            fdl_dimensions_f64_t _r = fdl_dimensions_scale(dims, scale_factor, target_squeeze);
            auto _out = to_val_DimensionsF64(_r);
            return _out;
        }));

    // fdl_dimensions_sub — Subtract two dimensions: result = a - b.
    emscripten::function(
        "fdl_dimensions_sub", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_dimensions_f64_t a = from_val_DimensionsF64(a_v);
            fdl_dimensions_f64_t b = from_val_DimensionsF64(b_v);
            fdl_dimensions_f64_t _r = fdl_dimensions_sub(a, b);
            auto _out = to_val_DimensionsF64(_r);
            return _out;
        }));

    // fdl_doc_add_canvas_template — Add a canvas template to the document.
    emscripten::function(
        "fdl_doc_add_canvas_template",
        emscripten::optional_override(
            [](emscripten::val doc_v,
               std::string id_str,
               std::string label_str,
               double target_w_d,
               double target_h_d,
               double target_squeeze,
               unsigned fit_source_i,
               unsigned fit_method_i,
               unsigned halign_i,
               unsigned valign_i,
               emscripten::val rounding_v) -> val {
                auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                int64_t target_w = static_cast<int64_t>(target_w_d);
                int64_t target_h = static_cast<int64_t>(target_h_d);
                fdl_geometry_path_t fit_source = static_cast<fdl_geometry_path_t>(fit_source_i);
                fdl_fit_method_t fit_method = static_cast<fdl_fit_method_t>(fit_method_i);
                fdl_halign_t halign = static_cast<fdl_halign_t>(halign_i);
                fdl_valign_t valign = static_cast<fdl_valign_t>(valign_i);
                fdl_round_strategy_t rounding = from_val_RoundStrategy(rounding_v);
                auto* _r = fdl_doc_add_canvas_template(
                    doc,
                    id_str.c_str(),
                    label_str.c_str(),
                    target_w,
                    target_h,
                    target_squeeze,
                    fit_source,
                    fit_method,
                    halign,
                    valign,
                    rounding);
                return wrap_handle(_r);
            }));

    // fdl_doc_add_context — Add a context to the document.
    emscripten::function(
        "fdl_doc_add_context",
        emscripten::optional_override(
            [](emscripten::val doc_v, std::string label_str, emscripten::val context_creator_v) -> val {
                auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                std::string context_creator_buf;
                const char* context_creator = val_to_cstr_or_null(context_creator_v, context_creator_buf);
                auto* _r = fdl_doc_add_context(doc, label_str.c_str(), context_creator);
                return wrap_handle(_r);
            }));

    // fdl_doc_add_framing_intent — Add a framing intent to the document.
    emscripten::function(
        "fdl_doc_add_framing_intent",
        emscripten::optional_override(
            [](emscripten::val doc_v,
               std::string id_str,
               std::string label_str,
               double aspect_w_d,
               double aspect_h_d,
               double protection) -> val {
                auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                int64_t aspect_w = static_cast<int64_t>(aspect_w_d);
                int64_t aspect_h = static_cast<int64_t>(aspect_h_d);
                auto* _r =
                    fdl_doc_add_framing_intent(doc, id_str.c_str(), label_str.c_str(), aspect_w, aspect_h, protection);
                return wrap_handle(_r);
            }));

    // fdl_doc_canvas_template_at — Get a canvas template by index.
    emscripten::function(
        "fdl_doc_canvas_template_at", emscripten::optional_override([](emscripten::val doc_v, uint32_t index) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            auto* _r = fdl_doc_canvas_template_at(doc, index);
            return wrap_handle(_r);
        }));

    // fdl_doc_canvas_template_find_by_id — Find a canvas template by its ID string.
    emscripten::function(
        "fdl_doc_canvas_template_find_by_id",
        emscripten::optional_override([](emscripten::val doc_v, std::string id_str) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            auto* _r = fdl_doc_canvas_template_find_by_id(doc, id_str.c_str());
            return wrap_handle(_r);
        }));

    // fdl_doc_canvas_templates_count — Get the number of canvas templates in the document.
    emscripten::function(
        "fdl_doc_canvas_templates_count", emscripten::optional_override([](emscripten::val doc_v) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            auto _r = fdl_doc_canvas_templates_count(doc);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_context_at — Get a context by index.
    emscripten::function(
        "fdl_doc_context_at", emscripten::optional_override([](emscripten::val doc_v, uint32_t index) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            auto* _r = fdl_doc_context_at(doc, index);
            return wrap_handle(_r);
        }));

    // fdl_doc_context_find_by_label — Find a context by its label string.
    emscripten::function(
        "fdl_doc_context_find_by_label",
        emscripten::optional_override([](emscripten::val doc_v, std::string label_str) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            auto* _r = fdl_doc_context_find_by_label(doc, label_str.c_str());
            return wrap_handle(_r);
        }));

    // fdl_doc_contexts_count — Get the number of contexts in the document.
    emscripten::function("fdl_doc_contexts_count", emscripten::optional_override([](emscripten::val doc_v) -> val {
                             auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                             auto _r = fdl_doc_contexts_count(doc);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_doc_create — Create an empty FDL document.
    emscripten::function("fdl_doc_create", emscripten::optional_override([]() -> val {
                             auto* _r = fdl_doc_create();
                             return wrap_handle(_r);
                         }));

    // fdl_doc_create_with_header — Create a new FDL document with header fields and empty collections.
    emscripten::function(
        "fdl_doc_create_with_header",
        emscripten::optional_override(
            [](std::string uuid_str,
               int version_major,
               int version_minor,
               std::string fdl_creator_str,
               emscripten::val default_framing_intent_v) -> val {
                std::string default_framing_intent_buf;
                const char* default_framing_intent =
                    val_to_cstr_or_null(default_framing_intent_v, default_framing_intent_buf);
                auto* _r = fdl_doc_create_with_header(
                    uuid_str.c_str(), version_major, version_minor, fdl_creator_str.c_str(), default_framing_intent);
                return wrap_handle(_r);
            }));

    // fdl_doc_framing_intent_at — Get a framing intent by index.
    emscripten::function(
        "fdl_doc_framing_intent_at", emscripten::optional_override([](emscripten::val doc_v, uint32_t index) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            auto* _r = fdl_doc_framing_intent_at(doc, index);
            return wrap_handle(_r);
        }));

    // fdl_doc_framing_intent_find_by_id — Find a framing intent by its ID string.
    emscripten::function(
        "fdl_doc_framing_intent_find_by_id",
        emscripten::optional_override([](emscripten::val doc_v, std::string id_str) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            auto* _r = fdl_doc_framing_intent_find_by_id(doc, id_str.c_str());
            return wrap_handle(_r);
        }));

    // fdl_doc_framing_intents_count — Get the number of framing intents in the document.
    emscripten::function(
        "fdl_doc_framing_intents_count", emscripten::optional_override([](emscripten::val doc_v) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            auto _r = fdl_doc_framing_intents_count(doc);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_free — Free an FDL document and all associated handles.
    emscripten::function("fdl_doc_free", emscripten::optional_override([](emscripten::val doc_v) -> void {
                             if (doc_v.isNull() || doc_v.isUndefined()) {
                                 return;
                             }
                             auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                             fdl_doc_free(doc);
                             return;
                         }));

    // fdl_doc_get_default_framing_intent — Get the default_framing_intent from a parsed FDL document.
    emscripten::function(
        "fdl_doc_get_default_framing_intent", emscripten::optional_override([](emscripten::val doc_v) -> val {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            const char* _r = fdl_doc_get_default_framing_intent(doc);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_doc_get_fdl_creator — Get the fdl_creator from a parsed FDL document.
    emscripten::function("fdl_doc_get_fdl_creator", emscripten::optional_override([](emscripten::val doc_v) -> val {
                             auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                             const char* _r = fdl_doc_get_fdl_creator(doc);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_doc_get_uuid — Get the UUID from a parsed FDL document.
    emscripten::function("fdl_doc_get_uuid", emscripten::optional_override([](emscripten::val doc_v) -> val {
                             auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                             const char* _r = fdl_doc_get_uuid(doc);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_doc_get_version_major — Get the FDL version major number.
    emscripten::function("fdl_doc_get_version_major", emscripten::optional_override([](emscripten::val doc_v) -> val {
                             auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                             auto _r = fdl_doc_get_version_major(doc);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_doc_get_version_minor — Get the FDL version minor number.
    emscripten::function("fdl_doc_get_version_minor", emscripten::optional_override([](emscripten::val doc_v) -> val {
                             auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                             auto _r = fdl_doc_get_version_minor(doc);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_doc_parse_json — Parse a JSON string into an FDL document.
    emscripten::function(
        "fdl_doc_parse_json", emscripten::optional_override([](std::string json_str_str, double json_len_d) -> val {
            size_t json_len = static_cast<size_t>(json_len_d);
            fdl_parse_result_t _r = fdl_doc_parse_json(json_str_str.c_str(), json_len);
            auto _out = to_val_ParseResult(_r);
            if (_r.error) {
                fdl_free(const_cast<char*>(_r.error));
            }
            return _out;
        }));

    // fdl_doc_set_default_framing_intent — Set the default_framing_intent on a document.
    emscripten::function(
        "fdl_doc_set_default_framing_intent",
        emscripten::optional_override([](emscripten::val doc_v, std::string fi_id_str) -> void {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            fdl_doc_set_default_framing_intent(doc, fi_id_str.c_str());
            return;
        }));

    // fdl_doc_set_fdl_creator — Set the fdl_creator on a document.
    emscripten::function(
        "fdl_doc_set_fdl_creator",
        emscripten::optional_override([](emscripten::val doc_v, std::string creator_str) -> void {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            fdl_doc_set_fdl_creator(doc, creator_str.c_str());
            return;
        }));

    // fdl_doc_set_uuid — Set the UUID on a document.
    emscripten::function(
        "fdl_doc_set_uuid", emscripten::optional_override([](emscripten::val doc_v, std::string uuid_str) -> void {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            fdl_doc_set_uuid(doc, uuid_str.c_str());
            return;
        }));

    // fdl_doc_set_version — Set the FDL version on a document.
    emscripten::function(
        "fdl_doc_set_version", emscripten::optional_override([](emscripten::val doc_v, int major, int minor) -> void {
            auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
            fdl_doc_set_version(doc, major, minor);
            return;
        }));

    // fdl_doc_to_json — Serialize document to canonical JSON string.
    emscripten::function("fdl_doc_to_json", emscripten::optional_override([](emscripten::val doc_v, int indent) -> val {
                             auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                             auto* _r = fdl_doc_to_json(doc, indent);
                             if (!_r) {
                                 fdl_throw_js_error("fdl_doc_to_json returned NULL");
                                 return val::null(); // unreachable: the line above throws
                             }
                             std::string _s(_r);
                             fdl_free(const_cast<char*>(_r));
                             return val(_s);
                         }));

    // fdl_doc_validate — Run schema and semantic validators on the document.
    emscripten::function("fdl_doc_validate", emscripten::optional_override([](emscripten::val doc_v) -> val {
                             auto* doc = unwrap_handle<fdl_doc_t>(doc_v);
                             auto* _r = fdl_doc_validate(doc);
                             return wrap_handle(_r);
                         }));

    // fdl_file_sequence_get_idx — Get the index variable name.
    emscripten::function("fdl_file_sequence_get_idx", emscripten::optional_override([](emscripten::val seq_v) -> val {
                             auto* seq = unwrap_handle<fdl_file_sequence_t>(seq_v);
                             const char* _r = fdl_file_sequence_get_idx(seq);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_file_sequence_get_max — Get the maximum (last) frame number.
    emscripten::function("fdl_file_sequence_get_max", emscripten::optional_override([](emscripten::val seq_v) -> val {
                             auto* seq = unwrap_handle<fdl_file_sequence_t>(seq_v);
                             auto _r = fdl_file_sequence_get_max(seq);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_file_sequence_get_min — Get the minimum (first) frame number.
    emscripten::function("fdl_file_sequence_get_min", emscripten::optional_override([](emscripten::val seq_v) -> val {
                             auto* seq = unwrap_handle<fdl_file_sequence_t>(seq_v);
                             auto _r = fdl_file_sequence_get_min(seq);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_file_sequence_get_value — Get the sequence pattern value string.
    emscripten::function("fdl_file_sequence_get_value", emscripten::optional_override([](emscripten::val seq_v) -> val {
                             auto* seq = unwrap_handle<fdl_file_sequence_t>(seq_v);
                             const char* _r = fdl_file_sequence_get_value(seq);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_fp_abs_tol — Absolute tolerance for floating-point comparison.
    emscripten::function("fdl_fp_abs_tol", emscripten::optional_override([]() -> val {
                             auto _r = fdl_fp_abs_tol();
                             return val(static_cast<double>(_r));
                         }));

    // fdl_fp_rel_tol — Relative tolerance for floating-point comparison.
    emscripten::function("fdl_fp_rel_tol", emscripten::optional_override([]() -> val {
                             auto _r = fdl_fp_rel_tol();
                             return val(static_cast<double>(_r));
                         }));

    // fdl_framing_decision_adjust_anchor — Adjust anchor_point on a framing decision based on alignment within canvas.
    emscripten::function(
        "fdl_framing_decision_adjust_anchor",
        emscripten::optional_override(
            [](emscripten::val fd_v, emscripten::val canvas_v, unsigned h_align_i, unsigned v_align_i) -> void {
                auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
                auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                fdl_halign_t h_align = static_cast<fdl_halign_t>(h_align_i);
                fdl_valign_t v_align = static_cast<fdl_valign_t>(v_align_i);
                fdl_framing_decision_adjust_anchor(fd, canvas, h_align, v_align);
                return;
            }));

    // fdl_framing_decision_adjust_protection_anchor — Adjust protection_anchor_point on a framing decision based on
    // alignment within canvas.
    emscripten::function(
        "fdl_framing_decision_adjust_protection_anchor",
        emscripten::optional_override(
            [](emscripten::val fd_v, emscripten::val canvas_v, unsigned h_align_i, unsigned v_align_i) -> void {
                auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
                auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                fdl_halign_t h_align = static_cast<fdl_halign_t>(h_align_i);
                fdl_valign_t v_align = static_cast<fdl_valign_t>(v_align_i);
                fdl_framing_decision_adjust_protection_anchor(fd, canvas, h_align, v_align);
                return;
            }));

    // fdl_framing_decision_get_anchor_point — Get the anchor point of a framing decision.
    emscripten::function(
        "fdl_framing_decision_get_anchor_point", emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_point_f64_t _r = fdl_framing_decision_get_anchor_point(fd);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_framing_decision_get_dimensions — Get the framing decision dimensions (floating-point sub-pixel).
    emscripten::function(
        "fdl_framing_decision_get_dimensions", emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_dimensions_f64_t _r = fdl_framing_decision_get_dimensions(fd);
            auto _out = to_val_DimensionsF64(_r);
            return _out;
        }));

    // fdl_framing_decision_get_framing_intent_id — Get the framing_intent_id that this framing decision references.
    emscripten::function(
        "fdl_framing_decision_get_framing_intent_id", emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            const char* _r = fdl_framing_decision_get_framing_intent_id(fd);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_framing_decision_get_id — Get the ID of a framing decision.
    emscripten::function("fdl_framing_decision_get_id", emscripten::optional_override([](emscripten::val fd_v) -> val {
                             auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
                             const char* _r = fdl_framing_decision_get_id(fd);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_framing_decision_get_label — Get the label of a framing decision.
    emscripten::function(
        "fdl_framing_decision_get_label", emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            const char* _r = fdl_framing_decision_get_label(fd);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_framing_decision_get_protection_anchor_point — Get the protection anchor point.
    emscripten::function(
        "fdl_framing_decision_get_protection_anchor_point",
        emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_point_f64_t _r = fdl_framing_decision_get_protection_anchor_point(fd);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_framing_decision_get_protection_dimensions — Get the protection area dimensions.
    emscripten::function(
        "fdl_framing_decision_get_protection_dimensions",
        emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_dimensions_f64_t _r = fdl_framing_decision_get_protection_dimensions(fd);
            auto _out = to_val_DimensionsF64(_r);
            return _out;
        }));

    // fdl_framing_decision_get_protection_rect — Get the framing decision protection rect.
    emscripten::function(
        "fdl_framing_decision_get_protection_rect", emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_rect_t out_rect{};
            auto _r = fdl_framing_decision_get_protection_rect(fd, &out_rect);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("rect", to_val_Rect(out_rect));
            return _out;
        }));

    // fdl_framing_decision_get_rect — Get the framing decision rect: (anchor.x, anchor.y, dims.width, dims.height).
    emscripten::function(
        "fdl_framing_decision_get_rect", emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_rect_t _r = fdl_framing_decision_get_rect(fd);
            auto _out = to_val_Rect(_r);
            return _out;
        }));

    // fdl_framing_decision_has_protection — Check if a framing decision has protection area set.
    emscripten::function(
        "fdl_framing_decision_has_protection", emscripten::optional_override([](emscripten::val fd_v) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            auto _r = fdl_framing_decision_has_protection(fd);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_populate_from_intent — Populate a framing decision from a canvas and framing intent.
    emscripten::function(
        "fdl_framing_decision_populate_from_intent",
        emscripten::optional_override(
            [](emscripten::val fd_v, emscripten::val canvas_v, emscripten::val intent_v, emscripten::val rounding_v)
                -> void {
                auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
                auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
                auto* intent = unwrap_handle<fdl_framing_intent_t>(intent_v);
                fdl_round_strategy_t rounding = from_val_RoundStrategy(rounding_v);
                fdl_framing_decision_populate_from_intent(fd, canvas, intent, rounding);
                return;
            }));

    // fdl_framing_decision_remove_protection — Remove protection dimensions and anchor from a framing decision.
    emscripten::function(
        "fdl_framing_decision_remove_protection", emscripten::optional_override([](emscripten::val fd_v) -> void {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_framing_decision_remove_protection(fd);
            return;
        }));

    // fdl_framing_decision_set_anchor_point — Set anchor point on a framing decision.
    emscripten::function(
        "fdl_framing_decision_set_anchor_point",
        emscripten::optional_override([](emscripten::val fd_v, emscripten::val point_v) -> void {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_point_f64_t point = from_val_PointF64(point_v);
            fdl_framing_decision_set_anchor_point(fd, point);
            return;
        }));

    // fdl_framing_decision_set_dimensions — Set dimensions on a framing decision.
    emscripten::function(
        "fdl_framing_decision_set_dimensions",
        emscripten::optional_override([](emscripten::val fd_v, emscripten::val dims_v) -> void {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
            fdl_framing_decision_set_dimensions(fd, dims);
            return;
        }));

    // fdl_framing_decision_set_protection — Set protection dimensions and anchor on a framing decision.
    emscripten::function(
        "fdl_framing_decision_set_protection",
        emscripten::optional_override(
            [](emscripten::val fd_v, emscripten::val dims_v, emscripten::val anchor_v) -> void {
                auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
                fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
                fdl_point_f64_t anchor = from_val_PointF64(anchor_v);
                fdl_framing_decision_set_protection(fd, dims, anchor);
                return;
            }));

    // fdl_framing_decision_set_protection_anchor_point — Set protection anchor point on a framing decision (without
    // changing dimensions).
    emscripten::function(
        "fdl_framing_decision_set_protection_anchor_point",
        emscripten::optional_override([](emscripten::val fd_v, emscripten::val point_v) -> void {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_point_f64_t point = from_val_PointF64(point_v);
            fdl_framing_decision_set_protection_anchor_point(fd, point);
            return;
        }));

    // fdl_framing_decision_set_protection_dimensions — Set protection dimensions on a framing decision (without
    // changing anchor).
    emscripten::function(
        "fdl_framing_decision_set_protection_dimensions",
        emscripten::optional_override([](emscripten::val fd_v, emscripten::val dims_v) -> void {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
            fdl_framing_decision_set_protection_dimensions(fd, dims);
            return;
        }));

    // fdl_framing_decision_to_json — Serialize a framing decision to canonical JSON.
    emscripten::function(
        "fdl_framing_decision_to_json", emscripten::optional_override([](emscripten::val fd_v, int indent) -> val {
            auto* fd = unwrap_handle<fdl_framing_decision_t>(fd_v);
            auto* _r = fdl_framing_decision_to_json(fd, indent);
            if (!_r) {
                fdl_throw_js_error("fdl_framing_decision_to_json returned NULL");
                return val::null(); // unreachable: the line above throws
            }
            std::string _s(_r);
            fdl_free(const_cast<char*>(_r));
            return val(_s);
        }));

    // fdl_framing_intent_get_aspect_ratio — Get the target aspect ratio of a framing intent.
    emscripten::function(
        "fdl_framing_intent_get_aspect_ratio", emscripten::optional_override([](emscripten::val fi_v) -> val {
            auto* fi = unwrap_handle<fdl_framing_intent_t>(fi_v);
            fdl_dimensions_i64_t _r = fdl_framing_intent_get_aspect_ratio(fi);
            auto _out = to_val_DimensionsI64(_r);
            return _out;
        }));

    // fdl_framing_intent_get_id — Get the ID of a framing intent.
    emscripten::function("fdl_framing_intent_get_id", emscripten::optional_override([](emscripten::val fi_v) -> val {
                             auto* fi = unwrap_handle<fdl_framing_intent_t>(fi_v);
                             const char* _r = fdl_framing_intent_get_id(fi);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_framing_intent_get_label — Get the label of a framing intent.
    emscripten::function("fdl_framing_intent_get_label", emscripten::optional_override([](emscripten::val fi_v) -> val {
                             auto* fi = unwrap_handle<fdl_framing_intent_t>(fi_v);
                             const char* _r = fdl_framing_intent_get_label(fi);
                             return _r ? val(std::string(_r)) : val::null();
                         }));

    // fdl_framing_intent_get_protection — Get the protection factor of a framing intent.
    emscripten::function(
        "fdl_framing_intent_get_protection", emscripten::optional_override([](emscripten::val fi_v) -> val {
            auto* fi = unwrap_handle<fdl_framing_intent_t>(fi_v);
            auto _r = fdl_framing_intent_get_protection(fi);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_set_aspect_ratio — Set aspect ratio on a framing intent.
    emscripten::function(
        "fdl_framing_intent_set_aspect_ratio",
        emscripten::optional_override([](emscripten::val fi_v, emscripten::val dims_v) -> void {
            auto* fi = unwrap_handle<fdl_framing_intent_t>(fi_v);
            fdl_dimensions_i64_t dims = from_val_DimensionsI64(dims_v);
            fdl_framing_intent_set_aspect_ratio(fi, dims);
            return;
        }));

    // fdl_framing_intent_set_protection — Set protection factor on a framing intent.
    emscripten::function(
        "fdl_framing_intent_set_protection",
        emscripten::optional_override([](emscripten::val fi_v, double protection) -> void {
            auto* fi = unwrap_handle<fdl_framing_intent_t>(fi_v);
            fdl_framing_intent_set_protection(fi, protection);
            return;
        }));

    // fdl_framing_intent_to_json — Serialize a framing intent to canonical JSON.
    emscripten::function(
        "fdl_framing_intent_to_json", emscripten::optional_override([](emscripten::val fi_v, int indent) -> val {
            auto* fi = unwrap_handle<fdl_framing_intent_t>(fi_v);
            auto* _r = fdl_framing_intent_to_json(fi, indent);
            if (!_r) {
                fdl_throw_js_error("fdl_framing_intent_to_json returned NULL");
                return val::null(); // unreachable: the line above throws
            }
            std::string _s(_r);
            fdl_free(const_cast<char*>(_r));
            return val(_s);
        }));

    // fdl_free — Free memory allocated by fdl_core functions.
    emscripten::function("fdl_free", emscripten::optional_override([](emscripten::val ptr_v) -> void {
                             if (ptr_v.isNull() || ptr_v.isUndefined()) {
                                 return;
                             }
                             auto* ptr = unwrap_handle<void>(ptr_v);
                             fdl_free(ptr);
                             return;
                         }));

    // fdl_geometry_apply_offset — Apply offset to all anchors, clamping to canvas bounds.
    emscripten::function(
        "fdl_geometry_apply_offset",
        emscripten::optional_override([](emscripten::val geo_v, emscripten::val offset_v) -> val {
            fdl_geometry_t geo = from_val_Geometry(geo_v);
            fdl_point_f64_t offset = from_val_PointF64(offset_v);
            fdl_point_f64_t theo_eff{};
            fdl_point_f64_t theo_prot{};
            fdl_point_f64_t theo_fram{};
            fdl_geometry_t _r = fdl_geometry_apply_offset(geo, offset, &theo_eff, &theo_prot, &theo_fram);
            auto _out = val::object();
            _out.set("_return", to_val_Geometry(_r));
            _out.set("theo_eff", to_val_PointF64(theo_eff));
            _out.set("theo_prot", to_val_PointF64(theo_prot));
            _out.set("theo_fram", to_val_PointF64(theo_fram));
            return _out;
        }));

    // fdl_geometry_crop — Crop all dimensions to visible portion within canvas.
    emscripten::function(
        "fdl_geometry_crop",
        emscripten::optional_override(
            [](emscripten::val geo_v,
               emscripten::val theo_eff_v,
               emscripten::val theo_prot_v,
               emscripten::val theo_fram_v) -> val {
                fdl_geometry_t geo = from_val_Geometry(geo_v);
                fdl_point_f64_t theo_eff = from_val_PointF64(theo_eff_v);
                fdl_point_f64_t theo_prot = from_val_PointF64(theo_prot_v);
                fdl_point_f64_t theo_fram = from_val_PointF64(theo_fram_v);
                fdl_geometry_t _r = fdl_geometry_crop(geo, theo_eff, theo_prot, theo_fram);
                auto _out = to_val_Geometry(_r);
                return _out;
            }));

    // fdl_geometry_fill_hierarchy_gaps — Fill gaps in the geometry hierarchy by propagating populated dimensions
    // upward.
    emscripten::function(
        "fdl_geometry_fill_hierarchy_gaps",
        emscripten::optional_override([](emscripten::val geo_v, emscripten::val anchor_offset_v) -> val {
            fdl_geometry_t geo = from_val_Geometry(geo_v);
            fdl_point_f64_t anchor_offset = from_val_PointF64(anchor_offset_v);
            fdl_geometry_t _r = fdl_geometry_fill_hierarchy_gaps(geo, anchor_offset);
            auto _out = to_val_Geometry(_r);
            return _out;
        }));

    // fdl_geometry_get_dims_anchor_from_path — Extract dimensions and anchor from geometry by path.
    emscripten::function(
        "fdl_geometry_get_dims_anchor_from_path",
        emscripten::optional_override([](emscripten::val geo_v, unsigned path_i) -> val {
            fdl_geometry_t geo = from_val_Geometry(geo_v);
            fdl_geometry_path_t path = static_cast<fdl_geometry_path_t>(path_i);
            fdl_dimensions_f64_t out_dims{};
            fdl_point_f64_t out_anchor{};
            auto _r = fdl_geometry_get_dims_anchor_from_path(&geo, path, &out_dims, &out_anchor);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("dims", to_val_DimensionsF64(out_dims));
            _out.set("anchor", to_val_PointF64(out_anchor));
            return _out;
        }));

    // fdl_geometry_normalize_and_scale — Normalize and scale all 7 fields of the geometry.
    emscripten::function(
        "fdl_geometry_normalize_and_scale",
        emscripten::optional_override(
            [](emscripten::val geo_v, double source_squeeze, double scale_factor, double target_squeeze) -> val {
                fdl_geometry_t geo = from_val_Geometry(geo_v);
                fdl_geometry_t _r = fdl_geometry_normalize_and_scale(geo, source_squeeze, scale_factor, target_squeeze);
                auto _out = to_val_Geometry(_r);
                return _out;
            }));

    // fdl_geometry_round — Round integer-typed schema fields and symmetrically absorb deltas into anchors.  Intended to
    // run once at the end of the template pipeline (post-crop).
    emscripten::function(
        "fdl_geometry_round",
        emscripten::optional_override([](emscripten::val geo_v, emscripten::val strategy_v) -> val {
            fdl_geometry_t geo = from_val_Geometry(geo_v);
            fdl_round_strategy_t strategy = from_val_RoundStrategy(strategy_v);
            fdl_geometry_t _r = fdl_geometry_round(geo, strategy);
            auto _out = to_val_Geometry(_r);
            return _out;
        }));

    // fdl_make_rect — Construct a rect from raw coordinates.
    emscripten::function(
        "fdl_make_rect", emscripten::optional_override([](double x, double y, double width, double height) -> val {
            fdl_rect_t _r = fdl_make_rect(x, y, width, height);
            auto _out = to_val_Rect(_r);
            return _out;
        }));

    // fdl_output_size_for_axis — Determine output canvas size for a single axis.
    emscripten::function(
        "fdl_output_size_for_axis",
        emscripten::optional_override([](double canvas_size, double max_size, int has_max, int pad_to_max) -> val {
            auto _r = fdl_output_size_for_axis(canvas_size, max_size, has_max, pad_to_max);
            return val(static_cast<double>(_r));
        }));

    // fdl_point_add — Add two points: result = a + b.
    emscripten::function(
        "fdl_point_add", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_point_f64_t a = from_val_PointF64(a_v);
            fdl_point_f64_t b = from_val_PointF64(b_v);
            fdl_point_f64_t _r = fdl_point_add(a, b);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_point_clamp — Clamp point values to [min_val, max_val].
    emscripten::function(
        "fdl_point_clamp",
        emscripten::optional_override(
            [](emscripten::val point_v, double min_val, double max_val, int has_min, int has_max) -> val {
                fdl_point_f64_t point = from_val_PointF64(point_v);
                fdl_point_f64_t _r = fdl_point_clamp(point, min_val, max_val, has_min, has_max);
                auto _out = to_val_PointF64(_r);
                return _out;
            }));

    // fdl_point_equal — Check approximate equality within FDL tolerances.
    emscripten::function(
        "fdl_point_equal", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_point_f64_t a = from_val_PointF64(a_v);
            fdl_point_f64_t b = from_val_PointF64(b_v);
            auto _r = fdl_point_equal(a, b);
            return val(static_cast<double>(_r));
        }));

    // fdl_point_f64_gt — Check if a > b using OR logic (either x or y is greater).
    emscripten::function(
        "fdl_point_f64_gt", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_point_f64_t a = from_val_PointF64(a_v);
            fdl_point_f64_t b = from_val_PointF64(b_v);
            auto _r = fdl_point_f64_gt(a, b);
            return val(static_cast<double>(_r));
        }));

    // fdl_point_f64_lt — Check if a < b using OR logic (either x or y is less).
    emscripten::function(
        "fdl_point_f64_lt", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_point_f64_t a = from_val_PointF64(a_v);
            fdl_point_f64_t b = from_val_PointF64(b_v);
            auto _r = fdl_point_f64_lt(a, b);
            return val(static_cast<double>(_r));
        }));

    // fdl_point_is_zero — Check if both x and y are zero.
    emscripten::function("fdl_point_is_zero", emscripten::optional_override([](emscripten::val point_v) -> val {
                             fdl_point_f64_t point = from_val_PointF64(point_v);
                             auto _r = fdl_point_is_zero(point);
                             return val(static_cast<double>(_r));
                         }));

    // fdl_point_mul_scalar — Multiply point by scalar.
    emscripten::function(
        "fdl_point_mul_scalar", emscripten::optional_override([](emscripten::val a_v, double scalar) -> val {
            fdl_point_f64_t a = from_val_PointF64(a_v);
            fdl_point_f64_t _r = fdl_point_mul_scalar(a, scalar);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_point_normalize — Normalize a point by applying anamorphic squeeze to x.
    emscripten::function(
        "fdl_point_normalize", emscripten::optional_override([](emscripten::val point_v, double squeeze) -> val {
            fdl_point_f64_t point = from_val_PointF64(point_v);
            fdl_point_f64_t _r = fdl_point_normalize(point, squeeze);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_point_normalize_and_scale — Normalize and scale a point in one step.
    emscripten::function(
        "fdl_point_normalize_and_scale",
        emscripten::optional_override(
            [](emscripten::val point_v, double input_squeeze, double scale_factor, double target_squeeze) -> val {
                fdl_point_f64_t point = from_val_PointF64(point_v);
                fdl_point_f64_t _r = fdl_point_normalize_and_scale(point, input_squeeze, scale_factor, target_squeeze);
                auto _out = to_val_PointF64(_r);
                return _out;
            }));

    // fdl_point_scale — Scale a normalized point and apply target squeeze.
    emscripten::function(
        "fdl_point_scale",
        emscripten::optional_override([](emscripten::val point_v, double scale_factor, double target_squeeze) -> val {
            fdl_point_f64_t point = from_val_PointF64(point_v);
            fdl_point_f64_t _r = fdl_point_scale(point, scale_factor, target_squeeze);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_point_sub — Subtract two points: result = a - b.
    emscripten::function(
        "fdl_point_sub", emscripten::optional_override([](emscripten::val a_v, emscripten::val b_v) -> val {
            fdl_point_f64_t a = from_val_PointF64(a_v);
            fdl_point_f64_t b = from_val_PointF64(b_v);
            fdl_point_f64_t _r = fdl_point_sub(a, b);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_resolve_geometry_layer — Resolve dimensions and anchor directly from canvas/framing handles for a path.
    emscripten::function(
        "fdl_resolve_geometry_layer",
        emscripten::optional_override([](emscripten::val canvas_v, emscripten::val framing_v, unsigned path_i) -> val {
            auto* canvas = unwrap_handle<fdl_canvas_t>(canvas_v);
            auto* framing = unwrap_handle<fdl_framing_decision_t>(framing_v);
            fdl_geometry_path_t path = static_cast<fdl_geometry_path_t>(path_i);
            fdl_dimensions_f64_t out_dims{};
            fdl_point_f64_t out_anchor{};
            auto _r = fdl_resolve_geometry_layer(canvas, framing, path, &out_dims, &out_anchor);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("dims", to_val_DimensionsF64(out_dims));
            _out.set("anchor", to_val_PointF64(out_anchor));
            return _out;
        }));

    // fdl_round — Round a single value according to FDL rounding rules.
    emscripten::function(
        "fdl_round", emscripten::optional_override([](double value, unsigned even_i, unsigned mode_i) -> val {
            fdl_rounding_even_t even = static_cast<fdl_rounding_even_t>(even_i);
            fdl_rounding_mode_t mode = static_cast<fdl_rounding_mode_t>(mode_i);
            auto _r = fdl_round(value, even, mode);
            return val(static_cast<double>(_r));
        }));

    // fdl_round_dimensions — Round dimensions according to FDL rounding rules.
    emscripten::function(
        "fdl_round_dimensions",
        emscripten::optional_override([](emscripten::val dims_v, unsigned even_i, unsigned mode_i) -> val {
            fdl_dimensions_f64_t dims = from_val_DimensionsF64(dims_v);
            fdl_rounding_even_t even = static_cast<fdl_rounding_even_t>(even_i);
            fdl_rounding_mode_t mode = static_cast<fdl_rounding_mode_t>(mode_i);
            fdl_dimensions_f64_t _r = fdl_round_dimensions(dims, even, mode);
            auto _out = to_val_DimensionsF64(_r);
            return _out;
        }));

    // fdl_round_point — Round a point according to FDL rounding rules.
    emscripten::function(
        "fdl_round_point",
        emscripten::optional_override([](emscripten::val point_v, unsigned even_i, unsigned mode_i) -> val {
            fdl_point_f64_t point = from_val_PointF64(point_v);
            fdl_rounding_even_t even = static_cast<fdl_rounding_even_t>(even_i);
            fdl_rounding_mode_t mode = static_cast<fdl_rounding_mode_t>(mode_i);
            fdl_point_f64_t _r = fdl_round_point(point, even, mode);
            auto _out = to_val_PointF64(_r);
            return _out;
        }));

    // fdl_validation_result_error_at — Get a specific error message by index.
    emscripten::function(
        "fdl_validation_result_error_at",
        emscripten::optional_override([](emscripten::val result_v, uint32_t index) -> val {
            auto* result = unwrap_handle<fdl_validation_result_t>(result_v);
            const char* _r = fdl_validation_result_error_at(result, index);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_validation_result_error_count — Get the number of validation errors.
    emscripten::function(
        "fdl_validation_result_error_count", emscripten::optional_override([](emscripten::val result_v) -> val {
            auto* result = unwrap_handle<fdl_validation_result_t>(result_v);
            auto _r = fdl_validation_result_error_count(result);
            return val(static_cast<double>(_r));
        }));

    // fdl_validation_result_free — Free a validation result. Safe to call with NULL.
    emscripten::function(
        "fdl_validation_result_free", emscripten::optional_override([](emscripten::val result_v) -> void {
            if (result_v.isNull() || result_v.isUndefined()) {
                return;
            }
            auto* result = unwrap_handle<fdl_validation_result_t>(result_v);
            fdl_validation_result_free(result);
            return;
        }));

    // fdl_doc_set_custom_attr_string — Custom attr: set_custom_attr_string on FDL
    emscripten::function(
        "fdl_doc_set_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, std::string arg1_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            auto _r = fdl_doc_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_set_custom_attr_int — Custom attr: set_custom_attr_int on FDL
    emscripten::function(
        "fdl_doc_set_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1_d) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            int64_t arg1 = static_cast<int64_t>(arg1_d);
            auto _r = fdl_doc_set_custom_attr_int(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_set_custom_attr_float — Custom attr: set_custom_attr_float on FDL
    emscripten::function(
        "fdl_doc_set_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            auto _r = fdl_doc_set_custom_attr_float(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_set_custom_attr_bool — Custom attr: set_custom_attr_bool on FDL
    emscripten::function(
        "fdl_doc_set_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, int arg1) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            auto _r = fdl_doc_set_custom_attr_bool(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_get_custom_attr_string — Custom attr: get_custom_attr_string on FDL
    emscripten::function(
        "fdl_doc_get_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            const char* _r = fdl_doc_get_custom_attr_string(handle, key_str.c_str());
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_doc_get_custom_attr_int — Custom attr: get_custom_attr_int on FDL
    emscripten::function(
        "fdl_doc_get_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            int64_t out_value{};
            auto _r = fdl_doc_get_custom_attr_int(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_doc_get_custom_attr_float — Custom attr: get_custom_attr_float on FDL
    emscripten::function(
        "fdl_doc_get_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            double out_value{};
            auto _r = fdl_doc_get_custom_attr_float(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_doc_get_custom_attr_bool — Custom attr: get_custom_attr_bool on FDL
    emscripten::function(
        "fdl_doc_get_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            int out_value{};
            auto _r = fdl_doc_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_doc_has_custom_attr — Custom attr: has_custom_attr on FDL
    emscripten::function(
        "fdl_doc_has_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            auto _r = fdl_doc_has_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_get_custom_attr_type — Custom attr: get_custom_attr_type on FDL
    emscripten::function(
        "fdl_doc_get_custom_attr_type",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            auto _r = fdl_doc_get_custom_attr_type(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_remove_custom_attr — Custom attr: remove_custom_attr on FDL
    emscripten::function(
        "fdl_doc_remove_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            auto _r = fdl_doc_remove_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_custom_attrs_count — Custom attr: custom_attrs_count on FDL
    emscripten::function(
        "fdl_doc_custom_attrs_count", emscripten::optional_override([](emscripten::val handle_v) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            auto _r = fdl_doc_custom_attrs_count(handle);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_custom_attr_name_at — Custom attr: custom_attr_name_at on FDL
    emscripten::function(
        "fdl_doc_custom_attr_name_at",
        emscripten::optional_override([](emscripten::val handle_v, uint32_t arg0) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            const char* _r = fdl_doc_custom_attr_name_at(handle, arg0);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_doc_set_custom_attr_point_f64 — Custom attr: set_custom_attr_point_f64 on FDL
    emscripten::function(
        "fdl_doc_set_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            fdl_point_f64_t arg1 = from_val_PointF64(arg1_v);
            auto _r = fdl_doc_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_get_custom_attr_point_f64 — Custom attr: get_custom_attr_point_f64 on FDL
    emscripten::function(
        "fdl_doc_get_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            fdl_point_f64_t out_value{};
            auto _r = fdl_doc_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_PointF64(out_value));
            return _out;
        }));

    // fdl_doc_set_custom_attr_dims_f64 — Custom attr: set_custom_attr_dims_f64 on FDL
    emscripten::function(
        "fdl_doc_set_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            fdl_dimensions_f64_t arg1 = from_val_DimensionsF64(arg1_v);
            auto _r = fdl_doc_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_get_custom_attr_dims_f64 — Custom attr: get_custom_attr_dims_f64 on FDL
    emscripten::function(
        "fdl_doc_get_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            fdl_dimensions_f64_t out_value{};
            auto _r = fdl_doc_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsF64(out_value));
            return _out;
        }));

    // fdl_doc_set_custom_attr_dims_i64 — Custom attr: set_custom_attr_dims_i64 on FDL
    emscripten::function(
        "fdl_doc_set_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            fdl_dimensions_i64_t arg1 = from_val_DimensionsI64(arg1_v);
            auto _r = fdl_doc_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_doc_get_custom_attr_dims_i64 — Custom attr: get_custom_attr_dims_i64 on FDL
    emscripten::function(
        "fdl_doc_get_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_doc_t>(handle_v);
            fdl_dimensions_i64_t out_value{};
            auto _r = fdl_doc_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsI64(out_value));
            return _out;
        }));

    // fdl_context_set_custom_attr_string — Custom attr: set_custom_attr_string on Context
    emscripten::function(
        "fdl_context_set_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, std::string arg1_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            auto _r = fdl_context_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_context_set_custom_attr_int — Custom attr: set_custom_attr_int on Context
    emscripten::function(
        "fdl_context_set_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1_d) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            int64_t arg1 = static_cast<int64_t>(arg1_d);
            auto _r = fdl_context_set_custom_attr_int(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_context_set_custom_attr_float — Custom attr: set_custom_attr_float on Context
    emscripten::function(
        "fdl_context_set_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            auto _r = fdl_context_set_custom_attr_float(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_context_set_custom_attr_bool — Custom attr: set_custom_attr_bool on Context
    emscripten::function(
        "fdl_context_set_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, int arg1) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            auto _r = fdl_context_set_custom_attr_bool(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_context_get_custom_attr_string — Custom attr: get_custom_attr_string on Context
    emscripten::function(
        "fdl_context_get_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            const char* _r = fdl_context_get_custom_attr_string(handle, key_str.c_str());
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_context_get_custom_attr_int — Custom attr: get_custom_attr_int on Context
    emscripten::function(
        "fdl_context_get_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            int64_t out_value{};
            auto _r = fdl_context_get_custom_attr_int(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_context_get_custom_attr_float — Custom attr: get_custom_attr_float on Context
    emscripten::function(
        "fdl_context_get_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            double out_value{};
            auto _r = fdl_context_get_custom_attr_float(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_context_get_custom_attr_bool — Custom attr: get_custom_attr_bool on Context
    emscripten::function(
        "fdl_context_get_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            int out_value{};
            auto _r = fdl_context_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_context_has_custom_attr — Custom attr: has_custom_attr on Context
    emscripten::function(
        "fdl_context_has_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            auto _r = fdl_context_has_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_context_get_custom_attr_type — Custom attr: get_custom_attr_type on Context
    emscripten::function(
        "fdl_context_get_custom_attr_type",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            auto _r = fdl_context_get_custom_attr_type(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_context_remove_custom_attr — Custom attr: remove_custom_attr on Context
    emscripten::function(
        "fdl_context_remove_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            auto _r = fdl_context_remove_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_context_custom_attrs_count — Custom attr: custom_attrs_count on Context
    emscripten::function(
        "fdl_context_custom_attrs_count", emscripten::optional_override([](emscripten::val handle_v) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            auto _r = fdl_context_custom_attrs_count(handle);
            return val(static_cast<double>(_r));
        }));

    // fdl_context_custom_attr_name_at — Custom attr: custom_attr_name_at on Context
    emscripten::function(
        "fdl_context_custom_attr_name_at",
        emscripten::optional_override([](emscripten::val handle_v, uint32_t arg0) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            const char* _r = fdl_context_custom_attr_name_at(handle, arg0);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_context_set_custom_attr_point_f64 — Custom attr: set_custom_attr_point_f64 on Context
    emscripten::function(
        "fdl_context_set_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            fdl_point_f64_t arg1 = from_val_PointF64(arg1_v);
            auto _r = fdl_context_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_context_get_custom_attr_point_f64 — Custom attr: get_custom_attr_point_f64 on Context
    emscripten::function(
        "fdl_context_get_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            fdl_point_f64_t out_value{};
            auto _r = fdl_context_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_PointF64(out_value));
            return _out;
        }));

    // fdl_context_set_custom_attr_dims_f64 — Custom attr: set_custom_attr_dims_f64 on Context
    emscripten::function(
        "fdl_context_set_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            fdl_dimensions_f64_t arg1 = from_val_DimensionsF64(arg1_v);
            auto _r = fdl_context_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_context_get_custom_attr_dims_f64 — Custom attr: get_custom_attr_dims_f64 on Context
    emscripten::function(
        "fdl_context_get_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            fdl_dimensions_f64_t out_value{};
            auto _r = fdl_context_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsF64(out_value));
            return _out;
        }));

    // fdl_context_set_custom_attr_dims_i64 — Custom attr: set_custom_attr_dims_i64 on Context
    emscripten::function(
        "fdl_context_set_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            fdl_dimensions_i64_t arg1 = from_val_DimensionsI64(arg1_v);
            auto _r = fdl_context_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_context_get_custom_attr_dims_i64 — Custom attr: get_custom_attr_dims_i64 on Context
    emscripten::function(
        "fdl_context_get_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_context_t>(handle_v);
            fdl_dimensions_i64_t out_value{};
            auto _r = fdl_context_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsI64(out_value));
            return _out;
        }));

    // fdl_canvas_set_custom_attr_string — Custom attr: set_custom_attr_string on Canvas
    emscripten::function(
        "fdl_canvas_set_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, std::string arg1_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            auto _r = fdl_canvas_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_set_custom_attr_int — Custom attr: set_custom_attr_int on Canvas
    emscripten::function(
        "fdl_canvas_set_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1_d) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            int64_t arg1 = static_cast<int64_t>(arg1_d);
            auto _r = fdl_canvas_set_custom_attr_int(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_set_custom_attr_float — Custom attr: set_custom_attr_float on Canvas
    emscripten::function(
        "fdl_canvas_set_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            auto _r = fdl_canvas_set_custom_attr_float(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_set_custom_attr_bool — Custom attr: set_custom_attr_bool on Canvas
    emscripten::function(
        "fdl_canvas_set_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, int arg1) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            auto _r = fdl_canvas_set_custom_attr_bool(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_get_custom_attr_string — Custom attr: get_custom_attr_string on Canvas
    emscripten::function(
        "fdl_canvas_get_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            const char* _r = fdl_canvas_get_custom_attr_string(handle, key_str.c_str());
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_canvas_get_custom_attr_int — Custom attr: get_custom_attr_int on Canvas
    emscripten::function(
        "fdl_canvas_get_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            int64_t out_value{};
            auto _r = fdl_canvas_get_custom_attr_int(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_canvas_get_custom_attr_float — Custom attr: get_custom_attr_float on Canvas
    emscripten::function(
        "fdl_canvas_get_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            double out_value{};
            auto _r = fdl_canvas_get_custom_attr_float(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_canvas_get_custom_attr_bool — Custom attr: get_custom_attr_bool on Canvas
    emscripten::function(
        "fdl_canvas_get_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            int out_value{};
            auto _r = fdl_canvas_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_canvas_has_custom_attr — Custom attr: has_custom_attr on Canvas
    emscripten::function(
        "fdl_canvas_has_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            auto _r = fdl_canvas_has_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_get_custom_attr_type — Custom attr: get_custom_attr_type on Canvas
    emscripten::function(
        "fdl_canvas_get_custom_attr_type",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            auto _r = fdl_canvas_get_custom_attr_type(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_remove_custom_attr — Custom attr: remove_custom_attr on Canvas
    emscripten::function(
        "fdl_canvas_remove_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            auto _r = fdl_canvas_remove_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_custom_attrs_count — Custom attr: custom_attrs_count on Canvas
    emscripten::function(
        "fdl_canvas_custom_attrs_count", emscripten::optional_override([](emscripten::val handle_v) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            auto _r = fdl_canvas_custom_attrs_count(handle);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_custom_attr_name_at — Custom attr: custom_attr_name_at on Canvas
    emscripten::function(
        "fdl_canvas_custom_attr_name_at",
        emscripten::optional_override([](emscripten::val handle_v, uint32_t arg0) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            const char* _r = fdl_canvas_custom_attr_name_at(handle, arg0);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_canvas_set_custom_attr_point_f64 — Custom attr: set_custom_attr_point_f64 on Canvas
    emscripten::function(
        "fdl_canvas_set_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            fdl_point_f64_t arg1 = from_val_PointF64(arg1_v);
            auto _r = fdl_canvas_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_get_custom_attr_point_f64 — Custom attr: get_custom_attr_point_f64 on Canvas
    emscripten::function(
        "fdl_canvas_get_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            fdl_point_f64_t out_value{};
            auto _r = fdl_canvas_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_PointF64(out_value));
            return _out;
        }));

    // fdl_canvas_set_custom_attr_dims_f64 — Custom attr: set_custom_attr_dims_f64 on Canvas
    emscripten::function(
        "fdl_canvas_set_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            fdl_dimensions_f64_t arg1 = from_val_DimensionsF64(arg1_v);
            auto _r = fdl_canvas_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_get_custom_attr_dims_f64 — Custom attr: get_custom_attr_dims_f64 on Canvas
    emscripten::function(
        "fdl_canvas_get_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            fdl_dimensions_f64_t out_value{};
            auto _r = fdl_canvas_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsF64(out_value));
            return _out;
        }));

    // fdl_canvas_set_custom_attr_dims_i64 — Custom attr: set_custom_attr_dims_i64 on Canvas
    emscripten::function(
        "fdl_canvas_set_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            fdl_dimensions_i64_t arg1 = from_val_DimensionsI64(arg1_v);
            auto _r = fdl_canvas_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_get_custom_attr_dims_i64 — Custom attr: get_custom_attr_dims_i64 on Canvas
    emscripten::function(
        "fdl_canvas_get_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_t>(handle_v);
            fdl_dimensions_i64_t out_value{};
            auto _r = fdl_canvas_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsI64(out_value));
            return _out;
        }));

    // fdl_framing_decision_set_custom_attr_string — Custom attr: set_custom_attr_string on FramingDecision
    emscripten::function(
        "fdl_framing_decision_set_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, std::string arg1_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            auto _r = fdl_framing_decision_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_set_custom_attr_int — Custom attr: set_custom_attr_int on FramingDecision
    emscripten::function(
        "fdl_framing_decision_set_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1_d) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            int64_t arg1 = static_cast<int64_t>(arg1_d);
            auto _r = fdl_framing_decision_set_custom_attr_int(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_set_custom_attr_float — Custom attr: set_custom_attr_float on FramingDecision
    emscripten::function(
        "fdl_framing_decision_set_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            auto _r = fdl_framing_decision_set_custom_attr_float(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_set_custom_attr_bool — Custom attr: set_custom_attr_bool on FramingDecision
    emscripten::function(
        "fdl_framing_decision_set_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, int arg1) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            auto _r = fdl_framing_decision_set_custom_attr_bool(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_get_custom_attr_string — Custom attr: get_custom_attr_string on FramingDecision
    emscripten::function(
        "fdl_framing_decision_get_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            const char* _r = fdl_framing_decision_get_custom_attr_string(handle, key_str.c_str());
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_framing_decision_get_custom_attr_int — Custom attr: get_custom_attr_int on FramingDecision
    emscripten::function(
        "fdl_framing_decision_get_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            int64_t out_value{};
            auto _r = fdl_framing_decision_get_custom_attr_int(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_framing_decision_get_custom_attr_float — Custom attr: get_custom_attr_float on FramingDecision
    emscripten::function(
        "fdl_framing_decision_get_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            double out_value{};
            auto _r = fdl_framing_decision_get_custom_attr_float(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_framing_decision_get_custom_attr_bool — Custom attr: get_custom_attr_bool on FramingDecision
    emscripten::function(
        "fdl_framing_decision_get_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            int out_value{};
            auto _r = fdl_framing_decision_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_framing_decision_has_custom_attr — Custom attr: has_custom_attr on FramingDecision
    emscripten::function(
        "fdl_framing_decision_has_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            auto _r = fdl_framing_decision_has_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_get_custom_attr_type — Custom attr: get_custom_attr_type on FramingDecision
    emscripten::function(
        "fdl_framing_decision_get_custom_attr_type",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            auto _r = fdl_framing_decision_get_custom_attr_type(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_remove_custom_attr — Custom attr: remove_custom_attr on FramingDecision
    emscripten::function(
        "fdl_framing_decision_remove_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            auto _r = fdl_framing_decision_remove_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_custom_attrs_count — Custom attr: custom_attrs_count on FramingDecision
    emscripten::function(
        "fdl_framing_decision_custom_attrs_count", emscripten::optional_override([](emscripten::val handle_v) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            auto _r = fdl_framing_decision_custom_attrs_count(handle);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_custom_attr_name_at — Custom attr: custom_attr_name_at on FramingDecision
    emscripten::function(
        "fdl_framing_decision_custom_attr_name_at",
        emscripten::optional_override([](emscripten::val handle_v, uint32_t arg0) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            const char* _r = fdl_framing_decision_custom_attr_name_at(handle, arg0);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_framing_decision_set_custom_attr_point_f64 — Custom attr: set_custom_attr_point_f64 on FramingDecision
    emscripten::function(
        "fdl_framing_decision_set_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            fdl_point_f64_t arg1 = from_val_PointF64(arg1_v);
            auto _r = fdl_framing_decision_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_get_custom_attr_point_f64 — Custom attr: get_custom_attr_point_f64 on FramingDecision
    emscripten::function(
        "fdl_framing_decision_get_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            fdl_point_f64_t out_value{};
            auto _r = fdl_framing_decision_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_PointF64(out_value));
            return _out;
        }));

    // fdl_framing_decision_set_custom_attr_dims_f64 — Custom attr: set_custom_attr_dims_f64 on FramingDecision
    emscripten::function(
        "fdl_framing_decision_set_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            fdl_dimensions_f64_t arg1 = from_val_DimensionsF64(arg1_v);
            auto _r = fdl_framing_decision_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_get_custom_attr_dims_f64 — Custom attr: get_custom_attr_dims_f64 on FramingDecision
    emscripten::function(
        "fdl_framing_decision_get_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            fdl_dimensions_f64_t out_value{};
            auto _r = fdl_framing_decision_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsF64(out_value));
            return _out;
        }));

    // fdl_framing_decision_set_custom_attr_dims_i64 — Custom attr: set_custom_attr_dims_i64 on FramingDecision
    emscripten::function(
        "fdl_framing_decision_set_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            fdl_dimensions_i64_t arg1 = from_val_DimensionsI64(arg1_v);
            auto _r = fdl_framing_decision_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_decision_get_custom_attr_dims_i64 — Custom attr: get_custom_attr_dims_i64 on FramingDecision
    emscripten::function(
        "fdl_framing_decision_get_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_decision_t>(handle_v);
            fdl_dimensions_i64_t out_value{};
            auto _r = fdl_framing_decision_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsI64(out_value));
            return _out;
        }));

    // fdl_framing_intent_set_custom_attr_string — Custom attr: set_custom_attr_string on FramingIntent
    emscripten::function(
        "fdl_framing_intent_set_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, std::string arg1_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            auto _r = fdl_framing_intent_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_set_custom_attr_int — Custom attr: set_custom_attr_int on FramingIntent
    emscripten::function(
        "fdl_framing_intent_set_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1_d) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            int64_t arg1 = static_cast<int64_t>(arg1_d);
            auto _r = fdl_framing_intent_set_custom_attr_int(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_set_custom_attr_float — Custom attr: set_custom_attr_float on FramingIntent
    emscripten::function(
        "fdl_framing_intent_set_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            auto _r = fdl_framing_intent_set_custom_attr_float(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_set_custom_attr_bool — Custom attr: set_custom_attr_bool on FramingIntent
    emscripten::function(
        "fdl_framing_intent_set_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, int arg1) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            auto _r = fdl_framing_intent_set_custom_attr_bool(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_get_custom_attr_string — Custom attr: get_custom_attr_string on FramingIntent
    emscripten::function(
        "fdl_framing_intent_get_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            const char* _r = fdl_framing_intent_get_custom_attr_string(handle, key_str.c_str());
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_framing_intent_get_custom_attr_int — Custom attr: get_custom_attr_int on FramingIntent
    emscripten::function(
        "fdl_framing_intent_get_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            int64_t out_value{};
            auto _r = fdl_framing_intent_get_custom_attr_int(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_framing_intent_get_custom_attr_float — Custom attr: get_custom_attr_float on FramingIntent
    emscripten::function(
        "fdl_framing_intent_get_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            double out_value{};
            auto _r = fdl_framing_intent_get_custom_attr_float(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_framing_intent_get_custom_attr_bool — Custom attr: get_custom_attr_bool on FramingIntent
    emscripten::function(
        "fdl_framing_intent_get_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            int out_value{};
            auto _r = fdl_framing_intent_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_framing_intent_has_custom_attr — Custom attr: has_custom_attr on FramingIntent
    emscripten::function(
        "fdl_framing_intent_has_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            auto _r = fdl_framing_intent_has_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_get_custom_attr_type — Custom attr: get_custom_attr_type on FramingIntent
    emscripten::function(
        "fdl_framing_intent_get_custom_attr_type",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            auto _r = fdl_framing_intent_get_custom_attr_type(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_remove_custom_attr — Custom attr: remove_custom_attr on FramingIntent
    emscripten::function(
        "fdl_framing_intent_remove_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            auto _r = fdl_framing_intent_remove_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_custom_attrs_count — Custom attr: custom_attrs_count on FramingIntent
    emscripten::function(
        "fdl_framing_intent_custom_attrs_count", emscripten::optional_override([](emscripten::val handle_v) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            auto _r = fdl_framing_intent_custom_attrs_count(handle);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_custom_attr_name_at — Custom attr: custom_attr_name_at on FramingIntent
    emscripten::function(
        "fdl_framing_intent_custom_attr_name_at",
        emscripten::optional_override([](emscripten::val handle_v, uint32_t arg0) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            const char* _r = fdl_framing_intent_custom_attr_name_at(handle, arg0);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_framing_intent_set_custom_attr_point_f64 — Custom attr: set_custom_attr_point_f64 on FramingIntent
    emscripten::function(
        "fdl_framing_intent_set_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            fdl_point_f64_t arg1 = from_val_PointF64(arg1_v);
            auto _r = fdl_framing_intent_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_get_custom_attr_point_f64 — Custom attr: get_custom_attr_point_f64 on FramingIntent
    emscripten::function(
        "fdl_framing_intent_get_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            fdl_point_f64_t out_value{};
            auto _r = fdl_framing_intent_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_PointF64(out_value));
            return _out;
        }));

    // fdl_framing_intent_set_custom_attr_dims_f64 — Custom attr: set_custom_attr_dims_f64 on FramingIntent
    emscripten::function(
        "fdl_framing_intent_set_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            fdl_dimensions_f64_t arg1 = from_val_DimensionsF64(arg1_v);
            auto _r = fdl_framing_intent_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_get_custom_attr_dims_f64 — Custom attr: get_custom_attr_dims_f64 on FramingIntent
    emscripten::function(
        "fdl_framing_intent_get_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            fdl_dimensions_f64_t out_value{};
            auto _r = fdl_framing_intent_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsF64(out_value));
            return _out;
        }));

    // fdl_framing_intent_set_custom_attr_dims_i64 — Custom attr: set_custom_attr_dims_i64 on FramingIntent
    emscripten::function(
        "fdl_framing_intent_set_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            fdl_dimensions_i64_t arg1 = from_val_DimensionsI64(arg1_v);
            auto _r = fdl_framing_intent_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_framing_intent_get_custom_attr_dims_i64 — Custom attr: get_custom_attr_dims_i64 on FramingIntent
    emscripten::function(
        "fdl_framing_intent_get_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_framing_intent_t>(handle_v);
            fdl_dimensions_i64_t out_value{};
            auto _r = fdl_framing_intent_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsI64(out_value));
            return _out;
        }));

    // fdl_canvas_template_set_custom_attr_string — Custom attr: set_custom_attr_string on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_set_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, std::string arg1_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            auto _r = fdl_canvas_template_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_set_custom_attr_int — Custom attr: set_custom_attr_int on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_set_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1_d) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            int64_t arg1 = static_cast<int64_t>(arg1_d);
            auto _r = fdl_canvas_template_set_custom_attr_int(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_set_custom_attr_float — Custom attr: set_custom_attr_float on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_set_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            auto _r = fdl_canvas_template_set_custom_attr_float(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_set_custom_attr_bool — Custom attr: set_custom_attr_bool on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_set_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, int arg1) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            auto _r = fdl_canvas_template_set_custom_attr_bool(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_get_custom_attr_string — Custom attr: get_custom_attr_string on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_get_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            const char* _r = fdl_canvas_template_get_custom_attr_string(handle, key_str.c_str());
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_canvas_template_get_custom_attr_int — Custom attr: get_custom_attr_int on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_get_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            int64_t out_value{};
            auto _r = fdl_canvas_template_get_custom_attr_int(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_canvas_template_get_custom_attr_float — Custom attr: get_custom_attr_float on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_get_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            double out_value{};
            auto _r = fdl_canvas_template_get_custom_attr_float(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_canvas_template_get_custom_attr_bool — Custom attr: get_custom_attr_bool on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_get_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            int out_value{};
            auto _r = fdl_canvas_template_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_canvas_template_has_custom_attr — Custom attr: has_custom_attr on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_has_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            auto _r = fdl_canvas_template_has_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_get_custom_attr_type — Custom attr: get_custom_attr_type on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_get_custom_attr_type",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            auto _r = fdl_canvas_template_get_custom_attr_type(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_remove_custom_attr — Custom attr: remove_custom_attr on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_remove_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            auto _r = fdl_canvas_template_remove_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_custom_attrs_count — Custom attr: custom_attrs_count on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_custom_attrs_count", emscripten::optional_override([](emscripten::val handle_v) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            auto _r = fdl_canvas_template_custom_attrs_count(handle);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_custom_attr_name_at — Custom attr: custom_attr_name_at on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_custom_attr_name_at",
        emscripten::optional_override([](emscripten::val handle_v, uint32_t arg0) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            const char* _r = fdl_canvas_template_custom_attr_name_at(handle, arg0);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_canvas_template_set_custom_attr_point_f64 — Custom attr: set_custom_attr_point_f64 on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_set_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            fdl_point_f64_t arg1 = from_val_PointF64(arg1_v);
            auto _r = fdl_canvas_template_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_get_custom_attr_point_f64 — Custom attr: get_custom_attr_point_f64 on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_get_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            fdl_point_f64_t out_value{};
            auto _r = fdl_canvas_template_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_PointF64(out_value));
            return _out;
        }));

    // fdl_canvas_template_set_custom_attr_dims_f64 — Custom attr: set_custom_attr_dims_f64 on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_set_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            fdl_dimensions_f64_t arg1 = from_val_DimensionsF64(arg1_v);
            auto _r = fdl_canvas_template_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_get_custom_attr_dims_f64 — Custom attr: get_custom_attr_dims_f64 on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_get_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            fdl_dimensions_f64_t out_value{};
            auto _r = fdl_canvas_template_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsF64(out_value));
            return _out;
        }));

    // fdl_canvas_template_set_custom_attr_dims_i64 — Custom attr: set_custom_attr_dims_i64 on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_set_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            fdl_dimensions_i64_t arg1 = from_val_DimensionsI64(arg1_v);
            auto _r = fdl_canvas_template_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_canvas_template_get_custom_attr_dims_i64 — Custom attr: get_custom_attr_dims_i64 on CanvasTemplate
    emscripten::function(
        "fdl_canvas_template_get_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_canvas_template_t>(handle_v);
            fdl_dimensions_i64_t out_value{};
            auto _r = fdl_canvas_template_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsI64(out_value));
            return _out;
        }));

    // fdl_clip_id_set_custom_attr_string — Custom attr: set_custom_attr_string on ClipID
    emscripten::function(
        "fdl_clip_id_set_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, std::string arg1_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            auto _r = fdl_clip_id_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_set_custom_attr_int — Custom attr: set_custom_attr_int on ClipID
    emscripten::function(
        "fdl_clip_id_set_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1_d) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            int64_t arg1 = static_cast<int64_t>(arg1_d);
            auto _r = fdl_clip_id_set_custom_attr_int(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_set_custom_attr_float — Custom attr: set_custom_attr_float on ClipID
    emscripten::function(
        "fdl_clip_id_set_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            auto _r = fdl_clip_id_set_custom_attr_float(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_set_custom_attr_bool — Custom attr: set_custom_attr_bool on ClipID
    emscripten::function(
        "fdl_clip_id_set_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, int arg1) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            auto _r = fdl_clip_id_set_custom_attr_bool(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_get_custom_attr_string — Custom attr: get_custom_attr_string on ClipID
    emscripten::function(
        "fdl_clip_id_get_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            const char* _r = fdl_clip_id_get_custom_attr_string(handle, key_str.c_str());
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_clip_id_get_custom_attr_int — Custom attr: get_custom_attr_int on ClipID
    emscripten::function(
        "fdl_clip_id_get_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            int64_t out_value{};
            auto _r = fdl_clip_id_get_custom_attr_int(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_clip_id_get_custom_attr_float — Custom attr: get_custom_attr_float on ClipID
    emscripten::function(
        "fdl_clip_id_get_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            double out_value{};
            auto _r = fdl_clip_id_get_custom_attr_float(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_clip_id_get_custom_attr_bool — Custom attr: get_custom_attr_bool on ClipID
    emscripten::function(
        "fdl_clip_id_get_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            int out_value{};
            auto _r = fdl_clip_id_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_clip_id_has_custom_attr — Custom attr: has_custom_attr on ClipID
    emscripten::function(
        "fdl_clip_id_has_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            auto _r = fdl_clip_id_has_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_get_custom_attr_type — Custom attr: get_custom_attr_type on ClipID
    emscripten::function(
        "fdl_clip_id_get_custom_attr_type",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            auto _r = fdl_clip_id_get_custom_attr_type(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_remove_custom_attr — Custom attr: remove_custom_attr on ClipID
    emscripten::function(
        "fdl_clip_id_remove_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            auto _r = fdl_clip_id_remove_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_custom_attrs_count — Custom attr: custom_attrs_count on ClipID
    emscripten::function(
        "fdl_clip_id_custom_attrs_count", emscripten::optional_override([](emscripten::val handle_v) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            auto _r = fdl_clip_id_custom_attrs_count(handle);
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_custom_attr_name_at — Custom attr: custom_attr_name_at on ClipID
    emscripten::function(
        "fdl_clip_id_custom_attr_name_at",
        emscripten::optional_override([](emscripten::val handle_v, uint32_t arg0) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            const char* _r = fdl_clip_id_custom_attr_name_at(handle, arg0);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_clip_id_set_custom_attr_point_f64 — Custom attr: set_custom_attr_point_f64 on ClipID
    emscripten::function(
        "fdl_clip_id_set_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            fdl_point_f64_t arg1 = from_val_PointF64(arg1_v);
            auto _r = fdl_clip_id_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_get_custom_attr_point_f64 — Custom attr: get_custom_attr_point_f64 on ClipID
    emscripten::function(
        "fdl_clip_id_get_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            fdl_point_f64_t out_value{};
            auto _r = fdl_clip_id_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_PointF64(out_value));
            return _out;
        }));

    // fdl_clip_id_set_custom_attr_dims_f64 — Custom attr: set_custom_attr_dims_f64 on ClipID
    emscripten::function(
        "fdl_clip_id_set_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            fdl_dimensions_f64_t arg1 = from_val_DimensionsF64(arg1_v);
            auto _r = fdl_clip_id_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_get_custom_attr_dims_f64 — Custom attr: get_custom_attr_dims_f64 on ClipID
    emscripten::function(
        "fdl_clip_id_get_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            fdl_dimensions_f64_t out_value{};
            auto _r = fdl_clip_id_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsF64(out_value));
            return _out;
        }));

    // fdl_clip_id_set_custom_attr_dims_i64 — Custom attr: set_custom_attr_dims_i64 on ClipID
    emscripten::function(
        "fdl_clip_id_set_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            fdl_dimensions_i64_t arg1 = from_val_DimensionsI64(arg1_v);
            auto _r = fdl_clip_id_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_clip_id_get_custom_attr_dims_i64 — Custom attr: get_custom_attr_dims_i64 on ClipID
    emscripten::function(
        "fdl_clip_id_get_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_clip_id_t>(handle_v);
            fdl_dimensions_i64_t out_value{};
            auto _r = fdl_clip_id_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsI64(out_value));
            return _out;
        }));

    // fdl_file_sequence_set_custom_attr_string — Custom attr: set_custom_attr_string on FileSequence
    emscripten::function(
        "fdl_file_sequence_set_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, std::string arg1_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            auto _r = fdl_file_sequence_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_set_custom_attr_int — Custom attr: set_custom_attr_int on FileSequence
    emscripten::function(
        "fdl_file_sequence_set_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1_d) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            int64_t arg1 = static_cast<int64_t>(arg1_d);
            auto _r = fdl_file_sequence_set_custom_attr_int(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_set_custom_attr_float — Custom attr: set_custom_attr_float on FileSequence
    emscripten::function(
        "fdl_file_sequence_set_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, double arg1) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            auto _r = fdl_file_sequence_set_custom_attr_float(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_set_custom_attr_bool — Custom attr: set_custom_attr_bool on FileSequence
    emscripten::function(
        "fdl_file_sequence_set_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, int arg1) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            auto _r = fdl_file_sequence_set_custom_attr_bool(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_get_custom_attr_string — Custom attr: get_custom_attr_string on FileSequence
    emscripten::function(
        "fdl_file_sequence_get_custom_attr_string",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            const char* _r = fdl_file_sequence_get_custom_attr_string(handle, key_str.c_str());
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_file_sequence_get_custom_attr_int — Custom attr: get_custom_attr_int on FileSequence
    emscripten::function(
        "fdl_file_sequence_get_custom_attr_int",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            int64_t out_value{};
            auto _r = fdl_file_sequence_get_custom_attr_int(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_file_sequence_get_custom_attr_float — Custom attr: get_custom_attr_float on FileSequence
    emscripten::function(
        "fdl_file_sequence_get_custom_attr_float",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            double out_value{};
            auto _r = fdl_file_sequence_get_custom_attr_float(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_file_sequence_get_custom_attr_bool — Custom attr: get_custom_attr_bool on FileSequence
    emscripten::function(
        "fdl_file_sequence_get_custom_attr_bool",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            int out_value{};
            auto _r = fdl_file_sequence_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", static_cast<double>(out_value));
            return _out;
        }));

    // fdl_file_sequence_has_custom_attr — Custom attr: has_custom_attr on FileSequence
    emscripten::function(
        "fdl_file_sequence_has_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            auto _r = fdl_file_sequence_has_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_get_custom_attr_type — Custom attr: get_custom_attr_type on FileSequence
    emscripten::function(
        "fdl_file_sequence_get_custom_attr_type",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            auto _r = fdl_file_sequence_get_custom_attr_type(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_remove_custom_attr — Custom attr: remove_custom_attr on FileSequence
    emscripten::function(
        "fdl_file_sequence_remove_custom_attr",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            auto _r = fdl_file_sequence_remove_custom_attr(handle, key_str.c_str());
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_custom_attrs_count — Custom attr: custom_attrs_count on FileSequence
    emscripten::function(
        "fdl_file_sequence_custom_attrs_count", emscripten::optional_override([](emscripten::val handle_v) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            auto _r = fdl_file_sequence_custom_attrs_count(handle);
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_custom_attr_name_at — Custom attr: custom_attr_name_at on FileSequence
    emscripten::function(
        "fdl_file_sequence_custom_attr_name_at",
        emscripten::optional_override([](emscripten::val handle_v, uint32_t arg0) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            const char* _r = fdl_file_sequence_custom_attr_name_at(handle, arg0);
            return _r ? val(std::string(_r)) : val::null();
        }));

    // fdl_file_sequence_set_custom_attr_point_f64 — Custom attr: set_custom_attr_point_f64 on FileSequence
    emscripten::function(
        "fdl_file_sequence_set_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            fdl_point_f64_t arg1 = from_val_PointF64(arg1_v);
            auto _r = fdl_file_sequence_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_get_custom_attr_point_f64 — Custom attr: get_custom_attr_point_f64 on FileSequence
    emscripten::function(
        "fdl_file_sequence_get_custom_attr_point_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            fdl_point_f64_t out_value{};
            auto _r = fdl_file_sequence_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_PointF64(out_value));
            return _out;
        }));

    // fdl_file_sequence_set_custom_attr_dims_f64 — Custom attr: set_custom_attr_dims_f64 on FileSequence
    emscripten::function(
        "fdl_file_sequence_set_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            fdl_dimensions_f64_t arg1 = from_val_DimensionsF64(arg1_v);
            auto _r = fdl_file_sequence_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_get_custom_attr_dims_f64 — Custom attr: get_custom_attr_dims_f64 on FileSequence
    emscripten::function(
        "fdl_file_sequence_get_custom_attr_dims_f64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            fdl_dimensions_f64_t out_value{};
            auto _r = fdl_file_sequence_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsF64(out_value));
            return _out;
        }));

    // fdl_file_sequence_set_custom_attr_dims_i64 — Custom attr: set_custom_attr_dims_i64 on FileSequence
    emscripten::function(
        "fdl_file_sequence_set_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str, emscripten::val arg1_v) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            fdl_dimensions_i64_t arg1 = from_val_DimensionsI64(arg1_v);
            auto _r = fdl_file_sequence_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
            return val(static_cast<double>(_r));
        }));

    // fdl_file_sequence_get_custom_attr_dims_i64 — Custom attr: get_custom_attr_dims_i64 on FileSequence
    emscripten::function(
        "fdl_file_sequence_get_custom_attr_dims_i64",
        emscripten::optional_override([](emscripten::val handle_v, std::string key_str) -> val {
            auto* handle = unwrap_handle<fdl_file_sequence_t>(handle_v);
            fdl_dimensions_i64_t out_value{};
            auto _r = fdl_file_sequence_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
            auto _out = val::object();
            _out.set("_return", static_cast<double>(_r));
            _out.set("value", to_val_DimensionsI64(out_value));
            return _out;
        }));
}
