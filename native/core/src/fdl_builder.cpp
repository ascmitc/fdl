// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * @file fdl_builder.cpp
 * @brief Builder functions: construct ojson objects with keys in canonical order.
 */
#include "fdl_builder.h"
#include "fdl_enum_map.h"

namespace fdl::detail {

/** @brief Build a version object with major and minor fields. */
ojson make_version(int major, int minor) {
    ojson v(jsoncons::json_object_arg);
    v.insert_or_assign("major", major);
    v.insert_or_assign("minor", minor);
    return v;
}

/** @brief Build an integer dimensions object (width, height). */
ojson make_dimensions_int(int64_t width, int64_t height) {
    ojson d(jsoncons::json_object_arg);
    d.insert_or_assign("width", width);
    d.insert_or_assign("height", height);
    return d;
}

/** @brief Build a floating-point dimensions object (width, height). */
ojson make_dimensions_float(double width, double height) {
    ojson d(jsoncons::json_object_arg);
    d.insert_or_assign("width", width);
    d.insert_or_assign("height", height);
    return d;
}

/** @brief Build a floating-point point object (x, y). */
ojson make_point_float(double x, double y) {
    ojson p(jsoncons::json_object_arg);
    p.insert_or_assign("x", x);
    p.insert_or_assign("y", y);
    return p;
}

/** @brief Build a rounding strategy object (even, mode). */
ojson make_round_strategy(const char* even, const char* mode) {
    ojson r(jsoncons::json_object_arg);
    r.insert_or_assign("even", even);
    r.insert_or_assign("mode", mode);
    return r;
}

ojson make_root(
    const char* uuid,
    int version_major,
    int version_minor,
    const char* fdl_creator,
    const char* default_framing_intent) {
    // Key order: uuid, version, fdl_creator, default_framing_intent,
    //            framing_intents, contexts, canvas_templates
    ojson root(jsoncons::json_object_arg);
    root.insert_or_assign("uuid", uuid);
    root.insert_or_assign("version", make_version(version_major, version_minor));
    root.insert_or_assign("fdl_creator", fdl_creator);
    if (default_framing_intent != nullptr) {
        root.insert_or_assign("default_framing_intent", default_framing_intent);
    }
    root.insert_or_assign("framing_intents", ojson(jsoncons::json_array_arg));
    root.insert_or_assign("contexts", ojson(jsoncons::json_array_arg));
    root.insert_or_assign("canvas_templates", ojson(jsoncons::json_array_arg));
    return root;
}

/** @brief Build a framing intent object with aspect ratio and protection. */
ojson make_framing_intent(const char* id, const char* label, int64_t aspect_w, int64_t aspect_h, double protection) {
    // Key order: label, id, aspect_ratio, protection
    ojson fi(jsoncons::json_object_arg);
    if (label != nullptr) {
        fi.insert_or_assign("label", label);
    }
    fi.insert_or_assign("id", id);
    fi.insert_or_assign("aspect_ratio", make_dimensions_int(aspect_w, aspect_h));
    fi.insert_or_assign("protection", protection);
    return fi;
}

/** @brief Build a context object with label and creator. */
ojson make_context(const char* label, const char* context_creator) {
    // Key order: label, context_creator, clip_id, canvases
    ojson ctx(jsoncons::json_object_arg);
    if (label != nullptr) {
        ctx.insert_or_assign("label", label);
    }
    if (context_creator != nullptr) {
        ctx.insert_or_assign("context_creator", context_creator);
    }
    ctx.insert_or_assign("canvases", ojson(jsoncons::json_array_arg));
    return ctx;
}

/** @brief Build a canvas object with dimensions and squeeze. */
ojson make_canvas(
    const char* id, const char* label, const char* source_canvas_id, int64_t dim_w, int64_t dim_h, double squeeze) {
    // Key order: label, id, source_canvas_id, dimensions,
    //            effective_dimensions, effective_anchor_point,
    //            photosite_dimensions, physical_dimensions,
    //            anamorphic_squeeze, framing_decisions
    ojson c(jsoncons::json_object_arg);
    if (label != nullptr) {
        c.insert_or_assign("label", label);
    }
    c.insert_or_assign("id", id);
    c.insert_or_assign("source_canvas_id", source_canvas_id);
    c.insert_or_assign("dimensions", make_dimensions_int(dim_w, dim_h));
    c.insert_or_assign("anamorphic_squeeze", squeeze);
    c.insert_or_assign("framing_decisions", ojson(jsoncons::json_array_arg));
    return c;
}

/** @brief Build a framing decision object with dimensions and anchor point. */
ojson make_framing_decision(
    const char* id,
    const char* label,
    const char* framing_intent_id,
    double dim_w,
    double dim_h,
    double anchor_x,
    double anchor_y) {
    // Key order: label, id, framing_intent_id, dimensions,
    //            anchor_point, protection_dimensions, protection_anchor_point
    ojson fd(jsoncons::json_object_arg);
    if (label != nullptr) {
        fd.insert_or_assign("label", label);
    }
    fd.insert_or_assign("id", id);
    fd.insert_or_assign("framing_intent_id", framing_intent_id);
    fd.insert_or_assign("dimensions", make_dimensions_float(dim_w, dim_h));
    fd.insert_or_assign("anchor_point", make_point_float(anchor_x, anchor_y));
    return fd;
}

/** @brief Build a canvas template object with all transform parameters. */
ojson make_canvas_template(
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
    // Key order: label, id, target_dimensions, target_anamorphic_squeeze,
    //            fit_source, fit_method, alignment_method_horizontal,
    //            alignment_method_vertical, round, preserve_from_source_canvas,
    //            maximum_dimensions, pad_to_maximum
    ojson ct(jsoncons::json_object_arg);
    if (label != nullptr) {
        ct.insert_or_assign("label", label);
    }
    ct.insert_or_assign("id", id);
    ct.insert_or_assign("target_dimensions", make_dimensions_int(target_w, target_h));
    ct.insert_or_assign("target_anamorphic_squeeze", target_squeeze);
    ct.insert_or_assign("fit_source", geometry_path_to_string(fit_source));
    ct.insert_or_assign("fit_method", fit_method_to_string(fit_method));
    ct.insert_or_assign("alignment_method_horizontal", halign_to_string(halign));
    ct.insert_or_assign("alignment_method_vertical", valign_to_string(valign));
    ct.insert_or_assign(
        "round", make_round_strategy(rounding_even_to_string(rounding.even), rounding_mode_to_string(rounding.mode)));
    return ct;
}

} // namespace fdl::detail
