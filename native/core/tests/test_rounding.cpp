// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>
#include <jsoncons/json.hpp>

#include "fdl/fdl_core.h"

#include <fstream>
#include <string>

using json = jsoncons::ojson;

static fdl_rounding_mode_t parse_mode(const std::string& s) {
    if (s == "up") {
        return FDL_ROUNDING_MODE_UP;
    }
    if (s == "down") {
        return FDL_ROUNDING_MODE_DOWN;
    }
    return FDL_ROUNDING_MODE_ROUND;
}

static fdl_rounding_even_t parse_even(const std::string& s) {
    if (s == "even") {
        return FDL_ROUNDING_EVEN_EVEN;
    }
    return FDL_ROUNDING_EVEN_WHOLE;
}

TEST_CASE("fdl_round matches Python golden vectors", "[rounding]") {
    std::string path = std::string(VECTORS_DIR) + "/rounding/rounding_vectors.json";
    std::ifstream f(path);
    REQUIRE(f.is_open());

    json data = json::parse(f);
    auto& vectors = data["vectors"];

    for (size_t i = 0; i < vectors.size(); ++i) {
        auto& v = vectors[i];
        double value = v["input"]["value"].as<double>();
        auto mode = parse_mode(v["params"]["mode"].as<std::string>());
        auto even = parse_even(v["params"]["even"].as<std::string>());
        int64_t expected = v["expected"].as<int64_t>();

        CAPTURE(i, value, expected);
        int64_t actual = fdl_round(value, even, mode);
        REQUIRE(actual == expected);
    }
}

TEST_CASE("fdl_round_dimensions rounds both components", "[rounding]") {
    fdl_dimensions_f64_t dims = {19.456, 79.5};
    fdl_dimensions_f64_t result = fdl_round_dimensions(dims, FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_UP);
    REQUIRE(result.width == 20.0);
    REQUIRE(result.height == 80.0);
}

TEST_CASE("fdl_round_point rounds both components", "[rounding]") {
    fdl_point_f64_t point = {19.456, 79.5};
    fdl_point_f64_t result = fdl_round_point(point, FDL_ROUNDING_EVEN_EVEN, FDL_ROUNDING_MODE_UP);
    REQUIRE(result.x == 20.0);
    REQUIRE(result.y == 80.0);
}
