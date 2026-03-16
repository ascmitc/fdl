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

static std::string to_pretty(const json& j, int indent = 2) {
    std::string s;
    jsoncons::json_options opts;
    opts.indent_size(indent);
    j.dump_pretty(s, opts);
    return s;
}

TEST_CASE("Document roundtrip matches Python golden vectors", "[doc][roundtrip]") {
    std::string path = std::string(VECTORS_DIR) + "/document/roundtrip_vectors.json";
    std::ifstream f(path);
    REQUIRE(f.is_open());

    auto data = json::parse(f);
    auto& vectors = data["vectors"];

    for (size_t i = 0; i < vectors.size(); ++i) {
        auto& v = vectors[i];
        std::string label = v["label"].as<std::string>();
        CAPTURE(i, label);

        // Get input JSON and serialize it as compact string for parsing
        std::string input_str = to_compact(v["input"]);

        // Parse with C API
        auto result = fdl_doc_parse_json(input_str.c_str(), input_str.size());
        REQUIRE(result.doc != nullptr);
        REQUIRE(result.error == nullptr);

        // Serialize canonically
        char* output = fdl_doc_to_json(result.doc, 2);
        REQUIRE(output != nullptr);

        // Parse expected and actual as ordered_json for comparison
        auto expected = v["expected"];
        auto actual = json::parse(std::string(output));

        // Compare JSON objects structurally
        REQUIRE(actual == expected);

        // Also verify key ordering by comparing serialized strings
        std::string expected_str = to_pretty(expected);
        std::string actual_str = std::string(output);
        REQUIRE(actual_str == expected_str);

        fdl_free(output);
        fdl_doc_free(result.doc);
    }
}
