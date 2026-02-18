// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>

#include "fdl/fdl_core.h"

#include <atomic>
#include <cstring>
#include <functional>
#include <string>
#include <thread>
#include <vector>

static void run_in_parallel(int num_threads, std::function<void(int)> fn) {
    std::vector<std::thread> threads;
    for (int i = 0; i < num_threads; ++i) {
        threads.emplace_back(fn, i);
    }
    for (auto& t : threads) {
        t.join();
    }
}

// Build a complete FDL document for testing
static fdl_doc_t* make_test_doc() {
    auto* doc = fdl_doc_create_with_header("11111111-1111-1111-1111-111111111111", 2, 0, "thread-test", "FI_239");

    fdl_doc_add_framing_intent(doc, "FI_239", "2.39:1", 239, 100, 0.1);
    fdl_doc_add_framing_intent(doc, "FI_178", "1.78:1", 178, 100, 0.0);

    auto* ctx = fdl_doc_add_context(doc, "Camera Original", "test-creator");
    auto* cvs = fdl_context_add_canvas(ctx, "CVS_OPEN_GATE", "Open Gate", "CVS_OPEN_GATE", 4096, 3072, 1.0);

    fdl_canvas_set_effective_dimensions(cvs, {3840, 2160}, {128.0, 456.0});

    fdl_canvas_add_framing_decision(cvs, "FD_239", "2.39 FD", "FI_239", 3840.0, 1607.0, 0.0, 276.5);

    auto* fd2 = fdl_canvas_add_framing_decision(cvs, "FD_178", "1.78 FD", "FI_178", 3840.0, 2160.0, 0.0, 0.0);
    fdl_framing_decision_set_protection(fd2, {4000.0, 2250.0}, {-80.0, -45.0});

    return doc;
}

TEST_CASE("get_string buffer aliasing regression", "[thread]") {
    // Single-threaded: verify per-key buffers prevent aliasing
    auto* doc = make_test_doc();
    auto* ctx = fdl_doc_context_at(doc, 0);
    auto* cvs = fdl_context_canvas_at(ctx, 0);

    // Get two different string properties from the same canvas
    const char* id = fdl_canvas_get_id(cvs);
    const char* label = fdl_canvas_get_label(cvs);

    // With per-key buffers, these must be independent (different keys)
    REQUIRE(std::string(id) == "CVS_OPEN_GATE");
    REQUIRE(std::string(label) == "Open Gate");

    // Also test across handle types
    const char* ctx_label = fdl_context_get_label(ctx);
    REQUIRE(std::string(ctx_label) == "Camera Original");
    // Previous results must still be valid (different keys)
    REQUIRE(std::string(id) == "CVS_OPEN_GATE");
    REQUIRE(std::string(label) == "Open Gate");

    // Test FD accessors don't alias canvas accessors
    auto* fd = fdl_canvas_framing_decision_at(cvs, 0);
    const char* fd_id = fdl_framing_decision_get_id(fd);
    const char* fd_label = fdl_framing_decision_get_label(fd);
    const char* fd_fi_id = fdl_framing_decision_get_framing_intent_id(fd);

    REQUIRE(std::string(fd_id) == "FD_239");
    REQUIRE(std::string(fd_label) == "2.39 FD");
    REQUIRE(std::string(fd_fi_id) == "FI_239");

    fdl_doc_free(doc);
}

TEST_CASE("Concurrent reads on same document", "[thread]") {
    auto* doc = make_test_doc();
    std::atomic<int> errors{0};

    run_in_parallel(8, [&](int) {
        for (int iter = 0; iter < 100; ++iter) {
            // Read doc-level properties
            const char* uuid = fdl_doc_get_uuid(doc);
            if (!uuid || std::string(uuid) != "11111111-1111-1111-1111-111111111111") {
                errors.fetch_add(1);
            }

            const char* creator = fdl_doc_get_fdl_creator(doc);
            if (!creator || std::string(creator) != "thread-test") {
                errors.fetch_add(1);
            }

            // Read context properties
            auto* ctx = fdl_doc_context_at(doc, 0);
            if (!ctx) {
                errors.fetch_add(1);
                continue;
            }
            const char* ctx_label = fdl_context_get_label(ctx);
            if (!ctx_label || std::string(ctx_label) != "Camera Original") {
                errors.fetch_add(1);
            }

            // Read canvas properties
            auto* cvs = fdl_context_canvas_at(ctx, 0);
            if (!cvs) {
                errors.fetch_add(1);
                continue;
            }
            auto dims = fdl_canvas_get_dimensions(cvs);
            if (dims.width != 4096 || dims.height != 3072) {
                errors.fetch_add(1);
            }

            // Read FD properties
            auto* fd = fdl_canvas_framing_decision_at(cvs, 0);
            if (!fd) {
                errors.fetch_add(1);
                continue;
            }
            auto fd_dims = fdl_framing_decision_get_dimensions(fd);
            if (fd_dims.width != 3840.0 || fd_dims.height != 1607.0) {
                errors.fetch_add(1);
            }

            auto anchor = fdl_framing_decision_get_anchor_point(fd);
            if (anchor.x != 0.0 || anchor.y != 276.5) {
                errors.fetch_add(1);
            }
        }
    });

    REQUIRE(errors.load() == 0);
    fdl_doc_free(doc);
}

TEST_CASE("Concurrent reads on independent documents", "[thread]") {
    // Each thread parses, reads, and frees its own document
    std::atomic<int> errors{0};

    // Serialize the template doc to JSON for each thread to parse
    auto* src = make_test_doc();
    char* json = fdl_doc_to_json(src, 2);
    std::string json_str(json);
    fdl_free(json);
    fdl_doc_free(src);

    run_in_parallel(8, [&](int) {
        for (int iter = 0; iter < 50; ++iter) {
            auto pr = fdl_doc_parse_json(json_str.c_str(), json_str.size());
            if (!pr.doc) {
                errors.fetch_add(1);
                continue;
            }

            const char* uuid = fdl_doc_get_uuid(pr.doc);
            if (!uuid || std::string(uuid) != "11111111-1111-1111-1111-111111111111") {
                errors.fetch_add(1);
            }

            auto* ctx = fdl_doc_context_at(pr.doc, 0);
            auto* cvs = fdl_context_canvas_at(ctx, 0);
            auto dims = fdl_canvas_get_dimensions(cvs);
            if (dims.width != 4096 || dims.height != 3072) {
                errors.fetch_add(1);
            }

            fdl_doc_free(pr.doc);
        }
    });

    REQUIRE(errors.load() == 0);
}

TEST_CASE("Concurrent read + write on same document", "[thread]") {
    auto* doc = make_test_doc();
    std::atomic<int> errors{0};
    std::atomic<int> writes_done{0};

    // 4 readers + 2 writers
    auto reader = [&](int) {
        for (int iter = 0; iter < 100; ++iter) {
            auto* ctx = fdl_doc_context_at(doc, 0);
            if (!ctx) {
                continue;
            }
            auto* cvs = fdl_context_canvas_at(ctx, 0);
            if (!cvs) {
                continue;
            }

            auto dims = fdl_canvas_get_dimensions(cvs);
            // Dimensions must be valid (either original or modified)
            if (dims.width <= 0 || dims.height <= 0) {
                errors.fetch_add(1);
            }

            const char* uuid = fdl_doc_get_uuid(doc);
            if (!uuid) {
                errors.fetch_add(1);
            }
        }
    };

    auto writer = [&](int thread_id) {
        for (int iter = 0; iter < 50; ++iter) {
            std::string new_uuid = "22222222-2222-2222-2222-" + std::to_string(thread_id) + std::to_string(iter);
            // Pad to valid UUID length
            while (new_uuid.size() < 36) {
                new_uuid += "0";
            }
            fdl_doc_set_uuid(doc, new_uuid.c_str());
            writes_done.fetch_add(1);
        }
    };

    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back(reader, i);
    }
    for (int i = 0; i < 2; ++i) {
        threads.emplace_back(writer, i);
    }
    for (auto& t : threads) {
        t.join();
    }

    REQUIRE(errors.load() == 0);
    REQUIRE(writes_done.load() == 100);
    fdl_doc_free(doc);
}

TEST_CASE("Handle stability after collection mutation", "[thread]") {
    auto* doc = make_test_doc();

    // Get handles to existing elements
    auto* ctx0 = fdl_doc_context_at(doc, 0);
    auto* cvs0 = fdl_context_canvas_at(ctx0, 0);
    auto* fd0 = fdl_canvas_framing_decision_at(cvs0, 0);
    auto* fi0 = fdl_doc_framing_intent_at(doc, 0);

    // Record original values
    std::string orig_ctx_label(fdl_context_get_label(ctx0));
    std::string orig_cvs_id(fdl_canvas_get_id(cvs0));
    std::string orig_fd_id(fdl_framing_decision_get_id(fd0));
    std::string orig_fi_id(fdl_framing_intent_get_id(fi0));

    // Mutate collections (push_back can reallocate underlying arrays)
    fdl_doc_add_context(doc, "New Context 1", "creator");
    fdl_doc_add_context(doc, "New Context 2", "creator");
    fdl_doc_add_framing_intent(doc, "FI_NEW", "New FI", 16, 9, 0.0);

    auto* cvs_new = fdl_context_add_canvas(ctx0, "CVS_NEW", "New Canvas", "CVS_NEW", 1920, 1080, 1.0);
    fdl_canvas_add_framing_decision(cvs0, "FD_NEW", "New FD", "FI_239", 1920.0, 803.0, 0.0, 138.5);

    // Verify original handles still resolve correctly via node()
    REQUIRE(std::string(fdl_context_get_label(ctx0)) == orig_ctx_label);
    REQUIRE(std::string(fdl_canvas_get_id(cvs0)) == orig_cvs_id);
    REQUIRE(std::string(fdl_framing_decision_get_id(fd0)) == orig_fd_id);
    REQUIRE(std::string(fdl_framing_intent_get_id(fi0)) == orig_fi_id);

    // Verify original values unchanged
    auto dims0 = fdl_canvas_get_dimensions(cvs0);
    REQUIRE(dims0.width == 4096);
    REQUIRE(dims0.height == 3072);

    // Verify new elements are accessible
    REQUIRE(fdl_doc_contexts_count(doc) == 3);
    REQUIRE(fdl_doc_framing_intents_count(doc) == 3);
    REQUIRE(fdl_canvas_framing_decisions_count(cvs0) == 3);

    fdl_doc_free(doc);
}

TEST_CASE("Handle deduplication returns same pointer", "[thread]") {
    auto* doc = make_test_doc();

    // Same index should return same handle
    auto* ctx_a = fdl_doc_context_at(doc, 0);
    auto* ctx_b = fdl_doc_context_at(doc, 0);
    REQUIRE(ctx_a == ctx_b);

    auto* fi_a = fdl_doc_framing_intent_at(doc, 0);
    auto* fi_b = fdl_doc_framing_intent_at(doc, 0);
    REQUIRE(fi_a == fi_b);

    // Child handles too
    auto* cvs_a = fdl_context_canvas_at(ctx_a, 0);
    auto* cvs_b = fdl_context_canvas_at(ctx_b, 0);
    REQUIRE(cvs_a == cvs_b);

    auto* fd_a = fdl_canvas_framing_decision_at(cvs_a, 0);
    auto* fd_b = fdl_canvas_framing_decision_at(cvs_b, 0);
    REQUIRE(fd_a == fd_b);

    // find_by returns same handle as _at for same index
    auto* fi_c = fdl_doc_framing_intent_find_by_id(doc, "FI_239");
    REQUIRE(fi_c == fi_a);

    auto* ctx_c = fdl_doc_context_find_by_label(doc, "Camera Original");
    REQUIRE(ctx_c == ctx_a);

    auto* cvs_c = fdl_context_find_canvas_by_id(ctx_a, "CVS_OPEN_GATE");
    REQUIRE(cvs_c == cvs_a);

    auto* fd_c = fdl_canvas_find_framing_decision_by_id(cvs_a, "FD_239");
    REQUIRE(fd_c == fd_a);

    fdl_doc_free(doc);
}

TEST_CASE("Concurrent template apply", "[thread]") {
    auto* doc = make_test_doc();

    // Add a canvas template
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
        {FDL_ROUNDING_EVEN_WHOLE, FDL_ROUNDING_MODE_ROUND});

    auto* ctx = fdl_doc_context_at(doc, 0);
    auto* cvs = fdl_context_canvas_at(ctx, 0);
    auto* fd = fdl_canvas_framing_decision_at(cvs, 0);

    std::atomic<int> errors{0};

    // 4 threads each apply the template, producing independent output docs
    run_in_parallel(4, [&](int thread_id) {
        std::string new_id = "OUT_" + std::to_string(thread_id);
        auto result = fdl_apply_canvas_template(ct, cvs, fd, new_id.c_str(), "Test FD", "Camera Original", "test");

        if (result.error) {
            errors.fetch_add(1);
            fdl_free(const_cast<char*>(result.error));
            return;
        }
        if (!result.output_fdl) {
            errors.fetch_add(1);
            return;
        }

        // Verify output is valid
        auto out_ctx_count = fdl_doc_contexts_count(result.output_fdl);
        if (out_ctx_count != 1) {
            errors.fetch_add(1);
        }

        auto* out_ctx = fdl_doc_context_at(result.output_fdl, 0);
        auto out_cvs_count = fdl_context_canvases_count(out_ctx);
        if (out_cvs_count != 2) {
            errors.fetch_add(1);
        }

        auto* out_new_cvs = fdl_context_canvas_at(out_ctx, 1);
        double sf_out = 0.0;
        fdl_canvas_get_custom_attr_float(out_new_cvs, FDL_ATTR_SCALE_FACTOR, &sf_out);
        if (sf_out <= 0.0) {
            errors.fetch_add(1);
        }

        fdl_template_result_free(&result);
    });

    REQUIRE(errors.load() == 0);
    fdl_doc_free(doc);
}

TEST_CASE("Stress test: parse-mutate-serialize cycle", "[thread]") {
    std::atomic<int> errors{0};

    run_in_parallel(8, [&](int thread_id) {
        for (int iter = 0; iter < 50; ++iter) {
            // Create fresh doc
            std::string uuid = "aaaaaaaa-bbbb-cccc-dddd-" + std::to_string(thread_id) + std::to_string(iter);
            while (uuid.size() < 36) {
                uuid += "0";
            }

            auto* doc = fdl_doc_create_with_header(uuid.c_str(), 2, 0, "stress-test", nullptr);
            if (!doc) {
                errors.fetch_add(1);
                continue;
            }

            // Add content
            auto* ctx = fdl_doc_add_context(doc, "Ctx", "creator");
            auto* cvs = fdl_context_add_canvas(ctx, "CVS", "Canvas", "CVS", 1920, 1080, 1.0);
            fdl_canvas_add_framing_decision(cvs, "FD", "FD", "FI", 1920.0, 1080.0, 0.0, 0.0);

            // Serialize
            char* json = fdl_doc_to_json(doc, 0);
            if (!json) {
                errors.fetch_add(1);
                fdl_doc_free(doc);
                continue;
            }

            // Re-parse to verify
            auto pr = fdl_doc_parse_json(json, strlen(json));
            fdl_free(json);

            if (!pr.doc) {
                errors.fetch_add(1);
                if (pr.error) {
                    fdl_free(const_cast<char*>(pr.error));
                }
                fdl_doc_free(doc);
                continue;
            }

            // Verify content survived round-trip
            auto ctx_count = fdl_doc_contexts_count(pr.doc);
            if (ctx_count != 1) {
                errors.fetch_add(1);
            }

            fdl_doc_free(pr.doc);
            fdl_doc_free(doc);
        }
    });

    REQUIRE(errors.load() == 0);
}
