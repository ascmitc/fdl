// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>
#include <jsoncons/json.hpp>

#include "fdl/fdl_core.h"

#include <fstream>
#include <string>
#include <vector>

using json = jsoncons::ojson;

static std::string to_compact(const json& j) {
    std::string s;
    j.dump(s);
    return s;
}

TEST_CASE("Semantic validation matches Python golden vectors", "[doc][validation]") {
    std::string path = std::string(VECTORS_DIR) + "/validation/validation_vectors.json";
    std::ifstream f(path);
    REQUIRE(f.is_open());

    auto data = json::parse(f);
    auto& vectors = data["vectors"];

    for (size_t i = 0; i < vectors.size(); ++i) {
        auto& v = vectors[i];
        std::string label = v["label"].as<std::string>();
        auto expected_count = v["expected_error_count"].as<uint32_t>();
        CAPTURE(i, label, expected_count);

        // Parse input
        std::string input_str = to_compact(v["input"]);
        auto parse_result = fdl_doc_parse_json(input_str.c_str(), input_str.size());
        REQUIRE(parse_result.doc != nullptr);

        // Validate
        auto* vr = fdl_doc_validate(parse_result.doc);
        REQUIRE(vr != nullptr);

        auto actual_count = fdl_validation_result_error_count(vr);
        CAPTURE(actual_count);
        REQUIRE(actual_count == expected_count);

        // Check error messages match exactly
        auto& expected_errors = v["expected_errors"];
        for (uint32_t j = 0; j < actual_count; ++j) {
            const char* actual_error = fdl_validation_result_error_at(vr, j);
            REQUIRE(actual_error != nullptr);

            std::string expected_error = expected_errors[j].as<std::string>();
            CAPTURE(j, expected_error, actual_error);
            REQUIRE(std::string(actual_error) == expected_error);
        }

        // Out-of-range returns NULL
        REQUIRE(fdl_validation_result_error_at(vr, actual_count) == nullptr);

        fdl_validation_result_free(vr);
        fdl_doc_free(parse_result.doc);
    }
}

TEST_CASE("Validation on NULL doc returns empty result", "[doc][validation]") {
    auto* vr = fdl_doc_validate(nullptr);
    REQUIRE(vr != nullptr);
    REQUIRE(fdl_validation_result_error_count(vr) == 0);
    fdl_validation_result_free(vr);
}

TEST_CASE("Validation result free with NULL is safe", "[doc][validation]") {
    fdl_validation_result_free(nullptr);
}
