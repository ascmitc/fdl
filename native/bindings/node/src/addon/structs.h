// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
// AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
/**
 * @file structs.h
 * @brief C struct <-> Napi::Object conversion helpers for the Node.js addon.
 */

#pragma once
#include "fdl/fdl_core.h"
#include <napi.h>

// -----------------------------------------------------------------------
// fdl_abi_version_t
// -----------------------------------------------------------------------

inline fdl_abi_version_t ObjectToAbiVersion(const Napi::Object& obj) {
    fdl_abi_version_t result;
    result.major = obj.Get("major").As<Napi::Number>().Uint32Value();
    result.minor = obj.Get("minor").As<Napi::Number>().Uint32Value();
    result.patch = obj.Get("patch").As<Napi::Number>().Uint32Value();
    return result;
}

inline Napi::Object AbiVersionToObject(Napi::Env env, const fdl_abi_version_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set("major", Napi::Number::New(env, d.major));
    obj.Set("minor", Napi::Number::New(env, d.minor));
    obj.Set("patch", Napi::Number::New(env, d.patch));
    return obj;
}

// -----------------------------------------------------------------------
// fdl_dimensions_i64_t
// -----------------------------------------------------------------------

inline fdl_dimensions_i64_t ObjectToDimensionsI64(const Napi::Object& obj) {
    fdl_dimensions_i64_t result;
    result.width = static_cast<int64_t>(obj.Get("width").As<Napi::Number>().Int64Value());
    result.height = static_cast<int64_t>(obj.Get("height").As<Napi::Number>().Int64Value());
    return result;
}

inline Napi::Object DimensionsI64ToObject(Napi::Env env, const fdl_dimensions_i64_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set("width", Napi::Number::New(env, static_cast<double>(d.width)));
    obj.Set("height", Napi::Number::New(env, static_cast<double>(d.height)));
    return obj;
}

// -----------------------------------------------------------------------
// fdl_dimensions_f64_t
// -----------------------------------------------------------------------

inline fdl_dimensions_f64_t ObjectToDimensionsF64(const Napi::Object& obj) {
    fdl_dimensions_f64_t result;
    result.width = obj.Get("width").As<Napi::Number>().DoubleValue();
    result.height = obj.Get("height").As<Napi::Number>().DoubleValue();
    return result;
}

inline Napi::Object DimensionsF64ToObject(Napi::Env env, const fdl_dimensions_f64_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set("width", Napi::Number::New(env, d.width));
    obj.Set("height", Napi::Number::New(env, d.height));
    return obj;
}

// -----------------------------------------------------------------------
// fdl_point_f64_t
// -----------------------------------------------------------------------

inline fdl_point_f64_t ObjectToPointF64(const Napi::Object& obj) {
    fdl_point_f64_t result;
    result.x = obj.Get("x").As<Napi::Number>().DoubleValue();
    result.y = obj.Get("y").As<Napi::Number>().DoubleValue();
    return result;
}

inline Napi::Object PointF64ToObject(Napi::Env env, const fdl_point_f64_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set("x", Napi::Number::New(env, d.x));
    obj.Set("y", Napi::Number::New(env, d.y));
    return obj;
}

// -----------------------------------------------------------------------
// fdl_rect_t
// -----------------------------------------------------------------------

inline fdl_rect_t ObjectToRect(const Napi::Object& obj) {
    fdl_rect_t result;
    result.x = obj.Get("x").As<Napi::Number>().DoubleValue();
    result.y = obj.Get("y").As<Napi::Number>().DoubleValue();
    result.width = obj.Get("width").As<Napi::Number>().DoubleValue();
    result.height = obj.Get("height").As<Napi::Number>().DoubleValue();
    return result;
}

inline Napi::Object RectToObject(Napi::Env env, const fdl_rect_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set("x", Napi::Number::New(env, d.x));
    obj.Set("y", Napi::Number::New(env, d.y));
    obj.Set("width", Napi::Number::New(env, d.width));
    obj.Set("height", Napi::Number::New(env, d.height));
    return obj;
}

// -----------------------------------------------------------------------
// fdl_round_strategy_t
// -----------------------------------------------------------------------

inline fdl_round_strategy_t ObjectToRoundStrategy(const Napi::Object& obj) {
    fdl_round_strategy_t result;
    result.even = static_cast<fdl_rounding_even_t>(obj.Get("even").As<Napi::Number>().Uint32Value());
    result.mode = static_cast<fdl_rounding_mode_t>(obj.Get("mode").As<Napi::Number>().Uint32Value());
    return result;
}

inline Napi::Object RoundStrategyToObject(Napi::Env env, const fdl_round_strategy_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set("even", Napi::Number::New(env, static_cast<uint32_t>(d.even)));
    obj.Set("mode", Napi::Number::New(env, static_cast<uint32_t>(d.mode)));
    return obj;
}

// -----------------------------------------------------------------------
// fdl_parse_result_t
// -----------------------------------------------------------------------

inline fdl_parse_result_t ObjectToParseResult(const Napi::Object& obj) {
    fdl_parse_result_t result;
    result.doc = static_cast<fdl_doc_t*>(obj.Get("doc").As<Napi::External<void>>().Data());
    {
        std::string _error = obj.Get("error").As<Napi::String>().Utf8Value();
        // Note: string is copied into the struct; caller must manage lifetime.
        result.error = _error.c_str();
    }
    return result;
}

inline Napi::Object ParseResultToObject(Napi::Env env, const fdl_parse_result_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set(
        "doc", d.doc ? Napi::External<void>::New(env, const_cast<void*>(static_cast<const void*>(d.doc))) : env.Null());
    obj.Set("error", d.error ? Napi::String::New(env, d.error) : env.Null());
    return obj;
}

// -----------------------------------------------------------------------
// fdl_template_result_t
// -----------------------------------------------------------------------

inline fdl_template_result_t ObjectToTemplateResult(const Napi::Object& obj) {
    fdl_template_result_t result;
    result.output_fdl = static_cast<fdl_doc_t*>(obj.Get("output_fdl").As<Napi::External<void>>().Data());
    {
        std::string _context_label = obj.Get("context_label").As<Napi::String>().Utf8Value();
        // Note: string is copied into the struct; caller must manage lifetime.
        result.context_label = _context_label.c_str();
    }
    {
        std::string _canvas_id = obj.Get("canvas_id").As<Napi::String>().Utf8Value();
        // Note: string is copied into the struct; caller must manage lifetime.
        result.canvas_id = _canvas_id.c_str();
    }
    {
        std::string _framing_decision_id = obj.Get("framing_decision_id").As<Napi::String>().Utf8Value();
        // Note: string is copied into the struct; caller must manage lifetime.
        result.framing_decision_id = _framing_decision_id.c_str();
    }
    {
        std::string _error = obj.Get("error").As<Napi::String>().Utf8Value();
        // Note: string is copied into the struct; caller must manage lifetime.
        result.error = _error.c_str();
    }
    return result;
}

inline Napi::Object TemplateResultToObject(Napi::Env env, const fdl_template_result_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set(
        "output_fdl",
        d.output_fdl ? Napi::External<void>::New(env, const_cast<void*>(static_cast<const void*>(d.output_fdl)))
                     : env.Null());
    obj.Set("context_label", d.context_label ? Napi::String::New(env, d.context_label) : env.Null());
    obj.Set("canvas_id", d.canvas_id ? Napi::String::New(env, d.canvas_id) : env.Null());
    obj.Set("framing_decision_id", d.framing_decision_id ? Napi::String::New(env, d.framing_decision_id) : env.Null());
    obj.Set("error", d.error ? Napi::String::New(env, d.error) : env.Null());
    return obj;
}

// -----------------------------------------------------------------------
// fdl_resolve_canvas_result_t
// -----------------------------------------------------------------------

inline fdl_resolve_canvas_result_t ObjectToResolveCanvasResult(const Napi::Object& obj) {
    fdl_resolve_canvas_result_t result;
    result.canvas = static_cast<fdl_canvas_t*>(obj.Get("canvas").As<Napi::External<void>>().Data());
    result.framing_decision =
        static_cast<fdl_framing_decision_t*>(obj.Get("framing_decision").As<Napi::External<void>>().Data());
    result.was_resolved = obj.Get("was_resolved").As<Napi::Number>().Int32Value();
    {
        std::string _error = obj.Get("error").As<Napi::String>().Utf8Value();
        // Note: string is copied into the struct; caller must manage lifetime.
        result.error = _error.c_str();
    }
    return result;
}

inline Napi::Object ResolveCanvasResultToObject(Napi::Env env, const fdl_resolve_canvas_result_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set(
        "canvas",
        d.canvas ? Napi::External<void>::New(env, const_cast<void*>(static_cast<const void*>(d.canvas))) : env.Null());
    obj.Set(
        "framing_decision",
        d.framing_decision
            ? Napi::External<void>::New(env, const_cast<void*>(static_cast<const void*>(d.framing_decision)))
            : env.Null());
    obj.Set("was_resolved", Napi::Number::New(env, d.was_resolved));
    obj.Set("error", d.error ? Napi::String::New(env, d.error) : env.Null());
    return obj;
}

// -----------------------------------------------------------------------
// fdl_geometry_t
// -----------------------------------------------------------------------

inline fdl_geometry_t ObjectToGeometry(const Napi::Object& obj) {
    fdl_geometry_t result;
    result.canvas_dims = ObjectToDimensionsF64(obj.Get("canvas_dims").As<Napi::Object>());
    result.effective_dims = ObjectToDimensionsF64(obj.Get("effective_dims").As<Napi::Object>());
    result.protection_dims = ObjectToDimensionsF64(obj.Get("protection_dims").As<Napi::Object>());
    result.framing_dims = ObjectToDimensionsF64(obj.Get("framing_dims").As<Napi::Object>());
    result.effective_anchor = ObjectToPointF64(obj.Get("effective_anchor").As<Napi::Object>());
    result.protection_anchor = ObjectToPointF64(obj.Get("protection_anchor").As<Napi::Object>());
    result.framing_anchor = ObjectToPointF64(obj.Get("framing_anchor").As<Napi::Object>());
    return result;
}

inline Napi::Object GeometryToObject(Napi::Env env, const fdl_geometry_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set("canvas_dims", DimensionsF64ToObject(env, d.canvas_dims));
    obj.Set("effective_dims", DimensionsF64ToObject(env, d.effective_dims));
    obj.Set("protection_dims", DimensionsF64ToObject(env, d.protection_dims));
    obj.Set("framing_dims", DimensionsF64ToObject(env, d.framing_dims));
    obj.Set("effective_anchor", PointF64ToObject(env, d.effective_anchor));
    obj.Set("protection_anchor", PointF64ToObject(env, d.protection_anchor));
    obj.Set("framing_anchor", PointF64ToObject(env, d.framing_anchor));
    return obj;
}

// -----------------------------------------------------------------------
// fdl_from_intent_result_t
// -----------------------------------------------------------------------

inline fdl_from_intent_result_t ObjectToFromIntentResult(const Napi::Object& obj) {
    fdl_from_intent_result_t result;
    result.dimensions = ObjectToDimensionsF64(obj.Get("dimensions").As<Napi::Object>());
    result.anchor_point = ObjectToPointF64(obj.Get("anchor_point").As<Napi::Object>());
    result.has_protection = obj.Get("has_protection").As<Napi::Number>().Int32Value();
    result.protection_dimensions = ObjectToDimensionsF64(obj.Get("protection_dimensions").As<Napi::Object>());
    result.protection_anchor_point = ObjectToPointF64(obj.Get("protection_anchor_point").As<Napi::Object>());
    return result;
}

inline Napi::Object FromIntentResultToObject(Napi::Env env, const fdl_from_intent_result_t& d) {
    auto obj = Napi::Object::New(env);
    obj.Set("dimensions", DimensionsF64ToObject(env, d.dimensions));
    obj.Set("anchor_point", PointF64ToObject(env, d.anchor_point));
    obj.Set("has_protection", Napi::Number::New(env, d.has_protection));
    obj.Set("protection_dimensions", DimensionsF64ToObject(env, d.protection_dimensions));
    obj.Set("protection_anchor_point", PointF64ToObject(env, d.protection_anchor_point));
    return obj;
}
