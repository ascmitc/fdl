// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include <catch2/catch_test_macros.hpp>

#include "fdl/fdl_core.h"

#include <cmath>
#include <fstream>
#include <jsoncons/json.hpp>
#include <string>

using ojson = jsoncons::ojson;

static ojson load_vectors() {
    std::ifstream f(VECTORS_DIR "/geometry/geometry_vectors.json");
    REQUIRE(f.is_open());
    return ojson::parse(f);
}

static fdl_dimensions_f64_t parse_dims(const ojson& j) {
    return {j["width"].as<double>(), j["height"].as<double>()};
}

static fdl_point_f64_t parse_point(const ojson& j) {
    return {j["x"].as<double>(), j["y"].as<double>()};
}

static fdl_geometry_t parse_geometry(const ojson& j) {
    return {
        parse_dims(j["canvas_dims"]),
        parse_dims(j["effective_dims"]),
        parse_dims(j["protection_dims"]),
        parse_dims(j["framing_dims"]),
        parse_point(j["effective_anchor"]),
        parse_point(j["protection_anchor"]),
        parse_point(j["framing_anchor"]),
    };
}

static bool dims_close(fdl_dimensions_f64_t a, fdl_dimensions_f64_t b, double tol = 1e-6) {
    return std::abs(a.width - b.width) < tol && std::abs(a.height - b.height) < tol;
}

static bool point_close(fdl_point_f64_t a, fdl_point_f64_t b, double tol = 1e-6) {
    return std::abs(a.x - b.x) < tol && std::abs(a.y - b.y) < tol;
}

static bool geo_close(const fdl_geometry_t& a, const fdl_geometry_t& b, double tol = 1e-6) {
    return dims_close(a.canvas_dims, b.canvas_dims, tol) && dims_close(a.effective_dims, b.effective_dims, tol) &&
           dims_close(a.protection_dims, b.protection_dims, tol) && dims_close(a.framing_dims, b.framing_dims, tol) &&
           point_close(a.effective_anchor, b.effective_anchor, tol) &&
           point_close(a.protection_anchor, b.protection_anchor, tol) &&
           point_close(a.framing_anchor, b.framing_anchor, tol);
}

TEST_CASE("Geometry fill_hierarchy_gaps matches Python golden vectors", "[geometry][fill]") {
    auto root = load_vectors();
    const auto& vectors = root["fill_hierarchy_gaps"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto geo = parse_geometry(v["input"]);
            auto offset = parse_point(v["anchor_offset"]);
            auto expected = parse_geometry(v["expected"]);

            auto result = fdl_geometry_fill_hierarchy_gaps(geo, offset);

            REQUIRE(geo_close(result, expected));
        }
    }
}

TEST_CASE("Geometry normalize_and_scale matches Python golden vectors", "[geometry][scale]") {
    auto root = load_vectors();
    const auto& vectors = root["normalize_and_scale"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto geo = parse_geometry(v["input"]);
            double squeeze = v["source_squeeze"].as<double>();
            double scale = v["scale_factor"].as<double>();
            double target = v["target_squeeze"].as<double>();
            auto expected = parse_geometry(v["expected"]);

            auto result = fdl_geometry_normalize_and_scale(geo, squeeze, scale, target);

            REQUIRE(geo_close(result, expected));
        }
    }
}

TEST_CASE("Geometry round matches Python golden vectors", "[geometry][round]") {
    auto root = load_vectors();
    const auto& vectors = root["round"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto geo = parse_geometry(v["input"]);
            auto even_str = v["even"].as<std::string>();
            auto mode_str = v["mode"].as<std::string>();

            fdl_round_strategy_t strategy;
            strategy.even = (even_str == "even") ? FDL_ROUNDING_EVEN_EVEN : FDL_ROUNDING_EVEN_WHOLE;
            if (mode_str == "up") {
                strategy.mode = FDL_ROUNDING_MODE_UP;
            } else if (mode_str == "down") {
                strategy.mode = FDL_ROUNDING_MODE_DOWN;
            } else {
                strategy.mode = FDL_ROUNDING_MODE_ROUND;
            }

            auto expected = parse_geometry(v["expected"]);
            auto result = fdl_geometry_round(geo, strategy);

            REQUIRE(geo_close(result, expected));
        }
    }
}

TEST_CASE("Geometry apply_offset matches Python golden vectors", "[geometry][offset]") {
    auto root = load_vectors();
    const auto& vectors = root["apply_offset"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto geo = parse_geometry(v["input"]);
            auto offset = parse_point(v["offset"]);
            auto expected_geo = parse_geometry(v["expected_geometry"]);
            auto expected_theo_eff = parse_point(v["expected_theo_eff"]);
            auto expected_theo_prot = parse_point(v["expected_theo_prot"]);
            auto expected_theo_fram = parse_point(v["expected_theo_fram"]);

            fdl_point_f64_t theo_eff, theo_prot, theo_fram;
            auto result = fdl_geometry_apply_offset(geo, offset, &theo_eff, &theo_prot, &theo_fram);

            REQUIRE(geo_close(result, expected_geo));
            REQUIRE(point_close(theo_eff, expected_theo_eff));
            REQUIRE(point_close(theo_prot, expected_theo_prot));
            REQUIRE(point_close(theo_fram, expected_theo_fram));
        }
    }
}

TEST_CASE("Geometry crop matches Python golden vectors", "[geometry][crop]") {
    auto root = load_vectors();
    const auto& vectors = root["crop"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto geo = parse_geometry(v["input"]);
            auto theo_eff = parse_point(v["theo_eff"]);
            auto theo_prot = parse_point(v["theo_prot"]);
            auto theo_fram = parse_point(v["theo_fram"]);
            auto expected = parse_geometry(v["expected"]);

            auto result = fdl_geometry_crop(geo, theo_eff, theo_prot, theo_fram);

            REQUIRE(geo_close(result, expected));
        }
    }
}

TEST_CASE("Geometry get_dims_anchor_from_path matches Python golden vectors", "[geometry][path]") {
    auto root = load_vectors();
    const auto& vectors = root["get_dims_anchor_from_path"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto geo = parse_geometry(v["input"]);
            auto path_str = v["path"].as<std::string>();
            auto expected_dims = parse_dims(v["expected_dims"]);
            auto expected_anchor = parse_point(v["expected_anchor"]);

            fdl_geometry_path_t path;
            if (path_str == "canvas.dimensions") {
                path = FDL_GEOMETRY_PATH_CANVAS_DIMENSIONS;
            } else if (path_str == "canvas.effective_dimensions") {
                path = FDL_GEOMETRY_PATH_CANVAS_EFFECTIVE_DIMENSIONS;
            } else if (path_str == "framing_decision.protection_dimensions") {
                path = FDL_GEOMETRY_PATH_FRAMING_PROTECTION_DIMENSIONS;
            } else {
                path = FDL_GEOMETRY_PATH_FRAMING_DIMENSIONS;
            }

            fdl_dimensions_f64_t out_dims;
            fdl_point_f64_t out_anchor;
            int rc = fdl_geometry_get_dims_anchor_from_path(&geo, path, &out_dims, &out_anchor);

            REQUIRE(rc == 0);
            REQUIRE(dims_close(out_dims, expected_dims));
            REQUIRE(point_close(out_anchor, expected_anchor));
        }
    }
}
