// SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
// SPDX-License-Identifier: Apache-2.0
#include "fdl/fdl_core.h"
#include <catch2/catch_test_macros.hpp>

TEST_CASE("ABI version returns expected values", "[abi]") {
    fdl_abi_version_t ver = fdl_abi_version();
    REQUIRE(ver.major == 0);
    REQUIRE(ver.minor == 6);
    REQUIRE(ver.patch == 0);
}

TEST_CASE("FP tolerance constants are correct", "[abi]") {
    REQUIRE(fdl_fp_rel_tol() == 1e-9);
    REQUIRE(fdl_fp_abs_tol() == 1e-6);
}
