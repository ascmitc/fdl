// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>
#include <jsoncons/json.hpp>

#include "fdl/fdl_core.h"

#include <fstream>
#include <string>

using json = jsoncons::ojson;

static std::string to_compact(const json& j) {
    std::string s;
    j.dump(s);
    return s;
}

TEST_CASE("Schema validation catches structural errors", "[doc][schema]") {
    std::string path = std::string(VECTORS_DIR) + "/validation/schema_validation_vectors.json";
    std::ifstream f(path);
    REQUIRE(f.is_open());

    auto data = json::parse(f);
    auto& vectors = data["vectors"];

    for (size_t i = 0; i < vectors.size(); ++i) {
        auto& v = vectors[i];
        std::string label = v["label"].as<std::string>();
        auto expected_count = v["expected_error_count"].as<uint32_t>();
        CAPTURE(i, label, expected_count);

        std::string input_str = to_compact(v["input"]);
        auto parse_result = fdl_doc_parse_json(input_str.c_str(), input_str.size());
        REQUIRE(parse_result.doc != nullptr);

        auto* vr = fdl_doc_validate(parse_result.doc);
        REQUIRE(vr != nullptr);

        auto actual_count = fdl_validation_result_error_count(vr);
        CAPTURE(actual_count);

        // For error vectors, verify at least one error was found
        if (expected_count > 0) {
            REQUIRE(actual_count >= 1);

            // Verify all errors start with "Schema Error:" prefix
            for (uint32_t j = 0; j < actual_count; ++j) {
                const char* err = fdl_validation_result_error_at(vr, j);
                REQUIRE(err != nullptr);
                CAPTURE(j, err);
                REQUIRE(std::string(err).find("Schema Error:") == 0);
            }
        } else {
            REQUIRE(actual_count == 0);
        }

        fdl_validation_result_free(vr);
        fdl_doc_free(parse_result.doc);
    }
}
