// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file binding.cc
 * @brief N-API addon wrapping all fdl_core C functions.
 *
 * Each exported function extracts arguments from Napi::CallbackInfo,
 * calls the underlying C function, and converts the result back to
 * a JavaScript value.
 */

#include "fdl/fdl_core.h"
#include "structs.h"
#include <napi.h>
#include <string>

// -----------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------

static void* UnwrapHandle(const Napi::Value& val) {
    return val.As<Napi::External<void>>().Data();
}

// -----------------------------------------------------------------------
// Wrapper functions
// -----------------------------------------------------------------------

// Return the ABI version of the loaded library.
Napi::Value Wrap_fdl_abi_version(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_abi_version_t _r = fdl_abi_version();
    return AbiVersionToObject(env, _r);
}

// Calculate content translation shift for a single axis.
Napi::Value Wrap_fdl_alignment_shift(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    double fit_size = info[0].As<Napi::Number>().DoubleValue();
    double fit_anchor = info[1].As<Napi::Number>().DoubleValue();
    double output_size = info[2].As<Napi::Number>().DoubleValue();
    double canvas_size = info[3].As<Napi::Number>().DoubleValue();
    double target_size = info[4].As<Napi::Number>().DoubleValue();
    int is_center = info[5].As<Napi::Number>().Int32Value();
    double align_factor = info[6].As<Napi::Number>().DoubleValue();
    int pad_to_max = info[7].As<Napi::Number>().Int32Value();
    auto _r = fdl_alignment_shift(
        fit_size, fit_anchor, output_size, canvas_size, target_size, is_center, align_factor, pad_to_max);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Apply a canvas template to a source canvas/framing.
Napi::Value Wrap_fdl_apply_canvas_template(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* tmpl = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto* source_canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[1]));
    auto* source_framing = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[2]));
    std::string new_canvas_id_str = info[3].As<Napi::String>().Utf8Value();
    std::string new_fd_name_str = info[4].As<Napi::String>().Utf8Value();
    bool source_context_label_is_null = info[5].IsNull() || info[5].IsUndefined();
    std::string source_context_label_str =
        source_context_label_is_null ? std::string() : info[5].As<Napi::String>().Utf8Value();
    bool context_creator_is_null = info[6].IsNull() || info[6].IsUndefined();
    std::string context_creator_str = context_creator_is_null ? std::string() : info[6].As<Napi::String>().Utf8Value();
    fdl_template_result_t _r = fdl_apply_canvas_template(
        tmpl,
        source_canvas,
        source_framing,
        new_canvas_id_str.c_str(),
        new_fd_name_str.c_str(),
        (source_context_label_is_null ? nullptr : source_context_label_str.c_str()),
        (context_creator_is_null ? nullptr : context_creator_str.c_str()));
    return TemplateResultToObject(env, _r);
}

// Calculate scale factor based on fit method.
Napi::Value Wrap_fdl_calculate_scale_factor(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t fit_norm = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_dimensions_f64_t target_norm = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    fdl_fit_method_t fit_method = static_cast<fdl_fit_method_t>(info[2].As<Napi::Number>().Uint32Value());
    auto _r = fdl_calculate_scale_factor(fit_norm, target_norm, fit_method);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Add a framing decision to a canvas.
Napi::Value Wrap_fdl_canvas_add_framing_decision(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string id_str = info[1].As<Napi::String>().Utf8Value();
    std::string label_str = info[2].As<Napi::String>().Utf8Value();
    std::string framing_intent_id_str = info[3].As<Napi::String>().Utf8Value();
    double dim_w = info[4].As<Napi::Number>().DoubleValue();
    double dim_h = info[5].As<Napi::Number>().DoubleValue();
    double anchor_x = info[6].As<Napi::Number>().DoubleValue();
    double anchor_y = info[7].As<Napi::Number>().DoubleValue();
    auto* _r = fdl_canvas_add_framing_decision(
        canvas, id_str.c_str(), label_str.c_str(), framing_intent_id_str.c_str(), dim_w, dim_h, anchor_x, anchor_y);
    return Napi::External<void>::New(env, _r);
}

// Find a framing decision by its ID within a canvas.
Napi::Value Wrap_fdl_canvas_find_framing_decision_by_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string id_str = info[1].As<Napi::String>().Utf8Value();
    auto* _r = fdl_canvas_find_framing_decision_by_id(canvas, id_str.c_str());
    if (!_r) {
        return env.Null();
    }
    return Napi::External<void>::New(env, _r);
}

// Get a framing decision by index within a canvas.
Napi::Value Wrap_fdl_canvas_framing_decision_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();
    auto* _r = fdl_canvas_framing_decision_at(canvas, index);
    return Napi::External<void>::New(env, _r);
}

// Get the number of framing decisions in a canvas.
Napi::Value Wrap_fdl_canvas_framing_decisions_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_framing_decisions_count(canvas);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the anamorphic squeeze factor.
Napi::Value Wrap_fdl_canvas_get_anamorphic_squeeze(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_get_anamorphic_squeeze(canvas);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the canvas dimensions in pixels.
Napi::Value Wrap_fdl_canvas_get_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t _r = fdl_canvas_get_dimensions(canvas);
    return DimensionsI64ToObject(env, _r);
}

// Get the effective anchor point (offset from canvas origin).
Napi::Value Wrap_fdl_canvas_get_effective_anchor_point(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_point_f64_t _r = fdl_canvas_get_effective_anchor_point(canvas);
    return PointF64ToObject(env, _r);
}

// Get effective (active image area) dimensions.
Napi::Value Wrap_fdl_canvas_get_effective_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t _r = fdl_canvas_get_effective_dimensions(canvas);
    return DimensionsI64ToObject(env, _r);
}

// Get the effective (active image) rect of a canvas.
Napi::Value Wrap_fdl_canvas_get_effective_rect(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_rect_t out_rect = {};
    int _rv = fdl_canvas_get_effective_rect(canvas, &out_rect);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("rect", RectToObject(env, out_rect));
    return _out;
}

// Get the ID of a canvas.
Napi::Value Wrap_fdl_canvas_get_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_canvas_get_id(canvas);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the label of a canvas.
Napi::Value Wrap_fdl_canvas_get_label(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_canvas_get_label(canvas);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get photosite (sensor) dimensions.
Napi::Value Wrap_fdl_canvas_get_photosite_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t _r = fdl_canvas_get_photosite_dimensions(canvas);
    return DimensionsI64ToObject(env, _r);
}

// Get physical dimensions (e.g. millimeters on sensor).
Napi::Value Wrap_fdl_canvas_get_physical_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_f64_t _r = fdl_canvas_get_physical_dimensions(canvas);
    return DimensionsF64ToObject(env, _r);
}

// Get the full canvas rect: (0, 0, dims.width, dims.height).
Napi::Value Wrap_fdl_canvas_get_rect(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_rect_t _r = fdl_canvas_get_rect(canvas);
    return RectToObject(env, _r);
}

// Get the source_canvas_id of a canvas (the canvas this was derived from).
Napi::Value Wrap_fdl_canvas_get_source_canvas_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_canvas_get_source_canvas_id(canvas);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Check if the canvas has effective dimensions set.
Napi::Value Wrap_fdl_canvas_has_effective_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_has_effective_dimensions(canvas);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if the canvas has photosite dimensions set.
Napi::Value Wrap_fdl_canvas_has_photosite_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_has_photosite_dimensions(canvas);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if the canvas has physical dimensions set.
Napi::Value Wrap_fdl_canvas_has_physical_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_has_physical_dimensions(canvas);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Remove effective dimensions and anchor from a canvas.
void Wrap_fdl_canvas_remove_effective(const Napi::CallbackInfo& info) {
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_canvas_remove_effective(canvas);
}

// Set anamorphic squeeze on a canvas.
void Wrap_fdl_canvas_set_anamorphic_squeeze(const Napi::CallbackInfo& info) {
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    double squeeze = info[1].As<Napi::Number>().DoubleValue();
    fdl_canvas_set_anamorphic_squeeze(canvas, squeeze);
}

// Set dimensions on a canvas.
void Wrap_fdl_canvas_set_dimensions(const Napi::CallbackInfo& info) {
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t dims = ObjectToDimensionsI64(info[1].As<Napi::Object>());
    fdl_canvas_set_dimensions(canvas, dims);
}

// Set effective dimensions and anchor on a canvas.
void Wrap_fdl_canvas_set_effective_dimensions(const Napi::CallbackInfo& info) {
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t dims = ObjectToDimensionsI64(info[1].As<Napi::Object>());
    fdl_point_f64_t anchor = ObjectToPointF64(info[2].As<Napi::Object>());
    fdl_canvas_set_effective_dimensions(canvas, dims, anchor);
}

// Set effective dimensions on a canvas.
void Wrap_fdl_canvas_set_effective_dims_only(const Napi::CallbackInfo& info) {
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t dims = ObjectToDimensionsI64(info[1].As<Napi::Object>());
    fdl_canvas_set_effective_dims_only(canvas, dims);
}

// Set photosite dimensions on a canvas.
void Wrap_fdl_canvas_set_photosite_dimensions(const Napi::CallbackInfo& info) {
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t dims = ObjectToDimensionsI64(info[1].As<Napi::Object>());
    fdl_canvas_set_photosite_dimensions(canvas, dims);
}

// Set physical dimensions on a canvas.
void Wrap_fdl_canvas_set_physical_dimensions(const Napi::CallbackInfo& info) {
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    fdl_canvas_set_physical_dimensions(canvas, dims);
}

// Get the horizontal alignment method.
Napi::Value Wrap_fdl_canvas_template_get_alignment_method_horizontal(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_get_alignment_method_horizontal(ct);
    return Napi::Number::New(env, static_cast<uint32_t>(_r));
}

// Get the vertical alignment method.
Napi::Value Wrap_fdl_canvas_template_get_alignment_method_vertical(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_get_alignment_method_vertical(ct);
    return Napi::Number::New(env, static_cast<uint32_t>(_r));
}

// Get the fit method — how source is scaled into target.
Napi::Value Wrap_fdl_canvas_template_get_fit_method(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_get_fit_method(ct);
    return Napi::Number::New(env, static_cast<uint32_t>(_r));
}

// Get the fit source — which dimension layer to scale from.
Napi::Value Wrap_fdl_canvas_template_get_fit_source(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_get_fit_source(ct);
    return Napi::Number::New(env, static_cast<uint32_t>(_r));
}

// Get the ID of a canvas template.
Napi::Value Wrap_fdl_canvas_template_get_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_canvas_template_get_id(ct);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the label of a canvas template.
Napi::Value Wrap_fdl_canvas_template_get_label(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_canvas_template_get_label(ct);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the maximum_dimensions constraint.
Napi::Value Wrap_fdl_canvas_template_get_maximum_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t _r = fdl_canvas_template_get_maximum_dimensions(ct);
    return DimensionsI64ToObject(env, _r);
}

// Get the pad_to_maximum flag.
Napi::Value Wrap_fdl_canvas_template_get_pad_to_maximum(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_get_pad_to_maximum(ct);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the preserve_from_source_canvas geometry path.
Napi::Value Wrap_fdl_canvas_template_get_preserve_from_source_canvas(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_get_preserve_from_source_canvas(ct);
    return Napi::Number::New(env, static_cast<uint32_t>(_r));
}

// Get the rounding strategy.
Napi::Value Wrap_fdl_canvas_template_get_round(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    fdl_round_strategy_t _r = fdl_canvas_template_get_round(ct);
    return RoundStrategyToObject(env, _r);
}

// Get the target anamorphic squeeze factor.
Napi::Value Wrap_fdl_canvas_template_get_target_anamorphic_squeeze(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_get_target_anamorphic_squeeze(ct);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the target dimensions of a canvas template.
Napi::Value Wrap_fdl_canvas_template_get_target_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t _r = fdl_canvas_template_get_target_dimensions(ct);
    return DimensionsI64ToObject(env, _r);
}

// Check if maximum_dimensions constraint is set.
Napi::Value Wrap_fdl_canvas_template_has_maximum_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_has_maximum_dimensions(ct);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if preserve_from_source_canvas is set.
Napi::Value Wrap_fdl_canvas_template_has_preserve_from_source_canvas(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_has_preserve_from_source_canvas(ct);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Set maximum_dimensions on a canvas template.
void Wrap_fdl_canvas_template_set_maximum_dimensions(const Napi::CallbackInfo& info) {
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t dims = ObjectToDimensionsI64(info[1].As<Napi::Object>());
    fdl_canvas_template_set_maximum_dimensions(ct, dims);
}

// Set pad_to_maximum flag on a canvas template.
void Wrap_fdl_canvas_template_set_pad_to_maximum(const Napi::CallbackInfo& info) {
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    int pad = info[1].As<Napi::Number>().Int32Value();
    fdl_canvas_template_set_pad_to_maximum(ct, pad);
}

// Set preserve_from_source_canvas on a canvas template.
void Wrap_fdl_canvas_template_set_preserve_from_source_canvas(const Napi::CallbackInfo& info) {
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    fdl_geometry_path_t path = static_cast<fdl_geometry_path_t>(info[1].As<Napi::Number>().Uint32Value());
    fdl_canvas_template_set_preserve_from_source_canvas(ct, path);
}

// Serialize a canvas template to canonical JSON.
Napi::Value Wrap_fdl_canvas_template_to_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ct = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    int indent = info[1].As<Napi::Number>().Int32Value();
    auto* _r = fdl_canvas_template_to_json(ct, indent);
    if (!_r) {
        Napi::Error::New(env, "fdl_canvas_template_to_json returned NULL").ThrowAsJavaScriptException();
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Serialize a canvas sub-object to canonical JSON.
Napi::Value Wrap_fdl_canvas_to_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    int indent = info[1].As<Napi::Number>().Int32Value();
    auto* _r = fdl_canvas_to_json(canvas, indent);
    if (!_r) {
        Napi::Error::New(env, "fdl_canvas_to_json returned NULL").ThrowAsJavaScriptException();
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Get the clip_name from a clip_id.
Napi::Value Wrap_fdl_clip_id_get_clip_name(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* cid = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_clip_id_get_clip_name(cid);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the file path from a clip_id.
Napi::Value Wrap_fdl_clip_id_get_file(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* cid = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_clip_id_get_file(cid);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Check if a clip_id has a file path.
Napi::Value Wrap_fdl_clip_id_has_file(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* cid = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_clip_id_has_file(cid);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if a clip_id has a file sequence.
Napi::Value Wrap_fdl_clip_id_has_sequence(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* cid = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_clip_id_has_sequence(cid);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the file sequence handle from a clip_id.
Napi::Value Wrap_fdl_clip_id_sequence(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* cid = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    auto* _r = fdl_clip_id_sequence(cid);
    return Napi::External<void>::New(env, _r);
}

// Serialize a clip_id to canonical JSON.
Napi::Value Wrap_fdl_clip_id_to_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* cid = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    int indent = info[1].As<Napi::Number>().Int32Value();
    auto* _r = fdl_clip_id_to_json(cid, indent);
    if (!_r) {
        Napi::Error::New(env, "fdl_clip_id_to_json returned NULL").ThrowAsJavaScriptException();
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Validate clip_id JSON for mutual exclusion (file vs sequence).
Napi::Value Wrap_fdl_clip_id_validate_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string json_str_str = info[0].As<Napi::String>().Utf8Value();
    size_t json_len = static_cast<size_t>(info[1].As<Napi::Number>().Int64Value());
    auto* _r = fdl_clip_id_validate_json(json_str_str.c_str(), json_len);
    if (!_r) {
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Compute a framing decision from a framing intent.
Napi::Value Wrap_fdl_compute_framing_from_intent(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t canvas_dims = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_dimensions_f64_t working_dims = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    double squeeze = info[2].As<Napi::Number>().DoubleValue();
    fdl_dimensions_i64_t aspect_ratio = ObjectToDimensionsI64(info[3].As<Napi::Object>());
    double protection = info[4].As<Napi::Number>().DoubleValue();
    fdl_round_strategy_t rounding = ObjectToRoundStrategy(info[5].As<Napi::Object>());
    fdl_from_intent_result_t _r =
        fdl_compute_framing_from_intent(canvas_dims, working_dims, squeeze, aspect_ratio, protection, rounding);
    return FromIntentResultToObject(env, _r);
}

// Add a canvas to a context.
Napi::Value Wrap_fdl_context_add_canvas(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string id_str = info[1].As<Napi::String>().Utf8Value();
    std::string label_str = info[2].As<Napi::String>().Utf8Value();
    std::string source_canvas_id_str = info[3].As<Napi::String>().Utf8Value();
    int64_t dim_w = static_cast<int64_t>(info[4].As<Napi::Number>().Int64Value());
    int64_t dim_h = static_cast<int64_t>(info[5].As<Napi::Number>().Int64Value());
    double squeeze = info[6].As<Napi::Number>().DoubleValue();
    auto* _r = fdl_context_add_canvas(
        ctx, id_str.c_str(), label_str.c_str(), source_canvas_id_str.c_str(), dim_w, dim_h, squeeze);
    return Napi::External<void>::New(env, _r);
}

// Get a canvas by index within a context.
Napi::Value Wrap_fdl_context_canvas_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();
    auto* _r = fdl_context_canvas_at(ctx, index);
    return Napi::External<void>::New(env, _r);
}

// Get the number of canvases in a context.
Napi::Value Wrap_fdl_context_canvases_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_context_canvases_count(ctx);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the clip_id handle from a context.
Napi::Value Wrap_fdl_context_clip_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    auto* _r = fdl_context_clip_id(ctx);
    return Napi::External<void>::New(env, _r);
}

// Find a canvas by its ID within a context.
Napi::Value Wrap_fdl_context_find_canvas_by_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string id_str = info[1].As<Napi::String>().Utf8Value();
    auto* _r = fdl_context_find_canvas_by_id(ctx, id_str.c_str());
    if (!_r) {
        return env.Null();
    }
    return Napi::External<void>::New(env, _r);
}

// Get clip_id as a JSON string.
Napi::Value Wrap_fdl_context_get_clip_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    auto* _r = fdl_context_get_clip_id(ctx);
    if (!_r) {
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Get the context_creator of a context.
Napi::Value Wrap_fdl_context_get_context_creator(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_context_get_context_creator(ctx);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the label of a context.
Napi::Value Wrap_fdl_context_get_label(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_context_get_label(ctx);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Check if a context has a clip_id.
Napi::Value Wrap_fdl_context_has_clip_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_context_has_clip_id(ctx);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Remove clip_id from a context. Safe to call if not present.
void Wrap_fdl_context_remove_clip_id(const Napi::CallbackInfo& info) {
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    fdl_context_remove_clip_id(ctx);
}

// Resolve canvas for given input dimensions.
Napi::Value Wrap_fdl_context_resolve_canvas_for_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_f64_t input_dims = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[2]));
    auto* framing = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[3]));
    fdl_resolve_canvas_result_t _r = fdl_context_resolve_canvas_for_dimensions(ctx, input_dims, canvas, framing);
    return ResolveCanvasResultToObject(env, _r);
}

// Set clip_id on a context from a JSON string.
Napi::Value Wrap_fdl_context_set_clip_id_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string json_str_str = info[1].As<Napi::String>().Utf8Value();
    size_t json_len = static_cast<size_t>(info[2].As<Napi::Number>().Int64Value());
    auto* _r = fdl_context_set_clip_id_json(ctx, json_str_str.c_str(), json_len);
    if (!_r) {
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Serialize a context sub-object to canonical JSON.
Napi::Value Wrap_fdl_context_to_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* ctx = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    int indent = info[1].As<Napi::Number>().Int32Value();
    auto* _r = fdl_context_to_json(ctx, indent);
    if (!_r) {
        Napi::Error::New(env, "fdl_context_to_json returned NULL").ThrowAsJavaScriptException();
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Clamp dimensions to maximum bounds.
Napi::Value Wrap_fdl_dimensions_clamp_to_dims(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_dimensions_f64_t clamp_dims = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    fdl_point_f64_t out_delta = {};
    fdl_dimensions_f64_t _rv = fdl_dimensions_clamp_to_dims(dims, clamp_dims, &out_delta);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", DimensionsF64ToObject(env, _rv));
    _out.Set("delta", PointF64ToObject(env, out_delta));
    return _out;
}

// Check if dimensions are approximately equal within FDL tolerance.
Napi::Value Wrap_fdl_dimensions_equal(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t a = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_dimensions_f64_t b = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    auto _r = fdl_dimensions_equal(a, b);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if a > b using OR logic (either width or height is greater).
Napi::Value Wrap_fdl_dimensions_f64_gt(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t a = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_dimensions_f64_t b = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    auto _r = fdl_dimensions_f64_gt(a, b);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if a < b using OR logic (either width or height is less).
Napi::Value Wrap_fdl_dimensions_f64_lt(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t a = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_dimensions_f64_t b = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    auto _r = fdl_dimensions_f64_lt(a, b);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Convert float dimensions to int64 by truncation.
Napi::Value Wrap_fdl_dimensions_f64_to_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_dimensions_i64_t _r = fdl_dimensions_f64_to_i64(dims);
    return DimensionsI64ToObject(env, _r);
}

// Check if a > b using OR logic (either width or height is greater).
Napi::Value Wrap_fdl_dimensions_i64_gt(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_i64_t a = ObjectToDimensionsI64(info[0].As<Napi::Object>());
    fdl_dimensions_i64_t b = ObjectToDimensionsI64(info[1].As<Napi::Object>());
    auto _r = fdl_dimensions_i64_gt(a, b);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if both width and height are zero (int64 variant).
Napi::Value Wrap_fdl_dimensions_i64_is_zero(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_i64_t dims = ObjectToDimensionsI64(info[0].As<Napi::Object>());
    auto _r = fdl_dimensions_i64_is_zero(dims);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if a < b using OR logic (either width or height is less).
Napi::Value Wrap_fdl_dimensions_i64_lt(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_i64_t a = ObjectToDimensionsI64(info[0].As<Napi::Object>());
    fdl_dimensions_i64_t b = ObjectToDimensionsI64(info[1].As<Napi::Object>());
    auto _r = fdl_dimensions_i64_lt(a, b);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Normalize int64 dimensions by applying anamorphic squeeze to width.
Napi::Value Wrap_fdl_dimensions_i64_normalize(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_i64_t dims = ObjectToDimensionsI64(info[0].As<Napi::Object>());
    double squeeze = info[1].As<Napi::Number>().DoubleValue();
    fdl_dimensions_f64_t _r = fdl_dimensions_i64_normalize(dims, squeeze);
    return DimensionsF64ToObject(env, _r);
}

// Check if both width and height are zero.
Napi::Value Wrap_fdl_dimensions_is_zero(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    auto _r = fdl_dimensions_is_zero(dims);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Normalize dimensions by applying anamorphic squeeze to width.
Napi::Value Wrap_fdl_dimensions_normalize(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    double squeeze = info[1].As<Napi::Number>().DoubleValue();
    fdl_dimensions_f64_t _r = fdl_dimensions_normalize(dims, squeeze);
    return DimensionsF64ToObject(env, _r);
}

// Normalize and scale in one step.
Napi::Value Wrap_fdl_dimensions_normalize_and_scale(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    double input_squeeze = info[1].As<Napi::Number>().DoubleValue();
    double scale_factor = info[2].As<Napi::Number>().DoubleValue();
    double target_squeeze = info[3].As<Napi::Number>().DoubleValue();
    fdl_dimensions_f64_t _r = fdl_dimensions_normalize_and_scale(dims, input_squeeze, scale_factor, target_squeeze);
    return DimensionsF64ToObject(env, _r);
}

// Scale normalized dimensions and apply target squeeze.
Napi::Value Wrap_fdl_dimensions_scale(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    double scale_factor = info[1].As<Napi::Number>().DoubleValue();
    double target_squeeze = info[2].As<Napi::Number>().DoubleValue();
    fdl_dimensions_f64_t _r = fdl_dimensions_scale(dims, scale_factor, target_squeeze);
    return DimensionsF64ToObject(env, _r);
}

// Subtract two dimensions: result = a - b.
Napi::Value Wrap_fdl_dimensions_sub(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t a = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_dimensions_f64_t b = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    fdl_dimensions_f64_t _r = fdl_dimensions_sub(a, b);
    return DimensionsF64ToObject(env, _r);
}

// Add a canvas template to the document.
Napi::Value Wrap_fdl_doc_add_canvas_template(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string id_str = info[1].As<Napi::String>().Utf8Value();
    std::string label_str = info[2].As<Napi::String>().Utf8Value();
    int64_t target_w = static_cast<int64_t>(info[3].As<Napi::Number>().Int64Value());
    int64_t target_h = static_cast<int64_t>(info[4].As<Napi::Number>().Int64Value());
    double target_squeeze = info[5].As<Napi::Number>().DoubleValue();
    fdl_geometry_path_t fit_source = static_cast<fdl_geometry_path_t>(info[6].As<Napi::Number>().Uint32Value());
    fdl_fit_method_t fit_method = static_cast<fdl_fit_method_t>(info[7].As<Napi::Number>().Uint32Value());
    fdl_halign_t halign = static_cast<fdl_halign_t>(info[8].As<Napi::Number>().Uint32Value());
    fdl_valign_t valign = static_cast<fdl_valign_t>(info[9].As<Napi::Number>().Uint32Value());
    fdl_round_strategy_t rounding = ObjectToRoundStrategy(info[10].As<Napi::Object>());
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
    return Napi::External<void>::New(env, _r);
}

// Add a context to the document.
Napi::Value Wrap_fdl_doc_add_context(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string label_str = info[1].As<Napi::String>().Utf8Value();
    bool context_creator_is_null = info[2].IsNull() || info[2].IsUndefined();
    std::string context_creator_str = context_creator_is_null ? std::string() : info[2].As<Napi::String>().Utf8Value();
    auto* _r =
        fdl_doc_add_context(doc, label_str.c_str(), (context_creator_is_null ? nullptr : context_creator_str.c_str()));
    return Napi::External<void>::New(env, _r);
}

// Add a framing intent to the document.
Napi::Value Wrap_fdl_doc_add_framing_intent(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string id_str = info[1].As<Napi::String>().Utf8Value();
    std::string label_str = info[2].As<Napi::String>().Utf8Value();
    int64_t aspect_w = static_cast<int64_t>(info[3].As<Napi::Number>().Int64Value());
    int64_t aspect_h = static_cast<int64_t>(info[4].As<Napi::Number>().Int64Value());
    double protection = info[5].As<Napi::Number>().DoubleValue();
    auto* _r = fdl_doc_add_framing_intent(doc, id_str.c_str(), label_str.c_str(), aspect_w, aspect_h, protection);
    return Napi::External<void>::New(env, _r);
}

// Get a canvas template by index.
Napi::Value Wrap_fdl_doc_canvas_template_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();
    auto* _r = fdl_doc_canvas_template_at(doc, index);
    return Napi::External<void>::New(env, _r);
}

// Find a canvas template by its ID string.
Napi::Value Wrap_fdl_doc_canvas_template_find_by_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string id_str = info[1].As<Napi::String>().Utf8Value();
    auto* _r = fdl_doc_canvas_template_find_by_id(doc, id_str.c_str());
    if (!_r) {
        return env.Null();
    }
    return Napi::External<void>::New(env, _r);
}

// Get the number of canvas templates in the document.
Napi::Value Wrap_fdl_doc_canvas_templates_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_doc_canvas_templates_count(doc);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get a context by index.
Napi::Value Wrap_fdl_doc_context_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();
    auto* _r = fdl_doc_context_at(doc, index);
    return Napi::External<void>::New(env, _r);
}

// Find a context by its label string.
Napi::Value Wrap_fdl_doc_context_find_by_label(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string label_str = info[1].As<Napi::String>().Utf8Value();
    auto* _r = fdl_doc_context_find_by_label(doc, label_str.c_str());
    if (!_r) {
        return env.Null();
    }
    return Napi::External<void>::New(env, _r);
}

// Get the number of contexts in the document.
Napi::Value Wrap_fdl_doc_contexts_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_doc_contexts_count(doc);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Create an empty FDL document.
Napi::Value Wrap_fdl_doc_create(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* _r = fdl_doc_create();
    return Napi::External<void>::New(env, _r);
}

// Create a new FDL document with header fields and empty collections.
Napi::Value Wrap_fdl_doc_create_with_header(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string uuid_str = info[0].As<Napi::String>().Utf8Value();
    int version_major = info[1].As<Napi::Number>().Int32Value();
    int version_minor = info[2].As<Napi::Number>().Int32Value();
    std::string fdl_creator_str = info[3].As<Napi::String>().Utf8Value();
    bool default_framing_intent_is_null = info[4].IsNull() || info[4].IsUndefined();
    std::string default_framing_intent_str =
        default_framing_intent_is_null ? std::string() : info[4].As<Napi::String>().Utf8Value();
    auto* _r = fdl_doc_create_with_header(
        uuid_str.c_str(),
        version_major,
        version_minor,
        fdl_creator_str.c_str(),
        (default_framing_intent_is_null ? nullptr : default_framing_intent_str.c_str()));
    return Napi::External<void>::New(env, _r);
}

// Get a framing intent by index.
Napi::Value Wrap_fdl_doc_framing_intent_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();
    auto* _r = fdl_doc_framing_intent_at(doc, index);
    return Napi::External<void>::New(env, _r);
}

// Find a framing intent by its ID string.
Napi::Value Wrap_fdl_doc_framing_intent_find_by_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string id_str = info[1].As<Napi::String>().Utf8Value();
    auto* _r = fdl_doc_framing_intent_find_by_id(doc, id_str.c_str());
    if (!_r) {
        return env.Null();
    }
    return Napi::External<void>::New(env, _r);
}

// Get the number of framing intents in the document.
Napi::Value Wrap_fdl_doc_framing_intents_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_doc_framing_intents_count(doc);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Free an FDL document and all associated handles.
void Wrap_fdl_doc_free(const Napi::CallbackInfo& info) {
    if (info[0].IsNull() || info[0].IsUndefined()) {
        return;
    }
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    fdl_doc_free(doc);
}

// Get the default_framing_intent from a parsed FDL document.
Napi::Value Wrap_fdl_doc_get_default_framing_intent(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_doc_get_default_framing_intent(doc);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the fdl_creator from a parsed FDL document.
Napi::Value Wrap_fdl_doc_get_fdl_creator(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_doc_get_fdl_creator(doc);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the UUID from a parsed FDL document.
Napi::Value Wrap_fdl_doc_get_uuid(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_doc_get_uuid(doc);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the FDL version major number.
Napi::Value Wrap_fdl_doc_get_version_major(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_doc_get_version_major(doc);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the FDL version minor number.
Napi::Value Wrap_fdl_doc_get_version_minor(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_doc_get_version_minor(doc);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Parse a JSON string into an FDL document.
Napi::Value Wrap_fdl_doc_parse_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string json_str_str = info[0].As<Napi::String>().Utf8Value();
    size_t json_len = static_cast<size_t>(info[1].As<Napi::Number>().Int64Value());
    fdl_parse_result_t _r = fdl_doc_parse_json(json_str_str.c_str(), json_len);
    return ParseResultToObject(env, _r);
}

// Set the default_framing_intent on a document.
void Wrap_fdl_doc_set_default_framing_intent(const Napi::CallbackInfo& info) {
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string fi_id_str = info[1].As<Napi::String>().Utf8Value();
    fdl_doc_set_default_framing_intent(doc, fi_id_str.c_str());
}

// Set the fdl_creator on a document.
void Wrap_fdl_doc_set_fdl_creator(const Napi::CallbackInfo& info) {
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string creator_str = info[1].As<Napi::String>().Utf8Value();
    fdl_doc_set_fdl_creator(doc, creator_str.c_str());
}

// Set the UUID on a document.
void Wrap_fdl_doc_set_uuid(const Napi::CallbackInfo& info) {
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string uuid_str = info[1].As<Napi::String>().Utf8Value();
    fdl_doc_set_uuid(doc, uuid_str.c_str());
}

// Set the FDL version on a document.
void Wrap_fdl_doc_set_version(const Napi::CallbackInfo& info) {
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    int major = info[1].As<Napi::Number>().Int32Value();
    int minor = info[2].As<Napi::Number>().Int32Value();
    fdl_doc_set_version(doc, major, minor);
}

// Serialize document to canonical JSON string.
Napi::Value Wrap_fdl_doc_to_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    int indent = info[1].As<Napi::Number>().Int32Value();
    auto* _r = fdl_doc_to_json(doc, indent);
    if (!_r) {
        Napi::Error::New(env, "fdl_doc_to_json returned NULL").ThrowAsJavaScriptException();
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Run schema and semantic validators on the document.
Napi::Value Wrap_fdl_doc_validate(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* doc = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    auto* _r = fdl_doc_validate(doc);
    return Napi::External<void>::New(env, _r);
}

// Get the index variable name.
Napi::Value Wrap_fdl_file_sequence_get_idx(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* seq = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_file_sequence_get_idx(seq);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the maximum (last) frame number.
Napi::Value Wrap_fdl_file_sequence_get_max(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* seq = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_file_sequence_get_max(seq);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the minimum (first) frame number.
Napi::Value Wrap_fdl_file_sequence_get_min(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* seq = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_file_sequence_get_min(seq);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Get the sequence pattern value string.
Napi::Value Wrap_fdl_file_sequence_get_value(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* seq = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_file_sequence_get_value(seq);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Absolute tolerance for floating-point comparison.
Napi::Value Wrap_fdl_fp_abs_tol(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto _r = fdl_fp_abs_tol();
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Relative tolerance for floating-point comparison.
Napi::Value Wrap_fdl_fp_rel_tol(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto _r = fdl_fp_rel_tol();
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Adjust anchor_point on a framing decision based on alignment within canvas.
void Wrap_fdl_framing_decision_adjust_anchor(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[1]));
    fdl_halign_t h_align = static_cast<fdl_halign_t>(info[2].As<Napi::Number>().Uint32Value());
    fdl_valign_t v_align = static_cast<fdl_valign_t>(info[3].As<Napi::Number>().Uint32Value());
    fdl_framing_decision_adjust_anchor(fd, canvas, h_align, v_align);
}

// Adjust protection_anchor_point on a framing decision based on alignment within canvas.
void Wrap_fdl_framing_decision_adjust_protection_anchor(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[1]));
    fdl_halign_t h_align = static_cast<fdl_halign_t>(info[2].As<Napi::Number>().Uint32Value());
    fdl_valign_t v_align = static_cast<fdl_valign_t>(info[3].As<Napi::Number>().Uint32Value());
    fdl_framing_decision_adjust_protection_anchor(fd, canvas, h_align, v_align);
}

// Get the anchor point of a framing decision.
Napi::Value Wrap_fdl_framing_decision_get_anchor_point(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_point_f64_t _r = fdl_framing_decision_get_anchor_point(fd);
    return PointF64ToObject(env, _r);
}

// Get the framing decision dimensions (floating-point sub-pixel).
Napi::Value Wrap_fdl_framing_decision_get_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_f64_t _r = fdl_framing_decision_get_dimensions(fd);
    return DimensionsF64ToObject(env, _r);
}

// Get the framing_intent_id that this framing decision references.
Napi::Value Wrap_fdl_framing_decision_get_framing_intent_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_framing_decision_get_framing_intent_id(fd);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the ID of a framing decision.
Napi::Value Wrap_fdl_framing_decision_get_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_framing_decision_get_id(fd);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the label of a framing decision.
Napi::Value Wrap_fdl_framing_decision_get_label(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_framing_decision_get_label(fd);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the protection anchor point.
Napi::Value Wrap_fdl_framing_decision_get_protection_anchor_point(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_point_f64_t _r = fdl_framing_decision_get_protection_anchor_point(fd);
    return PointF64ToObject(env, _r);
}

// Get the protection area dimensions.
Napi::Value Wrap_fdl_framing_decision_get_protection_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_f64_t _r = fdl_framing_decision_get_protection_dimensions(fd);
    return DimensionsF64ToObject(env, _r);
}

// Get the framing decision protection rect.
Napi::Value Wrap_fdl_framing_decision_get_protection_rect(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_rect_t out_rect = {};
    int _rv = fdl_framing_decision_get_protection_rect(fd, &out_rect);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("rect", RectToObject(env, out_rect));
    return _out;
}

// Get the framing decision rect: (anchor.x, anchor.y, dims.width, dims.height).
Napi::Value Wrap_fdl_framing_decision_get_rect(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_rect_t _r = fdl_framing_decision_get_rect(fd);
    return RectToObject(env, _r);
}

// Check if a framing decision has protection area set.
Napi::Value Wrap_fdl_framing_decision_has_protection(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_framing_decision_has_protection(fd);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Populate a framing decision from a canvas and framing intent.
void Wrap_fdl_framing_decision_populate_from_intent(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[1]));
    auto* intent = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[2]));
    fdl_round_strategy_t rounding = ObjectToRoundStrategy(info[3].As<Napi::Object>());
    fdl_framing_decision_populate_from_intent(fd, canvas, intent, rounding);
}

// Remove protection dimensions and anchor from a framing decision.
void Wrap_fdl_framing_decision_remove_protection(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_framing_decision_remove_protection(fd);
}

// Set anchor point on a framing decision.
void Wrap_fdl_framing_decision_set_anchor_point(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_point_f64_t point = ObjectToPointF64(info[1].As<Napi::Object>());
    fdl_framing_decision_set_anchor_point(fd, point);
}

// Set dimensions on a framing decision.
void Wrap_fdl_framing_decision_set_dimensions(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    fdl_framing_decision_set_dimensions(fd, dims);
}

// Set protection dimensions and anchor on a framing decision.
void Wrap_fdl_framing_decision_set_protection(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    fdl_point_f64_t anchor = ObjectToPointF64(info[2].As<Napi::Object>());
    fdl_framing_decision_set_protection(fd, dims, anchor);
}

// Set protection anchor point on a framing decision (without changing dimensions).
void Wrap_fdl_framing_decision_set_protection_anchor_point(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_point_f64_t point = ObjectToPointF64(info[1].As<Napi::Object>());
    fdl_framing_decision_set_protection_anchor_point(fd, point);
}

// Set protection dimensions on a framing decision (without changing anchor).
void Wrap_fdl_framing_decision_set_protection_dimensions(const Napi::CallbackInfo& info) {
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[1].As<Napi::Object>());
    fdl_framing_decision_set_protection_dimensions(fd, dims);
}

// Serialize a framing decision to canonical JSON.
Napi::Value Wrap_fdl_framing_decision_to_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fd = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    int indent = info[1].As<Napi::Number>().Int32Value();
    auto* _r = fdl_framing_decision_to_json(fd, indent);
    if (!_r) {
        Napi::Error::New(env, "fdl_framing_decision_to_json returned NULL").ThrowAsJavaScriptException();
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Get the target aspect ratio of a framing intent.
Napi::Value Wrap_fdl_framing_intent_get_aspect_ratio(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fi = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t _r = fdl_framing_intent_get_aspect_ratio(fi);
    return DimensionsI64ToObject(env, _r);
}

// Get the ID of a framing intent.
Napi::Value Wrap_fdl_framing_intent_get_id(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fi = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_framing_intent_get_id(fi);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the label of a framing intent.
Napi::Value Wrap_fdl_framing_intent_get_label(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fi = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    const char* _r = fdl_framing_intent_get_label(fi);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the protection factor of a framing intent.
Napi::Value Wrap_fdl_framing_intent_get_protection(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fi = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_framing_intent_get_protection(fi);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Set aspect ratio on a framing intent.
void Wrap_fdl_framing_intent_set_aspect_ratio(const Napi::CallbackInfo& info) {
    auto* fi = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    fdl_dimensions_i64_t dims = ObjectToDimensionsI64(info[1].As<Napi::Object>());
    fdl_framing_intent_set_aspect_ratio(fi, dims);
}

// Set protection factor on a framing intent.
void Wrap_fdl_framing_intent_set_protection(const Napi::CallbackInfo& info) {
    auto* fi = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    double protection = info[1].As<Napi::Number>().DoubleValue();
    fdl_framing_intent_set_protection(fi, protection);
}

// Serialize a framing intent to canonical JSON.
Napi::Value Wrap_fdl_framing_intent_to_json(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* fi = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    int indent = info[1].As<Napi::Number>().Int32Value();
    auto* _r = fdl_framing_intent_to_json(fi, indent);
    if (!_r) {
        Napi::Error::New(env, "fdl_framing_intent_to_json returned NULL").ThrowAsJavaScriptException();
        return env.Null();
    }
    std::string _result(_r);
    fdl_free(const_cast<char*>(_r));
    return Napi::String::New(env, _result);
}

// Free memory allocated by fdl_core functions.
void Wrap_fdl_free(const Napi::CallbackInfo& info) {
    if (info[0].IsNull() || info[0].IsUndefined()) {
        return;
    }
    auto* ptr = static_cast<void*>(UnwrapHandle(info[0]));
    fdl_free(ptr);
}

// Apply offset to all anchors, clamping to canvas bounds.
Napi::Value Wrap_fdl_geometry_apply_offset(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_geometry_t geo = ObjectToGeometry(info[0].As<Napi::Object>());
    fdl_point_f64_t offset = ObjectToPointF64(info[1].As<Napi::Object>());
    fdl_point_f64_t theo_eff = {};
    fdl_point_f64_t theo_prot = {};
    fdl_point_f64_t theo_fram = {};
    fdl_geometry_t _rv = fdl_geometry_apply_offset(geo, offset, &theo_eff, &theo_prot, &theo_fram);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", GeometryToObject(env, _rv));
    _out.Set("theo_eff", PointF64ToObject(env, theo_eff));
    _out.Set("theo_prot", PointF64ToObject(env, theo_prot));
    _out.Set("theo_fram", PointF64ToObject(env, theo_fram));
    return _out;
}

// Crop all dimensions to visible portion within canvas.
Napi::Value Wrap_fdl_geometry_crop(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_geometry_t geo = ObjectToGeometry(info[0].As<Napi::Object>());
    fdl_point_f64_t theo_eff = ObjectToPointF64(info[1].As<Napi::Object>());
    fdl_point_f64_t theo_prot = ObjectToPointF64(info[2].As<Napi::Object>());
    fdl_point_f64_t theo_fram = ObjectToPointF64(info[3].As<Napi::Object>());
    fdl_geometry_t _r = fdl_geometry_crop(geo, theo_eff, theo_prot, theo_fram);
    return GeometryToObject(env, _r);
}

// Fill gaps in the geometry hierarchy by propagating populated dimensions upward.
Napi::Value Wrap_fdl_geometry_fill_hierarchy_gaps(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_geometry_t geo = ObjectToGeometry(info[0].As<Napi::Object>());
    fdl_point_f64_t anchor_offset = ObjectToPointF64(info[1].As<Napi::Object>());
    fdl_geometry_t _r = fdl_geometry_fill_hierarchy_gaps(geo, anchor_offset);
    return GeometryToObject(env, _r);
}

// Extract dimensions and anchor from geometry by path.
Napi::Value Wrap_fdl_geometry_get_dims_anchor_from_path(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_geometry_t geo = ObjectToGeometry(info[0].As<Napi::Object>());
    fdl_geometry_path_t path = static_cast<fdl_geometry_path_t>(info[1].As<Napi::Number>().Uint32Value());
    fdl_dimensions_f64_t out_dims = {};
    fdl_point_f64_t out_anchor = {};
    int _rv = fdl_geometry_get_dims_anchor_from_path(&geo, path, &out_dims, &out_anchor);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("dims", DimensionsF64ToObject(env, out_dims));
    _out.Set("anchor", PointF64ToObject(env, out_anchor));
    return _out;
}

// Normalize and scale all 7 fields of the geometry.
Napi::Value Wrap_fdl_geometry_normalize_and_scale(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_geometry_t geo = ObjectToGeometry(info[0].As<Napi::Object>());
    double source_squeeze = info[1].As<Napi::Number>().DoubleValue();
    double scale_factor = info[2].As<Napi::Number>().DoubleValue();
    double target_squeeze = info[3].As<Napi::Number>().DoubleValue();
    fdl_geometry_t _r = fdl_geometry_normalize_and_scale(geo, source_squeeze, scale_factor, target_squeeze);
    return GeometryToObject(env, _r);
}

// Round all 7 fields of the geometry.
Napi::Value Wrap_fdl_geometry_round(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_geometry_t geo = ObjectToGeometry(info[0].As<Napi::Object>());
    fdl_round_strategy_t strategy = ObjectToRoundStrategy(info[1].As<Napi::Object>());
    fdl_geometry_t _r = fdl_geometry_round(geo, strategy);
    return GeometryToObject(env, _r);
}

// Construct a rect from raw coordinates.
Napi::Value Wrap_fdl_make_rect(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    double x = info[0].As<Napi::Number>().DoubleValue();
    double y = info[1].As<Napi::Number>().DoubleValue();
    double width = info[2].As<Napi::Number>().DoubleValue();
    double height = info[3].As<Napi::Number>().DoubleValue();
    fdl_rect_t _r = fdl_make_rect(x, y, width, height);
    return RectToObject(env, _r);
}

// Determine output canvas size for a single axis.
Napi::Value Wrap_fdl_output_size_for_axis(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    double canvas_size = info[0].As<Napi::Number>().DoubleValue();
    double max_size = info[1].As<Napi::Number>().DoubleValue();
    int has_max = info[2].As<Napi::Number>().Int32Value();
    int pad_to_max = info[3].As<Napi::Number>().Int32Value();
    auto _r = fdl_output_size_for_axis(canvas_size, max_size, has_max, pad_to_max);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Add two points: result = a + b.
Napi::Value Wrap_fdl_point_add(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t a = ObjectToPointF64(info[0].As<Napi::Object>());
    fdl_point_f64_t b = ObjectToPointF64(info[1].As<Napi::Object>());
    fdl_point_f64_t _r = fdl_point_add(a, b);
    return PointF64ToObject(env, _r);
}

// Clamp point values to [min_val, max_val].
Napi::Value Wrap_fdl_point_clamp(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t point = ObjectToPointF64(info[0].As<Napi::Object>());
    double min_val = info[1].As<Napi::Number>().DoubleValue();
    double max_val = info[2].As<Napi::Number>().DoubleValue();
    int has_min = info[3].As<Napi::Number>().Int32Value();
    int has_max = info[4].As<Napi::Number>().Int32Value();
    fdl_point_f64_t _r = fdl_point_clamp(point, min_val, max_val, has_min, has_max);
    return PointF64ToObject(env, _r);
}

// Check approximate equality within FDL tolerances.
Napi::Value Wrap_fdl_point_equal(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t a = ObjectToPointF64(info[0].As<Napi::Object>());
    fdl_point_f64_t b = ObjectToPointF64(info[1].As<Napi::Object>());
    auto _r = fdl_point_equal(a, b);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if a > b using OR logic (either x or y is greater).
Napi::Value Wrap_fdl_point_f64_gt(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t a = ObjectToPointF64(info[0].As<Napi::Object>());
    fdl_point_f64_t b = ObjectToPointF64(info[1].As<Napi::Object>());
    auto _r = fdl_point_f64_gt(a, b);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if a < b using OR logic (either x or y is less).
Napi::Value Wrap_fdl_point_f64_lt(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t a = ObjectToPointF64(info[0].As<Napi::Object>());
    fdl_point_f64_t b = ObjectToPointF64(info[1].As<Napi::Object>());
    auto _r = fdl_point_f64_lt(a, b);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Check if both x and y are zero.
Napi::Value Wrap_fdl_point_is_zero(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t point = ObjectToPointF64(info[0].As<Napi::Object>());
    auto _r = fdl_point_is_zero(point);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Multiply point by scalar.
Napi::Value Wrap_fdl_point_mul_scalar(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t a = ObjectToPointF64(info[0].As<Napi::Object>());
    double scalar = info[1].As<Napi::Number>().DoubleValue();
    fdl_point_f64_t _r = fdl_point_mul_scalar(a, scalar);
    return PointF64ToObject(env, _r);
}

// Normalize a point by applying anamorphic squeeze to x.
Napi::Value Wrap_fdl_point_normalize(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t point = ObjectToPointF64(info[0].As<Napi::Object>());
    double squeeze = info[1].As<Napi::Number>().DoubleValue();
    fdl_point_f64_t _r = fdl_point_normalize(point, squeeze);
    return PointF64ToObject(env, _r);
}

// Normalize and scale a point in one step.
Napi::Value Wrap_fdl_point_normalize_and_scale(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t point = ObjectToPointF64(info[0].As<Napi::Object>());
    double input_squeeze = info[1].As<Napi::Number>().DoubleValue();
    double scale_factor = info[2].As<Napi::Number>().DoubleValue();
    double target_squeeze = info[3].As<Napi::Number>().DoubleValue();
    fdl_point_f64_t _r = fdl_point_normalize_and_scale(point, input_squeeze, scale_factor, target_squeeze);
    return PointF64ToObject(env, _r);
}

// Scale a normalized point and apply target squeeze.
Napi::Value Wrap_fdl_point_scale(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t point = ObjectToPointF64(info[0].As<Napi::Object>());
    double scale_factor = info[1].As<Napi::Number>().DoubleValue();
    double target_squeeze = info[2].As<Napi::Number>().DoubleValue();
    fdl_point_f64_t _r = fdl_point_scale(point, scale_factor, target_squeeze);
    return PointF64ToObject(env, _r);
}

// Subtract two points: result = a - b.
Napi::Value Wrap_fdl_point_sub(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t a = ObjectToPointF64(info[0].As<Napi::Object>());
    fdl_point_f64_t b = ObjectToPointF64(info[1].As<Napi::Object>());
    fdl_point_f64_t _r = fdl_point_sub(a, b);
    return PointF64ToObject(env, _r);
}

// Resolve dimensions and anchor directly from canvas/framing handles for a path.
Napi::Value Wrap_fdl_resolve_geometry_layer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* canvas = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    auto* framing = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[1]));
    fdl_geometry_path_t path = static_cast<fdl_geometry_path_t>(info[2].As<Napi::Number>().Uint32Value());
    fdl_dimensions_f64_t out_dims = {};
    fdl_point_f64_t out_anchor = {};
    int _rv = fdl_resolve_geometry_layer(canvas, framing, path, &out_dims, &out_anchor);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("dims", DimensionsF64ToObject(env, out_dims));
    _out.Set("anchor", PointF64ToObject(env, out_anchor));
    return _out;
}

// Round a single value according to FDL rounding rules.
Napi::Value Wrap_fdl_round(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    double value = info[0].As<Napi::Number>().DoubleValue();
    fdl_rounding_even_t even = static_cast<fdl_rounding_even_t>(info[1].As<Napi::Number>().Uint32Value());
    fdl_rounding_mode_t mode = static_cast<fdl_rounding_mode_t>(info[2].As<Napi::Number>().Uint32Value());
    auto _r = fdl_round(value, even, mode);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Round dimensions according to FDL rounding rules.
Napi::Value Wrap_fdl_round_dimensions(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_dimensions_f64_t dims = ObjectToDimensionsF64(info[0].As<Napi::Object>());
    fdl_rounding_even_t even = static_cast<fdl_rounding_even_t>(info[1].As<Napi::Number>().Uint32Value());
    fdl_rounding_mode_t mode = static_cast<fdl_rounding_mode_t>(info[2].As<Napi::Number>().Uint32Value());
    fdl_dimensions_f64_t _r = fdl_round_dimensions(dims, even, mode);
    return DimensionsF64ToObject(env, _r);
}

// Round a point according to FDL rounding rules.
Napi::Value Wrap_fdl_round_point(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    fdl_point_f64_t point = ObjectToPointF64(info[0].As<Napi::Object>());
    fdl_rounding_even_t even = static_cast<fdl_rounding_even_t>(info[1].As<Napi::Number>().Uint32Value());
    fdl_rounding_mode_t mode = static_cast<fdl_rounding_mode_t>(info[2].As<Napi::Number>().Uint32Value());
    fdl_point_f64_t _r = fdl_round_point(point, even, mode);
    return PointF64ToObject(env, _r);
}

// Free a template result (doc + all allocated strings).
void Wrap_fdl_template_result_free(const Napi::CallbackInfo& info) {
    fdl_template_result_t result = ObjectToTemplateResult(info[0].As<Napi::Object>());
    fdl_template_result_free(&result);
}

// Get a specific error message by index.
Napi::Value Wrap_fdl_validation_result_error_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* result = static_cast<fdl_validation_result_t*>(UnwrapHandle(info[0]));
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_validation_result_error_at(result, index);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Get the number of validation errors.
Napi::Value Wrap_fdl_validation_result_error_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* result = static_cast<fdl_validation_result_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_validation_result_error_count(result);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Free a validation result. Safe to call with NULL.
void Wrap_fdl_validation_result_free(const Napi::CallbackInfo& info) {
    if (info[0].IsNull() || info[0].IsUndefined()) {
        return;
    }
    auto* result = static_cast<fdl_validation_result_t*>(UnwrapHandle(info[0]));
    fdl_validation_result_free(result);
}

// Custom attr: set_custom_attr_string on FDL
Napi::Value Wrap_fdl_doc_set_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    std::string arg1_str = info[2].As<Napi::String>().Utf8Value();
    auto _r = fdl_doc_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_int on FDL
Napi::Value Wrap_fdl_doc_set_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t arg1 = static_cast<int64_t>(info[2].As<Napi::Number>().Int64Value());
    auto _r = fdl_doc_set_custom_attr_int(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_float on FDL
Napi::Value Wrap_fdl_doc_set_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double arg1 = info[2].As<Napi::Number>().DoubleValue();
    auto _r = fdl_doc_set_custom_attr_float(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_bool on FDL
Napi::Value Wrap_fdl_doc_set_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int arg1 = info[2].As<Napi::Number>().Int32Value();
    auto _r = fdl_doc_set_custom_attr_bool(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_string on FDL
Napi::Value Wrap_fdl_doc_get_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    const char* _r = fdl_doc_get_custom_attr_string(handle, key_str.c_str());
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: get_custom_attr_int on FDL
Napi::Value Wrap_fdl_doc_get_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t out_value = {};
    int _rv = fdl_doc_get_custom_attr_int(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_float on FDL
Napi::Value Wrap_fdl_doc_get_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double out_value = {};
    int _rv = fdl_doc_get_custom_attr_float(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_bool on FDL
Napi::Value Wrap_fdl_doc_get_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int out_value = {};
    int _rv = fdl_doc_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: has_custom_attr on FDL
Napi::Value Wrap_fdl_doc_has_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_doc_has_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_type on FDL
Napi::Value Wrap_fdl_doc_get_custom_attr_type(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_doc_get_custom_attr_type(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: remove_custom_attr on FDL
Napi::Value Wrap_fdl_doc_remove_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_doc_remove_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attrs_count on FDL
Napi::Value Wrap_fdl_doc_custom_attrs_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_doc_custom_attrs_count(handle);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attr_name_at on FDL
Napi::Value Wrap_fdl_doc_custom_attr_name_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    uint32_t arg0 = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_doc_custom_attr_name_at(handle, arg0);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: set_custom_attr_point_f64 on FDL
Napi::Value Wrap_fdl_doc_set_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t arg1 = ObjectToPointF64(info[2].As<Napi::Object>());
    auto _r = fdl_doc_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_point_f64 on FDL
Napi::Value Wrap_fdl_doc_get_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t out_value = {};
    int _rv = fdl_doc_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", PointF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_f64 on FDL
Napi::Value Wrap_fdl_doc_set_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t arg1 = ObjectToDimensionsF64(info[2].As<Napi::Object>());
    auto _r = fdl_doc_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_f64 on FDL
Napi::Value Wrap_fdl_doc_get_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t out_value = {};
    int _rv = fdl_doc_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_i64 on FDL
Napi::Value Wrap_fdl_doc_set_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t arg1 = ObjectToDimensionsI64(info[2].As<Napi::Object>());
    auto _r = fdl_doc_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_i64 on FDL
Napi::Value Wrap_fdl_doc_get_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_doc_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t out_value = {};
    int _rv = fdl_doc_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsI64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_string on Context
Napi::Value Wrap_fdl_context_set_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    std::string arg1_str = info[2].As<Napi::String>().Utf8Value();
    auto _r = fdl_context_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_int on Context
Napi::Value Wrap_fdl_context_set_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t arg1 = static_cast<int64_t>(info[2].As<Napi::Number>().Int64Value());
    auto _r = fdl_context_set_custom_attr_int(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_float on Context
Napi::Value Wrap_fdl_context_set_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double arg1 = info[2].As<Napi::Number>().DoubleValue();
    auto _r = fdl_context_set_custom_attr_float(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_bool on Context
Napi::Value Wrap_fdl_context_set_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int arg1 = info[2].As<Napi::Number>().Int32Value();
    auto _r = fdl_context_set_custom_attr_bool(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_string on Context
Napi::Value Wrap_fdl_context_get_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    const char* _r = fdl_context_get_custom_attr_string(handle, key_str.c_str());
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: get_custom_attr_int on Context
Napi::Value Wrap_fdl_context_get_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t out_value = {};
    int _rv = fdl_context_get_custom_attr_int(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_float on Context
Napi::Value Wrap_fdl_context_get_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double out_value = {};
    int _rv = fdl_context_get_custom_attr_float(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_bool on Context
Napi::Value Wrap_fdl_context_get_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int out_value = {};
    int _rv = fdl_context_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: has_custom_attr on Context
Napi::Value Wrap_fdl_context_has_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_context_has_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_type on Context
Napi::Value Wrap_fdl_context_get_custom_attr_type(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_context_get_custom_attr_type(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: remove_custom_attr on Context
Napi::Value Wrap_fdl_context_remove_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_context_remove_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attrs_count on Context
Napi::Value Wrap_fdl_context_custom_attrs_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_context_custom_attrs_count(handle);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attr_name_at on Context
Napi::Value Wrap_fdl_context_custom_attr_name_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    uint32_t arg0 = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_context_custom_attr_name_at(handle, arg0);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: set_custom_attr_point_f64 on Context
Napi::Value Wrap_fdl_context_set_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t arg1 = ObjectToPointF64(info[2].As<Napi::Object>());
    auto _r = fdl_context_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_point_f64 on Context
Napi::Value Wrap_fdl_context_get_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t out_value = {};
    int _rv = fdl_context_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", PointF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_f64 on Context
Napi::Value Wrap_fdl_context_set_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t arg1 = ObjectToDimensionsF64(info[2].As<Napi::Object>());
    auto _r = fdl_context_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_f64 on Context
Napi::Value Wrap_fdl_context_get_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t out_value = {};
    int _rv = fdl_context_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_i64 on Context
Napi::Value Wrap_fdl_context_set_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t arg1 = ObjectToDimensionsI64(info[2].As<Napi::Object>());
    auto _r = fdl_context_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_i64 on Context
Napi::Value Wrap_fdl_context_get_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_context_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t out_value = {};
    int _rv = fdl_context_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsI64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_string on Canvas
Napi::Value Wrap_fdl_canvas_set_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    std::string arg1_str = info[2].As<Napi::String>().Utf8Value();
    auto _r = fdl_canvas_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_int on Canvas
Napi::Value Wrap_fdl_canvas_set_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t arg1 = static_cast<int64_t>(info[2].As<Napi::Number>().Int64Value());
    auto _r = fdl_canvas_set_custom_attr_int(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_float on Canvas
Napi::Value Wrap_fdl_canvas_set_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double arg1 = info[2].As<Napi::Number>().DoubleValue();
    auto _r = fdl_canvas_set_custom_attr_float(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_bool on Canvas
Napi::Value Wrap_fdl_canvas_set_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int arg1 = info[2].As<Napi::Number>().Int32Value();
    auto _r = fdl_canvas_set_custom_attr_bool(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_string on Canvas
Napi::Value Wrap_fdl_canvas_get_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    const char* _r = fdl_canvas_get_custom_attr_string(handle, key_str.c_str());
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: get_custom_attr_int on Canvas
Napi::Value Wrap_fdl_canvas_get_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t out_value = {};
    int _rv = fdl_canvas_get_custom_attr_int(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_float on Canvas
Napi::Value Wrap_fdl_canvas_get_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double out_value = {};
    int _rv = fdl_canvas_get_custom_attr_float(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_bool on Canvas
Napi::Value Wrap_fdl_canvas_get_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int out_value = {};
    int _rv = fdl_canvas_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: has_custom_attr on Canvas
Napi::Value Wrap_fdl_canvas_has_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_canvas_has_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_type on Canvas
Napi::Value Wrap_fdl_canvas_get_custom_attr_type(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_canvas_get_custom_attr_type(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: remove_custom_attr on Canvas
Napi::Value Wrap_fdl_canvas_remove_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_canvas_remove_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attrs_count on Canvas
Napi::Value Wrap_fdl_canvas_custom_attrs_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_custom_attrs_count(handle);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attr_name_at on Canvas
Napi::Value Wrap_fdl_canvas_custom_attr_name_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    uint32_t arg0 = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_canvas_custom_attr_name_at(handle, arg0);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: set_custom_attr_point_f64 on Canvas
Napi::Value Wrap_fdl_canvas_set_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t arg1 = ObjectToPointF64(info[2].As<Napi::Object>());
    auto _r = fdl_canvas_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_point_f64 on Canvas
Napi::Value Wrap_fdl_canvas_get_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t out_value = {};
    int _rv = fdl_canvas_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", PointF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_f64 on Canvas
Napi::Value Wrap_fdl_canvas_set_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t arg1 = ObjectToDimensionsF64(info[2].As<Napi::Object>());
    auto _r = fdl_canvas_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_f64 on Canvas
Napi::Value Wrap_fdl_canvas_get_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t out_value = {};
    int _rv = fdl_canvas_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_i64 on Canvas
Napi::Value Wrap_fdl_canvas_set_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t arg1 = ObjectToDimensionsI64(info[2].As<Napi::Object>());
    auto _r = fdl_canvas_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_i64 on Canvas
Napi::Value Wrap_fdl_canvas_get_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t out_value = {};
    int _rv = fdl_canvas_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsI64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_string on FramingDecision
Napi::Value Wrap_fdl_framing_decision_set_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    std::string arg1_str = info[2].As<Napi::String>().Utf8Value();
    auto _r = fdl_framing_decision_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_int on FramingDecision
Napi::Value Wrap_fdl_framing_decision_set_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t arg1 = static_cast<int64_t>(info[2].As<Napi::Number>().Int64Value());
    auto _r = fdl_framing_decision_set_custom_attr_int(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_float on FramingDecision
Napi::Value Wrap_fdl_framing_decision_set_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double arg1 = info[2].As<Napi::Number>().DoubleValue();
    auto _r = fdl_framing_decision_set_custom_attr_float(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_bool on FramingDecision
Napi::Value Wrap_fdl_framing_decision_set_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int arg1 = info[2].As<Napi::Number>().Int32Value();
    auto _r = fdl_framing_decision_set_custom_attr_bool(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_string on FramingDecision
Napi::Value Wrap_fdl_framing_decision_get_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    const char* _r = fdl_framing_decision_get_custom_attr_string(handle, key_str.c_str());
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: get_custom_attr_int on FramingDecision
Napi::Value Wrap_fdl_framing_decision_get_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t out_value = {};
    int _rv = fdl_framing_decision_get_custom_attr_int(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_float on FramingDecision
Napi::Value Wrap_fdl_framing_decision_get_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double out_value = {};
    int _rv = fdl_framing_decision_get_custom_attr_float(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_bool on FramingDecision
Napi::Value Wrap_fdl_framing_decision_get_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int out_value = {};
    int _rv = fdl_framing_decision_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: has_custom_attr on FramingDecision
Napi::Value Wrap_fdl_framing_decision_has_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_framing_decision_has_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_type on FramingDecision
Napi::Value Wrap_fdl_framing_decision_get_custom_attr_type(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_framing_decision_get_custom_attr_type(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: remove_custom_attr on FramingDecision
Napi::Value Wrap_fdl_framing_decision_remove_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_framing_decision_remove_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attrs_count on FramingDecision
Napi::Value Wrap_fdl_framing_decision_custom_attrs_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_framing_decision_custom_attrs_count(handle);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attr_name_at on FramingDecision
Napi::Value Wrap_fdl_framing_decision_custom_attr_name_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    uint32_t arg0 = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_framing_decision_custom_attr_name_at(handle, arg0);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: set_custom_attr_point_f64 on FramingDecision
Napi::Value Wrap_fdl_framing_decision_set_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t arg1 = ObjectToPointF64(info[2].As<Napi::Object>());
    auto _r = fdl_framing_decision_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_point_f64 on FramingDecision
Napi::Value Wrap_fdl_framing_decision_get_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t out_value = {};
    int _rv = fdl_framing_decision_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", PointF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_f64 on FramingDecision
Napi::Value Wrap_fdl_framing_decision_set_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t arg1 = ObjectToDimensionsF64(info[2].As<Napi::Object>());
    auto _r = fdl_framing_decision_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_f64 on FramingDecision
Napi::Value Wrap_fdl_framing_decision_get_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t out_value = {};
    int _rv = fdl_framing_decision_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_i64 on FramingDecision
Napi::Value Wrap_fdl_framing_decision_set_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t arg1 = ObjectToDimensionsI64(info[2].As<Napi::Object>());
    auto _r = fdl_framing_decision_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_i64 on FramingDecision
Napi::Value Wrap_fdl_framing_decision_get_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_decision_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t out_value = {};
    int _rv = fdl_framing_decision_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsI64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_string on FramingIntent
Napi::Value Wrap_fdl_framing_intent_set_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    std::string arg1_str = info[2].As<Napi::String>().Utf8Value();
    auto _r = fdl_framing_intent_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_int on FramingIntent
Napi::Value Wrap_fdl_framing_intent_set_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t arg1 = static_cast<int64_t>(info[2].As<Napi::Number>().Int64Value());
    auto _r = fdl_framing_intent_set_custom_attr_int(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_float on FramingIntent
Napi::Value Wrap_fdl_framing_intent_set_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double arg1 = info[2].As<Napi::Number>().DoubleValue();
    auto _r = fdl_framing_intent_set_custom_attr_float(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_bool on FramingIntent
Napi::Value Wrap_fdl_framing_intent_set_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int arg1 = info[2].As<Napi::Number>().Int32Value();
    auto _r = fdl_framing_intent_set_custom_attr_bool(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_string on FramingIntent
Napi::Value Wrap_fdl_framing_intent_get_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    const char* _r = fdl_framing_intent_get_custom_attr_string(handle, key_str.c_str());
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: get_custom_attr_int on FramingIntent
Napi::Value Wrap_fdl_framing_intent_get_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t out_value = {};
    int _rv = fdl_framing_intent_get_custom_attr_int(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_float on FramingIntent
Napi::Value Wrap_fdl_framing_intent_get_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double out_value = {};
    int _rv = fdl_framing_intent_get_custom_attr_float(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_bool on FramingIntent
Napi::Value Wrap_fdl_framing_intent_get_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int out_value = {};
    int _rv = fdl_framing_intent_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: has_custom_attr on FramingIntent
Napi::Value Wrap_fdl_framing_intent_has_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_framing_intent_has_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_type on FramingIntent
Napi::Value Wrap_fdl_framing_intent_get_custom_attr_type(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_framing_intent_get_custom_attr_type(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: remove_custom_attr on FramingIntent
Napi::Value Wrap_fdl_framing_intent_remove_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_framing_intent_remove_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attrs_count on FramingIntent
Napi::Value Wrap_fdl_framing_intent_custom_attrs_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_framing_intent_custom_attrs_count(handle);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attr_name_at on FramingIntent
Napi::Value Wrap_fdl_framing_intent_custom_attr_name_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    uint32_t arg0 = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_framing_intent_custom_attr_name_at(handle, arg0);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: set_custom_attr_point_f64 on FramingIntent
Napi::Value Wrap_fdl_framing_intent_set_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t arg1 = ObjectToPointF64(info[2].As<Napi::Object>());
    auto _r = fdl_framing_intent_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_point_f64 on FramingIntent
Napi::Value Wrap_fdl_framing_intent_get_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t out_value = {};
    int _rv = fdl_framing_intent_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", PointF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_f64 on FramingIntent
Napi::Value Wrap_fdl_framing_intent_set_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t arg1 = ObjectToDimensionsF64(info[2].As<Napi::Object>());
    auto _r = fdl_framing_intent_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_f64 on FramingIntent
Napi::Value Wrap_fdl_framing_intent_get_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t out_value = {};
    int _rv = fdl_framing_intent_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_i64 on FramingIntent
Napi::Value Wrap_fdl_framing_intent_set_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t arg1 = ObjectToDimensionsI64(info[2].As<Napi::Object>());
    auto _r = fdl_framing_intent_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_i64 on FramingIntent
Napi::Value Wrap_fdl_framing_intent_get_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_framing_intent_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t out_value = {};
    int _rv = fdl_framing_intent_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsI64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_string on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_set_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    std::string arg1_str = info[2].As<Napi::String>().Utf8Value();
    auto _r = fdl_canvas_template_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_int on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_set_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t arg1 = static_cast<int64_t>(info[2].As<Napi::Number>().Int64Value());
    auto _r = fdl_canvas_template_set_custom_attr_int(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_float on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_set_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double arg1 = info[2].As<Napi::Number>().DoubleValue();
    auto _r = fdl_canvas_template_set_custom_attr_float(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_bool on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_set_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int arg1 = info[2].As<Napi::Number>().Int32Value();
    auto _r = fdl_canvas_template_set_custom_attr_bool(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_string on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_get_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    const char* _r = fdl_canvas_template_get_custom_attr_string(handle, key_str.c_str());
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: get_custom_attr_int on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_get_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t out_value = {};
    int _rv = fdl_canvas_template_get_custom_attr_int(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_float on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_get_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double out_value = {};
    int _rv = fdl_canvas_template_get_custom_attr_float(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_bool on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_get_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int out_value = {};
    int _rv = fdl_canvas_template_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: has_custom_attr on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_has_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_canvas_template_has_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_type on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_get_custom_attr_type(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_canvas_template_get_custom_attr_type(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: remove_custom_attr on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_remove_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_canvas_template_remove_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attrs_count on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_custom_attrs_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_canvas_template_custom_attrs_count(handle);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attr_name_at on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_custom_attr_name_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    uint32_t arg0 = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_canvas_template_custom_attr_name_at(handle, arg0);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: set_custom_attr_point_f64 on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_set_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t arg1 = ObjectToPointF64(info[2].As<Napi::Object>());
    auto _r = fdl_canvas_template_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_point_f64 on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_get_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t out_value = {};
    int _rv = fdl_canvas_template_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", PointF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_f64 on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_set_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t arg1 = ObjectToDimensionsF64(info[2].As<Napi::Object>());
    auto _r = fdl_canvas_template_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_f64 on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_get_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t out_value = {};
    int _rv = fdl_canvas_template_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_i64 on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_set_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t arg1 = ObjectToDimensionsI64(info[2].As<Napi::Object>());
    auto _r = fdl_canvas_template_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_i64 on CanvasTemplate
Napi::Value Wrap_fdl_canvas_template_get_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_canvas_template_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t out_value = {};
    int _rv = fdl_canvas_template_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsI64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_string on ClipID
Napi::Value Wrap_fdl_clip_id_set_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    std::string arg1_str = info[2].As<Napi::String>().Utf8Value();
    auto _r = fdl_clip_id_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_int on ClipID
Napi::Value Wrap_fdl_clip_id_set_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t arg1 = static_cast<int64_t>(info[2].As<Napi::Number>().Int64Value());
    auto _r = fdl_clip_id_set_custom_attr_int(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_float on ClipID
Napi::Value Wrap_fdl_clip_id_set_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double arg1 = info[2].As<Napi::Number>().DoubleValue();
    auto _r = fdl_clip_id_set_custom_attr_float(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_bool on ClipID
Napi::Value Wrap_fdl_clip_id_set_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int arg1 = info[2].As<Napi::Number>().Int32Value();
    auto _r = fdl_clip_id_set_custom_attr_bool(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_string on ClipID
Napi::Value Wrap_fdl_clip_id_get_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    const char* _r = fdl_clip_id_get_custom_attr_string(handle, key_str.c_str());
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: get_custom_attr_int on ClipID
Napi::Value Wrap_fdl_clip_id_get_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t out_value = {};
    int _rv = fdl_clip_id_get_custom_attr_int(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_float on ClipID
Napi::Value Wrap_fdl_clip_id_get_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double out_value = {};
    int _rv = fdl_clip_id_get_custom_attr_float(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_bool on ClipID
Napi::Value Wrap_fdl_clip_id_get_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int out_value = {};
    int _rv = fdl_clip_id_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: has_custom_attr on ClipID
Napi::Value Wrap_fdl_clip_id_has_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_clip_id_has_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_type on ClipID
Napi::Value Wrap_fdl_clip_id_get_custom_attr_type(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_clip_id_get_custom_attr_type(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: remove_custom_attr on ClipID
Napi::Value Wrap_fdl_clip_id_remove_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_clip_id_remove_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attrs_count on ClipID
Napi::Value Wrap_fdl_clip_id_custom_attrs_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_clip_id_custom_attrs_count(handle);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attr_name_at on ClipID
Napi::Value Wrap_fdl_clip_id_custom_attr_name_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    uint32_t arg0 = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_clip_id_custom_attr_name_at(handle, arg0);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: set_custom_attr_point_f64 on ClipID
Napi::Value Wrap_fdl_clip_id_set_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t arg1 = ObjectToPointF64(info[2].As<Napi::Object>());
    auto _r = fdl_clip_id_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_point_f64 on ClipID
Napi::Value Wrap_fdl_clip_id_get_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t out_value = {};
    int _rv = fdl_clip_id_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", PointF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_f64 on ClipID
Napi::Value Wrap_fdl_clip_id_set_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t arg1 = ObjectToDimensionsF64(info[2].As<Napi::Object>());
    auto _r = fdl_clip_id_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_f64 on ClipID
Napi::Value Wrap_fdl_clip_id_get_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t out_value = {};
    int _rv = fdl_clip_id_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_i64 on ClipID
Napi::Value Wrap_fdl_clip_id_set_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t arg1 = ObjectToDimensionsI64(info[2].As<Napi::Object>());
    auto _r = fdl_clip_id_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_i64 on ClipID
Napi::Value Wrap_fdl_clip_id_get_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_clip_id_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t out_value = {};
    int _rv = fdl_clip_id_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsI64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_string on FileSequence
Napi::Value Wrap_fdl_file_sequence_set_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    std::string arg1_str = info[2].As<Napi::String>().Utf8Value();
    auto _r = fdl_file_sequence_set_custom_attr_string(handle, key_str.c_str(), arg1_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_int on FileSequence
Napi::Value Wrap_fdl_file_sequence_set_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t arg1 = static_cast<int64_t>(info[2].As<Napi::Number>().Int64Value());
    auto _r = fdl_file_sequence_set_custom_attr_int(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_float on FileSequence
Napi::Value Wrap_fdl_file_sequence_set_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double arg1 = info[2].As<Napi::Number>().DoubleValue();
    auto _r = fdl_file_sequence_set_custom_attr_float(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: set_custom_attr_bool on FileSequence
Napi::Value Wrap_fdl_file_sequence_set_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int arg1 = info[2].As<Napi::Number>().Int32Value();
    auto _r = fdl_file_sequence_set_custom_attr_bool(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_string on FileSequence
Napi::Value Wrap_fdl_file_sequence_get_custom_attr_string(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    const char* _r = fdl_file_sequence_get_custom_attr_string(handle, key_str.c_str());
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: get_custom_attr_int on FileSequence
Napi::Value Wrap_fdl_file_sequence_get_custom_attr_int(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int64_t out_value = {};
    int _rv = fdl_file_sequence_get_custom_attr_int(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_float on FileSequence
Napi::Value Wrap_fdl_file_sequence_get_custom_attr_float(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    double out_value = {};
    int _rv = fdl_file_sequence_get_custom_attr_float(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: get_custom_attr_bool on FileSequence
Napi::Value Wrap_fdl_file_sequence_get_custom_attr_bool(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    int out_value = {};
    int _rv = fdl_file_sequence_get_custom_attr_bool(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", Napi::Number::New(env, static_cast<double>(out_value)));
    return _out;
}

// Custom attr: has_custom_attr on FileSequence
Napi::Value Wrap_fdl_file_sequence_has_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_file_sequence_has_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_type on FileSequence
Napi::Value Wrap_fdl_file_sequence_get_custom_attr_type(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_file_sequence_get_custom_attr_type(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: remove_custom_attr on FileSequence
Napi::Value Wrap_fdl_file_sequence_remove_custom_attr(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    auto _r = fdl_file_sequence_remove_custom_attr(handle, key_str.c_str());
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attrs_count on FileSequence
Napi::Value Wrap_fdl_file_sequence_custom_attrs_count(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    auto _r = fdl_file_sequence_custom_attrs_count(handle);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: custom_attr_name_at on FileSequence
Napi::Value Wrap_fdl_file_sequence_custom_attr_name_at(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    uint32_t arg0 = info[1].As<Napi::Number>().Uint32Value();
    const char* _r = fdl_file_sequence_custom_attr_name_at(handle, arg0);
    return _r ? Napi::String::New(env, _r) : env.Null();
}

// Custom attr: set_custom_attr_point_f64 on FileSequence
Napi::Value Wrap_fdl_file_sequence_set_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t arg1 = ObjectToPointF64(info[2].As<Napi::Object>());
    auto _r = fdl_file_sequence_set_custom_attr_point_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_point_f64 on FileSequence
Napi::Value Wrap_fdl_file_sequence_get_custom_attr_point_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_point_f64_t out_value = {};
    int _rv = fdl_file_sequence_get_custom_attr_point_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", PointF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_f64 on FileSequence
Napi::Value Wrap_fdl_file_sequence_set_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t arg1 = ObjectToDimensionsF64(info[2].As<Napi::Object>());
    auto _r = fdl_file_sequence_set_custom_attr_dims_f64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_f64 on FileSequence
Napi::Value Wrap_fdl_file_sequence_get_custom_attr_dims_f64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_f64_t out_value = {};
    int _rv = fdl_file_sequence_get_custom_attr_dims_f64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsF64ToObject(env, out_value));
    return _out;
}

// Custom attr: set_custom_attr_dims_i64 on FileSequence
Napi::Value Wrap_fdl_file_sequence_set_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t arg1 = ObjectToDimensionsI64(info[2].As<Napi::Object>());
    auto _r = fdl_file_sequence_set_custom_attr_dims_i64(handle, key_str.c_str(), arg1);
    return Napi::Number::New(env, static_cast<double>(_r));
}

// Custom attr: get_custom_attr_dims_i64 on FileSequence
Napi::Value Wrap_fdl_file_sequence_get_custom_attr_dims_i64(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    auto* handle = static_cast<fdl_file_sequence_t*>(UnwrapHandle(info[0]));
    std::string key_str = info[1].As<Napi::String>().Utf8Value();
    fdl_dimensions_i64_t out_value = {};
    int _rv = fdl_file_sequence_get_custom_attr_dims_i64(handle, key_str.c_str(), &out_value);
    auto _out = Napi::Object::New(env);
    _out.Set("_return", Napi::Number::New(env, static_cast<double>(_rv)));
    _out.Set("value", DimensionsI64ToObject(env, out_value));
    return _out;
}

// -----------------------------------------------------------------------
// Module registration
// -----------------------------------------------------------------------

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set("fdl_abi_version", Napi::Function::New(env, Wrap_fdl_abi_version));
    exports.Set("fdl_alignment_shift", Napi::Function::New(env, Wrap_fdl_alignment_shift));
    exports.Set("fdl_apply_canvas_template", Napi::Function::New(env, Wrap_fdl_apply_canvas_template));
    exports.Set("fdl_calculate_scale_factor", Napi::Function::New(env, Wrap_fdl_calculate_scale_factor));
    exports.Set("fdl_canvas_add_framing_decision", Napi::Function::New(env, Wrap_fdl_canvas_add_framing_decision));
    exports.Set(
        "fdl_canvas_find_framing_decision_by_id",
        Napi::Function::New(env, Wrap_fdl_canvas_find_framing_decision_by_id));
    exports.Set("fdl_canvas_framing_decision_at", Napi::Function::New(env, Wrap_fdl_canvas_framing_decision_at));
    exports.Set(
        "fdl_canvas_framing_decisions_count", Napi::Function::New(env, Wrap_fdl_canvas_framing_decisions_count));
    exports.Set("fdl_canvas_get_anamorphic_squeeze", Napi::Function::New(env, Wrap_fdl_canvas_get_anamorphic_squeeze));
    exports.Set("fdl_canvas_get_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_get_dimensions));
    exports.Set(
        "fdl_canvas_get_effective_anchor_point", Napi::Function::New(env, Wrap_fdl_canvas_get_effective_anchor_point));
    exports.Set(
        "fdl_canvas_get_effective_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_get_effective_dimensions));
    exports.Set("fdl_canvas_get_effective_rect", Napi::Function::New(env, Wrap_fdl_canvas_get_effective_rect));
    exports.Set("fdl_canvas_get_id", Napi::Function::New(env, Wrap_fdl_canvas_get_id));
    exports.Set("fdl_canvas_get_label", Napi::Function::New(env, Wrap_fdl_canvas_get_label));
    exports.Set(
        "fdl_canvas_get_photosite_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_get_photosite_dimensions));
    exports.Set(
        "fdl_canvas_get_physical_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_get_physical_dimensions));
    exports.Set("fdl_canvas_get_rect", Napi::Function::New(env, Wrap_fdl_canvas_get_rect));
    exports.Set("fdl_canvas_get_source_canvas_id", Napi::Function::New(env, Wrap_fdl_canvas_get_source_canvas_id));
    exports.Set(
        "fdl_canvas_has_effective_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_has_effective_dimensions));
    exports.Set(
        "fdl_canvas_has_photosite_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_has_photosite_dimensions));
    exports.Set(
        "fdl_canvas_has_physical_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_has_physical_dimensions));
    exports.Set("fdl_canvas_remove_effective", Napi::Function::New(env, Wrap_fdl_canvas_remove_effective));
    exports.Set("fdl_canvas_set_anamorphic_squeeze", Napi::Function::New(env, Wrap_fdl_canvas_set_anamorphic_squeeze));
    exports.Set("fdl_canvas_set_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_set_dimensions));
    exports.Set(
        "fdl_canvas_set_effective_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_set_effective_dimensions));
    exports.Set(
        "fdl_canvas_set_effective_dims_only", Napi::Function::New(env, Wrap_fdl_canvas_set_effective_dims_only));
    exports.Set(
        "fdl_canvas_set_photosite_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_set_photosite_dimensions));
    exports.Set(
        "fdl_canvas_set_physical_dimensions", Napi::Function::New(env, Wrap_fdl_canvas_set_physical_dimensions));
    exports.Set(
        "fdl_canvas_template_get_alignment_method_horizontal",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_alignment_method_horizontal));
    exports.Set(
        "fdl_canvas_template_get_alignment_method_vertical",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_alignment_method_vertical));
    exports.Set(
        "fdl_canvas_template_get_fit_method", Napi::Function::New(env, Wrap_fdl_canvas_template_get_fit_method));
    exports.Set(
        "fdl_canvas_template_get_fit_source", Napi::Function::New(env, Wrap_fdl_canvas_template_get_fit_source));
    exports.Set("fdl_canvas_template_get_id", Napi::Function::New(env, Wrap_fdl_canvas_template_get_id));
    exports.Set("fdl_canvas_template_get_label", Napi::Function::New(env, Wrap_fdl_canvas_template_get_label));
    exports.Set(
        "fdl_canvas_template_get_maximum_dimensions",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_maximum_dimensions));
    exports.Set(
        "fdl_canvas_template_get_pad_to_maximum",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_pad_to_maximum));
    exports.Set(
        "fdl_canvas_template_get_preserve_from_source_canvas",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_preserve_from_source_canvas));
    exports.Set("fdl_canvas_template_get_round", Napi::Function::New(env, Wrap_fdl_canvas_template_get_round));
    exports.Set(
        "fdl_canvas_template_get_target_anamorphic_squeeze",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_target_anamorphic_squeeze));
    exports.Set(
        "fdl_canvas_template_get_target_dimensions",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_target_dimensions));
    exports.Set(
        "fdl_canvas_template_has_maximum_dimensions",
        Napi::Function::New(env, Wrap_fdl_canvas_template_has_maximum_dimensions));
    exports.Set(
        "fdl_canvas_template_has_preserve_from_source_canvas",
        Napi::Function::New(env, Wrap_fdl_canvas_template_has_preserve_from_source_canvas));
    exports.Set(
        "fdl_canvas_template_set_maximum_dimensions",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_maximum_dimensions));
    exports.Set(
        "fdl_canvas_template_set_pad_to_maximum",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_pad_to_maximum));
    exports.Set(
        "fdl_canvas_template_set_preserve_from_source_canvas",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_preserve_from_source_canvas));
    exports.Set("fdl_canvas_template_to_json", Napi::Function::New(env, Wrap_fdl_canvas_template_to_json));
    exports.Set("fdl_canvas_to_json", Napi::Function::New(env, Wrap_fdl_canvas_to_json));
    exports.Set("fdl_clip_id_get_clip_name", Napi::Function::New(env, Wrap_fdl_clip_id_get_clip_name));
    exports.Set("fdl_clip_id_get_file", Napi::Function::New(env, Wrap_fdl_clip_id_get_file));
    exports.Set("fdl_clip_id_has_file", Napi::Function::New(env, Wrap_fdl_clip_id_has_file));
    exports.Set("fdl_clip_id_has_sequence", Napi::Function::New(env, Wrap_fdl_clip_id_has_sequence));
    exports.Set("fdl_clip_id_sequence", Napi::Function::New(env, Wrap_fdl_clip_id_sequence));
    exports.Set("fdl_clip_id_to_json", Napi::Function::New(env, Wrap_fdl_clip_id_to_json));
    exports.Set("fdl_clip_id_validate_json", Napi::Function::New(env, Wrap_fdl_clip_id_validate_json));
    exports.Set("fdl_compute_framing_from_intent", Napi::Function::New(env, Wrap_fdl_compute_framing_from_intent));
    exports.Set("fdl_context_add_canvas", Napi::Function::New(env, Wrap_fdl_context_add_canvas));
    exports.Set("fdl_context_canvas_at", Napi::Function::New(env, Wrap_fdl_context_canvas_at));
    exports.Set("fdl_context_canvases_count", Napi::Function::New(env, Wrap_fdl_context_canvases_count));
    exports.Set("fdl_context_clip_id", Napi::Function::New(env, Wrap_fdl_context_clip_id));
    exports.Set("fdl_context_find_canvas_by_id", Napi::Function::New(env, Wrap_fdl_context_find_canvas_by_id));
    exports.Set("fdl_context_get_clip_id", Napi::Function::New(env, Wrap_fdl_context_get_clip_id));
    exports.Set("fdl_context_get_context_creator", Napi::Function::New(env, Wrap_fdl_context_get_context_creator));
    exports.Set("fdl_context_get_label", Napi::Function::New(env, Wrap_fdl_context_get_label));
    exports.Set("fdl_context_has_clip_id", Napi::Function::New(env, Wrap_fdl_context_has_clip_id));
    exports.Set("fdl_context_remove_clip_id", Napi::Function::New(env, Wrap_fdl_context_remove_clip_id));
    exports.Set(
        "fdl_context_resolve_canvas_for_dimensions",
        Napi::Function::New(env, Wrap_fdl_context_resolve_canvas_for_dimensions));
    exports.Set("fdl_context_set_clip_id_json", Napi::Function::New(env, Wrap_fdl_context_set_clip_id_json));
    exports.Set("fdl_context_to_json", Napi::Function::New(env, Wrap_fdl_context_to_json));
    exports.Set("fdl_dimensions_clamp_to_dims", Napi::Function::New(env, Wrap_fdl_dimensions_clamp_to_dims));
    exports.Set("fdl_dimensions_equal", Napi::Function::New(env, Wrap_fdl_dimensions_equal));
    exports.Set("fdl_dimensions_f64_gt", Napi::Function::New(env, Wrap_fdl_dimensions_f64_gt));
    exports.Set("fdl_dimensions_f64_lt", Napi::Function::New(env, Wrap_fdl_dimensions_f64_lt));
    exports.Set("fdl_dimensions_f64_to_i64", Napi::Function::New(env, Wrap_fdl_dimensions_f64_to_i64));
    exports.Set("fdl_dimensions_i64_gt", Napi::Function::New(env, Wrap_fdl_dimensions_i64_gt));
    exports.Set("fdl_dimensions_i64_is_zero", Napi::Function::New(env, Wrap_fdl_dimensions_i64_is_zero));
    exports.Set("fdl_dimensions_i64_lt", Napi::Function::New(env, Wrap_fdl_dimensions_i64_lt));
    exports.Set("fdl_dimensions_i64_normalize", Napi::Function::New(env, Wrap_fdl_dimensions_i64_normalize));
    exports.Set("fdl_dimensions_is_zero", Napi::Function::New(env, Wrap_fdl_dimensions_is_zero));
    exports.Set("fdl_dimensions_normalize", Napi::Function::New(env, Wrap_fdl_dimensions_normalize));
    exports.Set(
        "fdl_dimensions_normalize_and_scale", Napi::Function::New(env, Wrap_fdl_dimensions_normalize_and_scale));
    exports.Set("fdl_dimensions_scale", Napi::Function::New(env, Wrap_fdl_dimensions_scale));
    exports.Set("fdl_dimensions_sub", Napi::Function::New(env, Wrap_fdl_dimensions_sub));
    exports.Set("fdl_doc_add_canvas_template", Napi::Function::New(env, Wrap_fdl_doc_add_canvas_template));
    exports.Set("fdl_doc_add_context", Napi::Function::New(env, Wrap_fdl_doc_add_context));
    exports.Set("fdl_doc_add_framing_intent", Napi::Function::New(env, Wrap_fdl_doc_add_framing_intent));
    exports.Set("fdl_doc_canvas_template_at", Napi::Function::New(env, Wrap_fdl_doc_canvas_template_at));
    exports.Set(
        "fdl_doc_canvas_template_find_by_id", Napi::Function::New(env, Wrap_fdl_doc_canvas_template_find_by_id));
    exports.Set("fdl_doc_canvas_templates_count", Napi::Function::New(env, Wrap_fdl_doc_canvas_templates_count));
    exports.Set("fdl_doc_context_at", Napi::Function::New(env, Wrap_fdl_doc_context_at));
    exports.Set("fdl_doc_context_find_by_label", Napi::Function::New(env, Wrap_fdl_doc_context_find_by_label));
    exports.Set("fdl_doc_contexts_count", Napi::Function::New(env, Wrap_fdl_doc_contexts_count));
    exports.Set("fdl_doc_create", Napi::Function::New(env, Wrap_fdl_doc_create));
    exports.Set("fdl_doc_create_with_header", Napi::Function::New(env, Wrap_fdl_doc_create_with_header));
    exports.Set("fdl_doc_framing_intent_at", Napi::Function::New(env, Wrap_fdl_doc_framing_intent_at));
    exports.Set("fdl_doc_framing_intent_find_by_id", Napi::Function::New(env, Wrap_fdl_doc_framing_intent_find_by_id));
    exports.Set("fdl_doc_framing_intents_count", Napi::Function::New(env, Wrap_fdl_doc_framing_intents_count));
    exports.Set("fdl_doc_free", Napi::Function::New(env, Wrap_fdl_doc_free));
    exports.Set(
        "fdl_doc_get_default_framing_intent", Napi::Function::New(env, Wrap_fdl_doc_get_default_framing_intent));
    exports.Set("fdl_doc_get_fdl_creator", Napi::Function::New(env, Wrap_fdl_doc_get_fdl_creator));
    exports.Set("fdl_doc_get_uuid", Napi::Function::New(env, Wrap_fdl_doc_get_uuid));
    exports.Set("fdl_doc_get_version_major", Napi::Function::New(env, Wrap_fdl_doc_get_version_major));
    exports.Set("fdl_doc_get_version_minor", Napi::Function::New(env, Wrap_fdl_doc_get_version_minor));
    exports.Set("fdl_doc_parse_json", Napi::Function::New(env, Wrap_fdl_doc_parse_json));
    exports.Set(
        "fdl_doc_set_default_framing_intent", Napi::Function::New(env, Wrap_fdl_doc_set_default_framing_intent));
    exports.Set("fdl_doc_set_fdl_creator", Napi::Function::New(env, Wrap_fdl_doc_set_fdl_creator));
    exports.Set("fdl_doc_set_uuid", Napi::Function::New(env, Wrap_fdl_doc_set_uuid));
    exports.Set("fdl_doc_set_version", Napi::Function::New(env, Wrap_fdl_doc_set_version));
    exports.Set("fdl_doc_to_json", Napi::Function::New(env, Wrap_fdl_doc_to_json));
    exports.Set("fdl_doc_validate", Napi::Function::New(env, Wrap_fdl_doc_validate));
    exports.Set("fdl_file_sequence_get_idx", Napi::Function::New(env, Wrap_fdl_file_sequence_get_idx));
    exports.Set("fdl_file_sequence_get_max", Napi::Function::New(env, Wrap_fdl_file_sequence_get_max));
    exports.Set("fdl_file_sequence_get_min", Napi::Function::New(env, Wrap_fdl_file_sequence_get_min));
    exports.Set("fdl_file_sequence_get_value", Napi::Function::New(env, Wrap_fdl_file_sequence_get_value));
    exports.Set("fdl_fp_abs_tol", Napi::Function::New(env, Wrap_fdl_fp_abs_tol));
    exports.Set("fdl_fp_rel_tol", Napi::Function::New(env, Wrap_fdl_fp_rel_tol));
    exports.Set(
        "fdl_framing_decision_adjust_anchor", Napi::Function::New(env, Wrap_fdl_framing_decision_adjust_anchor));
    exports.Set(
        "fdl_framing_decision_adjust_protection_anchor",
        Napi::Function::New(env, Wrap_fdl_framing_decision_adjust_protection_anchor));
    exports.Set(
        "fdl_framing_decision_get_anchor_point", Napi::Function::New(env, Wrap_fdl_framing_decision_get_anchor_point));
    exports.Set(
        "fdl_framing_decision_get_dimensions", Napi::Function::New(env, Wrap_fdl_framing_decision_get_dimensions));
    exports.Set(
        "fdl_framing_decision_get_framing_intent_id",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_framing_intent_id));
    exports.Set("fdl_framing_decision_get_id", Napi::Function::New(env, Wrap_fdl_framing_decision_get_id));
    exports.Set("fdl_framing_decision_get_label", Napi::Function::New(env, Wrap_fdl_framing_decision_get_label));
    exports.Set(
        "fdl_framing_decision_get_protection_anchor_point",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_protection_anchor_point));
    exports.Set(
        "fdl_framing_decision_get_protection_dimensions",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_protection_dimensions));
    exports.Set(
        "fdl_framing_decision_get_protection_rect",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_protection_rect));
    exports.Set("fdl_framing_decision_get_rect", Napi::Function::New(env, Wrap_fdl_framing_decision_get_rect));
    exports.Set(
        "fdl_framing_decision_has_protection", Napi::Function::New(env, Wrap_fdl_framing_decision_has_protection));
    exports.Set(
        "fdl_framing_decision_populate_from_intent",
        Napi::Function::New(env, Wrap_fdl_framing_decision_populate_from_intent));
    exports.Set(
        "fdl_framing_decision_remove_protection",
        Napi::Function::New(env, Wrap_fdl_framing_decision_remove_protection));
    exports.Set(
        "fdl_framing_decision_set_anchor_point", Napi::Function::New(env, Wrap_fdl_framing_decision_set_anchor_point));
    exports.Set(
        "fdl_framing_decision_set_dimensions", Napi::Function::New(env, Wrap_fdl_framing_decision_set_dimensions));
    exports.Set(
        "fdl_framing_decision_set_protection", Napi::Function::New(env, Wrap_fdl_framing_decision_set_protection));
    exports.Set(
        "fdl_framing_decision_set_protection_anchor_point",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_protection_anchor_point));
    exports.Set(
        "fdl_framing_decision_set_protection_dimensions",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_protection_dimensions));
    exports.Set("fdl_framing_decision_to_json", Napi::Function::New(env, Wrap_fdl_framing_decision_to_json));
    exports.Set(
        "fdl_framing_intent_get_aspect_ratio", Napi::Function::New(env, Wrap_fdl_framing_intent_get_aspect_ratio));
    exports.Set("fdl_framing_intent_get_id", Napi::Function::New(env, Wrap_fdl_framing_intent_get_id));
    exports.Set("fdl_framing_intent_get_label", Napi::Function::New(env, Wrap_fdl_framing_intent_get_label));
    exports.Set("fdl_framing_intent_get_protection", Napi::Function::New(env, Wrap_fdl_framing_intent_get_protection));
    exports.Set(
        "fdl_framing_intent_set_aspect_ratio", Napi::Function::New(env, Wrap_fdl_framing_intent_set_aspect_ratio));
    exports.Set("fdl_framing_intent_set_protection", Napi::Function::New(env, Wrap_fdl_framing_intent_set_protection));
    exports.Set("fdl_framing_intent_to_json", Napi::Function::New(env, Wrap_fdl_framing_intent_to_json));
    exports.Set("fdl_free", Napi::Function::New(env, Wrap_fdl_free));
    exports.Set("fdl_geometry_apply_offset", Napi::Function::New(env, Wrap_fdl_geometry_apply_offset));
    exports.Set("fdl_geometry_crop", Napi::Function::New(env, Wrap_fdl_geometry_crop));
    exports.Set("fdl_geometry_fill_hierarchy_gaps", Napi::Function::New(env, Wrap_fdl_geometry_fill_hierarchy_gaps));
    exports.Set(
        "fdl_geometry_get_dims_anchor_from_path",
        Napi::Function::New(env, Wrap_fdl_geometry_get_dims_anchor_from_path));
    exports.Set("fdl_geometry_normalize_and_scale", Napi::Function::New(env, Wrap_fdl_geometry_normalize_and_scale));
    exports.Set("fdl_geometry_round", Napi::Function::New(env, Wrap_fdl_geometry_round));
    exports.Set("fdl_make_rect", Napi::Function::New(env, Wrap_fdl_make_rect));
    exports.Set("fdl_output_size_for_axis", Napi::Function::New(env, Wrap_fdl_output_size_for_axis));
    exports.Set("fdl_point_add", Napi::Function::New(env, Wrap_fdl_point_add));
    exports.Set("fdl_point_clamp", Napi::Function::New(env, Wrap_fdl_point_clamp));
    exports.Set("fdl_point_equal", Napi::Function::New(env, Wrap_fdl_point_equal));
    exports.Set("fdl_point_f64_gt", Napi::Function::New(env, Wrap_fdl_point_f64_gt));
    exports.Set("fdl_point_f64_lt", Napi::Function::New(env, Wrap_fdl_point_f64_lt));
    exports.Set("fdl_point_is_zero", Napi::Function::New(env, Wrap_fdl_point_is_zero));
    exports.Set("fdl_point_mul_scalar", Napi::Function::New(env, Wrap_fdl_point_mul_scalar));
    exports.Set("fdl_point_normalize", Napi::Function::New(env, Wrap_fdl_point_normalize));
    exports.Set("fdl_point_normalize_and_scale", Napi::Function::New(env, Wrap_fdl_point_normalize_and_scale));
    exports.Set("fdl_point_scale", Napi::Function::New(env, Wrap_fdl_point_scale));
    exports.Set("fdl_point_sub", Napi::Function::New(env, Wrap_fdl_point_sub));
    exports.Set("fdl_resolve_geometry_layer", Napi::Function::New(env, Wrap_fdl_resolve_geometry_layer));
    exports.Set("fdl_round", Napi::Function::New(env, Wrap_fdl_round));
    exports.Set("fdl_round_dimensions", Napi::Function::New(env, Wrap_fdl_round_dimensions));
    exports.Set("fdl_round_point", Napi::Function::New(env, Wrap_fdl_round_point));
    exports.Set("fdl_template_result_free", Napi::Function::New(env, Wrap_fdl_template_result_free));
    exports.Set("fdl_validation_result_error_at", Napi::Function::New(env, Wrap_fdl_validation_result_error_at));
    exports.Set("fdl_validation_result_error_count", Napi::Function::New(env, Wrap_fdl_validation_result_error_count));
    exports.Set("fdl_validation_result_free", Napi::Function::New(env, Wrap_fdl_validation_result_free));
    exports.Set("fdl_doc_set_custom_attr_string", Napi::Function::New(env, Wrap_fdl_doc_set_custom_attr_string));
    exports.Set("fdl_doc_set_custom_attr_int", Napi::Function::New(env, Wrap_fdl_doc_set_custom_attr_int));
    exports.Set("fdl_doc_set_custom_attr_float", Napi::Function::New(env, Wrap_fdl_doc_set_custom_attr_float));
    exports.Set("fdl_doc_set_custom_attr_bool", Napi::Function::New(env, Wrap_fdl_doc_set_custom_attr_bool));
    exports.Set("fdl_doc_get_custom_attr_string", Napi::Function::New(env, Wrap_fdl_doc_get_custom_attr_string));
    exports.Set("fdl_doc_get_custom_attr_int", Napi::Function::New(env, Wrap_fdl_doc_get_custom_attr_int));
    exports.Set("fdl_doc_get_custom_attr_float", Napi::Function::New(env, Wrap_fdl_doc_get_custom_attr_float));
    exports.Set("fdl_doc_get_custom_attr_bool", Napi::Function::New(env, Wrap_fdl_doc_get_custom_attr_bool));
    exports.Set("fdl_doc_has_custom_attr", Napi::Function::New(env, Wrap_fdl_doc_has_custom_attr));
    exports.Set("fdl_doc_get_custom_attr_type", Napi::Function::New(env, Wrap_fdl_doc_get_custom_attr_type));
    exports.Set("fdl_doc_remove_custom_attr", Napi::Function::New(env, Wrap_fdl_doc_remove_custom_attr));
    exports.Set("fdl_doc_custom_attrs_count", Napi::Function::New(env, Wrap_fdl_doc_custom_attrs_count));
    exports.Set("fdl_doc_custom_attr_name_at", Napi::Function::New(env, Wrap_fdl_doc_custom_attr_name_at));
    exports.Set("fdl_doc_set_custom_attr_point_f64", Napi::Function::New(env, Wrap_fdl_doc_set_custom_attr_point_f64));
    exports.Set("fdl_doc_get_custom_attr_point_f64", Napi::Function::New(env, Wrap_fdl_doc_get_custom_attr_point_f64));
    exports.Set("fdl_doc_set_custom_attr_dims_f64", Napi::Function::New(env, Wrap_fdl_doc_set_custom_attr_dims_f64));
    exports.Set("fdl_doc_get_custom_attr_dims_f64", Napi::Function::New(env, Wrap_fdl_doc_get_custom_attr_dims_f64));
    exports.Set("fdl_doc_set_custom_attr_dims_i64", Napi::Function::New(env, Wrap_fdl_doc_set_custom_attr_dims_i64));
    exports.Set("fdl_doc_get_custom_attr_dims_i64", Napi::Function::New(env, Wrap_fdl_doc_get_custom_attr_dims_i64));
    exports.Set(
        "fdl_context_set_custom_attr_string", Napi::Function::New(env, Wrap_fdl_context_set_custom_attr_string));
    exports.Set("fdl_context_set_custom_attr_int", Napi::Function::New(env, Wrap_fdl_context_set_custom_attr_int));
    exports.Set("fdl_context_set_custom_attr_float", Napi::Function::New(env, Wrap_fdl_context_set_custom_attr_float));
    exports.Set("fdl_context_set_custom_attr_bool", Napi::Function::New(env, Wrap_fdl_context_set_custom_attr_bool));
    exports.Set(
        "fdl_context_get_custom_attr_string", Napi::Function::New(env, Wrap_fdl_context_get_custom_attr_string));
    exports.Set("fdl_context_get_custom_attr_int", Napi::Function::New(env, Wrap_fdl_context_get_custom_attr_int));
    exports.Set("fdl_context_get_custom_attr_float", Napi::Function::New(env, Wrap_fdl_context_get_custom_attr_float));
    exports.Set("fdl_context_get_custom_attr_bool", Napi::Function::New(env, Wrap_fdl_context_get_custom_attr_bool));
    exports.Set("fdl_context_has_custom_attr", Napi::Function::New(env, Wrap_fdl_context_has_custom_attr));
    exports.Set("fdl_context_get_custom_attr_type", Napi::Function::New(env, Wrap_fdl_context_get_custom_attr_type));
    exports.Set("fdl_context_remove_custom_attr", Napi::Function::New(env, Wrap_fdl_context_remove_custom_attr));
    exports.Set("fdl_context_custom_attrs_count", Napi::Function::New(env, Wrap_fdl_context_custom_attrs_count));
    exports.Set("fdl_context_custom_attr_name_at", Napi::Function::New(env, Wrap_fdl_context_custom_attr_name_at));
    exports.Set(
        "fdl_context_set_custom_attr_point_f64", Napi::Function::New(env, Wrap_fdl_context_set_custom_attr_point_f64));
    exports.Set(
        "fdl_context_get_custom_attr_point_f64", Napi::Function::New(env, Wrap_fdl_context_get_custom_attr_point_f64));
    exports.Set(
        "fdl_context_set_custom_attr_dims_f64", Napi::Function::New(env, Wrap_fdl_context_set_custom_attr_dims_f64));
    exports.Set(
        "fdl_context_get_custom_attr_dims_f64", Napi::Function::New(env, Wrap_fdl_context_get_custom_attr_dims_f64));
    exports.Set(
        "fdl_context_set_custom_attr_dims_i64", Napi::Function::New(env, Wrap_fdl_context_set_custom_attr_dims_i64));
    exports.Set(
        "fdl_context_get_custom_attr_dims_i64", Napi::Function::New(env, Wrap_fdl_context_get_custom_attr_dims_i64));
    exports.Set("fdl_canvas_set_custom_attr_string", Napi::Function::New(env, Wrap_fdl_canvas_set_custom_attr_string));
    exports.Set("fdl_canvas_set_custom_attr_int", Napi::Function::New(env, Wrap_fdl_canvas_set_custom_attr_int));
    exports.Set("fdl_canvas_set_custom_attr_float", Napi::Function::New(env, Wrap_fdl_canvas_set_custom_attr_float));
    exports.Set("fdl_canvas_set_custom_attr_bool", Napi::Function::New(env, Wrap_fdl_canvas_set_custom_attr_bool));
    exports.Set("fdl_canvas_get_custom_attr_string", Napi::Function::New(env, Wrap_fdl_canvas_get_custom_attr_string));
    exports.Set("fdl_canvas_get_custom_attr_int", Napi::Function::New(env, Wrap_fdl_canvas_get_custom_attr_int));
    exports.Set("fdl_canvas_get_custom_attr_float", Napi::Function::New(env, Wrap_fdl_canvas_get_custom_attr_float));
    exports.Set("fdl_canvas_get_custom_attr_bool", Napi::Function::New(env, Wrap_fdl_canvas_get_custom_attr_bool));
    exports.Set("fdl_canvas_has_custom_attr", Napi::Function::New(env, Wrap_fdl_canvas_has_custom_attr));
    exports.Set("fdl_canvas_get_custom_attr_type", Napi::Function::New(env, Wrap_fdl_canvas_get_custom_attr_type));
    exports.Set("fdl_canvas_remove_custom_attr", Napi::Function::New(env, Wrap_fdl_canvas_remove_custom_attr));
    exports.Set("fdl_canvas_custom_attrs_count", Napi::Function::New(env, Wrap_fdl_canvas_custom_attrs_count));
    exports.Set("fdl_canvas_custom_attr_name_at", Napi::Function::New(env, Wrap_fdl_canvas_custom_attr_name_at));
    exports.Set(
        "fdl_canvas_set_custom_attr_point_f64", Napi::Function::New(env, Wrap_fdl_canvas_set_custom_attr_point_f64));
    exports.Set(
        "fdl_canvas_get_custom_attr_point_f64", Napi::Function::New(env, Wrap_fdl_canvas_get_custom_attr_point_f64));
    exports.Set(
        "fdl_canvas_set_custom_attr_dims_f64", Napi::Function::New(env, Wrap_fdl_canvas_set_custom_attr_dims_f64));
    exports.Set(
        "fdl_canvas_get_custom_attr_dims_f64", Napi::Function::New(env, Wrap_fdl_canvas_get_custom_attr_dims_f64));
    exports.Set(
        "fdl_canvas_set_custom_attr_dims_i64", Napi::Function::New(env, Wrap_fdl_canvas_set_custom_attr_dims_i64));
    exports.Set(
        "fdl_canvas_get_custom_attr_dims_i64", Napi::Function::New(env, Wrap_fdl_canvas_get_custom_attr_dims_i64));
    exports.Set(
        "fdl_framing_decision_set_custom_attr_string",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_custom_attr_string));
    exports.Set(
        "fdl_framing_decision_set_custom_attr_int",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_custom_attr_int));
    exports.Set(
        "fdl_framing_decision_set_custom_attr_float",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_custom_attr_float));
    exports.Set(
        "fdl_framing_decision_set_custom_attr_bool",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_custom_attr_bool));
    exports.Set(
        "fdl_framing_decision_get_custom_attr_string",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_custom_attr_string));
    exports.Set(
        "fdl_framing_decision_get_custom_attr_int",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_custom_attr_int));
    exports.Set(
        "fdl_framing_decision_get_custom_attr_float",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_custom_attr_float));
    exports.Set(
        "fdl_framing_decision_get_custom_attr_bool",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_custom_attr_bool));
    exports.Set(
        "fdl_framing_decision_has_custom_attr", Napi::Function::New(env, Wrap_fdl_framing_decision_has_custom_attr));
    exports.Set(
        "fdl_framing_decision_get_custom_attr_type",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_custom_attr_type));
    exports.Set(
        "fdl_framing_decision_remove_custom_attr",
        Napi::Function::New(env, Wrap_fdl_framing_decision_remove_custom_attr));
    exports.Set(
        "fdl_framing_decision_custom_attrs_count",
        Napi::Function::New(env, Wrap_fdl_framing_decision_custom_attrs_count));
    exports.Set(
        "fdl_framing_decision_custom_attr_name_at",
        Napi::Function::New(env, Wrap_fdl_framing_decision_custom_attr_name_at));
    exports.Set(
        "fdl_framing_decision_set_custom_attr_point_f64",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_custom_attr_point_f64));
    exports.Set(
        "fdl_framing_decision_get_custom_attr_point_f64",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_custom_attr_point_f64));
    exports.Set(
        "fdl_framing_decision_set_custom_attr_dims_f64",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_custom_attr_dims_f64));
    exports.Set(
        "fdl_framing_decision_get_custom_attr_dims_f64",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_custom_attr_dims_f64));
    exports.Set(
        "fdl_framing_decision_set_custom_attr_dims_i64",
        Napi::Function::New(env, Wrap_fdl_framing_decision_set_custom_attr_dims_i64));
    exports.Set(
        "fdl_framing_decision_get_custom_attr_dims_i64",
        Napi::Function::New(env, Wrap_fdl_framing_decision_get_custom_attr_dims_i64));
    exports.Set(
        "fdl_framing_intent_set_custom_attr_string",
        Napi::Function::New(env, Wrap_fdl_framing_intent_set_custom_attr_string));
    exports.Set(
        "fdl_framing_intent_set_custom_attr_int",
        Napi::Function::New(env, Wrap_fdl_framing_intent_set_custom_attr_int));
    exports.Set(
        "fdl_framing_intent_set_custom_attr_float",
        Napi::Function::New(env, Wrap_fdl_framing_intent_set_custom_attr_float));
    exports.Set(
        "fdl_framing_intent_set_custom_attr_bool",
        Napi::Function::New(env, Wrap_fdl_framing_intent_set_custom_attr_bool));
    exports.Set(
        "fdl_framing_intent_get_custom_attr_string",
        Napi::Function::New(env, Wrap_fdl_framing_intent_get_custom_attr_string));
    exports.Set(
        "fdl_framing_intent_get_custom_attr_int",
        Napi::Function::New(env, Wrap_fdl_framing_intent_get_custom_attr_int));
    exports.Set(
        "fdl_framing_intent_get_custom_attr_float",
        Napi::Function::New(env, Wrap_fdl_framing_intent_get_custom_attr_float));
    exports.Set(
        "fdl_framing_intent_get_custom_attr_bool",
        Napi::Function::New(env, Wrap_fdl_framing_intent_get_custom_attr_bool));
    exports.Set(
        "fdl_framing_intent_has_custom_attr", Napi::Function::New(env, Wrap_fdl_framing_intent_has_custom_attr));
    exports.Set(
        "fdl_framing_intent_get_custom_attr_type",
        Napi::Function::New(env, Wrap_fdl_framing_intent_get_custom_attr_type));
    exports.Set(
        "fdl_framing_intent_remove_custom_attr", Napi::Function::New(env, Wrap_fdl_framing_intent_remove_custom_attr));
    exports.Set(
        "fdl_framing_intent_custom_attrs_count", Napi::Function::New(env, Wrap_fdl_framing_intent_custom_attrs_count));
    exports.Set(
        "fdl_framing_intent_custom_attr_name_at",
        Napi::Function::New(env, Wrap_fdl_framing_intent_custom_attr_name_at));
    exports.Set(
        "fdl_framing_intent_set_custom_attr_point_f64",
        Napi::Function::New(env, Wrap_fdl_framing_intent_set_custom_attr_point_f64));
    exports.Set(
        "fdl_framing_intent_get_custom_attr_point_f64",
        Napi::Function::New(env, Wrap_fdl_framing_intent_get_custom_attr_point_f64));
    exports.Set(
        "fdl_framing_intent_set_custom_attr_dims_f64",
        Napi::Function::New(env, Wrap_fdl_framing_intent_set_custom_attr_dims_f64));
    exports.Set(
        "fdl_framing_intent_get_custom_attr_dims_f64",
        Napi::Function::New(env, Wrap_fdl_framing_intent_get_custom_attr_dims_f64));
    exports.Set(
        "fdl_framing_intent_set_custom_attr_dims_i64",
        Napi::Function::New(env, Wrap_fdl_framing_intent_set_custom_attr_dims_i64));
    exports.Set(
        "fdl_framing_intent_get_custom_attr_dims_i64",
        Napi::Function::New(env, Wrap_fdl_framing_intent_get_custom_attr_dims_i64));
    exports.Set(
        "fdl_canvas_template_set_custom_attr_string",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_custom_attr_string));
    exports.Set(
        "fdl_canvas_template_set_custom_attr_int",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_custom_attr_int));
    exports.Set(
        "fdl_canvas_template_set_custom_attr_float",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_custom_attr_float));
    exports.Set(
        "fdl_canvas_template_set_custom_attr_bool",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_custom_attr_bool));
    exports.Set(
        "fdl_canvas_template_get_custom_attr_string",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_custom_attr_string));
    exports.Set(
        "fdl_canvas_template_get_custom_attr_int",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_custom_attr_int));
    exports.Set(
        "fdl_canvas_template_get_custom_attr_float",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_custom_attr_float));
    exports.Set(
        "fdl_canvas_template_get_custom_attr_bool",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_custom_attr_bool));
    exports.Set(
        "fdl_canvas_template_has_custom_attr", Napi::Function::New(env, Wrap_fdl_canvas_template_has_custom_attr));
    exports.Set(
        "fdl_canvas_template_get_custom_attr_type",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_custom_attr_type));
    exports.Set(
        "fdl_canvas_template_remove_custom_attr",
        Napi::Function::New(env, Wrap_fdl_canvas_template_remove_custom_attr));
    exports.Set(
        "fdl_canvas_template_custom_attrs_count",
        Napi::Function::New(env, Wrap_fdl_canvas_template_custom_attrs_count));
    exports.Set(
        "fdl_canvas_template_custom_attr_name_at",
        Napi::Function::New(env, Wrap_fdl_canvas_template_custom_attr_name_at));
    exports.Set(
        "fdl_canvas_template_set_custom_attr_point_f64",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_custom_attr_point_f64));
    exports.Set(
        "fdl_canvas_template_get_custom_attr_point_f64",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_custom_attr_point_f64));
    exports.Set(
        "fdl_canvas_template_set_custom_attr_dims_f64",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_custom_attr_dims_f64));
    exports.Set(
        "fdl_canvas_template_get_custom_attr_dims_f64",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_custom_attr_dims_f64));
    exports.Set(
        "fdl_canvas_template_set_custom_attr_dims_i64",
        Napi::Function::New(env, Wrap_fdl_canvas_template_set_custom_attr_dims_i64));
    exports.Set(
        "fdl_canvas_template_get_custom_attr_dims_i64",
        Napi::Function::New(env, Wrap_fdl_canvas_template_get_custom_attr_dims_i64));
    exports.Set(
        "fdl_clip_id_set_custom_attr_string", Napi::Function::New(env, Wrap_fdl_clip_id_set_custom_attr_string));
    exports.Set("fdl_clip_id_set_custom_attr_int", Napi::Function::New(env, Wrap_fdl_clip_id_set_custom_attr_int));
    exports.Set("fdl_clip_id_set_custom_attr_float", Napi::Function::New(env, Wrap_fdl_clip_id_set_custom_attr_float));
    exports.Set("fdl_clip_id_set_custom_attr_bool", Napi::Function::New(env, Wrap_fdl_clip_id_set_custom_attr_bool));
    exports.Set(
        "fdl_clip_id_get_custom_attr_string", Napi::Function::New(env, Wrap_fdl_clip_id_get_custom_attr_string));
    exports.Set("fdl_clip_id_get_custom_attr_int", Napi::Function::New(env, Wrap_fdl_clip_id_get_custom_attr_int));
    exports.Set("fdl_clip_id_get_custom_attr_float", Napi::Function::New(env, Wrap_fdl_clip_id_get_custom_attr_float));
    exports.Set("fdl_clip_id_get_custom_attr_bool", Napi::Function::New(env, Wrap_fdl_clip_id_get_custom_attr_bool));
    exports.Set("fdl_clip_id_has_custom_attr", Napi::Function::New(env, Wrap_fdl_clip_id_has_custom_attr));
    exports.Set("fdl_clip_id_get_custom_attr_type", Napi::Function::New(env, Wrap_fdl_clip_id_get_custom_attr_type));
    exports.Set("fdl_clip_id_remove_custom_attr", Napi::Function::New(env, Wrap_fdl_clip_id_remove_custom_attr));
    exports.Set("fdl_clip_id_custom_attrs_count", Napi::Function::New(env, Wrap_fdl_clip_id_custom_attrs_count));
    exports.Set("fdl_clip_id_custom_attr_name_at", Napi::Function::New(env, Wrap_fdl_clip_id_custom_attr_name_at));
    exports.Set(
        "fdl_clip_id_set_custom_attr_point_f64", Napi::Function::New(env, Wrap_fdl_clip_id_set_custom_attr_point_f64));
    exports.Set(
        "fdl_clip_id_get_custom_attr_point_f64", Napi::Function::New(env, Wrap_fdl_clip_id_get_custom_attr_point_f64));
    exports.Set(
        "fdl_clip_id_set_custom_attr_dims_f64", Napi::Function::New(env, Wrap_fdl_clip_id_set_custom_attr_dims_f64));
    exports.Set(
        "fdl_clip_id_get_custom_attr_dims_f64", Napi::Function::New(env, Wrap_fdl_clip_id_get_custom_attr_dims_f64));
    exports.Set(
        "fdl_clip_id_set_custom_attr_dims_i64", Napi::Function::New(env, Wrap_fdl_clip_id_set_custom_attr_dims_i64));
    exports.Set(
        "fdl_clip_id_get_custom_attr_dims_i64", Napi::Function::New(env, Wrap_fdl_clip_id_get_custom_attr_dims_i64));
    exports.Set(
        "fdl_file_sequence_set_custom_attr_string",
        Napi::Function::New(env, Wrap_fdl_file_sequence_set_custom_attr_string));
    exports.Set(
        "fdl_file_sequence_set_custom_attr_int", Napi::Function::New(env, Wrap_fdl_file_sequence_set_custom_attr_int));
    exports.Set(
        "fdl_file_sequence_set_custom_attr_float",
        Napi::Function::New(env, Wrap_fdl_file_sequence_set_custom_attr_float));
    exports.Set(
        "fdl_file_sequence_set_custom_attr_bool",
        Napi::Function::New(env, Wrap_fdl_file_sequence_set_custom_attr_bool));
    exports.Set(
        "fdl_file_sequence_get_custom_attr_string",
        Napi::Function::New(env, Wrap_fdl_file_sequence_get_custom_attr_string));
    exports.Set(
        "fdl_file_sequence_get_custom_attr_int", Napi::Function::New(env, Wrap_fdl_file_sequence_get_custom_attr_int));
    exports.Set(
        "fdl_file_sequence_get_custom_attr_float",
        Napi::Function::New(env, Wrap_fdl_file_sequence_get_custom_attr_float));
    exports.Set(
        "fdl_file_sequence_get_custom_attr_bool",
        Napi::Function::New(env, Wrap_fdl_file_sequence_get_custom_attr_bool));
    exports.Set("fdl_file_sequence_has_custom_attr", Napi::Function::New(env, Wrap_fdl_file_sequence_has_custom_attr));
    exports.Set(
        "fdl_file_sequence_get_custom_attr_type",
        Napi::Function::New(env, Wrap_fdl_file_sequence_get_custom_attr_type));
    exports.Set(
        "fdl_file_sequence_remove_custom_attr", Napi::Function::New(env, Wrap_fdl_file_sequence_remove_custom_attr));
    exports.Set(
        "fdl_file_sequence_custom_attrs_count", Napi::Function::New(env, Wrap_fdl_file_sequence_custom_attrs_count));
    exports.Set(
        "fdl_file_sequence_custom_attr_name_at", Napi::Function::New(env, Wrap_fdl_file_sequence_custom_attr_name_at));
    exports.Set(
        "fdl_file_sequence_set_custom_attr_point_f64",
        Napi::Function::New(env, Wrap_fdl_file_sequence_set_custom_attr_point_f64));
    exports.Set(
        "fdl_file_sequence_get_custom_attr_point_f64",
        Napi::Function::New(env, Wrap_fdl_file_sequence_get_custom_attr_point_f64));
    exports.Set(
        "fdl_file_sequence_set_custom_attr_dims_f64",
        Napi::Function::New(env, Wrap_fdl_file_sequence_set_custom_attr_dims_f64));
    exports.Set(
        "fdl_file_sequence_get_custom_attr_dims_f64",
        Napi::Function::New(env, Wrap_fdl_file_sequence_get_custom_attr_dims_f64));
    exports.Set(
        "fdl_file_sequence_set_custom_attr_dims_i64",
        Napi::Function::New(env, Wrap_fdl_file_sequence_set_custom_attr_dims_i64));
    exports.Set(
        "fdl_file_sequence_get_custom_attr_dims_i64",
        Napi::Function::New(env, Wrap_fdl_file_sequence_get_custom_attr_dims_i64));
    return exports;
}

NODE_API_MODULE(fdl_addon, Init)
