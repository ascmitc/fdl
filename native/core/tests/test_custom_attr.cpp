// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
//
// Tests for the custom attributes API (fdl_*_set/get/has/remove_custom_attr).
//
#include <catch2/catch_test_macros.hpp>

#include "fdl/fdl_core.h"

#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Read the custom_attrs_fixture.json test vector into a string.
static std::string load_fixture() {
    std::string path = std::string(VECTORS_DIR) + "/document/custom_attrs_fixture.json";
    std::ifstream ifs(path);
    REQUIRE(ifs.good());
    std::ostringstream ss;
    ss << ifs.rdbuf();
    return ss.str();
}

/// Create a minimal FDL document with one context, canvas, and framing decision.
static fdl_doc_t* make_doc() {
    fdl_doc_t* doc = fdl_doc_create_with_header("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", 2, 0, "test", nullptr);
    REQUIRE(doc != nullptr);

    fdl_framing_intent_t* fi = fdl_doc_add_framing_intent(doc, "FI_01", "Default", 16, 9, 0.0);
    REQUIRE(fi != nullptr);

    fdl_context_t* ctx = fdl_doc_add_context(doc, "Source", "test");
    REQUIRE(ctx != nullptr);

    fdl_canvas_t* cvs = fdl_context_add_canvas(ctx, "CV_01", "Source Canvas", "CV_01", 3840, 2160, 1.0);
    REQUIRE(cvs != nullptr);

    fdl_framing_decision_t* fd =
        fdl_canvas_add_framing_decision(cvs, "CV_01-FI_01", "Default FD", "FI_01", 3840.0, 2160.0, 0.0, 0.0);
    REQUIRE(fd != nullptr);

    return doc;
}

// ---------------------------------------------------------------------------
// Document-level custom attrs
// ---------------------------------------------------------------------------

TEST_CASE("Custom attrs CRUD on fdl_doc_t", "[custom_attr][doc]") {
    fdl_doc_t* doc = make_doc();

    SECTION("initially empty") {
        REQUIRE(fdl_doc_custom_attrs_count(doc) == 0);
        REQUIRE(fdl_doc_has_custom_attr(doc, "note") == 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "note") == FDL_CUSTOM_ATTR_TYPE_NONE);
    }

    SECTION("set and get string") {
        REQUIRE(fdl_doc_set_custom_attr_string(doc, "note", "hello") == 0);
        REQUIRE(fdl_doc_has_custom_attr(doc, "note") != 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "note") == FDL_CUSTOM_ATTR_TYPE_STRING);
        REQUIRE(std::string(fdl_doc_get_custom_attr_string(doc, "note")) == "hello");
        REQUIRE(fdl_doc_custom_attrs_count(doc) == 1);
        REQUIRE(std::string(fdl_doc_custom_attr_name_at(doc, 0)) == "note");
    }

    SECTION("set and get int") {
        REQUIRE(fdl_doc_set_custom_attr_int(doc, "count", 42) == 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "count") == FDL_CUSTOM_ATTR_TYPE_INT);
        int64_t val = 0;
        REQUIRE(fdl_doc_get_custom_attr_int(doc, "count", &val) == 0);
        REQUIRE(val == 42);
    }

    SECTION("set and get float") {
        REQUIRE(fdl_doc_set_custom_attr_float(doc, "ratio", 1.5) == 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "ratio") == FDL_CUSTOM_ATTR_TYPE_FLOAT);
        double val = 0.0;
        REQUIRE(fdl_doc_get_custom_attr_float(doc, "ratio", &val) == 0);
        REQUIRE(val == 1.5);
    }

    SECTION("set and get bool true") {
        REQUIRE(fdl_doc_set_custom_attr_bool(doc, "active", FDL_TRUE) == 0);
        REQUIRE(fdl_doc_has_custom_attr(doc, "active") != 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "active") == FDL_CUSTOM_ATTR_TYPE_BOOL);
        int val = 0;
        REQUIRE(fdl_doc_get_custom_attr_bool(doc, "active", &val) == 0);
        REQUIRE(val == FDL_TRUE);
        REQUIRE(fdl_doc_custom_attrs_count(doc) == 1);
    }

    SECTION("set and get bool false") {
        REQUIRE(fdl_doc_set_custom_attr_bool(doc, "disabled", FDL_FALSE) == 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "disabled") == FDL_CUSTOM_ATTR_TYPE_BOOL);
        int val = 1;
        REQUIRE(fdl_doc_get_custom_attr_bool(doc, "disabled", &val) == 0);
        REQUIRE(val == FDL_FALSE);
    }

    SECTION("update same type") {
        REQUIRE(fdl_doc_set_custom_attr_string(doc, "note", "first") == 0);
        REQUIRE(fdl_doc_set_custom_attr_string(doc, "note", "second") == 0);
        REQUIRE(std::string(fdl_doc_get_custom_attr_string(doc, "note")) == "second");
    }

    SECTION("type mismatch error") {
        REQUIRE(fdl_doc_set_custom_attr_int(doc, "x", 10) == 0);
        // Attempting to set as string should fail
        REQUIRE(fdl_doc_set_custom_attr_string(doc, "x", "nope") == -1);
        // Attempting to set as bool should fail
        REQUIRE(fdl_doc_set_custom_attr_bool(doc, "x", FDL_TRUE) == -1);
        // Original value preserved
        int64_t val = 0;
        REQUIRE(fdl_doc_get_custom_attr_int(doc, "x", &val) == 0);
        REQUIRE(val == 10);
    }

    SECTION("bool type mismatch") {
        REQUIRE(fdl_doc_set_custom_attr_bool(doc, "flag", FDL_TRUE) == 0);
        // Cannot overwrite bool with int, string, or float
        REQUIRE(fdl_doc_set_custom_attr_int(doc, "flag", 42) == -1);
        REQUIRE(fdl_doc_set_custom_attr_string(doc, "flag", "no") == -1);
        REQUIRE(fdl_doc_set_custom_attr_float(doc, "flag", 1.0) == -1);
        // Bool still true
        int bval = 0;
        REQUIRE(fdl_doc_get_custom_attr_bool(doc, "flag", &bval) == 0);
        REQUIRE(bval == FDL_TRUE);
    }

    SECTION("remove") {
        fdl_doc_set_custom_attr_string(doc, "tmp", "gone");
        REQUIRE(fdl_doc_custom_attrs_count(doc) == 1);
        REQUIRE(fdl_doc_remove_custom_attr(doc, "tmp") == 0);
        REQUIRE(fdl_doc_custom_attrs_count(doc) == 0);
        REQUIRE(fdl_doc_has_custom_attr(doc, "tmp") == 0);
        // Removing non-existent returns -1
        REQUIRE(fdl_doc_remove_custom_attr(doc, "tmp") == -1);
    }

    SECTION("get missing returns error") {
        REQUIRE(fdl_doc_get_custom_attr_string(doc, "nope") == nullptr);
        int64_t ival = 0;
        REQUIRE(fdl_doc_get_custom_attr_int(doc, "nope", &ival) == -1);
        double fval = 0.0;
        REQUIRE(fdl_doc_get_custom_attr_float(doc, "nope", &fval) == -1);
        int bval = 0;
        REQUIRE(fdl_doc_get_custom_attr_bool(doc, "nope", &bval) == -1);
    }

    SECTION("enumerate multiple attrs including bool") {
        fdl_doc_set_custom_attr_string(doc, "alpha", "a");
        fdl_doc_set_custom_attr_int(doc, "beta", 2);
        fdl_doc_set_custom_attr_float(doc, "gamma", 3.14);
        fdl_doc_set_custom_attr_bool(doc, "delta", FDL_TRUE);
        REQUIRE(fdl_doc_custom_attrs_count(doc) == 4);
    }

    fdl_doc_free(doc);
}

// ---------------------------------------------------------------------------
// Sub-handle custom attrs (context, canvas, FD, FI, canvas_template)
// ---------------------------------------------------------------------------

TEST_CASE("Custom attrs on context", "[custom_attr][context]") {
    fdl_doc_t* doc = make_doc();
    fdl_context_t* ctx = fdl_doc_context_at(doc, 0);
    REQUIRE(ctx != nullptr);

    REQUIRE(fdl_context_set_custom_attr_string(ctx, "shot", "A001") == 0);
    REQUIRE(fdl_context_has_custom_attr(ctx, "shot") != 0);
    REQUIRE(std::string(fdl_context_get_custom_attr_string(ctx, "shot")) == "A001");
    REQUIRE(fdl_context_custom_attrs_count(ctx) == 1);

    fdl_doc_free(doc);
}

TEST_CASE("Custom attrs on canvas", "[custom_attr][canvas]") {
    fdl_doc_t* doc = make_doc();
    fdl_context_t* ctx = fdl_doc_context_at(doc, 0);
    fdl_canvas_t* cvs = fdl_context_canvas_at(ctx, 0);
    REQUIRE(cvs != nullptr);

    REQUIRE(fdl_canvas_set_custom_attr_int(cvs, "layer", 5) == 0);
    int64_t val = 0;
    REQUIRE(fdl_canvas_get_custom_attr_int(cvs, "layer", &val) == 0);
    REQUIRE(val == 5);

    fdl_doc_free(doc);
}

TEST_CASE("Custom attrs on framing_decision", "[custom_attr][framing_decision]") {
    fdl_doc_t* doc = make_doc();
    fdl_context_t* ctx = fdl_doc_context_at(doc, 0);
    fdl_canvas_t* cvs = fdl_context_canvas_at(ctx, 0);
    fdl_framing_decision_t* fd = fdl_canvas_framing_decision_at(cvs, 0);
    REQUIRE(fd != nullptr);

    REQUIRE(fdl_framing_decision_set_custom_attr_float(fd, "weight", 0.75) == 0);
    double val = 0.0;
    REQUIRE(fdl_framing_decision_get_custom_attr_float(fd, "weight", &val) == 0);
    REQUIRE(val == 0.75);

    fdl_doc_free(doc);
}

TEST_CASE("Custom attrs on framing_intent", "[custom_attr][framing_intent]") {
    fdl_doc_t* doc = make_doc();
    fdl_framing_intent_t* fi = fdl_doc_framing_intent_at(doc, 0);
    REQUIRE(fi != nullptr);

    REQUIRE(fdl_framing_intent_set_custom_attr_string(fi, "origin", "camera") == 0);
    REQUIRE(std::string(fdl_framing_intent_get_custom_attr_string(fi, "origin")) == "camera");

    fdl_doc_free(doc);
}

TEST_CASE("Custom attrs on canvas_template", "[custom_attr][canvas_template]") {
    const char* json = R"({
        "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "version": {"major": 2, "minor": 0},
        "fdl_creator": "test",
        "framing_intents": [],
        "contexts": [],
        "canvas_templates": [
            {
                "label": "Test Template",
                "id": "CT_01",
                "target_dimensions": {"width": 3840, "height": 2160},
                "target_anamorphic_squeeze": 1.0,
                "fit_source": "field_of_view",
                "fit_method": "width",
                "alignment_method_vertical": "center",
                "alignment_method_horizontal": "center",
                "round_even_x": "even",
                "round_even_y": "even"
            }
        ]
    })";

    fdl_parse_result_t res = fdl_doc_parse_json(json, std::strlen(json));
    REQUIRE(res.error == nullptr);
    fdl_doc_t* doc = res.doc;

    fdl_canvas_template_t* ct = fdl_doc_canvas_template_at(doc, 0);
    REQUIRE(ct != nullptr);

    REQUIRE(fdl_canvas_template_set_custom_attr_string(ct, "vendor", "acme") == 0);
    REQUIRE(std::string(fdl_canvas_template_get_custom_attr_string(ct, "vendor")) == "acme");
    REQUIRE(fdl_canvas_template_custom_attrs_count(ct) == 1);

    fdl_doc_free(doc);
}

// ---------------------------------------------------------------------------
// ClipID and FileSequence custom attrs
// ---------------------------------------------------------------------------

TEST_CASE("Custom attrs on clip_id", "[custom_attr][clip_id]") {
    fdl_doc_t* doc = make_doc();
    fdl_context_t* ctx = fdl_doc_context_at(doc, 0);

    const char* cid_json = R"({"clip_name":"A001","file":"A001C001.ari"})";
    REQUIRE(fdl_context_set_clip_id_json(ctx, cid_json, std::strlen(cid_json)) == nullptr);
    fdl_clip_id_t* cid = fdl_context_clip_id(ctx);
    REQUIRE(cid != nullptr);

    REQUIRE(fdl_clip_id_set_custom_attr_string(cid, "reel", "A001") == 0);
    REQUIRE(fdl_clip_id_has_custom_attr(cid, "reel") != 0);
    REQUIRE(std::string(fdl_clip_id_get_custom_attr_string(cid, "reel")) == "A001");
    REQUIRE(fdl_clip_id_custom_attrs_count(cid) == 1);

    fdl_doc_free(doc);
}

TEST_CASE("Custom attrs on file_sequence", "[custom_attr][file_sequence]") {
    fdl_doc_t* doc = make_doc();
    fdl_context_t* ctx = fdl_doc_context_at(doc, 0);

    const char* cid_json = R"({"clip_name":"B001","sequence":{"value":"B001.####.exr","idx":"#","min":0,"max":100}})";
    REQUIRE(fdl_context_set_clip_id_json(ctx, cid_json, std::strlen(cid_json)) == nullptr);
    fdl_clip_id_t* cid = fdl_context_clip_id(ctx);
    REQUIRE(cid != nullptr);
    fdl_file_sequence_t* seq = fdl_clip_id_sequence(cid);
    REQUIRE(seq != nullptr);

    REQUIRE(fdl_file_sequence_set_custom_attr_int(seq, "fps", 24) == 0);
    int64_t val = 0;
    REQUIRE(fdl_file_sequence_get_custom_attr_int(seq, "fps", &val) == 0);
    REQUIRE(val == 24);
    REQUIRE(fdl_file_sequence_custom_attrs_count(seq) == 1);

    fdl_doc_free(doc);
}

// ---------------------------------------------------------------------------
// Roundtrip preservation
// ---------------------------------------------------------------------------

TEST_CASE("Custom attrs survive parse-serialize roundtrip", "[custom_attr][roundtrip]") {
    std::string json = load_fixture();

    fdl_parse_result_t res = fdl_doc_parse_json(json.c_str(), json.size());
    REQUIRE(res.error == nullptr);
    fdl_doc_t* doc = res.doc;

    // Verify pre-existing custom attrs from fixture
    REQUIRE(fdl_doc_has_custom_attr(doc, "vendor_note") != 0);
    REQUIRE(std::string(fdl_doc_get_custom_attr_string(doc, "vendor_note")) == "This is a doc-level custom attr");
    REQUIRE(fdl_doc_get_custom_attr_type(doc, "vendor_count") == FDL_CUSTOM_ATTR_TYPE_INT);
    int64_t count = 0;
    fdl_doc_get_custom_attr_int(doc, "vendor_count", &count);
    REQUIRE(count == 42);

    fdl_framing_intent_t* fi = fdl_doc_framing_intent_at(doc, 0);
    REQUIRE(std::string(fdl_framing_intent_get_custom_attr_string(fi, "fi_tag")) == "intent-custom");

    fdl_context_t* ctx = fdl_doc_context_at(doc, 0);
    int64_t pri = 0;
    fdl_context_get_custom_attr_int(ctx, "ctx_priority", &pri);
    REQUIRE(pri == 1);

    fdl_canvas_t* cvs = fdl_context_canvas_at(ctx, 0);
    REQUIRE(std::string(fdl_canvas_get_custom_attr_string(cvs, "canvas_vendor")) == "test-tool");

    fdl_framing_decision_t* fd = fdl_canvas_framing_decision_at(cvs, 0);
    REQUIRE(std::string(fdl_framing_decision_get_custom_attr_string(fd, "fd_note")) == "hero framing");

    // Verify clip_id custom attrs
    fdl_clip_id_t* cid = fdl_context_clip_id(ctx);
    REQUIRE(cid != nullptr);
    REQUIRE(std::string(fdl_clip_id_get_custom_attr_string(cid, "cid_reel")) == "reel_A");

    // Serialize and re-parse
    char* out_json = fdl_doc_to_json(doc, 2);
    REQUIRE(out_json != nullptr);
    std::string serialized(out_json);
    fdl_free(out_json);

    fdl_parse_result_t res2 = fdl_doc_parse_json(serialized.c_str(), serialized.size());
    REQUIRE(res2.error == nullptr);
    fdl_doc_t* doc2 = res2.doc;

    // Verify all attrs survived roundtrip
    REQUIRE(std::string(fdl_doc_get_custom_attr_string(doc2, "vendor_note")) == "This is a doc-level custom attr");

    fdl_framing_intent_t* fi2 = fdl_doc_framing_intent_at(doc2, 0);
    REQUIRE(std::string(fdl_framing_intent_get_custom_attr_string(fi2, "fi_tag")) == "intent-custom");

    fdl_context_t* ctx2 = fdl_doc_context_at(doc2, 0);
    fdl_canvas_t* cvs2 = fdl_context_canvas_at(ctx2, 0);
    REQUIRE(std::string(fdl_canvas_get_custom_attr_string(cvs2, "canvas_vendor")) == "test-tool");

    fdl_clip_id_t* cid2 = fdl_context_clip_id(ctx2);
    REQUIRE(cid2 != nullptr);
    REQUIRE(std::string(fdl_clip_id_get_custom_attr_string(cid2, "cid_reel")) == "reel_A");

    fdl_doc_free(doc2);
    fdl_doc_free(doc);
}

TEST_CASE("Add custom attrs then roundtrip", "[custom_attr][roundtrip]") {
    fdl_doc_t* doc = make_doc();

    // Add custom attrs on every object type
    fdl_doc_set_custom_attr_string(doc, "tool", "test-suite");
    fdl_doc_set_custom_attr_int(doc, "version_num", 1);
    fdl_doc_set_custom_attr_float(doc, "scale", 2.5);
    fdl_doc_set_custom_attr_bool(doc, "approved", FDL_TRUE);

    fdl_context_t* ctx = fdl_doc_context_at(doc, 0);
    fdl_context_set_custom_attr_string(ctx, "note", "ctx-note");

    fdl_canvas_t* cvs = fdl_context_canvas_at(ctx, 0);
    fdl_canvas_set_custom_attr_int(cvs, "order", 1);

    fdl_framing_decision_t* fd = fdl_canvas_framing_decision_at(cvs, 0);
    fdl_framing_decision_set_custom_attr_float(fd, "confidence", 0.95);

    fdl_framing_intent_t* fi = fdl_doc_framing_intent_at(doc, 0);
    fdl_framing_intent_set_custom_attr_string(fi, "source", "director");

    // Add clip_id with custom attrs
    const char* cid_json = R"({"clip_name":"A001","file":"A001.ari"})";
    fdl_context_set_clip_id_json(ctx, cid_json, std::strlen(cid_json));
    fdl_clip_id_t* cid = fdl_context_clip_id(ctx);
    REQUIRE(cid != nullptr);
    fdl_clip_id_set_custom_attr_string(cid, "reel", "reel_A");

    // Serialize
    char* json = fdl_doc_to_json(doc, 2);
    REQUIRE(json != nullptr);
    std::string serialized(json);
    fdl_free(json);

    // Re-parse and verify
    fdl_parse_result_t res = fdl_doc_parse_json(serialized.c_str(), serialized.size());
    REQUIRE(res.error == nullptr);
    fdl_doc_t* doc2 = res.doc;

    REQUIRE(std::string(fdl_doc_get_custom_attr_string(doc2, "tool")) == "test-suite");
    int64_t ver = 0;
    fdl_doc_get_custom_attr_int(doc2, "version_num", &ver);
    REQUIRE(ver == 1);
    double sc = 0;
    fdl_doc_get_custom_attr_float(doc2, "scale", &sc);
    REQUIRE(sc == 2.5);
    int approved = 0;
    fdl_doc_get_custom_attr_bool(doc2, "approved", &approved);
    REQUIRE(approved == FDL_TRUE);
    REQUIRE(fdl_doc_get_custom_attr_type(doc2, "approved") == FDL_CUSTOM_ATTR_TYPE_BOOL);

    fdl_context_t* ctx2 = fdl_doc_context_at(doc2, 0);
    REQUIRE(std::string(fdl_context_get_custom_attr_string(ctx2, "note")) == "ctx-note");

    fdl_canvas_t* cvs2 = fdl_context_canvas_at(ctx2, 0);
    int64_t ord = 0;
    fdl_canvas_get_custom_attr_int(cvs2, "order", &ord);
    REQUIRE(ord == 1);

    fdl_framing_decision_t* fd2 = fdl_canvas_framing_decision_at(cvs2, 0);
    double conf = 0;
    fdl_framing_decision_get_custom_attr_float(fd2, "confidence", &conf);
    REQUIRE(conf == 0.95);

    fdl_framing_intent_t* fi2 = fdl_doc_framing_intent_at(doc2, 0);
    REQUIRE(std::string(fdl_framing_intent_get_custom_attr_string(fi2, "source")) == "director");

    fdl_clip_id_t* cid2 = fdl_context_clip_id(ctx2);
    REQUIRE(cid2 != nullptr);
    REQUIRE(std::string(fdl_clip_id_get_custom_attr_string(cid2, "reel")) == "reel_A");

    fdl_doc_free(doc2);
    fdl_doc_free(doc);
}

// ---------------------------------------------------------------------------
// Composite type custom attrs (PointFloat, DimensionsFloat, DimensionsInt)
// ---------------------------------------------------------------------------

TEST_CASE("Custom attrs composite point_f64 on fdl_doc_t", "[custom_attr][composite][doc]") {
    fdl_doc_t* doc = make_doc();

    SECTION("set and get point_f64") {
        fdl_point_f64_t pt{128.5, 276.0};
        REQUIRE(fdl_doc_set_custom_attr_point_f64(doc, "origin", pt) == 0);
        REQUIRE(fdl_doc_has_custom_attr(doc, "origin") != 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "origin") == FDL_CUSTOM_ATTR_TYPE_POINT_F64);
        REQUIRE(fdl_doc_custom_attrs_count(doc) == 1);
        REQUIRE(std::string(fdl_doc_custom_attr_name_at(doc, 0)) == "origin");

        fdl_point_f64_t out{};
        REQUIRE(fdl_doc_get_custom_attr_point_f64(doc, "origin", &out) == 0);
        REQUIRE(out.x == 128.5);
        REQUIRE(out.y == 276.0);
    }

    SECTION("set and get zero point") {
        fdl_point_f64_t pt{0.0, 0.0};
        REQUIRE(fdl_doc_set_custom_attr_point_f64(doc, "zero_pt", pt) == 0);
        fdl_point_f64_t out{};
        REQUIRE(fdl_doc_get_custom_attr_point_f64(doc, "zero_pt", &out) == 0);
        REQUIRE(out.x == 0.0);
        REQUIRE(out.y == 0.0);
    }

    SECTION("update point_f64 same type") {
        fdl_point_f64_t pt1{1.0, 2.0};
        REQUIRE(fdl_doc_set_custom_attr_point_f64(doc, "pos", pt1) == 0);
        fdl_point_f64_t pt2{3.0, 4.0};
        REQUIRE(fdl_doc_set_custom_attr_point_f64(doc, "pos", pt2) == 0);
        fdl_point_f64_t out{};
        REQUIRE(fdl_doc_get_custom_attr_point_f64(doc, "pos", &out) == 0);
        REQUIRE(out.x == 3.0);
        REQUIRE(out.y == 4.0);
    }

    SECTION("get missing point returns error") {
        fdl_point_f64_t out{};
        REQUIRE(fdl_doc_get_custom_attr_point_f64(doc, "missing", &out) == -1);
    }

    fdl_doc_free(doc);
}

TEST_CASE("Custom attrs composite dims_f64 on fdl_doc_t", "[custom_attr][composite][doc]") {
    fdl_doc_t* doc = make_doc();

    SECTION("set and get dims_f64") {
        fdl_dimensions_f64_t dims{3840.0, 2160.0};
        REQUIRE(fdl_doc_set_custom_attr_dims_f64(doc, "bounding_box", dims) == 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "bounding_box") == FDL_CUSTOM_ATTR_TYPE_DIMS_F64);

        fdl_dimensions_f64_t out{};
        REQUIRE(fdl_doc_get_custom_attr_dims_f64(doc, "bounding_box", &out) == 0);
        REQUIRE(out.width == 3840.0);
        REQUIRE(out.height == 2160.0);
    }

    SECTION("update dims_f64") {
        fdl_dimensions_f64_t d1{1920.0, 1080.0};
        REQUIRE(fdl_doc_set_custom_attr_dims_f64(doc, "box", d1) == 0);
        fdl_dimensions_f64_t d2{3840.0, 2160.0};
        REQUIRE(fdl_doc_set_custom_attr_dims_f64(doc, "box", d2) == 0);
        fdl_dimensions_f64_t out{};
        REQUIRE(fdl_doc_get_custom_attr_dims_f64(doc, "box", &out) == 0);
        REQUIRE(out.width == 3840.0);
        REQUIRE(out.height == 2160.0);
    }

    fdl_doc_free(doc);
}

TEST_CASE("Custom attrs composite dims_i64 on fdl_doc_t", "[custom_attr][composite][doc]") {
    fdl_doc_t* doc = make_doc();

    SECTION("set and get dims_i64") {
        fdl_dimensions_i64_t dims{3840, 2160};
        REQUIRE(fdl_doc_set_custom_attr_dims_i64(doc, "resolution", dims) == 0);
        REQUIRE(fdl_doc_get_custom_attr_type(doc, "resolution") == FDL_CUSTOM_ATTR_TYPE_DIMS_I64);

        fdl_dimensions_i64_t out{};
        REQUIRE(fdl_doc_get_custom_attr_dims_i64(doc, "resolution", &out) == 0);
        REQUIRE(out.width == 3840);
        REQUIRE(out.height == 2160);
    }

    fdl_doc_free(doc);
}

TEST_CASE("Composite type mismatch between composite types", "[custom_attr][composite][mismatch]") {
    fdl_doc_t* doc = make_doc();

    // Set as point, try to overwrite with dims
    fdl_point_f64_t pt{1.0, 2.0};
    REQUIRE(fdl_doc_set_custom_attr_point_f64(doc, "attr", pt) == 0);

    fdl_dimensions_f64_t df{100.0, 200.0};
    REQUIRE(fdl_doc_set_custom_attr_dims_f64(doc, "attr", df) == -1);

    fdl_dimensions_i64_t di{100, 200};
    REQUIRE(fdl_doc_set_custom_attr_dims_i64(doc, "attr", di) == -1);

    // Original point preserved
    fdl_point_f64_t out{};
    REQUIRE(fdl_doc_get_custom_attr_point_f64(doc, "attr", &out) == 0);
    REQUIRE(out.x == 1.0);
    REQUIRE(out.y == 2.0);

    fdl_doc_free(doc);
}

TEST_CASE("Composite type mismatch between dims_f64 and dims_i64", "[custom_attr][composite][mismatch]") {
    fdl_doc_t* doc = make_doc();

    fdl_dimensions_f64_t df{100.0, 200.0};
    REQUIRE(fdl_doc_set_custom_attr_dims_f64(doc, "dims", df) == 0);

    fdl_dimensions_i64_t di{100, 200};
    REQUIRE(fdl_doc_set_custom_attr_dims_i64(doc, "dims", di) == -1);

    // Original dims_f64 preserved
    fdl_dimensions_f64_t out{};
    REQUIRE(fdl_doc_get_custom_attr_dims_f64(doc, "dims", &out) == 0);
    REQUIRE(out.width == 100.0);

    fdl_doc_free(doc);
}

TEST_CASE("Composite type mismatch with scalar types", "[custom_attr][composite][mismatch]") {
    fdl_doc_t* doc = make_doc();

    // Scalar -> composite mismatch
    REQUIRE(fdl_doc_set_custom_attr_float(doc, "val", 1.5) == 0);
    fdl_point_f64_t pt{1.0, 2.0};
    REQUIRE(fdl_doc_set_custom_attr_point_f64(doc, "val", pt) == -1);
    fdl_dimensions_f64_t df{1.0, 2.0};
    REQUIRE(fdl_doc_set_custom_attr_dims_f64(doc, "val", df) == -1);

    // Composite -> scalar mismatch
    fdl_point_f64_t pt2{3.0, 4.0};
    REQUIRE(fdl_doc_set_custom_attr_point_f64(doc, "pt", pt2) == 0);
    REQUIRE(fdl_doc_set_custom_attr_float(doc, "pt", 5.0) == -1);
    REQUIRE(fdl_doc_set_custom_attr_int(doc, "pt", 5) == -1);
    REQUIRE(fdl_doc_set_custom_attr_string(doc, "pt", "nope") == -1);
    REQUIRE(fdl_doc_set_custom_attr_bool(doc, "pt", FDL_TRUE) == -1);

    fdl_doc_free(doc);
}

TEST_CASE("Composite attrs enumerate with count and name_at", "[custom_attr][composite][enumerate]") {
    fdl_doc_t* doc = make_doc();

    fdl_doc_set_custom_attr_string(doc, "alpha", "a");
    fdl_point_f64_t pt{1.0, 2.0};
    fdl_doc_set_custom_attr_point_f64(doc, "beta", pt);
    fdl_dimensions_f64_t df{3.0, 4.0};
    fdl_doc_set_custom_attr_dims_f64(doc, "gamma", df);
    fdl_dimensions_i64_t di{5, 6};
    fdl_doc_set_custom_attr_dims_i64(doc, "delta", di);

    REQUIRE(fdl_doc_custom_attrs_count(doc) == 4);

    // Verify all names are accessible via name_at
    bool found_alpha = false, found_beta = false, found_gamma = false, found_delta = false;
    for (uint32_t i = 0; i < 4; ++i) {
        std::string name = fdl_doc_custom_attr_name_at(doc, i);
        if (name == "alpha") {
            found_alpha = true;
        }
        if (name == "beta") {
            found_beta = true;
        }
        if (name == "gamma") {
            found_gamma = true;
        }
        if (name == "delta") {
            found_delta = true;
        }
    }
    REQUIRE(found_alpha);
    REQUIRE(found_beta);
    REQUIRE(found_gamma);
    REQUIRE(found_delta);

    fdl_doc_free(doc);
}

TEST_CASE("Composite attrs remove", "[custom_attr][composite]") {
    fdl_doc_t* doc = make_doc();

    fdl_point_f64_t pt{1.0, 2.0};
    fdl_doc_set_custom_attr_point_f64(doc, "pos", pt);
    REQUIRE(fdl_doc_custom_attrs_count(doc) == 1);
    REQUIRE(fdl_doc_remove_custom_attr(doc, "pos") == 0);
    REQUIRE(fdl_doc_custom_attrs_count(doc) == 0);
    REQUIRE(fdl_doc_has_custom_attr(doc, "pos") == 0);

    fdl_doc_free(doc);
}

TEST_CASE("Composite attrs roundtrip through JSON", "[custom_attr][composite][roundtrip]") {
    fdl_doc_t* doc = make_doc();

    fdl_point_f64_t pt{128.5, 276.0};
    fdl_doc_set_custom_attr_point_f64(doc, "translation", pt);
    fdl_dimensions_f64_t df{3840.0, 2160.0};
    fdl_doc_set_custom_attr_dims_f64(doc, "bounding_box", df);
    fdl_dimensions_i64_t di{1920, 1080};
    fdl_doc_set_custom_attr_dims_i64(doc, "resolution", di);
    fdl_doc_set_custom_attr_float(doc, "scale", 0.5);

    // Serialize
    char* json = fdl_doc_to_json(doc, 2);
    REQUIRE(json != nullptr);
    std::string serialized(json);
    fdl_free(json);

    // Re-parse
    fdl_parse_result_t res = fdl_doc_parse_json(serialized.c_str(), serialized.size());
    REQUIRE(res.error == nullptr);
    fdl_doc_t* doc2 = res.doc;

    // Verify composite attrs survived roundtrip
    REQUIRE(fdl_doc_get_custom_attr_type(doc2, "translation") == FDL_CUSTOM_ATTR_TYPE_POINT_F64);
    fdl_point_f64_t pt_out{};
    REQUIRE(fdl_doc_get_custom_attr_point_f64(doc2, "translation", &pt_out) == 0);
    REQUIRE(pt_out.x == 128.5);
    REQUIRE(pt_out.y == 276.0);

    REQUIRE(fdl_doc_get_custom_attr_type(doc2, "bounding_box") == FDL_CUSTOM_ATTR_TYPE_DIMS_F64);
    fdl_dimensions_f64_t df_out{};
    REQUIRE(fdl_doc_get_custom_attr_dims_f64(doc2, "bounding_box", &df_out) == 0);
    REQUIRE(df_out.width == 3840.0);
    REQUIRE(df_out.height == 2160.0);

    REQUIRE(fdl_doc_get_custom_attr_type(doc2, "resolution") == FDL_CUSTOM_ATTR_TYPE_DIMS_I64);
    fdl_dimensions_i64_t di_out{};
    REQUIRE(fdl_doc_get_custom_attr_dims_i64(doc2, "resolution", &di_out) == 0);
    REQUIRE(di_out.width == 1920);
    REQUIRE(di_out.height == 1080);

    double scale = 0.0;
    REQUIRE(fdl_doc_get_custom_attr_float(doc2, "scale", &scale) == 0);
    REQUIRE(scale == 0.5);

    fdl_doc_free(doc2);
    fdl_doc_free(doc);
}

TEST_CASE("Composite attrs on sub-handle types", "[custom_attr][composite][subhandle]") {
    fdl_doc_t* doc = make_doc();
    fdl_context_t* ctx = fdl_doc_context_at(doc, 0);
    fdl_canvas_t* cvs = fdl_context_canvas_at(ctx, 0);
    fdl_framing_decision_t* fd = fdl_canvas_framing_decision_at(cvs, 0);

    // Context
    fdl_point_f64_t pt{10.0, 20.0};
    REQUIRE(fdl_context_set_custom_attr_point_f64(ctx, "offset", pt) == 0);
    fdl_point_f64_t ctx_out{};
    REQUIRE(fdl_context_get_custom_attr_point_f64(ctx, "offset", &ctx_out) == 0);
    REQUIRE(ctx_out.x == 10.0);
    REQUIRE(ctx_out.y == 20.0);

    // Canvas
    fdl_dimensions_f64_t df{1920.5, 1080.5};
    REQUIRE(fdl_canvas_set_custom_attr_dims_f64(cvs, "box", df) == 0);
    fdl_dimensions_f64_t cvs_out{};
    REQUIRE(fdl_canvas_get_custom_attr_dims_f64(cvs, "box", &cvs_out) == 0);
    REQUIRE(cvs_out.width == 1920.5);
    REQUIRE(cvs_out.height == 1080.5);

    // FramingDecision
    fdl_dimensions_i64_t di{3840, 2160};
    REQUIRE(fdl_framing_decision_set_custom_attr_dims_i64(fd, "target_res", di) == 0);
    fdl_dimensions_i64_t fd_out{};
    REQUIRE(fdl_framing_decision_get_custom_attr_dims_i64(fd, "target_res", &fd_out) == 0);
    REQUIRE(fd_out.width == 3840);
    REQUIRE(fd_out.height == 2160);

    fdl_doc_free(doc);
}
