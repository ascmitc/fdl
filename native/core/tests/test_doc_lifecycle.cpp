// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>

#include "fdl/fdl_core.h"

#include <cstring>
#include <string>

// Minimal valid FDL JSON for testing
static const char* MINIMAL_FDL = R"({
  "uuid": "test-uuid-1234",
  "version": {"major": 2, "minor": 0},
  "fdl_creator": "test-creator",
  "framing_intents": [],
  "contexts": [],
  "canvas_templates": []
})";

TEST_CASE("fdl_doc_create and fdl_doc_free", "[doc][lifecycle]") {
    auto* doc = fdl_doc_create();
    REQUIRE(doc != nullptr);
    fdl_doc_free(doc);
    // free(NULL) is safe
    fdl_doc_free(nullptr);
}

TEST_CASE("fdl_doc_parse_json with valid JSON", "[doc][parse]") {
    auto result = fdl_doc_parse_json(MINIMAL_FDL, std::strlen(MINIMAL_FDL));
    REQUIRE(result.doc != nullptr);
    REQUIRE(result.error == nullptr);

    // Check accessors
    const char* uuid = fdl_doc_get_uuid(result.doc);
    REQUIRE(uuid != nullptr);
    REQUIRE(std::string(uuid) == "test-uuid-1234");

    const char* creator = fdl_doc_get_fdl_creator(result.doc);
    REQUIRE(creator != nullptr);
    REQUIRE(std::string(creator) == "test-creator");

    fdl_doc_free(result.doc);
}

TEST_CASE("fdl_doc_parse_json with invalid JSON", "[doc][parse]") {
    const char* bad_json = "{ not valid json }";
    auto result = fdl_doc_parse_json(bad_json, std::strlen(bad_json));
    REQUIRE(result.doc == nullptr);
    REQUIRE(result.error != nullptr);
    // Error message should contain parse location info
    REQUIRE(std::string(result.error).find("line") != std::string::npos);
    fdl_free(const_cast<char*>(result.error));
}

TEST_CASE("fdl_doc_parse_json with empty string", "[doc][parse]") {
    auto result = fdl_doc_parse_json("", 0);
    REQUIRE(result.doc == nullptr);
    REQUIRE(result.error != nullptr);
    fdl_free(const_cast<char*>(result.error));
}

TEST_CASE("fdl_doc_get_uuid returns NULL for empty doc", "[doc][accessors]") {
    auto* doc = fdl_doc_create();
    REQUIRE(doc != nullptr);
    REQUIRE(fdl_doc_get_uuid(doc) == nullptr);
    REQUIRE(fdl_doc_get_fdl_creator(doc) == nullptr);
    fdl_doc_free(doc);
}

TEST_CASE("fdl_doc_get_uuid returns NULL for NULL doc", "[doc][accessors]") {
    REQUIRE(fdl_doc_get_uuid(nullptr) == nullptr);
    REQUIRE(fdl_doc_get_fdl_creator(nullptr) == nullptr);
}

TEST_CASE("fdl_doc_to_json produces valid output", "[doc][serialize]") {
    auto result = fdl_doc_parse_json(MINIMAL_FDL, std::strlen(MINIMAL_FDL));
    REQUIRE(result.doc != nullptr);

    char* json = fdl_doc_to_json(result.doc, 2);
    REQUIRE(json != nullptr);

    // Should contain the uuid
    REQUIRE(std::string(json).find("test-uuid-1234") != std::string::npos);

    fdl_free(json);
    fdl_doc_free(result.doc);
}

TEST_CASE("fdl_doc_to_json returns NULL for NULL doc", "[doc][serialize]") {
    REQUIRE(fdl_doc_to_json(nullptr, 2) == nullptr);
}

TEST_CASE("fdl_doc_to_json strips null values", "[doc][serialize]") {
    const char* json_with_nulls = R"({
      "uuid": "test-uuid",
      "version": {"major": 2, "minor": 0},
      "fdl_creator": "test",
      "default_framing_intent": null,
      "framing_intents": [],
      "contexts": [],
      "canvas_templates": []
    })";
    auto result = fdl_doc_parse_json(json_with_nulls, std::strlen(json_with_nulls));
    REQUIRE(result.doc != nullptr);

    char* json = fdl_doc_to_json(result.doc, 2);
    REQUIRE(json != nullptr);

    std::string output(json);
    // null values should be stripped
    REQUIRE(output.find("default_framing_intent") == std::string::npos);
    // empty arrays should remain
    REQUIRE(output.find("framing_intents") != std::string::npos);

    fdl_free(json);
    fdl_doc_free(result.doc);
}

TEST_CASE("fdl_doc_to_json orders keys canonically", "[doc][serialize]") {
    // Keys in wrong order
    const char* unordered = R"({
      "canvas_templates": [],
      "fdl_creator": "test",
      "uuid": "abc",
      "version": {"minor": 0, "major": 2},
      "contexts": [],
      "framing_intents": []
    })";
    auto result = fdl_doc_parse_json(unordered, std::strlen(unordered));
    REQUIRE(result.doc != nullptr);

    char* json = fdl_doc_to_json(result.doc, 2);
    REQUIRE(json != nullptr);

    std::string output(json);
    // uuid should appear before fdl_creator
    auto uuid_pos = output.find("\"uuid\"");
    auto creator_pos = output.find("\"fdl_creator\"");
    auto fi_pos = output.find("\"framing_intents\"");
    auto ctx_pos = output.find("\"contexts\"");
    auto ct_pos = output.find("\"canvas_templates\"");

    REQUIRE(uuid_pos < creator_pos);
    REQUIRE(creator_pos < fi_pos);
    REQUIRE(fi_pos < ctx_pos);
    REQUIRE(ctx_pos < ct_pos);

    // version keys should be ordered: major before minor
    auto major_pos = output.find("\"major\"");
    auto minor_pos = output.find("\"minor\"");
    REQUIRE(major_pos < minor_pos);

    fdl_free(json);
    fdl_doc_free(result.doc);
}

// -----------------------------------------------------------------------
// Sub-object to_json
// -----------------------------------------------------------------------

// Full FDL for sub-object serialization tests
static const char* FULL_FDL = R"({
  "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "version": {"major": 2, "minor": 0},
  "fdl_creator": "test",
  "default_framing_intent": "FI_01",
  "framing_intents": [
    {"label": "Default", "id": "FI_01", "aspect_ratio": {"width": 16, "height": 9}, "protection": 0.0}
  ],
  "contexts": [
    {
      "label": "Source",
      "context_creator": "test",
      "canvases": [
        {
          "label": "Source Canvas",
          "id": "CV_01",
          "source_canvas_id": "CV_01",
          "dimensions": {"width": 3840, "height": 2160},
          "anamorphic_squeeze": 1.0,
          "framing_decisions": [
            {
              "label": "Default FD",
              "id": "CV_01-FI_01",
              "framing_intent_id": "FI_01",
              "dimensions": {"width": 3840.0, "height": 2160.0},
              "anchor_point": {"x": 0.0, "y": 0.0}
            }
          ]
        }
      ]
    }
  ],
  "canvas_templates": [
    {
      "label": "HD Delivery",
      "id": "CT_01",
      "target_dimensions": {"width": 1920, "height": 1080},
      "target_anamorphic_squeeze": 1.0,
      "fit_source": "canvas.dimensions",
      "fit_method": "width",
      "alignment_method_vertical": "center",
      "alignment_method_horizontal": "center",
      "round": {"even": "even", "mode": "round"}
    }
  ]
})";

TEST_CASE("fdl_context_to_json serializes context", "[serialize][subobject]") {
    auto result = fdl_doc_parse_json(FULL_FDL, std::strlen(FULL_FDL));
    REQUIRE(result.doc != nullptr);

    auto* ctx = fdl_doc_context_at(result.doc, 0);
    REQUIRE(ctx != nullptr);

    char* json = fdl_context_to_json(ctx, 2);
    REQUIRE(json != nullptr);
    std::string output(json);
    REQUIRE(output.find("\"label\"") != std::string::npos);
    REQUIRE(output.find("\"Source\"") != std::string::npos);
    REQUIRE(output.find("\"canvases\"") != std::string::npos);
    REQUIRE(output.find("\"framing_decisions\"") != std::string::npos);

    fdl_free(json);
    fdl_doc_free(result.doc);
}

TEST_CASE("fdl_canvas_to_json serializes canvas", "[serialize][subobject]") {
    auto result = fdl_doc_parse_json(FULL_FDL, std::strlen(FULL_FDL));
    REQUIRE(result.doc != nullptr);

    auto* ctx = fdl_doc_context_at(result.doc, 0);
    auto* canvas = fdl_context_canvas_at(ctx, 0);
    REQUIRE(canvas != nullptr);

    char* json = fdl_canvas_to_json(canvas, 2);
    REQUIRE(json != nullptr);
    std::string output(json);
    REQUIRE(output.find("\"id\"") != std::string::npos);
    REQUIRE(output.find("\"CV_01\"") != std::string::npos);
    REQUIRE(output.find("\"dimensions\"") != std::string::npos);

    fdl_free(json);
    fdl_doc_free(result.doc);
}

TEST_CASE("fdl_framing_decision_to_json serializes FD", "[serialize][subobject]") {
    auto result = fdl_doc_parse_json(FULL_FDL, std::strlen(FULL_FDL));
    REQUIRE(result.doc != nullptr);

    auto* ctx = fdl_doc_context_at(result.doc, 0);
    auto* canvas = fdl_context_canvas_at(ctx, 0);
    auto* fd = fdl_canvas_framing_decision_at(canvas, 0);
    REQUIRE(fd != nullptr);

    char* json = fdl_framing_decision_to_json(fd, 0);
    REQUIRE(json != nullptr);
    std::string output(json);
    REQUIRE(output.find("\"framing_intent_id\"") != std::string::npos);
    REQUIRE(output.find("\"anchor_point\"") != std::string::npos);

    fdl_free(json);
    fdl_doc_free(result.doc);
}

TEST_CASE("fdl_framing_intent_to_json serializes FI", "[serialize][subobject]") {
    auto result = fdl_doc_parse_json(FULL_FDL, std::strlen(FULL_FDL));
    REQUIRE(result.doc != nullptr);

    auto* fi = fdl_doc_framing_intent_at(result.doc, 0);
    REQUIRE(fi != nullptr);

    char* json = fdl_framing_intent_to_json(fi, 2);
    REQUIRE(json != nullptr);
    std::string output(json);
    REQUIRE(output.find("\"aspect_ratio\"") != std::string::npos);
    REQUIRE(output.find("\"FI_01\"") != std::string::npos);

    fdl_free(json);
    fdl_doc_free(result.doc);
}

TEST_CASE("fdl_canvas_template_to_json serializes CT", "[serialize][subobject]") {
    auto result = fdl_doc_parse_json(FULL_FDL, std::strlen(FULL_FDL));
    REQUIRE(result.doc != nullptr);

    auto* ct = fdl_doc_canvas_template_at(result.doc, 0);
    REQUIRE(ct != nullptr);

    char* json = fdl_canvas_template_to_json(ct, 2);
    REQUIRE(json != nullptr);
    std::string output(json);
    REQUIRE(output.find("\"target_dimensions\"") != std::string::npos);
    REQUIRE(output.find("\"fit_method\"") != std::string::npos);
    REQUIRE(output.find("\"CT_01\"") != std::string::npos);

    fdl_free(json);
    fdl_doc_free(result.doc);
}

TEST_CASE("Sub-object to_json returns NULL for NULL handles", "[serialize][subobject]") {
    REQUIRE(fdl_context_to_json(nullptr, 2) == nullptr);
    REQUIRE(fdl_canvas_to_json(nullptr, 2) == nullptr);
    REQUIRE(fdl_framing_decision_to_json(nullptr, 2) == nullptr);
    REQUIRE(fdl_framing_intent_to_json(nullptr, 2) == nullptr);
    REQUIRE(fdl_canvas_template_to_json(nullptr, 2) == nullptr);
}
