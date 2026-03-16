# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from fdl.cli import main

SAMPLE_FDL_DIR = Path(__file__).parent / "sample_data"
SAMPLE_FDL_FILE = SAMPLE_FDL_DIR / "Scenario-9__FDL_DeliveredToVFXVendor.fdl"


def test_validate_valid_file():
    result = main([str(SAMPLE_FDL_FILE)])
    assert result == 0


def test_validate_nonexistent_file():
    result = main(["nonexistent.fdl"])
    assert result == 1


def test_validate_malformed_file(tmp_path):
    bad_file = tmp_path / "bad.fdl"
    bad_file.write_text("{not valid json", encoding="utf-8")
    result = main([str(bad_file)])
    assert result == 1


def test_validate_multiple_files():
    files = list(SAMPLE_FDL_DIR.glob("*.fdl"))
    result = main([str(f) for f in files])
    assert result == 0
