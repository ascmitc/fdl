# SPDX-License-Identifier: Apache-2.0
"""The committed scenario_inputs.json (read by the Node tests) must match the Python scenarios."""

import json

from scenario_inputs import JSON_PATH, bridge_inputs


def test_scenario_inputs_json_is_current():
    committed = json.loads(JSON_PATH.read_text())
    assert committed == bridge_inputs(), (
        "scenario_inputs.json is out of date; run: python examples/web_viewer/server/tests/scenario_inputs.py"
    )
