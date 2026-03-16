# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Pytest configuration for fdl_imaging tests.

Provides parameterization hooks for template scenario tests.
"""

from fdl.testing import (
    SCENARIO_CONFIGS,
    build_test_params,
    get_scenario_test_id,
)


def pytest_generate_tests(metafunc):
    """
    Pytest hook to generate parameterized tests for template scenarios.

    Generates (scen_num, variant_letter) parameters for any test function
    that declares both 'scen_num' and 'variant_letter' fixtures.
    """
    if "scen_num" in metafunc.fixturenames and "variant_letter" in metafunc.fixturenames:
        params = [p for p in build_test_params() if not SCENARIO_CONFIGS[p[0]].is_error_test]
        ids = [get_scenario_test_id(p) for p in params]
        metafunc.parametrize("scen_num,variant_letter", params, ids=ids)
