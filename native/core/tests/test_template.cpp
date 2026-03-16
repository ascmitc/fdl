// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>

#include "fdl/fdl_core.h"

#include <cmath>
#include <cstring>
#include <fstream>
#include <jsoncons/json.hpp>
#include <string>

using ojson = jsoncons::ojson;

static ojson load_vectors() {
    std::ifstream f(VECTORS_DIR "/template/template_vectors.json");
    REQUIRE(f.is_open());
    return ojson::parse(f);
}

static bool close_enough(double a, double b, double tol = 1e-4) {
    return std::abs(a - b) < tol;
}

// Build a source FDL document from vector data and return parsed doc + handles
struct TestInputs {
    fdl_doc_t* doc;
    fdl_canvas_t* canvas;
    fdl_framing_decision_t* framing;
    fdl_canvas_template_t* tmpl;
};

static TestInputs build_test_inputs(const ojson& v) {
    TestInputs inputs = {};

    // Build a complete FDL document containing source canvas, framing, and template
    const auto& sc = v["source_canvas"];
    const auto& sf = v["source_framing"];
    const auto& t = v["template"];

    // Build JSON document
    ojson root(jsoncons::json_object_arg);
    root.insert_or_assign("uuid", "00000000-0000-0000-0000-000000000001");
    root.insert_or_assign("version", ojson(jsoncons::json_object_arg));
    root["version"].insert_or_assign("major", 2);
    root["version"].insert_or_assign("minor", 0);
    root.insert_or_assign("fdl_creator", "test");
    root.insert_or_assign("framing_intents", ojson(jsoncons::json_array_arg));
    root.insert_or_assign("contexts", ojson(jsoncons::json_array_arg));
    root.insert_or_assign("canvas_templates", ojson(jsoncons::json_array_arg));

    // Build canvas
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

    // Build framing decision
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

    // Build canvas template
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

    // Serialize and parse
    std::string json_str;
    root.dump(json_str);

    auto parse_result = fdl_doc_parse_json(json_str.c_str(), json_str.size());
    REQUIRE(parse_result.doc != nullptr);
    inputs.doc = parse_result.doc;

    // Get handles
    auto* ctx_handle = fdl_doc_context_at(inputs.doc, 0);
    REQUIRE(ctx_handle != nullptr);
    inputs.canvas = fdl_context_canvas_at(ctx_handle, 0);
    REQUIRE(inputs.canvas != nullptr);
    inputs.framing = fdl_canvas_framing_decision_at(inputs.canvas, 0);
    REQUIRE(inputs.framing != nullptr);
    inputs.tmpl = fdl_doc_canvas_template_at(inputs.doc, 0);
    REQUIRE(inputs.tmpl != nullptr);

    return inputs;
}

TEST_CASE("apply_canvas_template matches Python golden vectors", "[template][apply]") {
    auto root = load_vectors();
    const auto& vectors = root["vectors"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto inputs = build_test_inputs(v);

            auto new_fd_name = v["new_fd_name"].as<std::string>();
            std::string ctx_label;
            if (!v["source_context_label"].is_null()) {
                ctx_label = v["source_context_label"].as<std::string>();
            }
            std::string ctx_creator;
            if (!v["context_creator"].is_null()) {
                ctx_creator = v["context_creator"].as<std::string>();
            }

            auto result = fdl_apply_canvas_template(
                inputs.tmpl,
                inputs.canvas,
                inputs.framing,
                "NEW_CANVAS_ID",
                new_fd_name.c_str(),
                ctx_label.empty() ? nullptr : ctx_label.c_str(),
                ctx_creator.empty() ? nullptr : ctx_creator.c_str());

            // Check no error
            INFO("Error: " << (result.error ? result.error : "none"));
            REQUIRE(result.error == nullptr);
            REQUIRE(result.output_fdl != nullptr);

            const auto& exp = v["expected"];

            // Verify output FDL structure via accessors
            REQUIRE(fdl_doc_contexts_count(result.output_fdl) == 1);
            auto* out_ctx = fdl_doc_context_at(result.output_fdl, 0);
            REQUIRE(out_ctx != nullptr);

            // Context should have 2 canvases: source + new
            REQUIRE(fdl_context_canvases_count(out_ctx) == 2);
            auto* out_new_canvas = fdl_context_canvas_at(out_ctx, 1);
            REQUIRE(out_new_canvas != nullptr);

            // Check scale factor (from canvas custom attr)
            double exp_sf = exp["scale_factor"].as<double>();
            double sf_out = 0.0;
            REQUIRE(fdl_canvas_get_custom_attr_float(out_new_canvas, FDL_ATTR_SCALE_FACTOR, &sf_out) == 0);
            REQUIRE(close_enough(sf_out, exp_sf));

            // Check scaled bounding box (from canvas custom attr)
            double exp_bb_w = exp["scaled_bounding_box"]["width"].as<double>();
            double exp_bb_h = exp["scaled_bounding_box"]["height"].as<double>();
            fdl_dimensions_f64_t bb_out = {};
            REQUIRE(fdl_canvas_get_custom_attr_dims_f64(out_new_canvas, FDL_ATTR_SCALED_BOUNDING_BOX, &bb_out) == 0);
            REQUIRE(close_enough(bb_out.width, exp_bb_w));
            REQUIRE(close_enough(bb_out.height, exp_bb_h));

            // Check content translation (from canvas custom attr)
            double exp_ct_x = exp["content_translation"]["x"].as<double>();
            double exp_ct_y = exp["content_translation"]["y"].as<double>();
            fdl_point_f64_t ct_out = {};
            REQUIRE(fdl_canvas_get_custom_attr_point_f64(out_new_canvas, FDL_ATTR_CONTENT_TRANSLATION, &ct_out) == 0);
            REQUIRE(close_enough(ct_out.x, exp_ct_x));
            REQUIRE(close_enough(ct_out.y, exp_ct_y));

            // Check output canvas dimensions
            auto out_dims = fdl_canvas_get_dimensions(out_new_canvas);
            double exp_out_w = exp["output_canvas_dims"]["width"].as<double>();
            double exp_out_h = exp["output_canvas_dims"]["height"].as<double>();
            REQUIRE(close_enough(static_cast<double>(out_dims.width), exp_out_w));
            REQUIRE(close_enough(static_cast<double>(out_dims.height), exp_out_h));

            // Check output framing decision
            REQUIRE(fdl_canvas_framing_decisions_count(out_new_canvas) == 1);
            auto* out_fd = fdl_canvas_framing_decision_at(out_new_canvas, 0);
            REQUIRE(out_fd != nullptr);

            auto out_fd_dims = fdl_framing_decision_get_dimensions(out_fd);
            double exp_fd_w = exp["output_fd_dims"]["width"].as<double>();
            double exp_fd_h = exp["output_fd_dims"]["height"].as<double>();
            REQUIRE(close_enough(out_fd_dims.width, exp_fd_w));
            REQUIRE(close_enough(out_fd_dims.height, exp_fd_h));

            auto out_fd_anchor = fdl_framing_decision_get_anchor_point(out_fd);
            double exp_fd_ax = exp["output_fd_anchor"]["x"].as<double>();
            double exp_fd_ay = exp["output_fd_anchor"]["y"].as<double>();
            REQUIRE(close_enough(out_fd_anchor.x, exp_fd_ax));
            REQUIRE(close_enough(out_fd_anchor.y, exp_fd_ay));

            // Check protection if expected
            bool exp_has_prot = exp["output_has_protection"].as<bool>();
            REQUIRE((fdl_framing_decision_has_protection(out_fd) != 0) == exp_has_prot);

            if (exp_has_prot) {
                auto out_prot_dims = fdl_framing_decision_get_protection_dimensions(out_fd);
                double exp_pd_w = exp["output_protection_dims"]["width"].as<double>();
                double exp_pd_h = exp["output_protection_dims"]["height"].as<double>();
                REQUIRE(close_enough(out_prot_dims.width, exp_pd_w));
                REQUIRE(close_enough(out_prot_dims.height, exp_pd_h));
            }

            fdl_template_result_free(&result);
            fdl_doc_free(inputs.doc);
        }
    }
}

TEST_CASE("apply_canvas_template target_anamorphic_squeeze=0 inherits source squeeze", "[template][apply][squeeze]") {
    // When target_anamorphic_squeeze is 0, it should fall back to the source
    // canvas anamorphic_squeeze for both geometry and output document values.
    ojson root(jsoncons::json_object_arg);
    root.insert_or_assign("uuid", "00000000-0000-0000-0000-000000000099");
    root.insert_or_assign("version", ojson(jsoncons::json_object_arg));
    root["version"].insert_or_assign("major", 2);
    root["version"].insert_or_assign("minor", 0);
    root.insert_or_assign("fdl_creator", "test");
    root.insert_or_assign("framing_intents", ojson(jsoncons::json_array_arg));
    root.insert_or_assign("contexts", ojson(jsoncons::json_array_arg));
    root.insert_or_assign("canvas_templates", ojson(jsoncons::json_array_arg));

    // Anamorphic source canvas (squeeze = 2.0)
    ojson canvas_json(jsoncons::json_object_arg);
    canvas_json.insert_or_assign("id", "CVS_ANA");
    canvas_json.insert_or_assign("label", "Anamorphic");
    canvas_json.insert_or_assign("source_canvas_id", "CVS_ANA");
    canvas_json.insert_or_assign("dimensions", ojson(jsoncons::json_object_arg));
    canvas_json["dimensions"].insert_or_assign("width", 4096);
    canvas_json["dimensions"].insert_or_assign("height", 3432);
    canvas_json.insert_or_assign("anamorphic_squeeze", 2.0);

    ojson fd_json(jsoncons::json_object_arg);
    fd_json.insert_or_assign("id", "CVS_ANA-FI_239");
    fd_json.insert_or_assign("label", "2.39:1");
    fd_json.insert_or_assign("framing_intent_id", "FI_239");
    fd_json.insert_or_assign("dimensions", ojson(jsoncons::json_object_arg));
    fd_json["dimensions"].insert_or_assign("width", 4096.0);
    fd_json["dimensions"].insert_or_assign("height", 1714.0);
    fd_json.insert_or_assign("anchor_point", ojson(jsoncons::json_object_arg));
    fd_json["anchor_point"].insert_or_assign("x", 0.0);
    fd_json["anchor_point"].insert_or_assign("y", 859.0);

    ojson fds(jsoncons::json_array_arg);
    fds.push_back(std::move(fd_json));
    canvas_json.insert_or_assign("framing_decisions", std::move(fds));

    ojson canvases(jsoncons::json_array_arg);
    canvases.push_back(std::move(canvas_json));
    ojson ctx(jsoncons::json_object_arg);
    ctx.insert_or_assign("label", "Test");
    ctx.insert_or_assign("canvases", std::move(canvases));
    root["contexts"].push_back(std::move(ctx));

    // Template with target_anamorphic_squeeze = 0 (should inherit source squeeze)
    ojson tmpl_json(jsoncons::json_object_arg);
    tmpl_json.insert_or_assign("id", "CT_SQUEEZE_ZERO");
    tmpl_json.insert_or_assign("label", "Squeeze zero");
    tmpl_json.insert_or_assign("target_dimensions", ojson(jsoncons::json_object_arg));
    tmpl_json["target_dimensions"].insert_or_assign("width", 1920);
    tmpl_json["target_dimensions"].insert_or_assign("height", 1080);
    tmpl_json.insert_or_assign("target_anamorphic_squeeze", 0.0);
    tmpl_json.insert_or_assign("fit_source", "framing_decision.dimensions");
    tmpl_json.insert_or_assign("fit_method", "width");
    tmpl_json.insert_or_assign("alignment_method_horizontal", "center");
    tmpl_json.insert_or_assign("alignment_method_vertical", "center");
    tmpl_json.insert_or_assign("round", ojson(jsoncons::json_object_arg));
    tmpl_json["round"].insert_or_assign("even", "even");
    tmpl_json["round"].insert_or_assign("mode", "up");
    root["canvas_templates"].push_back(std::move(tmpl_json));

    std::string json_str;
    root.dump(json_str);

    auto parse_result = fdl_doc_parse_json(json_str.c_str(), json_str.size());
    REQUIRE(parse_result.doc != nullptr);

    auto* ctx_handle = fdl_doc_context_at(parse_result.doc, 0);
    auto* canvas = fdl_context_canvas_at(ctx_handle, 0);
    auto* framing = fdl_canvas_framing_decision_at(canvas, 0);
    auto* tmpl = fdl_doc_canvas_template_at(parse_result.doc, 0);

    auto result = fdl_apply_canvas_template(tmpl, canvas, framing, "NEW_CVS", "test", "Test", "test");
    INFO("Error: " << (result.error ? result.error : "none"));
    REQUIRE(result.error == nullptr);
    REQUIRE(result.output_fdl != nullptr);

    // The output canvas should inherit squeeze=2.0 from the source, not 0
    auto* out_ctx = fdl_doc_context_at(result.output_fdl, 0);
    auto* out_new_canvas = fdl_context_canvas_at(out_ctx, 1);
    REQUIRE(out_new_canvas != nullptr);

    double out_squeeze = fdl_canvas_get_anamorphic_squeeze(out_new_canvas);
    REQUIRE(close_enough(out_squeeze, 2.0));

    fdl_template_result_free(&result);
    fdl_doc_free(parse_result.doc);
}

TEST_CASE("apply_canvas_template NULL safety", "[template][null]") {
    auto result = fdl_apply_canvas_template(nullptr, nullptr, nullptr, "id", "name", nullptr, nullptr);
    REQUIRE(result.error != nullptr);
    REQUIRE(result.output_fdl == nullptr);
    fdl_template_result_free(&result);
}
