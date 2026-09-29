# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Guards scripts/zip_scenario_resources.py: every configured scenario must be packaged."""

import importlib.util
import tempfile
from pathlib import Path

import pytest
from fdl.testing.scenario_config import SCENARIO_CONFIGS

_SCRIPT = Path(__file__).resolve().parents[4] / "scripts" / "zip_scenario_resources.py"


@pytest.fixture(scope="module")
def zip_script():
    spec = importlib.util.spec_from_file_location("zip_scenario_resources", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def arcnames(zip_script):
    with tempfile.TemporaryDirectory() as tmp:
        return {arcname for _, arcname in zip_script.stage_scenarios(Path(tmp))}


@pytest.mark.parametrize(
    "scen_num",
    sorted(n for n, c in SCENARIO_CONFIGS.items() if not c.is_error_test and c.variants),
    ids=lambda n: f"scen{n}",
)
def test_scenario_fully_packaged(arcnames, scen_num):
    config = SCENARIO_CONFIGS[scen_num]
    in_dir = {a for a in arcnames if a.startswith(f"{config.dir_name}/")}
    # template + (source fdl, image, result fdl, result exr) per variant; shared files dedupe
    assert any(a.endswith(config.template_filename) for a in in_dir), f"template missing for scen {scen_num}"
    assert any("/Results/" in a and a.endswith(".fdl") for a in in_dir)
    assert any("/Results/" in a and a.endswith(".exr") for a in in_dir)
    assert any("/SourceFiles/" in a and a.endswith(".fdl") for a in in_dir)


def test_new_zero_height_sentinel_scenarios_included(arcnames):
    for n in (33, 34):
        assert any(a.startswith(SCENARIO_CONFIGS[n].dir_name + "/") for a in arcnames)


def test_missing_file_fails_loudly(zip_script, monkeypatch, tmp_path):
    monkeypatch.setattr(zip_script, "SAMPLE_FILES_DIR", tmp_path)
    with pytest.raises(zip_script.MissingResourcesError):
        zip_script.stage_scenarios(tmp_path / "stage")
