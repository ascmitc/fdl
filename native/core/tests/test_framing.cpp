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
    std::ifstream f(VECTORS_DIR "/framing/from_intent_vectors.json");
    REQUIRE(f.is_open());
    return ojson::parse(f);
}

static bool close_enough(double a, double b, double tol = 1e-6) {
    return std::abs(a - b) < tol;
}

TEST_CASE("compute_framing_from_intent matches Python golden vectors", "[framing][from_intent]") {
    auto root = load_vectors();
    const auto& vectors = root["vectors"];

    for (const auto& v : vectors.array_range()) {
        auto label = v["label"].as<std::string>();
        SECTION(label) {
            // Parse inputs
            fdl_dimensions_f64_t canvas_dims = {
                v["canvas_dims"]["width"].as<double>(), v["canvas_dims"]["height"].as<double>()};
            fdl_dimensions_f64_t working_dims = {
                v["working_dims"]["width"].as<double>(), v["working_dims"]["height"].as<double>()};
            double squeeze = v["squeeze"].as<double>();
            fdl_dimensions_i64_t aspect_ratio = {
                v["aspect_ratio"]["width"].as<int64_t>(), v["aspect_ratio"]["height"].as<int64_t>()};
            double protection = v["protection"].as<double>();

            fdl_round_strategy_t rounding;
            auto even_str = v["rounding"]["even"].as<std::string>();
            auto mode_str = v["rounding"]["mode"].as<std::string>();
            rounding.even = (even_str == "even") ? FDL_ROUNDING_EVEN_EVEN : FDL_ROUNDING_EVEN_WHOLE;
            if (mode_str == "up") {
                rounding.mode = FDL_ROUNDING_MODE_UP;
            } else if (mode_str == "down") {
                rounding.mode = FDL_ROUNDING_MODE_DOWN;
            } else {
                rounding.mode = FDL_ROUNDING_MODE_ROUND;
            }

            // Parse expected
            const auto& exp = v["expected"];
            double exp_dim_w = exp["dimensions"]["width"].as<double>();
            double exp_dim_h = exp["dimensions"]["height"].as<double>();
            double exp_anchor_x = exp["anchor_point"]["x"].as<double>();
            double exp_anchor_y = exp["anchor_point"]["y"].as<double>();
            bool exp_has_prot = exp["has_protection"].as<bool>();

            // Run
            auto result =
                fdl_compute_framing_from_intent(canvas_dims, working_dims, squeeze, aspect_ratio, protection, rounding);

            // Verify dimensions and anchor
            REQUIRE(close_enough(result.dimensions.width, exp_dim_w));
            REQUIRE(close_enough(result.dimensions.height, exp_dim_h));
            REQUIRE(close_enough(result.anchor_point.x, exp_anchor_x));
            REQUIRE(close_enough(result.anchor_point.y, exp_anchor_y));

            // Verify protection
            REQUIRE((result.has_protection != 0) == exp_has_prot);
            if (exp_has_prot) {
                double exp_prot_w = exp["protection_dimensions"]["width"].as<double>();
                double exp_prot_h = exp["protection_dimensions"]["height"].as<double>();
                double exp_prot_ax = exp["protection_anchor_point"]["x"].as<double>();
                double exp_prot_ay = exp["protection_anchor_point"]["y"].as<double>();

                REQUIRE(close_enough(result.protection_dimensions.width, exp_prot_w));
                REQUIRE(close_enough(result.protection_dimensions.height, exp_prot_h));
                REQUIRE(close_enough(result.protection_anchor_point.x, exp_prot_ax));
                REQUIRE(close_enough(result.protection_anchor_point.y, exp_prot_ay));
            }
        }
    }
}
