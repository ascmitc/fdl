// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>

#include "fdl/fdl_core.h"

#include <cstring>
#include <string>

// A complete FDL document with all sub-object types for accessor testing.
// Uses the valid_full_document from schema_validation_vectors.
static const char* FULL_FDL = R"({
  "uuid": "00000000-0000-0000-0000-000000000018",
  "version": {"major": 2, "minor": 0},
  "fdl_creator": "test",
  "default_framing_intent": "FI_239",
  "framing_intents": [
    {
      "label": "2.39:1",
      "id": "FI_239",
      "aspect_ratio": {"width": 239, "height": 100},
      "protection": 0.1
    },
    {
      "label": "1.78:1",
      "id": "FI_178",
      "aspect_ratio": {"width": 16, "height": 9},
      "protection": 0.0
    }
  ],
  "contexts": [
    {
      "label": "Camera A",
      "context_creator": "DIT Station",
      "clip_id": {"clip_name": "A001", "file": "A001C001_220101_R1AB.ari"},
      "canvases": [
        {
          "label": "OCF",
          "id": "CVS_OCF",
          "source_canvas_id": "CVS_OCF",
          "dimensions": {"width": 4096, "height": 2160},
          "effective_dimensions": {"width": 4000, "height": 2100},
          "effective_anchor_point": {"x": 48.0, "y": 30.0},
          "photosite_dimensions": {"width": 4096, "height": 2160},
          "physical_dimensions": {"width": 23.76, "height": 12.528},
          "anamorphic_squeeze": 1.0,
          "framing_decisions": [
            {
              "label": "2.39:1",
              "id": "CVS_OCF-FI_239",
              "framing_intent_id": "FI_239",
              "dimensions": {"width": 3800.0, "height": 1600.0},
              "anchor_point": {"x": 100.0, "y": 250.0},
              "protection_dimensions": {"width": 3900.0, "height": 1700.0},
              "protection_anchor_point": {"x": 50.0, "y": 200.0}
            }
          ]
        },
        {
          "label": "Anamorphic",
          "id": "CVS_ANA",
          "source_canvas_id": "CVS_ANA",
          "dimensions": {"width": 4096, "height": 3432},
          "anamorphic_squeeze": 2.0,
          "framing_decisions": []
        }
      ]
    }
  ],
  "canvas_templates": [
    {
      "label": "HD",
      "id": "CT_HD",
      "target_dimensions": {"width": 1920, "height": 1080},
      "target_anamorphic_squeeze": 1.0,
      "fit_source": "framing_decision.dimensions",
      "fit_method": "width",
      "alignment_method_vertical": "center",
      "alignment_method_horizontal": "center",
      "round": {"even": "even", "mode": "up"}
    },
    {
      "label": "UHD",
      "id": "CT_UHD",
      "target_dimensions": {"width": 3840, "height": 2160},
      "target_anamorphic_squeeze": 1.0,
      "fit_source": "canvas.dimensions",
      "fit_method": "fit_all",
      "alignment_method_vertical": "top",
      "alignment_method_horizontal": "left",
      "preserve_from_source_canvas": "canvas.effective_dimensions",
      "maximum_dimensions": {"width": 3840, "height": 2160},
      "pad_to_maximum": true,
      "round": {"even": "whole", "mode": "round"}
    }
  ]
})";

static fdl_doc_t* parse_full_fdl() {
    auto result = fdl_doc_parse_json(FULL_FDL, std::strlen(FULL_FDL));
    REQUIRE(result.doc != nullptr);
    REQUIRE(result.error == nullptr);
    return result.doc;
}

// -----------------------------------------------------------------------
// Collection traversal tests
// -----------------------------------------------------------------------

TEST_CASE("Document collection counts", "[accessors][collections]") {
    auto* doc = parse_full_fdl();

    REQUIRE(fdl_doc_framing_intents_count(doc) == 2);
    REQUIRE(fdl_doc_contexts_count(doc) == 1);
    REQUIRE(fdl_doc_canvas_templates_count(doc) == 2);

    fdl_doc_free(doc);
}

TEST_CASE("Framing intent find_by_id", "[accessors][collections]") {
    auto* doc = parse_full_fdl();

    auto* fi = fdl_doc_framing_intent_find_by_id(doc, "FI_239");
    REQUIRE(fi != nullptr);
    REQUIRE(std::string(fdl_framing_intent_get_id(fi)) == "FI_239");

    auto* fi2 = fdl_doc_framing_intent_find_by_id(doc, "FI_178");
    REQUIRE(fi2 != nullptr);
    REQUIRE(std::string(fdl_framing_intent_get_id(fi2)) == "FI_178");

    auto* fi3 = fdl_doc_framing_intent_find_by_id(doc, "NONEXISTENT");
    REQUIRE(fi3 == nullptr);

    fdl_doc_free(doc);
}

TEST_CASE("Canvas template find_by_id", "[accessors][collections]") {
    auto* doc = parse_full_fdl();

    auto* ct = fdl_doc_canvas_template_find_by_id(doc, "CT_HD");
    REQUIRE(ct != nullptr);
    REQUIRE(std::string(fdl_canvas_template_get_id(ct)) == "CT_HD");

    auto* ct2 = fdl_doc_canvas_template_find_by_id(doc, "NONEXISTENT");
    REQUIRE(ct2 == nullptr);

    fdl_doc_free(doc);
}

TEST_CASE("Context -> Canvas -> FramingDecision traversal", "[accessors][collections]") {
    auto* doc = parse_full_fdl();

    auto* ctx = fdl_doc_context_at(doc, 0);
    REQUIRE(ctx != nullptr);
    REQUIRE(fdl_context_canvases_count(ctx) == 2);

    auto* canvas = fdl_context_canvas_at(ctx, 0);
    REQUIRE(canvas != nullptr);
    REQUIRE(fdl_canvas_framing_decisions_count(canvas) == 1);

    auto* fd = fdl_canvas_framing_decision_at(canvas, 0);
    REQUIRE(fd != nullptr);

    // Second canvas has 0 framing decisions
    auto* canvas2 = fdl_context_canvas_at(ctx, 1);
    REQUIRE(canvas2 != nullptr);
    REQUIRE(fdl_canvas_framing_decisions_count(canvas2) == 0);

    fdl_doc_free(doc);
}

TEST_CASE("Out-of-bounds returns NULL", "[accessors][collections]") {
    auto* doc = parse_full_fdl();

    REQUIRE(fdl_doc_context_at(doc, 99) == nullptr);
    REQUIRE(fdl_doc_framing_intent_at(doc, 99) == nullptr);
    REQUIRE(fdl_doc_canvas_template_at(doc, 99) == nullptr);

    auto* ctx = fdl_doc_context_at(doc, 0);
    REQUIRE(fdl_context_canvas_at(ctx, 99) == nullptr);

    auto* canvas = fdl_context_canvas_at(ctx, 0);
    REQUIRE(fdl_canvas_framing_decision_at(canvas, 99) == nullptr);

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// Document header accessors
// -----------------------------------------------------------------------

TEST_CASE("Document header accessors", "[accessors][header]") {
    auto* doc = parse_full_fdl();

    REQUIRE(std::string(fdl_doc_get_uuid(doc)) == "00000000-0000-0000-0000-000000000018");
    REQUIRE(std::string(fdl_doc_get_fdl_creator(doc)) == "test");
    REQUIRE(std::string(fdl_doc_get_default_framing_intent(doc)) == "FI_239");

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// Context field accessors
// -----------------------------------------------------------------------

TEST_CASE("Context field accessors", "[accessors][context]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    REQUIRE(std::string(fdl_context_get_label(ctx)) == "Camera A");
    REQUIRE(std::string(fdl_context_get_context_creator(ctx)) == "DIT Station");

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// Canvas field accessors
// -----------------------------------------------------------------------

TEST_CASE("Canvas field accessors", "[accessors][canvas]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    SECTION("Canvas with effective dimensions") {
        auto* canvas = fdl_context_canvas_at(ctx, 0);

        REQUIRE(std::string(fdl_canvas_get_label(canvas)) == "OCF");
        REQUIRE(std::string(fdl_canvas_get_id(canvas)) == "CVS_OCF");
        REQUIRE(std::string(fdl_canvas_get_source_canvas_id(canvas)) == "CVS_OCF");

        auto dims = fdl_canvas_get_dimensions(canvas);
        REQUIRE(dims.width == 4096);
        REQUIRE(dims.height == 2160);

        REQUIRE(fdl_canvas_has_effective_dimensions(canvas) == 1);
        auto eff = fdl_canvas_get_effective_dimensions(canvas);
        REQUIRE(eff.width == 4000);
        REQUIRE(eff.height == 2100);

        auto anchor = fdl_canvas_get_effective_anchor_point(canvas);
        REQUIRE(anchor.x == 48.0);
        REQUIRE(anchor.y == 30.0);

        REQUIRE(fdl_canvas_get_anamorphic_squeeze(canvas) == 1.0);
    }

    SECTION("Canvas without effective dimensions, with squeeze") {
        auto* canvas = fdl_context_canvas_at(ctx, 1);

        REQUIRE(std::string(fdl_canvas_get_label(canvas)) == "Anamorphic");
        REQUIRE(std::string(fdl_canvas_get_id(canvas)) == "CVS_ANA");

        REQUIRE(fdl_canvas_has_effective_dimensions(canvas) == 0);
        REQUIRE(fdl_canvas_get_anamorphic_squeeze(canvas) == 2.0);
    }

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// Framing decision field accessors
// -----------------------------------------------------------------------

TEST_CASE("Framing decision field accessors", "[accessors][framing_decision]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);
    auto* canvas = fdl_context_canvas_at(ctx, 0);
    auto* fd = fdl_canvas_framing_decision_at(canvas, 0);

    REQUIRE(std::string(fdl_framing_decision_get_label(fd)) == "2.39:1");
    REQUIRE(std::string(fdl_framing_decision_get_id(fd)) == "CVS_OCF-FI_239");
    REQUIRE(std::string(fdl_framing_decision_get_framing_intent_id(fd)) == "FI_239");

    auto dims = fdl_framing_decision_get_dimensions(fd);
    REQUIRE(dims.width == 3800.0);
    REQUIRE(dims.height == 1600.0);

    auto anchor = fdl_framing_decision_get_anchor_point(fd);
    REQUIRE(anchor.x == 100.0);
    REQUIRE(anchor.y == 250.0);

    REQUIRE(fdl_framing_decision_has_protection(fd) == 1);

    auto prot_dims = fdl_framing_decision_get_protection_dimensions(fd);
    REQUIRE(prot_dims.width == 3900.0);
    REQUIRE(prot_dims.height == 1700.0);

    auto prot_anchor = fdl_framing_decision_get_protection_anchor_point(fd);
    REQUIRE(prot_anchor.x == 50.0);
    REQUIRE(prot_anchor.y == 200.0);

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// Framing intent field accessors
// -----------------------------------------------------------------------

TEST_CASE("Framing intent field accessors", "[accessors][framing_intent]") {
    auto* doc = parse_full_fdl();

    auto* fi = fdl_doc_framing_intent_at(doc, 0);
    REQUIRE(std::string(fdl_framing_intent_get_label(fi)) == "2.39:1");
    REQUIRE(std::string(fdl_framing_intent_get_id(fi)) == "FI_239");

    auto ar = fdl_framing_intent_get_aspect_ratio(fi);
    REQUIRE(ar.width == 239);
    REQUIRE(ar.height == 100);
    REQUIRE(fdl_framing_intent_get_protection(fi) == 0.1);

    auto* fi2 = fdl_doc_framing_intent_at(doc, 1);
    REQUIRE(fdl_framing_intent_get_protection(fi2) == 0.0);

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// Canvas template field accessors
// -----------------------------------------------------------------------

TEST_CASE("Canvas template field accessors -basic", "[accessors][canvas_template]") {
    auto* doc = parse_full_fdl();
    auto* ct = fdl_doc_canvas_template_at(doc, 0);

    REQUIRE(std::string(fdl_canvas_template_get_label(ct)) == "HD");
    REQUIRE(std::string(fdl_canvas_template_get_id(ct)) == "CT_HD");

    auto td = fdl_canvas_template_get_target_dimensions(ct);
    REQUIRE(td.width == 1920);
    REQUIRE(td.height == 1080);

    REQUIRE(fdl_canvas_template_get_target_anamorphic_squeeze(ct) == 1.0);
    REQUIRE(fdl_canvas_template_get_fit_source(ct) == FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS);
    REQUIRE(fdl_canvas_template_get_fit_method(ct) == FDL_FIT_METHOD_WIDTH);
    REQUIRE(fdl_canvas_template_get_alignment_method_horizontal(ct) == FDL_HALIGN_CENTER);
    REQUIRE(fdl_canvas_template_get_alignment_method_vertical(ct) == FDL_VALIGN_CENTER);

    REQUIRE(fdl_canvas_template_has_preserve_from_source_canvas(ct) == 0);
    REQUIRE(fdl_canvas_template_has_maximum_dimensions(ct) == 0);
    REQUIRE(fdl_canvas_template_get_pad_to_maximum(ct) == 0);

    auto rnd = fdl_canvas_template_get_round(ct);
    REQUIRE(rnd.even == FDL_ROUNDING_EVEN_EVEN);
    REQUIRE(rnd.mode == FDL_ROUNDING_MODE_UP);

    fdl_doc_free(doc);
}

TEST_CASE("Canvas template field accessors -with optional fields", "[accessors][canvas_template]") {
    auto* doc = parse_full_fdl();
    auto* ct = fdl_doc_canvas_template_at(doc, 1); // CT_UHD

    REQUIRE(std::string(fdl_canvas_template_get_id(ct)) == "CT_UHD");
    REQUIRE(fdl_canvas_template_get_fit_source(ct) == FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS);
    REQUIRE(fdl_canvas_template_get_fit_method(ct) == FDL_FIT_METHOD_FIT_ALL);
    REQUIRE(fdl_canvas_template_get_alignment_method_horizontal(ct) == FDL_HALIGN_LEFT);
    REQUIRE(fdl_canvas_template_get_alignment_method_vertical(ct) == FDL_VALIGN_TOP);

    REQUIRE(fdl_canvas_template_has_preserve_from_source_canvas(ct) == 1);
    REQUIRE(fdl_canvas_template_get_preserve_from_source_canvas(ct) == FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS);

    REQUIRE(fdl_canvas_template_has_maximum_dimensions(ct) == 1);
    auto max_dims = fdl_canvas_template_get_maximum_dimensions(ct);
    REQUIRE(max_dims.width == 3840);
    REQUIRE(max_dims.height == 2160);

    REQUIRE(fdl_canvas_template_get_pad_to_maximum(ct) == 1);

    auto rnd = fdl_canvas_template_get_round(ct);
    REQUIRE(rnd.even == FDL_ROUNDING_EVEN_WHOLE);
    REQUIRE(rnd.mode == FDL_ROUNDING_MODE_ROUND);

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// Version accessors
// -----------------------------------------------------------------------

TEST_CASE("Document version accessors", "[accessors][header]") {
    auto* doc = parse_full_fdl();

    REQUIRE(fdl_doc_get_version_major(doc) == 2);
    REQUIRE(fdl_doc_get_version_minor(doc) == 0);

    fdl_doc_free(doc);
}

TEST_CASE("Document version accessors -NULL safety", "[accessors][header][null]") {
    REQUIRE(fdl_doc_get_version_major(nullptr) == 0);
    REQUIRE(fdl_doc_get_version_minor(nullptr) == 0);
}

// -----------------------------------------------------------------------
// Canvas optional field accessors (photosite, physical, clip_id)
// -----------------------------------------------------------------------

TEST_CASE("Canvas photosite_dimensions accessors", "[accessors][canvas]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    SECTION("Canvas with photosite_dimensions") {
        auto* canvas = fdl_context_canvas_at(ctx, 0); // CVS_OCF has it
        REQUIRE(fdl_canvas_has_photosite_dimensions(canvas) == 1);
        auto pd = fdl_canvas_get_photosite_dimensions(canvas);
        REQUIRE(pd.width == 4096);
        REQUIRE(pd.height == 2160);
    }

    SECTION("Canvas without photosite_dimensions") {
        auto* canvas = fdl_context_canvas_at(ctx, 1); // CVS_ANA does not have it
        REQUIRE(fdl_canvas_has_photosite_dimensions(canvas) == 0);
        auto pd = fdl_canvas_get_photosite_dimensions(canvas);
        REQUIRE(pd.width == 0);
        REQUIRE(pd.height == 0);
    }

    fdl_doc_free(doc);
}

TEST_CASE("Canvas physical_dimensions accessors", "[accessors][canvas]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    SECTION("Canvas with physical_dimensions") {
        auto* canvas = fdl_context_canvas_at(ctx, 0); // CVS_OCF has it
        REQUIRE(fdl_canvas_has_physical_dimensions(canvas) == 1);
        auto pd = fdl_canvas_get_physical_dimensions(canvas);
        REQUIRE(pd.width == 23.76);
        REQUIRE(pd.height == 12.528);
    }

    SECTION("Canvas without physical_dimensions") {
        auto* canvas = fdl_context_canvas_at(ctx, 1); // CVS_ANA does not have it
        REQUIRE(fdl_canvas_has_physical_dimensions(canvas) == 0);
    }

    fdl_doc_free(doc);
}

TEST_CASE("Context clip_id accessors", "[accessors][context]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    SECTION("Context with clip_id -JSON getter") {
        REQUIRE(fdl_context_has_clip_id(ctx) == 1);
        auto* json = fdl_context_get_clip_id(ctx);
        REQUIRE(json != nullptr);
        std::string json_str(json);
        REQUIRE(json_str.find("A001") != std::string::npos);
    }

    SECTION("Context with clip_id -handle getter (file variant)") {
        auto* cid = fdl_context_clip_id(ctx);
        REQUIRE(cid != nullptr);
        REQUIRE(std::string(fdl_clip_id_get_clip_name(cid)) == "A001");
        REQUIRE(fdl_clip_id_has_file(cid) == 1);
        REQUIRE(std::string(fdl_clip_id_get_file(cid)) == "A001C001_220101_R1AB.ari");
        REQUIRE(fdl_clip_id_has_sequence(cid) == 0);
        REQUIRE(fdl_clip_id_sequence(cid) == nullptr);
    }

    SECTION("clip_id handle NULL safety") {
        REQUIRE(fdl_context_clip_id(nullptr) == nullptr);
        REQUIRE(fdl_clip_id_get_clip_name(nullptr) == nullptr);
        REQUIRE(fdl_clip_id_has_file(nullptr) == 0);
        REQUIRE(fdl_clip_id_get_file(nullptr) == nullptr);
        REQUIRE(fdl_clip_id_has_sequence(nullptr) == 0);
        REQUIRE(fdl_clip_id_sequence(nullptr) == nullptr);
        REQUIRE(fdl_clip_id_to_json(nullptr, 0) == nullptr);
    }

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// Collection find helpers
// -----------------------------------------------------------------------

TEST_CASE("Context find_by_label", "[accessors][collections]") {
    auto* doc = parse_full_fdl();

    auto* ctx = fdl_doc_context_find_by_label(doc, "Camera A");
    REQUIRE(ctx != nullptr);
    REQUIRE(std::string(fdl_context_get_label(ctx)) == "Camera A");

    auto* ctx2 = fdl_doc_context_find_by_label(doc, "NONEXISTENT");
    REQUIRE(ctx2 == nullptr);

    REQUIRE(fdl_doc_context_find_by_label(doc, nullptr) == nullptr);
    REQUIRE(fdl_doc_context_find_by_label(nullptr, "Camera A") == nullptr);

    fdl_doc_free(doc);
}

TEST_CASE("Canvas find_by_id (child of context)", "[accessors][collections]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    auto* canvas = fdl_context_find_canvas_by_id(ctx, "CVS_OCF");
    REQUIRE(canvas != nullptr);
    REQUIRE(std::string(fdl_canvas_get_id(canvas)) == "CVS_OCF");

    auto* canvas2 = fdl_context_find_canvas_by_id(ctx, "CVS_ANA");
    REQUIRE(canvas2 != nullptr);
    REQUIRE(std::string(fdl_canvas_get_id(canvas2)) == "CVS_ANA");

    auto* canvas3 = fdl_context_find_canvas_by_id(ctx, "NONEXISTENT");
    REQUIRE(canvas3 == nullptr);

    REQUIRE(fdl_context_find_canvas_by_id(ctx, nullptr) == nullptr);
    REQUIRE(fdl_context_find_canvas_by_id(nullptr, "CVS_OCF") == nullptr);

    fdl_doc_free(doc);
}

TEST_CASE("Framing decision find_by_id (child of canvas)", "[accessors][collections]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);
    auto* canvas = fdl_context_canvas_at(ctx, 0);

    auto* fd = fdl_canvas_find_framing_decision_by_id(canvas, "CVS_OCF-FI_239");
    REQUIRE(fd != nullptr);
    REQUIRE(std::string(fdl_framing_decision_get_id(fd)) == "CVS_OCF-FI_239");

    auto* fd2 = fdl_canvas_find_framing_decision_by_id(canvas, "NONEXISTENT");
    REQUIRE(fd2 == nullptr);

    REQUIRE(fdl_canvas_find_framing_decision_by_id(canvas, nullptr) == nullptr);
    REQUIRE(fdl_canvas_find_framing_decision_by_id(nullptr, "CVS_OCF-FI_239") == nullptr);

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// clip_id setter / remover / validator
// -----------------------------------------------------------------------

TEST_CASE("set_clip_id_json -file variant", "[accessors][context][clip_id]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    // Set a new clip_id with file variant
    const char* json = R"({"clip_name": "B001", "file": "B001C001.ari"})";
    auto* err = fdl_context_set_clip_id_json(ctx, json, std::strlen(json));
    REQUIRE(err == nullptr);

    // Verify via handle getter
    REQUIRE(fdl_context_has_clip_id(ctx) == 1);
    auto* cid = fdl_context_clip_id(ctx);
    REQUIRE(cid != nullptr);
    REQUIRE(std::string(fdl_clip_id_get_clip_name(cid)) == "B001");
    REQUIRE(fdl_clip_id_has_file(cid) == 1);
    REQUIRE(std::string(fdl_clip_id_get_file(cid)) == "B001C001.ari");
    REQUIRE(fdl_clip_id_has_sequence(cid) == 0);

    fdl_doc_free(doc);
}

TEST_CASE("set_clip_id_json -sequence variant", "[accessors][context][clip_id]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    const char* json =
        R"({"clip_name": "C001", "sequence": {"value": "C001.####.exr", "idx": "#", "min": 0, "max": 100}})";
    auto* err = fdl_context_set_clip_id_json(ctx, json, std::strlen(json));
    REQUIRE(err == nullptr);

    REQUIRE(fdl_context_has_clip_id(ctx) == 1);
    auto* cid = fdl_context_clip_id(ctx);
    REQUIRE(cid != nullptr);
    REQUIRE(std::string(fdl_clip_id_get_clip_name(cid)) == "C001");
    REQUIRE(fdl_clip_id_has_file(cid) == 0);
    REQUIRE(fdl_clip_id_has_sequence(cid) == 1);
    auto* seq = fdl_clip_id_sequence(cid);
    REQUIRE(seq != nullptr);
    REQUIRE(std::string(fdl_file_sequence_get_value(seq)) == "C001.####.exr");

    fdl_doc_free(doc);
}

TEST_CASE("set_clip_id_json -mutual exclusion rejected", "[accessors][context][clip_id]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    // Remove existing clip_id first so we can verify it stays removed on error
    fdl_context_remove_clip_id(ctx);
    REQUIRE(fdl_context_has_clip_id(ctx) == 0);

    const char* json =
        R"({"clip_name": "D001", "file": "D001.ari", "sequence": {"value": "D001.####.exr", "idx": "#", "min": 0, "max": 10}})";
    auto* err = fdl_context_set_clip_id_json(ctx, json, std::strlen(json));
    REQUIRE(err != nullptr);
    REQUIRE(std::string(err).find("Both file and sequence") != std::string::npos);
    fdl_free(const_cast<char*>(err));

    // clip_id should not have been set
    REQUIRE(fdl_context_has_clip_id(ctx) == 0);

    fdl_doc_free(doc);
}

TEST_CASE("remove_clip_id", "[accessors][context][clip_id]") {
    auto* doc = parse_full_fdl();
    auto* ctx = fdl_doc_context_at(doc, 0);

    // Initially present
    REQUIRE(fdl_context_has_clip_id(ctx) == 1);

    fdl_context_remove_clip_id(ctx);
    REQUIRE(fdl_context_has_clip_id(ctx) == 0);

    // Remove again -should be safe
    fdl_context_remove_clip_id(ctx);
    REQUIRE(fdl_context_has_clip_id(ctx) == 0);

    fdl_doc_free(doc);
}

// -----------------------------------------------------------------------
// NULL safety tests
// -----------------------------------------------------------------------

TEST_CASE("NULL handle safety", "[accessors][null]") {
    REQUIRE(fdl_context_get_label(nullptr) == nullptr);
    REQUIRE(fdl_canvas_get_label(nullptr) == nullptr);
    REQUIRE(fdl_canvas_get_id(nullptr) == nullptr);
    REQUIRE(fdl_framing_decision_get_label(nullptr) == nullptr);
    REQUIRE(fdl_framing_intent_get_label(nullptr) == nullptr);
    REQUIRE(fdl_canvas_template_get_label(nullptr) == nullptr);

    REQUIRE(fdl_canvas_has_effective_dimensions(nullptr) == 0);
    REQUIRE(fdl_canvas_has_photosite_dimensions(nullptr) == 0);
    REQUIRE(fdl_canvas_has_physical_dimensions(nullptr) == 0);
    REQUIRE(fdl_context_has_clip_id(nullptr) == 0);
    REQUIRE(fdl_context_get_clip_id(nullptr) == nullptr);
    REQUIRE(fdl_context_clip_id(nullptr) == nullptr);
    REQUIRE(fdl_clip_id_get_clip_name(nullptr) == nullptr);
    REQUIRE(fdl_clip_id_has_file(nullptr) == 0);
    REQUIRE(fdl_clip_id_get_file(nullptr) == nullptr);
    REQUIRE(fdl_clip_id_has_sequence(nullptr) == 0);
    REQUIRE(fdl_clip_id_sequence(nullptr) == nullptr);
    REQUIRE(fdl_clip_id_to_json(nullptr, 0) == nullptr);
    REQUIRE(fdl_file_sequence_get_value(nullptr) == nullptr);
    REQUIRE(fdl_file_sequence_get_idx(nullptr) == nullptr);
    REQUIRE(fdl_file_sequence_get_min(nullptr) == 0);
    REQUIRE(fdl_file_sequence_get_max(nullptr) == 0);
    REQUIRE(fdl_framing_decision_has_protection(nullptr) == 0);
    REQUIRE(fdl_canvas_template_has_preserve_from_source_canvas(nullptr) == 0);
    REQUIRE(fdl_canvas_template_has_maximum_dimensions(nullptr) == 0);

    REQUIRE(fdl_context_canvases_count(nullptr) == 0);
    REQUIRE(fdl_canvas_framing_decisions_count(nullptr) == 0);
    REQUIRE(fdl_doc_framing_intents_count(nullptr) == 0);
    REQUIRE(fdl_doc_contexts_count(nullptr) == 0);
    REQUIRE(fdl_doc_canvas_templates_count(nullptr) == 0);
}
