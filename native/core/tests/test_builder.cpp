// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>

#include "fdl/fdl_core.h"

#include <cstring>
#include <jsoncons/json.hpp>
#include <string>

using ojson = jsoncons::ojson;

TEST_CASE("Build minimal FDL and serialize", "[builder]") {
    auto* doc = fdl_doc_create_with_header("00000000-0000-0000-0000-000000000099", 2, 0, "test-builder", nullptr);
    REQUIRE(doc != nullptr);

    char* json = fdl_doc_to_json(doc, 2);
    REQUIRE(json != nullptr);

    // Parse the output and verify structure
    auto parsed = ojson::parse(json);
    REQUIRE(parsed["uuid"].as<std::string>() == "00000000-0000-0000-0000-000000000099");
    REQUIRE(parsed["version"]["major"].as<int>() == 2);
    REQUIRE(parsed["version"]["minor"].as<int>() == 0);
    REQUIRE(parsed["fdl_creator"].as<std::string>() == "test-builder");
    REQUIRE(parsed["framing_intents"].is_array());
    REQUIRE(parsed["framing_intents"].size() == 0);
    REQUIRE(parsed["contexts"].is_array());
    REQUIRE(parsed["contexts"].size() == 0);
    REQUIRE(parsed["canvas_templates"].is_array());
    REQUIRE(parsed["canvas_templates"].size() == 0);
    // default_framing_intent should not be present (was NULL)
    REQUIRE_FALSE(parsed.contains("default_framing_intent"));

    fdl_free(json);
    fdl_doc_free(doc);
}

TEST_CASE("Build FDL with framing intents", "[builder]") {
    auto* doc = fdl_doc_create_with_header("00000000-0000-0000-0000-000000000099", 2, 0, "test-builder", "FI_239");

    auto* fi = fdl_doc_add_framing_intent(doc, "FI_239", "2.39:1", 239, 100, 0.1);
    REQUIRE(fi != nullptr);

    // Verify via accessor
    REQUIRE(std::string(fdl_framing_intent_get_id(fi)) == "FI_239");
    REQUIRE(std::string(fdl_framing_intent_get_label(fi)) == "2.39:1");
    auto ar = fdl_framing_intent_get_aspect_ratio(fi);
    REQUIRE(ar.width == 239);
    REQUIRE(ar.height == 100);
    REQUIRE(fdl_framing_intent_get_protection(fi) == 0.1);

    // Verify count
    REQUIRE(fdl_doc_framing_intents_count(doc) == 1);

    fdl_doc_free(doc);
}

TEST_CASE("Build FDL with full hierarchy", "[builder]") {
    auto* doc = fdl_doc_create_with_header("00000000-0000-0000-0000-000000000099", 2, 0, "test-builder", "FI_239");

    // Add framing intent
    fdl_doc_add_framing_intent(doc, "FI_239", "2.39:1", 239, 100, 0.0);

    // Add context
    auto* ctx = fdl_doc_add_context(doc, "Camera A", "DIT Station");
    REQUIRE(ctx != nullptr);

    // Add canvas to context
    auto* canvas = fdl_context_add_canvas(ctx, "CVS_OCF", "OCF", "CVS_OCF", 4096, 2160, 1.0);
    REQUIRE(canvas != nullptr);

    // Set effective dimensions on canvas
    fdl_canvas_set_effective_dimensions(canvas, {4000, 2100}, {48.0, 30.0});

    // Add framing decision to canvas
    auto* fd =
        fdl_canvas_add_framing_decision(canvas, "CVS_OCF-FI_239", "2.39:1", "FI_239", 3800.0, 1600.0, 100.0, 250.0);
    REQUIRE(fd != nullptr);

    // Set protection on framing decision
    fdl_framing_decision_set_protection(fd, {3900.0, 1700.0}, {50.0, 200.0});

    // Serialize and re-parse to verify
    char* json = fdl_doc_to_json(doc, 2);
    REQUIRE(json != nullptr);

    auto parsed = ojson::parse(json);

    // Verify structure
    REQUIRE(parsed["default_framing_intent"].as<std::string>() == "FI_239");
    REQUIRE(parsed["framing_intents"].size() == 1);
    REQUIRE(parsed["contexts"].size() == 1);

    auto& ctx_json = parsed["contexts"][0];
    REQUIRE(ctx_json["label"].as<std::string>() == "Camera A");
    REQUIRE(ctx_json["context_creator"].as<std::string>() == "DIT Station");

    auto& canvas_json = ctx_json["canvases"][0];
    REQUIRE(canvas_json["id"].as<std::string>() == "CVS_OCF");
    REQUIRE(canvas_json["dimensions"]["width"].as<int>() == 4096);
    REQUIRE(canvas_json["effective_dimensions"]["width"].as<int>() == 4000);
    REQUIRE(canvas_json["effective_anchor_point"]["x"].as<double>() == 48.0);
    REQUIRE(canvas_json["anamorphic_squeeze"].as<double>() == 1.0);

    auto& fd_json = canvas_json["framing_decisions"][0];
    REQUIRE(fd_json["id"].as<std::string>() == "CVS_OCF-FI_239");
    REQUIRE(fd_json["framing_intent_id"].as<std::string>() == "FI_239");
    REQUIRE(fd_json["dimensions"]["width"].as<double>() == 3800.0);
    REQUIRE(fd_json["anchor_point"]["x"].as<double>() == 100.0);
    REQUIRE(fd_json["protection_dimensions"]["width"].as<double>() == 3900.0);
    REQUIRE(fd_json["protection_anchor_point"]["x"].as<double>() == 50.0);

    fdl_free(json);
    fdl_doc_free(doc);
}

TEST_CASE("Built document roundtrips through parse", "[builder][roundtrip]") {
    // Build a document, serialize, re-parse, verify accessors match
    auto* doc = fdl_doc_create_with_header("00000000-0000-0000-0000-000000000099", 2, 0, "test-builder", nullptr);

    fdl_doc_add_framing_intent(doc, "FI_178", "1.78:1", 16, 9, 0.0);

    auto* ctx = fdl_doc_add_context(doc, "Camera B", nullptr);
    auto* canvas = fdl_context_add_canvas(ctx, "CVS_ANA", "Anamorphic", "CVS_ANA", 4096, 3432, 2.0);
    fdl_canvas_add_framing_decision(canvas, "CVS_ANA-FI_178", "1.78:1", "FI_178", 4096.0, 2304.0, 0.0, 564.0);

    // Serialize
    char* json = fdl_doc_to_json(doc, 2);
    REQUIRE(json != nullptr);

    // Re-parse
    auto result = fdl_doc_parse_json(json, std::strlen(json));
    REQUIRE(result.doc != nullptr);

    // Verify via accessors on re-parsed document
    REQUIRE(fdl_doc_framing_intents_count(result.doc) == 1);
    auto* fi = fdl_doc_framing_intent_at(result.doc, 0);
    REQUIRE(std::string(fdl_framing_intent_get_id(fi)) == "FI_178");

    REQUIRE(fdl_doc_contexts_count(result.doc) == 1);
    auto* ctx2 = fdl_doc_context_at(result.doc, 0);
    REQUIRE(std::string(fdl_context_get_label(ctx2)) == "Camera B");
    REQUIRE(fdl_context_get_context_creator(ctx2) == nullptr); // was NULL

    auto* canvas2 = fdl_context_canvas_at(ctx2, 0);
    REQUIRE(std::string(fdl_canvas_get_id(canvas2)) == "CVS_ANA");
    REQUIRE(fdl_canvas_get_anamorphic_squeeze(canvas2) == 2.0);

    auto* fd = fdl_canvas_framing_decision_at(canvas2, 0);
    REQUIRE(std::string(fdl_framing_decision_get_id(fd)) == "CVS_ANA-FI_178");

    fdl_free(json);
    fdl_doc_free(result.doc);
    fdl_doc_free(doc);
}

TEST_CASE("Document setters modify existing fields", "[builder][setters]") {
    auto* doc = fdl_doc_create_with_header("old-uuid", 2, 0, "old-creator", nullptr);

    fdl_doc_set_uuid(doc, "new-uuid");
    fdl_doc_set_fdl_creator(doc, "new-creator");
    fdl_doc_set_version(doc, 3, 1);
    fdl_doc_set_default_framing_intent(doc, "FI_DEFAULT");

    REQUIRE(std::string(fdl_doc_get_uuid(doc)) == "new-uuid");
    REQUIRE(std::string(fdl_doc_get_fdl_creator(doc)) == "new-creator");
    REQUIRE(std::string(fdl_doc_get_default_framing_intent(doc)) == "FI_DEFAULT");

    fdl_doc_free(doc);
}

TEST_CASE("Build FDL with canvas template", "[builder][canvas_template]") {
    auto* doc = fdl_doc_create_with_header("00000000-0000-0000-0000-000000000099", 2, 0, "test-builder", nullptr);

    fdl_round_strategy_t rounding = {FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_UP};
    auto* ct = fdl_doc_add_canvas_template(
        doc,
        "CT_HD",
        "HD",
        1920,
        1080,
        1.0,
        FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS,
        FDL_FIT_METHOD_WIDTH,
        FDL_HALIGN_CENTER,
        FDL_VALIGN_CENTER,
        rounding);

    REQUIRE(ct != nullptr);
    REQUIRE(fdl_doc_canvas_templates_count(doc) == 1);

    // Verify via accessors
    REQUIRE(std::string(fdl_canvas_template_get_id(ct)) == "CT_HD");
    REQUIRE(std::string(fdl_canvas_template_get_label(ct)) == "HD");
    auto td = fdl_canvas_template_get_target_dimensions(ct);
    REQUIRE(td.width == 1920);
    REQUIRE(td.height == 1080);
    REQUIRE(fdl_canvas_template_get_target_anamorphic_squeeze(ct) == 1.0);
    REQUIRE(fdl_canvas_template_get_fit_source(ct) == FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS);
    REQUIRE(fdl_canvas_template_get_fit_method(ct) == FDL_FIT_METHOD_WIDTH);
    REQUIRE(fdl_canvas_template_get_alignment_method_horizontal(ct) == FDL_HALIGN_CENTER);
    REQUIRE(fdl_canvas_template_get_alignment_method_vertical(ct) == FDL_VALIGN_CENTER);

    auto rnd = fdl_canvas_template_get_round(ct);
    REQUIRE(rnd.even == FDL_ROUNDING_EVEN_EVEN);
    REQUIRE(rnd.mode == FDL_ROUNDING_MODE_UP);

    // Optional fields should not be present yet
    REQUIRE(fdl_canvas_template_has_preserve_from_source_canvas(ct) == 0);
    REQUIRE(fdl_canvas_template_has_maximum_dimensions(ct) == 0);
    REQUIRE(fdl_canvas_template_get_pad_to_maximum(ct) == 0);

    fdl_doc_free(doc);
}

TEST_CASE("Canvas template setters", "[builder][canvas_template]") {
    auto* doc = fdl_doc_create_with_header("00000000-0000-0000-0000-000000000099", 2, 0, "test-builder", nullptr);

    fdl_round_strategy_t rounding = {FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND};
    auto* ct = fdl_doc_add_canvas_template(
        doc,
        "CT_UHD",
        "UHD",
        3840,
        2160,
        1.0,
        FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS,
        FDL_FIT_METHOD_FIT_ALL,
        FDL_HALIGN_LEFT,
        FDL_VALIGN_TOP,
        rounding);
    REQUIRE(ct != nullptr);

    // Set optional fields
    fdl_canvas_template_set_preserve_from_source_canvas(ct, FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS);
    fdl_canvas_template_set_maximum_dimensions(ct, {3840, 2160});
    fdl_canvas_template_set_pad_to_maximum(ct, 1);

    // Verify optional fields
    REQUIRE(fdl_canvas_template_has_preserve_from_source_canvas(ct) == 1);
    REQUIRE(fdl_canvas_template_get_preserve_from_source_canvas(ct) == FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS);

    REQUIRE(fdl_canvas_template_has_maximum_dimensions(ct) == 1);
    auto max_dims = fdl_canvas_template_get_maximum_dimensions(ct);
    REQUIRE(max_dims.width == 3840);
    REQUIRE(max_dims.height == 2160);

    REQUIRE(fdl_canvas_template_get_pad_to_maximum(ct) == 1);

    // Verify roundtrip through serialization
    char* json = fdl_doc_to_json(doc, 2);
    REQUIRE(json != nullptr);

    auto parsed = ojson::parse(json);
    auto& ct_json = parsed["canvas_templates"][0];
    REQUIRE(ct_json["id"].as<std::string>() == "CT_UHD");
    REQUIRE(ct_json["fit_source"].as<std::string>() == "canvas.dimensions");
    REQUIRE(ct_json["fit_method"].as<std::string>() == "fit_all");
    REQUIRE(ct_json["alignment_method_horizontal"].as<std::string>() == "left");
    REQUIRE(ct_json["alignment_method_vertical"].as<std::string>() == "top");
    REQUIRE(ct_json["preserve_from_source_canvas"].as<std::string>() == "canvas.effective_dimensions");
    REQUIRE(ct_json["maximum_dimensions"]["width"].as<int>() == 3840);
    REQUIRE(ct_json["maximum_dimensions"]["height"].as<int>() == 2160);
    REQUIRE(ct_json["pad_to_maximum"].as<bool>() == true);
    REQUIRE(ct_json["round"]["even"].as<std::string>() == "whole");
    REQUIRE(ct_json["round"]["mode"].as<std::string>() == "round");

    fdl_free(json);
    fdl_doc_free(doc);
}

TEST_CASE("Canvas template builder NULL safety", "[builder][canvas_template][null]") {
    fdl_round_strategy_t rounding = {FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND};

    REQUIRE(
        fdl_doc_add_canvas_template(
            nullptr,
            "CT_HD",
            "HD",
            1920,
            1080,
            1.0,
            FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS,
            FDL_FIT_METHOD_WIDTH,
            FDL_HALIGN_CENTER,
            FDL_VALIGN_CENTER,
            rounding) == nullptr);

    auto* doc = fdl_doc_create_with_header("00000000-0000-0000-0000-000000000099", 2, 0, "test-builder", nullptr);

    REQUIRE(
        fdl_doc_add_canvas_template(
            doc,
            nullptr,
            "HD",
            1920,
            1080,
            1.0,
            FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS,
            FDL_FIT_METHOD_WIDTH,
            FDL_HALIGN_CENTER,
            FDL_VALIGN_CENTER,
            rounding) == nullptr);

    // Setter NULL safety
    fdl_canvas_template_set_preserve_from_source_canvas(nullptr, FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS);
    fdl_canvas_template_set_maximum_dimensions(nullptr, {0, 0});
    fdl_canvas_template_set_pad_to_maximum(nullptr, 1);

    fdl_doc_free(doc);
}

TEST_CASE("Builder NULL safety", "[builder][null]") {
    // These should not crash
    fdl_doc_set_uuid(nullptr, "x");
    fdl_doc_set_fdl_creator(nullptr, "x");
    fdl_doc_set_default_framing_intent(nullptr, "x");
    fdl_doc_set_version(nullptr, 2, 0);

    REQUIRE(fdl_doc_create_with_header(nullptr, 2, 0, "test", nullptr) == nullptr);
    REQUIRE(fdl_doc_create_with_header("uuid", 2, 0, nullptr, nullptr) == nullptr);

    REQUIRE(fdl_doc_add_framing_intent(nullptr, "id", "label", 16, 9, 0.0) == nullptr);
    REQUIRE(fdl_doc_add_context(nullptr, "label", nullptr) == nullptr);

    fdl_canvas_set_effective_dimensions(nullptr, {0, 0}, {0.0, 0.0});
    fdl_framing_decision_set_protection(nullptr, {0.0, 0.0}, {0.0, 0.0});
}
