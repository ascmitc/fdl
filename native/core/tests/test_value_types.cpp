// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>
#include <jsoncons/json.hpp>

#include "fdl/fdl_core.h"

#include <fstream>
#include <string>

using json = jsoncons::ojson;
using Catch::Matchers::WithinAbs;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

static void require_dims_close(fdl_dimensions_f64_t actual, fdl_dimensions_f64_t expected) {
    REQUIRE(fdl_dimensions_equal(actual, expected) == 1);
}

static void require_point_close(fdl_point_f64_t actual, fdl_point_f64_t expected) {
    REQUIRE(fdl_point_equal(actual, expected) == 1);
}

// ---------------------------------------------------------------------------
// Dimensions math vectors
// ---------------------------------------------------------------------------

TEST_CASE("Dimensions math matches Python golden vectors", "[value_types][dimensions]") {
    std::string path = std::string(VECTORS_DIR) + "/value_types/dimensions_math_vectors.json";
    std::ifstream f(path);
    REQUIRE(f.is_open());

    json data = json::parse(f);
    auto& vectors = data["vectors"];

    for (size_t i = 0; i < vectors.size(); ++i) {
        auto& v = vectors[i];
        std::string op = v["op"].as<std::string>();
        CAPTURE(i, op);

        if (op == "normalize") {
            fdl_dimensions_f64_t dims = {v["input"]["width"].as<double>(), v["input"]["height"].as<double>()};
            double squeeze = v["params"]["squeeze"].as<double>();
            fdl_dimensions_f64_t expected = {v["expected"]["width"].as<double>(), v["expected"]["height"].as<double>()};
            require_dims_close(fdl_dimensions_normalize(dims, squeeze), expected);
        } else if (op == "scale") {
            fdl_dimensions_f64_t dims = {v["input"]["width"].as<double>(), v["input"]["height"].as<double>()};
            double sf = v["params"]["scale_factor"].as<double>();
            double tsq = v["params"]["target_squeeze"].as<double>();
            fdl_dimensions_f64_t expected = {v["expected"]["width"].as<double>(), v["expected"]["height"].as<double>()};
            require_dims_close(fdl_dimensions_scale(dims, sf, tsq), expected);
        } else if (op == "normalize_and_scale") {
            fdl_dimensions_f64_t dims = {v["input"]["width"].as<double>(), v["input"]["height"].as<double>()};
            double isq = v["params"]["input_squeeze"].as<double>();
            double sf = v["params"]["scale_factor"].as<double>();
            double tsq = v["params"]["target_squeeze"].as<double>();
            fdl_dimensions_f64_t expected = {v["expected"]["width"].as<double>(), v["expected"]["height"].as<double>()};
            require_dims_close(fdl_dimensions_normalize_and_scale(dims, isq, sf, tsq), expected);
        } else if (op == "sub") {
            fdl_dimensions_f64_t a = {v["input"]["a"]["width"].as<double>(), v["input"]["a"]["height"].as<double>()};
            fdl_dimensions_f64_t b = {v["input"]["b"]["width"].as<double>(), v["input"]["b"]["height"].as<double>()};
            fdl_dimensions_f64_t expected = {v["expected"]["width"].as<double>(), v["expected"]["height"].as<double>()};
            require_dims_close(fdl_dimensions_sub(a, b), expected);
        } else if (op == "is_zero") {
            fdl_dimensions_f64_t dims = {v["input"]["width"].as<double>(), v["input"]["height"].as<double>()};
            bool expected = v["expected"].as<bool>();
            REQUIRE(fdl_dimensions_is_zero(dims) == (expected ? 1 : 0));
        } else if (op == "equal") {
            fdl_dimensions_f64_t a = {v["input"]["a"]["width"].as<double>(), v["input"]["a"]["height"].as<double>()};
            fdl_dimensions_f64_t b = {v["input"]["b"]["width"].as<double>(), v["input"]["b"]["height"].as<double>()};
            bool expected = v["expected"].as<bool>();
            REQUIRE(fdl_dimensions_equal(a, b) == (expected ? 1 : 0));
        } else if (op == "gt_i64") {
            fdl_dimensions_i64_t a = {v["input"]["a"]["width"].as<int64_t>(), v["input"]["a"]["height"].as<int64_t>()};
            fdl_dimensions_i64_t b = {v["input"]["b"]["width"].as<int64_t>(), v["input"]["b"]["height"].as<int64_t>()};
            bool expected = v["expected"].as<bool>();
            REQUIRE(fdl_dimensions_i64_gt(a, b) == (expected ? 1 : 0));
        } else if (op == "lt_i64") {
            fdl_dimensions_i64_t a = {v["input"]["a"]["width"].as<int64_t>(), v["input"]["a"]["height"].as<int64_t>()};
            fdl_dimensions_i64_t b = {v["input"]["b"]["width"].as<int64_t>(), v["input"]["b"]["height"].as<int64_t>()};
            bool expected = v["expected"].as<bool>();
            REQUIRE(fdl_dimensions_i64_lt(a, b) == (expected ? 1 : 0));
        } else if (op == "gt_f64") {
            fdl_dimensions_f64_t a = {v["input"]["a"]["width"].as<double>(), v["input"]["a"]["height"].as<double>()};
            fdl_dimensions_f64_t b = {v["input"]["b"]["width"].as<double>(), v["input"]["b"]["height"].as<double>()};
            bool expected = v["expected"].as<bool>();
            REQUIRE(fdl_dimensions_f64_gt(a, b) == (expected ? 1 : 0));
        } else if (op == "lt_f64") {
            fdl_dimensions_f64_t a = {v["input"]["a"]["width"].as<double>(), v["input"]["a"]["height"].as<double>()};
            fdl_dimensions_f64_t b = {v["input"]["b"]["width"].as<double>(), v["input"]["b"]["height"].as<double>()};
            bool expected = v["expected"].as<bool>();
            REQUIRE(fdl_dimensions_f64_lt(a, b) == (expected ? 1 : 0));
        }
    }
}

// ---------------------------------------------------------------------------
// Point math vectors
// ---------------------------------------------------------------------------

TEST_CASE("Point math matches Python golden vectors", "[value_types][points]") {
    std::string path = std::string(VECTORS_DIR) + "/value_types/point_math_vectors.json";
    std::ifstream f(path);
    REQUIRE(f.is_open());

    json data = json::parse(f);
    auto& vectors = data["vectors"];

    for (size_t i = 0; i < vectors.size(); ++i) {
        auto& v = vectors[i];
        std::string op = v["op"].as<std::string>();
        CAPTURE(i, op);

        if (op == "normalize") {
            fdl_point_f64_t point = {v["input"]["x"].as<double>(), v["input"]["y"].as<double>()};
            double squeeze = v["params"]["squeeze"].as<double>();
            fdl_point_f64_t expected = {v["expected"]["x"].as<double>(), v["expected"]["y"].as<double>()};
            require_point_close(fdl_point_normalize(point, squeeze), expected);
        } else if (op == "scale") {
            fdl_point_f64_t point = {v["input"]["x"].as<double>(), v["input"]["y"].as<double>()};
            double sf = v["params"]["scale_factor"].as<double>();
            double tsq = v["params"]["target_squeeze"].as<double>();
            fdl_point_f64_t expected = {v["expected"]["x"].as<double>(), v["expected"]["y"].as<double>()};
            require_point_close(fdl_point_scale(point, sf, tsq), expected);
        } else if (op == "add") {
            fdl_point_f64_t a = {v["input"]["a"]["x"].as<double>(), v["input"]["a"]["y"].as<double>()};
            fdl_point_f64_t b = {v["input"]["b"]["x"].as<double>(), v["input"]["b"]["y"].as<double>()};
            fdl_point_f64_t expected = {v["expected"]["x"].as<double>(), v["expected"]["y"].as<double>()};
            require_point_close(fdl_point_add(a, b), expected);
        } else if (op == "sub") {
            fdl_point_f64_t a = {v["input"]["a"]["x"].as<double>(), v["input"]["a"]["y"].as<double>()};
            fdl_point_f64_t b = {v["input"]["b"]["x"].as<double>(), v["input"]["b"]["y"].as<double>()};
            fdl_point_f64_t expected = {v["expected"]["x"].as<double>(), v["expected"]["y"].as<double>()};
            require_point_close(fdl_point_sub(a, b), expected);
        } else if (op == "mul_scalar") {
            fdl_point_f64_t point = {v["input"]["x"].as<double>(), v["input"]["y"].as<double>()};
            double scalar = v["params"]["scalar"].as<double>();
            fdl_point_f64_t expected = {v["expected"]["x"].as<double>(), v["expected"]["y"].as<double>()};
            require_point_close(fdl_point_mul_scalar(point, scalar), expected);
        } else if (op == "clamp") {
            fdl_point_f64_t point = {v["input"]["x"].as<double>(), v["input"]["y"].as<double>()};
            double min_val = v["params"]["min_val"].as<double>();
            double max_val = v["params"]["max_val"].as<double>();
            int has_min = v["params"]["has_min"].as<bool>() ? 1 : 0;
            int has_max = v["params"]["has_max"].as<bool>() ? 1 : 0;
            fdl_point_f64_t expected = {v["expected"]["x"].as<double>(), v["expected"]["y"].as<double>()};
            require_point_close(fdl_point_clamp(point, min_val, max_val, has_min, has_max), expected);
        } else if (op == "equal") {
            fdl_point_f64_t a = {v["input"]["a"]["x"].as<double>(), v["input"]["a"]["y"].as<double>()};
            fdl_point_f64_t b = {v["input"]["b"]["x"].as<double>(), v["input"]["b"]["y"].as<double>()};
            bool expected = v["expected"].as<bool>();
            REQUIRE(fdl_point_equal(a, b) == (expected ? 1 : 0));
        } else if (op == "lt") {
            fdl_point_f64_t a = {v["input"]["a"]["x"].as<double>(), v["input"]["a"]["y"].as<double>()};
            fdl_point_f64_t b = {v["input"]["b"]["x"].as<double>(), v["input"]["b"]["y"].as<double>()};
            bool expected = v["expected"].as<bool>();
            REQUIRE(fdl_point_f64_lt(a, b) == (expected ? 1 : 0));
        }
    }
}

// ---------------------------------------------------------------------------
// Standalone unit tests (not from vectors)
// ---------------------------------------------------------------------------

TEST_CASE("Dimensions basic arithmetic", "[value_types][dimensions]") {
    fdl_dimensions_f64_t a = {100.0, 200.0};
    fdl_dimensions_f64_t b = {30.0, 50.0};

    auto result = fdl_dimensions_sub(a, b);
    REQUIRE(result.width == 70.0);
    REQUIRE(result.height == 150.0);
}

TEST_CASE("Dimensions i64 operations", "[value_types][dimensions]") {
    SECTION("is_zero true") {
        fdl_dimensions_i64_t zero = {0, 0};
        REQUIRE(fdl_dimensions_i64_is_zero(zero) == 1);
    }
    SECTION("is_zero false") {
        fdl_dimensions_i64_t nonzero = {1920, 1080};
        REQUIRE(fdl_dimensions_i64_is_zero(nonzero) == 0);
    }
    SECTION("is_zero partial") {
        fdl_dimensions_i64_t partial = {0, 1080};
        REQUIRE(fdl_dimensions_i64_is_zero(partial) == 0);
    }
    SECTION("normalize") {
        fdl_dimensions_i64_t dims = {1920, 1080};
        auto result = fdl_dimensions_i64_normalize(dims, 2.0);
        REQUIRE(result.width == 3840.0);
        REQUIRE(result.height == 1080.0);
    }
    SECTION("f64_to_i64") {
        fdl_dimensions_f64_t dims = {1920.7, 1080.3};
        auto result = fdl_dimensions_f64_to_i64(dims);
        REQUIRE(result.width == 1920);
        REQUIRE(result.height == 1080);
    }
    SECTION("f64_to_i64 negative") {
        fdl_dimensions_f64_t dims = {-1920.9, -1080.1};
        auto result = fdl_dimensions_f64_to_i64(dims);
        REQUIRE(result.width == -1920);
        REQUIRE(result.height == -1080);
    }
}

TEST_CASE("Point is_zero", "[value_types][points]") {
    SECTION("true") {
        fdl_point_f64_t zero = {0.0, 0.0};
        REQUIRE(fdl_point_is_zero(zero) == 1);
    }
    SECTION("false") {
        fdl_point_f64_t nonzero = {1.0, 2.0};
        REQUIRE(fdl_point_is_zero(nonzero) == 0);
    }
    SECTION("partial") {
        fdl_point_f64_t partial = {0.0, 1.0};
        REQUIRE(fdl_point_is_zero(partial) == 0);
    }
}

TEST_CASE("Point normalize_and_scale", "[value_types][points]") {
    fdl_point_f64_t point = {100.0, 200.0};
    auto result = fdl_point_normalize_and_scale(point, 2.0, 0.5, 1.0);
    // normalize: x = 100 * 2 = 200, y = 200
    // scale: x = (200 * 0.5) / 1.0 = 100, y = 200 * 0.5 = 100
    REQUIRE(result.x == 100.0);
    REQUIRE(result.y == 100.0);
}

TEST_CASE("Point basic arithmetic", "[value_types][points]") {
    fdl_point_f64_t a = {100.0, 200.0};
    fdl_point_f64_t b = {30.0, 50.0};

    auto sum = fdl_point_add(a, b);
    REQUIRE(sum.x == 130.0);
    REQUIRE(sum.y == 250.0);

    auto diff = fdl_point_sub(a, b);
    REQUIRE(diff.x == 70.0);
    REQUIRE(diff.y == 150.0);

    auto scaled = fdl_point_mul_scalar(a, 2.0);
    REQUIRE(scaled.x == 200.0);
    REQUIRE(scaled.y == 400.0);
}
