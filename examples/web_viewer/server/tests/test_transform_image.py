# SPDX-License-Identifier: Apache-2.0
"""Tests for the web viewer's Python image bridge (``scripts/transform_image.py``).

The Express server runs the bridge as a subprocess and sends it JSON on stdin.
These tests build that JSON from the shared scenario inputs exactly as the client
would, run the real bridge, and require the output image to be pixel-identical to the
scenario's golden EXR.

Run from the repository root:

    python -m pytest examples/web_viewer/server/tests -v
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import OpenImageIO as oiio
import pytest
from scenario_inputs import REPO_ROOT, bridge_inputs

BRIDGE_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "transform_image.py"

# The golden EXRs are generated with the "triangle" (bilinear) filter.
GOLDEN_FILTER = "triangle"


def _pixels(path: Path) -> np.ndarray:
    return oiio.ImageBuf(str(path)).get_pixels()


@pytest.mark.parametrize("entry", bridge_inputs(), ids=lambda e: e["id"])
def test_bridge_output_matches_golden(entry: dict, tmp_path: Path):
    output_path = tmp_path / "out.exr"
    payload = {
        "sourceFdlJson": (REPO_ROOT / entry["sourceFdl"]).read_text(),
        "contextIndex": entry["contextIndex"],
        "canvasId": entry["canvasId"],
        "framingId": entry["framingId"],
        "template": entry["template"],
        "inputImagePath": str(REPO_ROOT / entry["sourceImage"]),
        "outputImagePath": str(output_path),
        "filterName": GOLDEN_FILTER,
    }

    result = subprocess.run(
        [sys.executable, str(BRIDGE_SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )

    assert result.returncode == 0, f"bridge failed: {result.stdout.strip()} {result.stderr.strip()}"
    response = json.loads(result.stdout)
    assert response.get("success") is True, response

    expected = _pixels(REPO_ROOT / entry["expectedImage"])
    actual = _pixels(output_path)
    assert actual.shape == expected.shape, f"size mismatch: {actual.shape} vs {expected.shape}"
    max_diff = float(np.abs(actual.astype(np.float64) - expected.astype(np.float64)).max())
    assert max_diff == 0.0, f"output differs from golden EXR (max abs diff {max_diff})"


def test_bridge_selects_context_by_index_when_contexts_have_no_label(tmp_path: Path):
    """Contexts without labels (or sharing one) are addressed by position, not label."""
    entry = next(e for e in bridge_inputs() if e["id"] == "scen1_B")
    fdl = json.loads((REPO_ROOT / entry["sourceFdl"]).read_text())
    second = json.loads(json.dumps(fdl["contexts"][0]))
    second["canvases"][0]["id"] = "SECOND"
    second["canvases"][0]["framing_decisions"][0]["id"] = "SECOND-1"
    for context in (*fdl["contexts"], second):
        context.pop("label", None)
    fdl["contexts"].append(second)

    payload = {
        "sourceFdlJson": json.dumps(fdl),
        "contextIndex": 1,
        "canvasId": "SECOND",
        "framingId": "SECOND-1",
        "template": entry["template"],
        "inputImagePath": str(REPO_ROOT / entry["sourceImage"]),
        "outputImagePath": str(tmp_path / "out.exr"),
    }
    result = subprocess.run([sys.executable, str(BRIDGE_SCRIPT)], input=json.dumps(payload), capture_output=True, text=True, check=False)
    assert result.returncode == 0, f"bridge failed: {result.stdout.strip()} {result.stderr.strip()}"
    assert json.loads(result.stdout).get("success") is True
