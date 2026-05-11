// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
//
// One-off helper: re-executes every vector in template_vectors.json through
// the current C++ implementation and rewrites each vector's "expected" block
// with the fresh output.  Keeps inputs and labels intact so the file remains
// a valid test fixture; only the golden side changes.
//
// Build (one-off): append this source to fdl_core_tests target in a scratch
// CMake, or compile it with the same flags as the test binary and link
// against libfdl_core.  The simpler path here is to build it as a small
// executable alongside the test binary.
#include "fdl/fdl_core.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <jsoncons/json.hpp>
#include <sstream>
#include <string>

using ojson = jsoncons::ojson;

namespace {

ojson dims_json(double w, double h) {
    ojson o(jsoncons::json_object_arg);
    o.insert_or_assign("width", w);
    o.insert_or_assign("height", h);
    return o;
}

ojson point_json(double x, double y) {
    ojson o(jsoncons::json_object_arg);
    o.insert_or_assign("x", x);
    o.insert_or_assign("y", y);
    return o;
}

// Build a full FDL document JSON from a vector's source_canvas / source_framing
// / template.  Mirrors build_test_inputs in test_template.cpp exactly.
std::string build_input_doc(const ojson& v) {
    const auto& sc = v["source_canvas"];
    const auto& sf = v["source_framing"];
    const auto& t = v["template"];

    ojson root(jsoncons::json_object_arg);
    root.insert_or_assign("uuid", "00000000-0000-0000-0000-000000000001");
    root.insert_or_assign("version", ojson(jsoncons::json_object_arg));
    root["version"].insert_or_assign("major", 2);
    root["version"].insert_or_assign("minor", 0);
    root.insert_or_assign("fdl_creator", "test");
    root.insert_or_assign("framing_intents", ojson(jsoncons::json_array_arg));
    root.insert_or_assign("contexts", ojson(jsoncons::json_array_arg));
    root.insert_or_assign("canvas_templates", ojson(jsoncons::json_array_arg));

    ojson canvas_json(jsoncons::json_object_arg);
    canvas_json.insert_or_assign("label", sc["label"]);
    canvas_json.insert_or_assign("id", sc["id"]);
    canvas_json.insert_or_assign("source_canvas_id", sc["source_canvas_id"]);
    canvas_json.insert_or_assign("dimensions", sc["dimensions"]);
    if (!sc["effective_dimensions"].is_null()) {
        canvas_json.insert_or_assign("effective_dimensions", sc["effective_dimensions"]);
        canvas_json.insert_or_assign("effective_anchor_point", sc["effective_anchor_point"]);
    }
    canvas_json.insert_or_assign("anamorphic_squeeze", sc["anamorphic_squeeze"]);

    ojson fd_json(jsoncons::json_object_arg);
    fd_json.insert_or_assign("label", sf["label"]);
    fd_json.insert_or_assign("id", sf["id"]);
    fd_json.insert_or_assign("framing_intent_id", sf["framing_intent_id"]);
    fd_json.insert_or_assign("dimensions", sf["dimensions"]);
    fd_json.insert_or_assign("anchor_point", sf["anchor_point"]);
    if (!sf["protection_dimensions"].is_null()) {
        fd_json.insert_or_assign("protection_dimensions", sf["protection_dimensions"]);
        fd_json.insert_or_assign("protection_anchor_point", sf["protection_anchor_point"]);
    }

    ojson fds(jsoncons::json_array_arg);
    fds.push_back(std::move(fd_json));
    canvas_json.insert_or_assign("framing_decisions", std::move(fds));

    ojson canvases(jsoncons::json_array_arg);
    canvases.push_back(std::move(canvas_json));

    ojson ctx(jsoncons::json_object_arg);
    ctx.insert_or_assign("label", "Test");
    ctx.insert_or_assign("canvases", std::move(canvases));
    root["contexts"].push_back(std::move(ctx));

    ojson tmpl_json(jsoncons::json_object_arg);
    tmpl_json.insert_or_assign("label", t["label"]);
    tmpl_json.insert_or_assign("id", t["id"]);
    tmpl_json.insert_or_assign("target_dimensions", t["target_dimensions"]);
    tmpl_json.insert_or_assign("target_anamorphic_squeeze", t["target_anamorphic_squeeze"]);
    tmpl_json.insert_or_assign("fit_source", t["fit_source"]);
    tmpl_json.insert_or_assign("fit_method", t["fit_method"]);
    tmpl_json.insert_or_assign("alignment_method_vertical", t["alignment_method_vertical"]);
    tmpl_json.insert_or_assign("alignment_method_horizontal", t["alignment_method_horizontal"]);
    if (!t["preserve_from_source_canvas"].is_null()) {
        tmpl_json.insert_or_assign("preserve_from_source_canvas", t["preserve_from_source_canvas"]);
    }
    if (t["has_maximum_dimensions"].as<bool>()) {
        tmpl_json.insert_or_assign("maximum_dimensions", t["maximum_dimensions"]);
    }
    if (t["pad_to_maximum"].as<bool>()) {
        tmpl_json.insert_or_assign("pad_to_maximum", true);
    }
    tmpl_json.insert_or_assign("round", t["round"]);
    root["canvas_templates"].push_back(std::move(tmpl_json));

    std::string out;
    root.dump(out);
    return out;
}

ojson run_vector(const ojson& v) {
    auto json_str = build_input_doc(v);
    auto parse_result = fdl_doc_parse_json(json_str.c_str(), json_str.size());
    if (parse_result.doc == nullptr) {
        std::fprintf(
            stderr,
            "parse error for vector %s: %s\n",
            v["label"].as<std::string>().c_str(),
            parse_result.error ? parse_result.error : "(none)");
        std::abort();
    }

    auto* ctx = fdl_doc_context_at(parse_result.doc, 0);
    auto* canvas = fdl_context_canvas_at(ctx, 0);
    auto* framing = fdl_canvas_framing_decision_at(canvas, 0);
    auto* tmpl = fdl_doc_canvas_template_at(parse_result.doc, 0);

    std::string new_fd_name = v["new_fd_name"].as<std::string>();
    std::string ctx_label;
    if (!v["source_context_label"].is_null()) {
        ctx_label = v["source_context_label"].as<std::string>();
    }
    std::string ctx_creator;
    if (!v["context_creator"].is_null()) {
        ctx_creator = v["context_creator"].as<std::string>();
    }

    auto result = fdl_apply_canvas_template(
        tmpl,
        canvas,
        framing,
        "NEW_CANVAS_ID",
        new_fd_name.c_str(),
        ctx_label.empty() ? nullptr : ctx_label.c_str(),
        ctx_creator.empty() ? nullptr : ctx_creator.c_str());

    if (result.error != nullptr) {
        std::fprintf(stderr, "apply error for vector %s: %s\n", v["label"].as<std::string>().c_str(), result.error);
        std::abort();
    }

    auto* out_ctx = fdl_doc_context_at(result.output_fdl, 0);
    auto* out_new_canvas = fdl_context_canvas_at(out_ctx, 1);
    auto* out_fd = fdl_canvas_framing_decision_at(out_new_canvas, 0);

    // Gather expected outputs
    double scale_factor = 0.0;
    fdl_canvas_get_custom_attr_float(out_new_canvas, FDL_ATTR_SCALE_FACTOR, &scale_factor);
    fdl_dimensions_f64_t bb = {};
    fdl_canvas_get_custom_attr_dims_f64(out_new_canvas, FDL_ATTR_SCALED_BOUNDING_BOX, &bb);
    fdl_point_f64_t ct = {};
    fdl_canvas_get_custom_attr_point_f64(out_new_canvas, FDL_ATTR_CONTENT_TRANSLATION, &ct);

    auto cv_dims = fdl_canvas_get_dimensions(out_new_canvas);
    auto fd_dims = fdl_framing_decision_get_dimensions(out_fd);
    auto fd_anchor = fdl_framing_decision_get_anchor_point(out_fd);

    bool has_eff = fdl_canvas_has_effective_dimensions(out_new_canvas) != 0;
    fdl_dimensions_i64_t eff_dims = {};
    fdl_point_f64_t eff_anchor = {};
    if (has_eff) {
        eff_dims = fdl_canvas_get_effective_dimensions(out_new_canvas);
        eff_anchor = fdl_canvas_get_effective_anchor_point(out_new_canvas);
    }

    bool has_prot = fdl_framing_decision_has_protection(out_fd) != 0;
    fdl_dimensions_f64_t prot_dims = {};
    fdl_point_f64_t prot_anchor = {};
    if (has_prot) {
        prot_dims = fdl_framing_decision_get_protection_dimensions(out_fd);
        prot_anchor = fdl_framing_decision_get_protection_anchor_point(out_fd);
    }

    ojson expected(jsoncons::json_object_arg);
    expected.insert_or_assign("scale_factor", scale_factor);
    expected.insert_or_assign("scaled_bounding_box", dims_json(bb.width, bb.height));
    expected.insert_or_assign("content_translation", point_json(ct.x, ct.y));
    expected.insert_or_assign(
        "output_canvas_dims", dims_json(static_cast<double>(cv_dims.width), static_cast<double>(cv_dims.height)));
    if (has_eff) {
        expected.insert_or_assign(
            "output_effective_dims",
            dims_json(static_cast<double>(eff_dims.width), static_cast<double>(eff_dims.height)));
        expected.insert_or_assign("output_effective_anchor", point_json(eff_anchor.x, eff_anchor.y));
    } else {
        expected.insert_or_assign("output_effective_dims", ojson::null());
        expected.insert_or_assign("output_effective_anchor", ojson::null());
    }
    expected.insert_or_assign("output_fd_dims", dims_json(fd_dims.width, fd_dims.height));
    expected.insert_or_assign("output_fd_anchor", point_json(fd_anchor.x, fd_anchor.y));
    expected.insert_or_assign("output_has_protection", has_prot);
    if (has_prot) {
        expected.insert_or_assign("output_protection_dims", dims_json(prot_dims.width, prot_dims.height));
        expected.insert_or_assign("output_protection_anchor", point_json(prot_anchor.x, prot_anchor.y));
    } else {
        expected.insert_or_assign("output_protection_dims", ojson::null());
        expected.insert_or_assign("output_protection_anchor", ojson::null());
    }

    fdl_template_result_free(&result);
    fdl_doc_free(parse_result.doc);
    return expected;
}

} // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::fprintf(stderr, "usage: %s <input.json> <output.json>\n", argv[0]);
        return 1;
    }

    std::ifstream in(argv[1]);
    if (!in) {
        std::fprintf(stderr, "cannot open %s\n", argv[1]);
        return 1;
    }
    auto root = ojson::parse(in);

    int changed = 0, total = 0;
    for (auto& v : root["vectors"].array_range()) {
        ++total;
        auto new_expected = run_vector(v);
        if (v["expected"] != new_expected) {
            ++changed;
            std::fprintf(stderr, "[CHANGED] %s\n", v["label"].as<std::string>().c_str());
        }
        v["expected"] = std::move(new_expected);
    }

    std::ofstream out(argv[2]);
    if (!out) {
        std::fprintf(stderr, "cannot write %s\n", argv[2]);
        return 1;
    }
    jsoncons::json_options opts;
    opts.indent_size(2);
    opts.spaces_around_comma(jsoncons::spaces_option::no_spaces);
    opts.object_array_line_splits(jsoncons::line_split_kind::multi_line);
    out << jsoncons::pretty_print(root, opts) << '\n';

    std::fprintf(stderr, "regenerated %d/%d vectors (%d changed)\n", total, total, changed);
    return 0;
}
