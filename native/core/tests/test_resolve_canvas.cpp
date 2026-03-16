// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>

#include <fdl/fdl_core.h>

#include <cstring>

// Helper: build a minimal FDL doc with one context, two canvases, and framing decisions.
// canvas1 ("cvs1") is 1920x1080 with source_canvas_id="cvs1" (i.e. it IS the source).
// canvas2 ("cvs2") is 3840x2160 with source_canvas_id="cvs1" (derived from cvs1).
// Both have a framing decision with label "Main FI".
static fdl_doc_t* build_test_doc(
    fdl_context_t** out_ctx,
    fdl_canvas_t** out_cvs1,
    fdl_framing_decision_t** out_fd1,
    fdl_canvas_t** out_cvs2,
    fdl_framing_decision_t** out_fd2) {

    auto* doc = fdl_doc_create_with_header("00000000-0000-0000-0000-000000000001", 2, 0, "test", nullptr);
    REQUIRE(doc != nullptr);

    fdl_doc_add_framing_intent(doc, "fi_main", "Main FI", 16, 9, 0.0);

    auto* ctx = fdl_doc_add_context(doc, "ctx", "tester");
    REQUIRE(ctx != nullptr);

    // Canvas 1 -source canvas (id == source_canvas_id)
    auto* cvs1 = fdl_context_add_canvas(ctx, "cvs1", "Canvas 1920x1080", "cvs1", 1920, 1080, 1.0);
    REQUIRE(cvs1 != nullptr);

    auto* fd1 = fdl_canvas_add_framing_decision(cvs1, "cvs1-fi_main", "Main FI", "fi_main", 1920.0, 1080.0, 0.0, 0.0);
    REQUIRE(fd1 != nullptr);

    // Canvas 2 -derived canvas (source_canvas_id = "cvs1")
    auto* cvs2 = fdl_context_add_canvas(ctx, "cvs2", "Canvas 3840x2160", "cvs1", 3840, 2160, 1.0);
    REQUIRE(cvs2 != nullptr);

    auto* fd2 = fdl_canvas_add_framing_decision(cvs2, "cvs2-fi_main", "Main FI", "fi_main", 3840.0, 2160.0, 0.0, 0.0);
    REQUIRE(fd2 != nullptr);

    *out_ctx = ctx;
    *out_cvs1 = cvs1;
    *out_fd1 = fd1;
    *out_cvs2 = cvs2;
    *out_fd2 = fd2;
    return doc;
}

TEST_CASE("resolve_canvas_for_dimensions", "[resolve_canvas]") {
    fdl_context_t* ctx = nullptr;
    fdl_canvas_t* cvs1 = nullptr;
    fdl_framing_decision_t* fd1 = nullptr;
    fdl_canvas_t* cvs2 = nullptr;
    fdl_framing_decision_t* fd2 = nullptr;

    auto* doc = build_test_doc(&ctx, &cvs1, &fd1, &cvs2, &fd2);

    SECTION("exact match") {
        // Input dims match canvas2's own dimensions (3840x2160) -no resolution needed.
        fdl_dimensions_f64_t input = {3840.0, 2160.0};
        auto result = fdl_context_resolve_canvas_for_dimensions(ctx, input, cvs2, fd2);

        REQUIRE(result.error == nullptr);
        REQUIRE(result.was_resolved == 0);
        REQUIRE(result.canvas == cvs2);
        REQUIRE(result.framing_decision == fd2);
    }

    SECTION("resolution via sibling") {
        // Canvas2 is derived (id="cvs2", source_canvas_id="cvs1").
        // Input dims are 1920x1080, which match sibling canvas1.
        // The function should find cvs1 and its framing decision with the same label.
        fdl_dimensions_f64_t input = {1920.0, 1080.0};
        auto result = fdl_context_resolve_canvas_for_dimensions(ctx, input, cvs2, fd2);

        REQUIRE(result.error == nullptr);
        REQUIRE(result.was_resolved == 1);
        // The resolved canvas should have dimensions 1920x1080 (i.e. cvs1)
        REQUIRE(result.canvas != nullptr);
        REQUIRE(result.framing_decision != nullptr);
        // Verify we got a handle to the right canvas by checking its id
        REQUIRE(std::string(fdl_canvas_get_id(result.canvas)) == "cvs1");
        REQUIRE(std::string(fdl_framing_decision_get_id(result.framing_decision)) == "cvs1-fi_main");
    }

    SECTION("no match") {
        // Canvas2 is derived, but no sibling has 7680x4320 dimensions.
        fdl_dimensions_f64_t input = {7680.0, 4320.0};
        auto result = fdl_context_resolve_canvas_for_dimensions(ctx, input, cvs2, fd2);

        REQUIRE(result.was_resolved == 0);
        REQUIRE(result.error != nullptr);
        REQUIRE(std::strlen(result.error) > 0);
        // Clean up the caller-owned error string
        fdl_free(const_cast<char*>(result.error));
    }

    fdl_doc_free(doc);
}
