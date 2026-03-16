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
    std::ifstream f(VECTORS_DIR "/pipeline/pipeline_vectors.json");
    REQUIRE(f.is_open());
    return ojson::parse(f);
}

static fdl_dimensions_f64_t parse_dims(const ojson& j) {
    return {j["width"].as<double>(), j["height"].as<double>()};
}

static bool close_enough(double a, double b, double tol = 1e-9) {
    return std::abs(a - b) < tol;
}

TEST_CASE("calculate_scale_factor matches Python golden vectors", "[pipeline][scale]") {
    auto root = load_vectors();
    const auto& vectors = root["scale_factor"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto fit = parse_dims(v["fit_norm"]);
            auto target = parse_dims(v["target_norm"]);
            auto method_str = v["fit_method"].as<std::string>();
            double expected = v["expected"].as<double>();

            fdl_fit_method_t method;
            if (method_str == "width") {
                method = FDL_FIT_METHOD_WIDTH;
            } else if (method_str == "height") {
                method = FDL_FIT_METHOD_HEIGHT;
            } else if (method_str == "fit_all") {
                method = FDL_FIT_METHOD_FIT_ALL;
            } else {
                method = FDL_FIT_METHOD_FILL;
            }

            double result = fdl_calculate_scale_factor(fit, target, method);

            REQUIRE(close_enough(result, expected));
        }
    }
}

TEST_CASE("output_size_for_axis matches Python golden vectors", "[pipeline][output_size]") {
    auto root = load_vectors();
    const auto& vectors = root["output_size"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            double canvas = v["canvas_size"].as<double>();
            double max_s = v["max_size"].as<double>();
            bool has = v["has_max"].as<bool>();
            bool pad = v["pad_to_max"].as<bool>();
            double expected = v["expected"].as<double>();

            double result = fdl_output_size_for_axis(canvas, max_s, has ? 1 : 0, pad ? 1 : 0);

            REQUIRE(close_enough(result, expected));
        }
    }
}

TEST_CASE("alignment_shift matches Python golden vectors", "[pipeline][alignment]") {
    auto root = load_vectors();
    const auto& vectors = root["alignment_shift"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            double fit_size = v["fit_size"].as<double>();
            double fit_anchor = v["fit_anchor"].as<double>();
            double output_size = v["output_size"].as<double>();
            double canvas_size = v["canvas_size"].as<double>();
            double target_size = v["target_size"].as<double>();
            bool is_center = v["is_center"].as<bool>();
            double align_factor = v["align_factor"].as<double>();
            bool pad = v["pad_to_max"].as<bool>();
            double expected = v["expected"].as<double>();

            double result = fdl_alignment_shift(
                fit_size,
                fit_anchor,
                output_size,
                canvas_size,
                target_size,
                is_center ? 1 : 0,
                align_factor,
                pad ? 1 : 0);

            REQUIRE(close_enough(result, expected, 1e-6));
        }
    }
}

TEST_CASE("clamp_to_dims matches Python golden vectors", "[pipeline][clamp]") {
    auto root = load_vectors();
    const auto& vectors = root["clamp_to_dims"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            auto dims = parse_dims(v["dims"]);
            auto clamp = parse_dims(v["clamp_dims"]);
            auto expected_dims = parse_dims(v["expected_dims"]);
            double expected_dx = v["expected_delta"]["x"].as<double>();
            double expected_dy = v["expected_delta"]["y"].as<double>();

            fdl_point_f64_t delta;
            auto result = fdl_dimensions_clamp_to_dims(dims, clamp, &delta);

            REQUIRE(close_enough(result.width, expected_dims.width));
            REQUIRE(close_enough(result.height, expected_dims.height));
            REQUIRE(close_enough(delta.x, expected_dx));
            REQUIRE(close_enough(delta.y, expected_dy));
        }
    }
}
