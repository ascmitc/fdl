// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
/**
 * C++ RAII facade tests -mirrors Python fdl_core test_facade.py and
 * test_facade_mutation.py to verify feature parity.
 */

#include <catch2/catch_approx.hpp>
#include <catch2/catch_test_macros.hpp>

#include "fdl/fdl.hpp"

#include <cstring>
#include <string>

using Catch::Approx;

// -----------------------------------------------------------------------
// Minimal FDL JSON fixture
// -----------------------------------------------------------------------

static const char* MINIMAL_FDL_JSON = R"({
  "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "version": {"major": 2, "minor": 0},
  "fdl_creator": "test",
  "default_framing_intent": "FI_01",
  "framing_intents": [
    {
      "id": "FI_01",
      "label": "Default",
      "aspect_ratio": {"width": 16, "height": 9},
      "protection": 0.0
    }
  ],
  "contexts": [
    {
      "label": "Source",
      "canvases": [
        {
          "id": "CV_01",
          "label": "Source Canvas",
          "source_canvas_id": "CV_01",
          "dimensions": {"width": 3840, "height": 2160},
          "anamorphic_squeeze": 1.0,
          "framing_decisions": [
            {
              "id": "CV_01-FI_01",
              "label": "Default FD",
              "framing_intent_id": "FI_01",
              "dimensions": {"width": 3840.0, "height": 2160.0},
              "anchor_point": {"x": 0.0, "y": 0.0}
            }
          ]
        }
      ]
    }
  ],
  "canvas_templates": []
})";

// -----------------------------------------------------------------------
// Value type wrappers (mirrors Python test_value_types + test_ffi_smoke)
// -----------------------------------------------------------------------

TEST_CASE("DimensionsInt wrapper", "[raii][value_types][dimensions]") {
    SECTION("construction and accessors") {
        fdl::DimensionsInt d(3840, 2160);
        REQUIRE(d.width() == 3840);
        REQUIRE(d.height() == 2160);
    }

    SECTION("default construction") {
        fdl::DimensionsInt d;
        REQUIRE(d.width() == 0);
        REQUIRE(d.height() == 0);
    }

    SECTION("implicit conversion to/from C struct") {
        fdl_dimensions_i64_t raw = {1920, 1080};
        fdl::DimensionsInt d(raw);
        REQUIRE(d.width() == 1920);
        REQUIRE(d.height() == 1080);

        fdl_dimensions_i64_t back = d;
        REQUIRE(back.width == 1920);
        REQUIRE(back.height == 1080);
    }

    SECTION("is_zero") {
        REQUIRE(fdl::DimensionsInt(0, 0).is_zero());
        REQUIRE_FALSE(fdl::DimensionsInt(1, 0).is_zero());
        REQUIRE_FALSE(fdl::DimensionsInt(0, 1).is_zero());
    }

    SECTION("normalize") {
        auto result = fdl::DimensionsInt(1920, 1080).normalize(2.0);
        REQUIRE(result.width() == Approx(3840.0));
        REQUIRE(result.height() == Approx(1080.0));
    }

    SECTION("format") {
        REQUIRE(fdl::DimensionsInt(3840, 2160).format() == "3840x2160");
    }

    SECTION("operator >") {
        REQUIRE(fdl::DimensionsInt(3840, 2160) > fdl::DimensionsInt(1920, 1080));
        REQUIRE_FALSE(fdl::DimensionsInt(1920, 1080) > fdl::DimensionsInt(3840, 2160));
    }

    SECTION("operator <") {
        REQUIRE(fdl::DimensionsInt(1920, 1080) < fdl::DimensionsInt(3840, 2160));
        REQUIRE_FALSE(fdl::DimensionsInt(3840, 2160) < fdl::DimensionsInt(1920, 1080));
    }

    SECTION("explicit bool") {
        REQUIRE(static_cast<bool>(fdl::DimensionsInt(1, 1)));
        REQUIRE(static_cast<bool>(fdl::DimensionsInt(1, 0))); // one nonzero → true
        REQUIRE(static_cast<bool>(fdl::DimensionsInt(0, 1))); // one nonzero → true
        REQUIRE_FALSE(static_cast<bool>(fdl::DimensionsInt(0, 0)));
    }

    SECTION("equality") {
        REQUIRE(fdl::DimensionsInt(1920, 1080) == fdl::DimensionsInt(1920, 1080));
        REQUIRE_FALSE(fdl::DimensionsInt(1920, 1080) == fdl::DimensionsInt(3840, 2160));
        REQUIRE(fdl::DimensionsInt(1920, 1080) != fdl::DimensionsInt(3840, 2160));
        REQUIRE_FALSE(fdl::DimensionsInt(1920, 1080) != fdl::DimensionsInt(1920, 1080));
    }
}

TEST_CASE("DimensionsFloat wrapper", "[raii][value_types][dimensions]") {
    SECTION("construction and accessors") {
        fdl::DimensionsFloat d(3840.0, 2160.0);
        REQUIRE(d.width() == 3840.0);
        REQUIRE(d.height() == 2160.0);
    }

    SECTION("implicit conversion to/from C struct") {
        fdl_dimensions_f64_t raw = {1920.0, 1080.0};
        fdl::DimensionsFloat d(raw);
        REQUIRE(d.width() == 1920.0);
        fdl_dimensions_f64_t back = d;
        REQUIRE(back.width == 1920.0);
    }

    SECTION("is_zero") {
        REQUIRE(fdl::DimensionsFloat(0.0, 0.0).is_zero());
        REQUIRE_FALSE(fdl::DimensionsFloat(1.0, 0.0).is_zero());
    }

    SECTION("normalize") {
        auto r = fdl::DimensionsFloat(1920.0, 1080.0).normalize(2.0);
        REQUIRE(r.width() == Approx(3840.0));
        REQUIRE(r.height() == Approx(1080.0));
    }

    SECTION("scale") {
        auto r = fdl::DimensionsFloat(3840.0, 2160.0).scale(0.5, 1.0);
        REQUIRE(r.width() == Approx(1920.0));
        REQUIRE(r.height() == Approx(1080.0));
    }

    SECTION("normalize_and_scale") {
        auto r = fdl::DimensionsFloat(1920.0, 1080.0).normalize_and_scale(2.0, 0.5, 1.0);
        REQUIRE(r.width() == Approx(1920.0));
        REQUIRE(r.height() == Approx(540.0));
    }

    SECTION("round") {
        auto r = fdl::DimensionsFloat(1920.5, 1080.5).round(FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND);
        REQUIRE(r.width() == Approx(1920.0));
        REQUIRE(r.height() == Approx(1080.0));
    }

    SECTION("to_int") {
        auto r = fdl::DimensionsFloat(1920.7, 1080.3).to_int();
        REQUIRE(r.width() == 1920);
        REQUIRE(r.height() == 1080);
    }

    SECTION("format") {
        REQUIRE(fdl::DimensionsFloat(1920.0, 1080.0).format() == "1920x1080");
    }

    SECTION("scale_by") {
        fdl::DimensionsFloat d(1920.0, 1080.0);
        d.scale_by(2.0);
        REQUIRE(d.width() == Approx(3840.0));
        REQUIRE(d.height() == Approx(2160.0));
    }

    SECTION("clamp_to_dims") {
        auto [clamped, delta] =
            fdl::DimensionsFloat(3840.0, 2160.0).clamp_to_dims(fdl::DimensionsFloat(1920.0, 1080.0));
        REQUIRE(clamped.width() == Approx(1920.0));
        REQUIRE(clamped.height() == Approx(1080.0));
    }

    SECTION("operator -") {
        auto r = fdl::DimensionsFloat(100.0, 200.0) - fdl::DimensionsFloat(30.0, 50.0);
        REQUIRE(r.width() == Approx(70.0));
        REQUIRE(r.height() == Approx(150.0));
    }

    SECTION("operator < and >") {
        REQUIRE(fdl::DimensionsFloat(100.0, 100.0) < fdl::DimensionsFloat(200.0, 200.0));
        REQUIRE(fdl::DimensionsFloat(200.0, 200.0) > fdl::DimensionsFloat(100.0, 100.0));
    }

    SECTION("explicit bool") {
        REQUIRE(static_cast<bool>(fdl::DimensionsFloat(1.0, 1.0)));
        REQUIRE(static_cast<bool>(fdl::DimensionsFloat(1.0, 0.0))); // one nonzero → true
        REQUIRE(static_cast<bool>(fdl::DimensionsFloat(0.0, 1.0))); // one nonzero → true
        REQUIRE_FALSE(static_cast<bool>(fdl::DimensionsFloat(0.0, 0.0)));
    }

    SECTION("equality") {
        REQUIRE(fdl::DimensionsFloat(1920.0, 1080.0) == fdl::DimensionsFloat(1920.0, 1080.0));
        REQUIRE_FALSE(fdl::DimensionsFloat(1920.0, 1080.0) == fdl::DimensionsFloat(1920.1, 1080.0));
        REQUIRE(fdl::DimensionsFloat(1920.0, 1080.0) != fdl::DimensionsFloat(1920.1, 1080.0));
        // FP-tolerant: values within tolerance are equal
        REQUIRE(fdl::DimensionsFloat(1.0, 2.0) == fdl::DimensionsFloat(1.0 + 1e-12, 2.0));
    }
}

TEST_CASE("PointFloat wrapper", "[raii][value_types][points]") {
    SECTION("construction and accessors") {
        fdl::PointFloat p(100.0, 200.0);
        REQUIRE(p.x() == 100.0);
        REQUIRE(p.y() == 200.0);
    }

    SECTION("implicit conversion to/from C struct") {
        fdl_point_f64_t raw = {10.0, 20.0};
        fdl::PointFloat p(raw);
        REQUIRE(p.x() == 10.0);
        fdl_point_f64_t back = p;
        REQUIRE(back.x == 10.0);
    }

    SECTION("is_zero") {
        REQUIRE(fdl::PointFloat(0.0, 0.0).is_zero());
        REQUIRE_FALSE(fdl::PointFloat(1.0, 0.0).is_zero());
    }

    SECTION("normalize") {
        auto r = fdl::PointFloat(100.0, 200.0).normalize(2.0);
        REQUIRE(r.x() == Approx(200.0));
        REQUIRE(r.y() == Approx(200.0));
    }

    SECTION("scale") {
        auto r = fdl::PointFloat(100.0, 200.0).scale(2.0, 1.0);
        REQUIRE(r.x() == Approx(200.0));
        REQUIRE(r.y() == Approx(400.0));
    }

    SECTION("clamp with limits") {
        auto r = fdl::PointFloat(150.0, -50.0).clamp(0.0, 100.0);
        REQUIRE(r.x() == Approx(100.0));
        REQUIRE(r.y() == Approx(0.0));
    }

    SECTION("round") {
        auto r = fdl::PointFloat(10.5, 20.5).round(FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND);
        REQUIRE(r.x() == Approx(10.0));
        REQUIRE(r.y() == Approx(20.0));
    }

    SECTION("format") {
        REQUIRE(fdl::PointFloat(100.0, 200.0).format() == "100x200");
    }

    SECTION("operator +") {
        auto r = fdl::PointFloat(100.0, 200.0) + fdl::PointFloat(30.0, 50.0);
        REQUIRE(r.x() == Approx(130.0));
        REQUIRE(r.y() == Approx(250.0));
    }

    SECTION("operator +=") {
        fdl::PointFloat p(100.0, 200.0);
        p += fdl::PointFloat(10.0, 20.0);
        REQUIRE(p.x() == Approx(110.0));
        REQUIRE(p.y() == Approx(220.0));
    }

    SECTION("operator -") {
        auto r = fdl::PointFloat(100.0, 200.0) - fdl::PointFloat(30.0, 50.0);
        REQUIRE(r.x() == Approx(70.0));
        REQUIRE(r.y() == Approx(150.0));
    }

    SECTION("operator * scalar") {
        auto r = fdl::PointFloat(100.0, 200.0) * 2.0;
        REQUIRE(r.x() == Approx(200.0));
        REQUIRE(r.y() == Approx(400.0));
    }

    SECTION("operator * element-wise") {
        auto r = fdl::PointFloat(10.0, 20.0) * fdl::PointFloat(3.0, 4.0);
        REQUIRE(r.x() == Approx(30.0));
        REQUIRE(r.y() == Approx(80.0));
    }

    SECTION("operator <") {
        REQUIRE(fdl::PointFloat(10.0, 20.0) < fdl::PointFloat(100.0, 200.0));
    }

    SECTION("equality") {
        REQUIRE(fdl::PointFloat(100.0, 200.0) == fdl::PointFloat(100.0, 200.0));
        REQUIRE_FALSE(fdl::PointFloat(100.0, 200.0) == fdl::PointFloat(100.1, 200.0));
        REQUIRE(fdl::PointFloat(100.0, 200.0) != fdl::PointFloat(100.1, 200.0));
        // FP-tolerant: values within tolerance are equal
        REQUIRE(fdl::PointFloat(1.0, 2.0) == fdl::PointFloat(1.0 + 1e-12, 2.0));
    }
}

// -----------------------------------------------------------------------
// Free functions (mirrors Python test_ffi_smoke TestRounding + TestPipeline)
// -----------------------------------------------------------------------

TEST_CASE("fdl::round", "[raii][free_functions][rounding]") {
    REQUIRE(fdl::round(2.5, FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND) == 2);
    REQUIRE(fdl::round(3.5, FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND) == 4);
    REQUIRE(fdl::round(2.5, FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND) == 2);
    // mode=up, even=even → round UP to nearest even: 2.3 → 4
    REQUIRE(fdl::round(2.3, FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_UP) == 4);
    // mode=down, even=even → round DOWN to nearest even: 2.7 → 2
    REQUIRE(fdl::round(2.7, FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_DOWN) == 2);
}

TEST_CASE("fdl::calculate_scale_factor", "[raii][free_functions][pipeline]") {
    auto sf = fdl::calculate_scale_factor(
        fdl::DimensionsFloat(3840.0, 2160.0), fdl::DimensionsFloat(1920.0, 1080.0), FDL_FIT_METHOD_WIDTH);
    REQUIRE(sf == Approx(0.5));

    auto sf2 = fdl::calculate_scale_factor(
        fdl::DimensionsFloat(3840.0, 2160.0), fdl::DimensionsFloat(1920.0, 1080.0), FDL_FIT_METHOD_HEIGHT);
    REQUIRE(sf2 == Approx(0.5));
}

// -----------------------------------------------------------------------
// FDL Document (mirrors Python TestDocument)
// -----------------------------------------------------------------------

TEST_CASE("FDL parse and properties", "[raii][facade][doc]") {
    auto doc = fdl::FDL::parse(MINIMAL_FDL_JSON);

    SECTION("uuid") {
        REQUIRE(doc.uuid() == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee");
    }

    SECTION("fdl_creator") {
        REQUIRE(doc.fdl_creator() == "test");
    }

    SECTION("default_framing_intent") {
        REQUIRE(doc.default_framing_intent() == "FI_01");
    }

    SECTION("version composite") {
        auto v = doc.version();
        REQUIRE(v.major == 2);
        REQUIRE(v.minor == 0);
    }

    SECTION("version_major and version_minor") {
        REQUIRE(doc.version_major() == 2);
        REQUIRE(doc.version_minor() == 0);
    }

    SECTION("as_json produces valid JSON") {
        auto json = doc.as_json(2);
        REQUIRE(json.find("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") != std::string::npos);
        REQUIRE(json.find("\"version\"") != std::string::npos);
    }

    SECTION("validate succeeds") {
        auto errors = doc.validate();
        REQUIRE(errors.empty());
    }

    SECTION("bool operator") {
        REQUIRE(static_cast<bool>(doc));
        fdl::FDL empty;
        REQUIRE_FALSE(static_cast<bool>(empty));
    }

    SECTION("move semantics") {
        fdl::FDL doc2 = std::move(doc);
        REQUIRE(static_cast<bool>(doc2));
        REQUIRE(doc2.uuid() == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee");
    }
}

// -----------------------------------------------------------------------
// Collections (mirrors Python TestCollections)
// -----------------------------------------------------------------------

TEST_CASE("FDL collections", "[raii][facade][collections]") {
    auto doc = fdl::FDL::parse(MINIMAL_FDL_JSON);

    SECTION("contexts count") {
        REQUIRE(doc.contexts_count() == 1);
    }

    SECTION("context_at") {
        auto ctx = doc.context_at(0);
        REQUIRE(ctx.label() == "Source");
    }

    SECTION("context_find_by_label") {
        auto ctx = doc.context_find_by_label("Source");
        REQUIRE(ctx.get() != nullptr);
        REQUIRE(ctx.label() == "Source");
    }

    SECTION("framing_intents count") {
        REQUIRE(doc.framing_intents_count() == 1);
    }

    SECTION("framing_intent_find_by_id") {
        auto fi = doc.framing_intent_find_by_id("FI_01");
        REQUIRE(fi.get() != nullptr);
        REQUIRE(fi.id() == "FI_01");
    }

    SECTION("canvas_templates count") {
        REQUIRE(doc.canvas_templates_count() == 0);
    }
}

// -----------------------------------------------------------------------
// Context (mirrors Python TestContext)
// -----------------------------------------------------------------------

TEST_CASE("ContextRef properties", "[raii][facade][context]") {
    auto doc = fdl::FDL::parse(MINIMAL_FDL_JSON);
    auto ctx = doc.context_at(0);

    SECTION("label") {
        REQUIRE(ctx.label() == "Source");
    }

    SECTION("context_creator is empty for null") {
        // In our minimal FDL, context_creator is not set
        auto creator = ctx.context_creator();
        REQUIRE(creator.empty());
    }

    SECTION("clip_id absent") {
        REQUIRE_FALSE(ctx.has_clip_id());
        REQUIRE_FALSE(ctx.clip_id().has_value());
    }

    SECTION("canvases count") {
        REQUIRE(ctx.canvases_count() == 1);
    }

    SECTION("to_json") {
        auto json = ctx.to_json(2);
        REQUIRE(json.find("Source") != std::string::npos);
        REQUIRE(json.find("CV_01") != std::string::npos);
    }
}

// -----------------------------------------------------------------------
// Canvas (mirrors Python TestCanvas)
// -----------------------------------------------------------------------

TEST_CASE("CanvasRef properties", "[raii][facade][canvas]") {
    auto doc = fdl::FDL::parse(MINIMAL_FDL_JSON);
    auto canvas = doc.context_at(0).canvas_at(0);

    SECTION("id and label") {
        REQUIRE(canvas.id() == "CV_01");
        REQUIRE(canvas.label() == "Source Canvas");
    }

    SECTION("source_canvas_id") {
        REQUIRE(canvas.source_canvas_id() == "CV_01");
    }

    SECTION("dimensions") {
        fdl::DimensionsInt dims = canvas.dimensions();
        REQUIRE(dims.width() == 3840);
        REQUIRE(dims.height() == 2160);
    }

    SECTION("anamorphic_squeeze") {
        REQUIRE(canvas.anamorphic_squeeze() == 1.0);
    }

    SECTION("optional fields not set") {
        REQUIRE_FALSE(canvas.has_effective_dimensions());
        REQUIRE_FALSE(canvas.has_effective_anchor_point());
        REQUIRE_FALSE(canvas.has_photosite_dimensions());
        REQUIRE_FALSE(canvas.has_physical_dimensions());
    }

    SECTION("framing_decisions count") {
        REQUIRE(canvas.framing_decisions_count() == 1);
    }

    SECTION("to_json") {
        auto json = canvas.to_json(2);
        REQUIRE(json.find("CV_01") != std::string::npos);
        REQUIRE(json.find("3840") != std::string::npos);
    }
}

// -----------------------------------------------------------------------
// FramingDecision (mirrors Python TestFramingDecision)
// -----------------------------------------------------------------------

TEST_CASE("FramingDecisionRef properties", "[raii][facade][framing_decision]") {
    auto doc = fdl::FDL::parse(MINIMAL_FDL_JSON);
    auto fd = doc.context_at(0).canvas_at(0).framing_decision_at(0);

    SECTION("id and label") {
        REQUIRE(fd.id() == "CV_01-FI_01");
        REQUIRE(fd.label() == "Default FD");
    }

    SECTION("framing_intent_id") {
        REQUIRE(fd.framing_intent_id() == "FI_01");
    }

    SECTION("dimensions") {
        fdl::DimensionsFloat dims = fd.dimensions();
        REQUIRE(dims.width() == Approx(3840.0));
        REQUIRE(dims.height() == Approx(2160.0));
    }

    SECTION("anchor_point") {
        fdl::PointFloat pt = fd.anchor_point();
        REQUIRE(pt.x() == Approx(0.0));
        REQUIRE(pt.y() == Approx(0.0));
    }

    SECTION("protection not set") {
        REQUIRE_FALSE(fd.has_protection_dimensions());
        REQUIRE_FALSE(fd.has_protection_anchor_point());
    }

    SECTION("to_json") {
        auto json = fd.to_json(2);
        REQUIRE(json.find("CV_01-FI_01") != std::string::npos);
        REQUIRE(json.find("3840") != std::string::npos);
    }
}

// -----------------------------------------------------------------------
// FramingIntent (mirrors Python TestFramingIntent)
// -----------------------------------------------------------------------

TEST_CASE("FramingIntentRef properties", "[raii][facade][framing_intent]") {
    auto doc = fdl::FDL::parse(MINIMAL_FDL_JSON);
    auto fi = doc.framing_intent_at(0);

    SECTION("id and label") {
        REQUIRE(fi.id() == "FI_01");
        REQUIRE(fi.label() == "Default");
    }

    SECTION("aspect_ratio") {
        fdl::DimensionsInt ar = fi.aspect_ratio();
        REQUIRE(ar.width() == 16);
        REQUIRE(ar.height() == 9);
    }

    SECTION("protection") {
        REQUIRE(fi.protection() == Approx(0.0));
    }

    SECTION("to_json") {
        auto json = fi.to_json(2);
        REQUIRE(json.find("FI_01") != std::string::npos);
    }
}

// -----------------------------------------------------------------------
// Serialization parity (mirrors Python TestModelDumpParity)
// -----------------------------------------------------------------------

TEST_CASE("Serialization parity", "[raii][facade][serialization]") {
    auto doc = fdl::FDL::parse(MINIMAL_FDL_JSON);

    SECTION("as_json contains expected fields") {
        auto json = doc.as_json(2);
        REQUIRE(json.find("\"uuid\"") != std::string::npos);
        REQUIRE(json.find("\"version\"") != std::string::npos);
        REQUIRE(json.find("\"fdl_creator\"") != std::string::npos);
        REQUIRE(json.find("\"contexts\"") != std::string::npos);
        REQUIRE(json.find("\"framing_intents\"") != std::string::npos);
    }

    SECTION("RAII as_json matches C API") {
        auto raii_json = doc.as_json(2);
        auto result = fdl_doc_parse_json(MINIMAL_FDL_JSON, std::strlen(MINIMAL_FDL_JSON));
        REQUIRE(result.doc != nullptr);
        char* c_json = fdl_doc_to_json(result.doc, 2);
        REQUIRE(std::string(c_json) == raii_json);
        fdl_free(c_json);
        fdl_doc_free(result.doc);
    }
}

// -----------------------------------------------------------------------
// FDL.create (mirrors Python TestDocumentCreate)
// -----------------------------------------------------------------------

TEST_CASE("FDL create from scratch", "[raii][facade][doc][create]") {
    SECTION("empty document") {
        auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");
        REQUIRE(doc.uuid() == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee");
        REQUIRE(doc.fdl_creator() == "test");
        REQUIRE(doc.version_major() == 2);
        REQUIRE(doc.version_minor() == 0);
        REQUIRE(doc.contexts_count() == 0);
        REQUIRE(doc.framing_intents_count() == 0);
        REQUIRE(doc.canvas_templates_count() == 0);
    }

    SECTION("with default framing intent") {
        auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test", "FI_01");
        REQUIRE(doc.default_framing_intent() == "FI_01");
    }
}

// -----------------------------------------------------------------------
// Property setters (mirrors Python TestPropertySetters)
// -----------------------------------------------------------------------

TEST_CASE("Property setters", "[raii][facade][doc][setters]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");

    SECTION("set_uuid") {
        doc.set_uuid("11111111-2222-3333-4444-555555555555");
        REQUIRE(doc.uuid() == "11111111-2222-3333-4444-555555555555");
    }

    SECTION("set_fdl_creator") {
        doc.set_fdl_creator("updated_creator");
        REQUIRE(doc.fdl_creator() == "updated_creator");
    }

    SECTION("set_default_framing_intent") {
        doc.set_default_framing_intent("FI_NEW");
        REQUIRE(doc.default_framing_intent() == "FI_NEW");
    }
}

// -----------------------------------------------------------------------
// Builder: add_framing_intent (mirrors Python TestAddFramingIntent)
// -----------------------------------------------------------------------

TEST_CASE("Builder: add_framing_intent", "[raii][facade][builder]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");

    SECTION("single framing intent") {
        auto fi = doc.add_framing_intent("FI_01", "Default", fdl_dimensions_i64_t{16, 9}, 0.0);
        REQUIRE(fi.id() == "FI_01");
        REQUIRE(fi.label() == "Default");
        fdl::DimensionsInt ar = fi.aspect_ratio();
        REQUIRE(ar.width() == 16);
        REQUIRE(ar.height() == 9);
        REQUIRE(fi.protection() == Approx(0.0));
        REQUIRE(doc.framing_intents_count() == 1);
    }

    SECTION("multiple framing intents") {
        doc.add_framing_intent("FI_01", "Default", fdl_dimensions_i64_t{16, 9}, 0.0);
        doc.add_framing_intent("FI_02", "Alt", fdl_dimensions_i64_t{4, 3}, 0.05);
        REQUIRE(doc.framing_intents_count() == 2);
        REQUIRE(doc.framing_intent_at(1).id() == "FI_02");
        REQUIRE(doc.framing_intent_at(1).protection() == Approx(0.05));
    }
}

// -----------------------------------------------------------------------
// Builder: add_context (mirrors Python TestAddContext)
// -----------------------------------------------------------------------

TEST_CASE("Builder: add_context", "[raii][facade][builder]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");

    SECTION("with creator") {
        auto ctx = doc.add_context("Source", "test");
        REQUIRE(ctx.label() == "Source");
        REQUIRE(ctx.context_creator() == "test");
        REQUIRE(doc.contexts_count() == 1);
    }

    SECTION("without creator") {
        auto ctx = doc.add_context("Source");
        REQUIRE(ctx.label() == "Source");
        REQUIRE(ctx.context_creator().empty());
    }
}

// -----------------------------------------------------------------------
// Builder: add_canvas (mirrors Python TestAddCanvas)
// -----------------------------------------------------------------------

TEST_CASE("Builder: add_canvas", "[raii][facade][builder]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");
    auto ctx = doc.add_context("Source");
    auto canvas = ctx.add_canvas("CV_01", "Source Canvas", "CV_01", fdl_dimensions_i64_t{3840, 2160}, 1.0);

    REQUIRE(canvas.id() == "CV_01");
    REQUIRE(canvas.label() == "Source Canvas");
    REQUIRE(canvas.source_canvas_id() == "CV_01");
    fdl::DimensionsInt dims = canvas.dimensions();
    REQUIRE(dims.width() == 3840);
    REQUIRE(dims.height() == 2160);
    REQUIRE(canvas.anamorphic_squeeze() == 1.0);
    REQUIRE(ctx.canvases_count() == 1);
}

// -----------------------------------------------------------------------
// Builder: add_framing_decision (mirrors Python TestAddFramingDecision)
// -----------------------------------------------------------------------

TEST_CASE("Builder: add_framing_decision", "[raii][facade][builder]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");
    doc.add_framing_intent("FI_01", "Default", fdl_dimensions_i64_t{16, 9}, 0.0);
    auto ctx = doc.add_context("Source");
    auto canvas = ctx.add_canvas("CV_01", "Source Canvas", "CV_01", fdl_dimensions_i64_t{3840, 2160}, 1.0);
    auto fd = canvas.add_framing_decision(
        "CV_01-FI_01", "Default FD", "FI_01", fdl_dimensions_f64_t{3840.0, 2160.0}, fdl_point_f64_t{0.0, 0.0});

    REQUIRE(fd.id() == "CV_01-FI_01");
    REQUIRE(fd.label() == "Default FD");
    REQUIRE(fd.framing_intent_id() == "FI_01");
    fdl::DimensionsFloat dims = fd.dimensions();
    REQUIRE(dims.width() == Approx(3840.0));
    REQUIRE(dims.height() == Approx(2160.0));
    fdl::PointFloat pt = fd.anchor_point();
    REQUIRE(pt.x() == Approx(0.0));
    REQUIRE(pt.y() == Approx(0.0));
    REQUIRE(canvas.framing_decisions_count() == 1);
}

// -----------------------------------------------------------------------
// Compound setters (mirrors Python TestCompoundSetters)
// -----------------------------------------------------------------------

TEST_CASE("Compound setters", "[raii][facade][setters]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");
    doc.add_framing_intent("FI_01", "Default", fdl_dimensions_i64_t{16, 9}, 0.05);
    auto ctx = doc.add_context("Source");
    auto canvas = ctx.add_canvas("CV_01", "Source", "CV_01", fdl_dimensions_i64_t{3840, 2160}, 1.0);

    SECTION("set_effective") {
        REQUIRE_FALSE(canvas.has_effective_dimensions());
        REQUIRE_FALSE(canvas.has_effective_anchor_point());

        canvas.set_effective(fdl_dimensions_i64_t{3000, 1688}, fdl_point_f64_t{420.0, 236.0});

        REQUIRE(canvas.has_effective_dimensions());
        fdl::DimensionsInt eff_dims = canvas.effective_dimensions().value();
        REQUIRE(eff_dims.width() == 3000);
        REQUIRE(eff_dims.height() == 1688);

        fdl::PointFloat eff_anchor = canvas.effective_anchor_point().value();
        REQUIRE(eff_anchor.x() == Approx(420.0));
        REQUIRE(eff_anchor.y() == Approx(236.0));
    }

    SECTION("set_protection") {
        auto fd = canvas.add_framing_decision(
            "CV_01-FI_01", "Default FD", "FI_01", fdl_dimensions_f64_t{3840.0, 2160.0}, fdl_point_f64_t{0.0, 0.0});

        REQUIRE_FALSE(fd.has_protection_dimensions());

        fd.set_protection(fdl_dimensions_f64_t{4032.0, 2268.0}, fdl_point_f64_t{-96.0, -54.0});

        REQUIRE(fd.has_protection_dimensions());
        fdl::DimensionsFloat prot_dims = fd.protection_dimensions().value();
        REQUIRE(prot_dims.width() == Approx(4032.0));
        REQUIRE(prot_dims.height() == Approx(2268.0));

        fdl::PointFloat prot_anchor = fd.protection_anchor_point().value();
        REQUIRE(prot_anchor.x() == Approx(-96.0));
        REQUIRE(prot_anchor.y() == Approx(-54.0));
    }
}

// -----------------------------------------------------------------------
// clip_id operations (mirrors Python TestContext clip_id tests)
// -----------------------------------------------------------------------

TEST_CASE("ContextRef clip_id", "[raii][facade][context][clip_id]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");
    auto ctx = doc.add_context("Source");

    SECTION("initially absent") {
        REQUIRE_FALSE(ctx.has_clip_id());
        REQUIRE_FALSE(ctx.clip_id().has_value());
    }

    SECTION("set via JSON and read back") {
        ctx.set_clip_id(R"({"clip_name": "A001", "file": "A001C001.ari"})");
        REQUIRE(ctx.has_clip_id());
        auto cid = ctx.clip_id();
        REQUIRE(cid.has_value());
        REQUIRE(cid->clip_name() == "A001");
        REQUIRE(cid->has_file());
        REQUIRE(cid->file().value() == "A001C001.ari");
        REQUIRE_FALSE(cid->has_sequence());
    }

    SECTION("set with file_sequence") {
        ctx.set_clip_id(R"({"clip_name":"B001","sequence":{"value":"B001.####.exr","idx":"#","min":0,"max":100}})");
        auto cid = ctx.clip_id();
        REQUIRE(cid.has_value());
        REQUIRE(cid->clip_name() == "B001");
        REQUIRE_FALSE(cid->has_file());
        REQUIRE(cid->has_sequence());
        auto seq = cid->sequence();
        REQUIRE(seq.has_value());
        REQUIRE(seq->value() == "B001.####.exr");
        REQUIRE(seq->idx() == "#");
        REQUIRE(seq->min() == 0);
        REQUIRE(seq->max() == 100);
    }

    SECTION("remove clip_id") {
        ctx.set_clip_id(R"({"clip_name":"A001","file":"A001C001.ari"})");
        REQUIRE(ctx.has_clip_id());
        ctx.remove_clip_id();
        REQUIRE_FALSE(ctx.has_clip_id());
    }
}

// -----------------------------------------------------------------------
// CanvasTemplate (mirrors Python TestCanvasTemplate)
// -----------------------------------------------------------------------

TEST_CASE("CanvasTemplate builders", "[raii][facade][canvas_template]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");

    SECTION("add canvas template") {
        auto ct = doc.add_canvas_template(
            "CT_01",
            "HD Delivery",
            fdl_dimensions_i64_t{1920, 1080},
            1.0,
            FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS,
            FDL_FIT_METHOD_WIDTH,
            FDL_HALIGN_CENTER,
            FDL_VALIGN_CENTER,
            fdl_round_strategy_t{FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND});

        REQUIRE(ct.id() == "CT_01");
        REQUIRE(ct.label() == "HD Delivery");
        fdl::DimensionsInt target_dims = ct.target_dimensions();
        REQUIRE(target_dims.width() == 1920);
        REQUIRE(target_dims.height() == 1080);
        REQUIRE(ct.target_anamorphic_squeeze() == 1.0);
        REQUIRE(doc.canvas_templates_count() == 1);
    }

    SECTION("optional properties") {
        auto ct = doc.add_canvas_template(
            "CT_01",
            "HD Delivery",
            fdl_dimensions_i64_t{1920, 1080},
            1.0,
            FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS,
            FDL_FIT_METHOD_WIDTH,
            FDL_HALIGN_CENTER,
            FDL_VALIGN_CENTER,
            fdl_round_strategy_t{FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND});

        REQUIRE_FALSE(ct.has_preserve_from_source_canvas());
        REQUIRE_FALSE(ct.has_maximum_dimensions());
        REQUIRE(ct.pad_to_maximum() == false);

        ct.set_preserve_from_source_canvas(FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS);
        ct.set_maximum_dimensions(fdl_dimensions_i64_t{4096, 2160});
        ct.set_pad_to_maximum(true);

        REQUIRE(ct.has_preserve_from_source_canvas());
        REQUIRE(ct.has_maximum_dimensions());
        fdl::DimensionsInt max_dims = ct.maximum_dimensions().value();
        REQUIRE(max_dims.width() == 4096);
        REQUIRE(max_dims.height() == 2160);
        REQUIRE(ct.pad_to_maximum() == true);
    }
}

// -----------------------------------------------------------------------
// CanvasTemplate apply (mirrors Python TestApplyCanvasTemplate)
// -----------------------------------------------------------------------

TEST_CASE("CanvasTemplate apply", "[raii][facade][canvas_template][apply]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test", "FI_01");
    doc.add_framing_intent("FI_01", "Default", fdl_dimensions_i64_t{16, 9}, 0.0);
    auto ctx = doc.add_context("Source", "test");
    auto canvas = ctx.add_canvas("CV_01", "Source Canvas", "CV_01", fdl_dimensions_i64_t{3840, 2160}, 1.0);
    auto fd = canvas.add_framing_decision(
        "CV_01-FI_01", "Default FD", "FI_01", fdl_dimensions_f64_t{3840.0, 2160.0}, fdl_point_f64_t{0.0, 0.0});
    auto ct = doc.add_canvas_template(
        "CT_01",
        "HD Delivery",
        fdl_dimensions_i64_t{1920, 1080},
        1.0,
        FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS,
        FDL_FIT_METHOD_WIDTH,
        FDL_HALIGN_CENTER,
        FDL_VALIGN_CENTER,
        fdl_round_strategy_t{FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND});

    auto result = ct.apply(canvas, fd, "CV_02", "HD FD", "Source", "test");

    REQUIRE(static_cast<bool>(result.fdl));
    // Verify the result FDL has the new canvas
    auto result_json = result.fdl.as_json(2);
    REQUIRE(result_json.find("CV_02") != std::string::npos);

    // Verify computed values are stored as custom attrs on the output canvas
    auto sf = result.canvas().get_custom_attr_float(fdl::ATTR_SCALE_FACTOR);
    REQUIRE(sf.has_value());
    REQUIRE(sf.value() == Approx(0.5));
}

// -----------------------------------------------------------------------
// populate_from_intent (mirrors Python from_framing_intent)
// -----------------------------------------------------------------------

TEST_CASE("FramingDecision from_framing_intent", "[raii][facade][framing]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test");
    doc.add_framing_intent("FI_01", "Default", fdl_dimensions_i64_t{16, 9}, 0.0);
    auto ctx = doc.add_context("Source");
    auto canvas = ctx.add_canvas("CV_01", "Source Canvas", "CV_01", fdl_dimensions_i64_t{3840, 2160}, 1.0);
    // Create FD with placeholder dims/anchor (will be overwritten)
    auto fd = canvas.add_framing_decision(
        "CV_01-FI_01", "Default FD", "FI_01", fdl_dimensions_f64_t{0.0, 0.0}, fdl_point_f64_t{0.0, 0.0});

    auto fi = doc.framing_intent_at(0);
    fdl_round_strategy_t rounding = {FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_ROUND};

    fd.from_framing_intent(canvas, fi, rounding);

    // Verify FD dimensions were populated from FI + canvas
    fdl::DimensionsFloat dims = fd.dimensions();
    REQUIRE(dims.width() > 0);
    REQUIRE(dims.height() > 0);
}

// -----------------------------------------------------------------------
// as_json after mutation (mirrors Python TestModelDumpAfterMutation)
// -----------------------------------------------------------------------

TEST_CASE("as_json after mutation", "[raii][facade][serialization]") {
    auto doc = fdl::FDL::create("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test", "FI_01");
    doc.add_framing_intent("FI_01", "Default", fdl_dimensions_i64_t{16, 9}, 0.0);
    auto ctx = doc.add_context("Source", "test");
    auto canvas = ctx.add_canvas("CV_01", "Source Canvas", "CV_01", fdl_dimensions_i64_t{3840, 2160}, 1.0);
    canvas.add_framing_decision(
        "CV_01-FI_01", "Default FD", "FI_01", fdl_dimensions_f64_t{3840.0, 2160.0}, fdl_point_f64_t{0.0, 0.0});

    auto json = doc.as_json(2);
    REQUIRE(json.find("\"uuid\"") != std::string::npos);
    REQUIRE(json.find("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") != std::string::npos);
    REQUIRE(json.find("\"fdl_creator\"") != std::string::npos);
    REQUIRE(json.find("FI_01") != std::string::npos);
    REQUIRE(json.find("CV_01") != std::string::npos);
    REQUIRE(json.find("CV_01-FI_01") != std::string::npos);

    // Roundtrip: as_json → parse → as_json should produce same result
    auto doc2 = fdl::FDL::parse(json);
    auto json2 = doc2.as_json(2);
    REQUIRE(json == json2);
}
