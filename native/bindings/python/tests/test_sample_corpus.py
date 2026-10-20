# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Every sample FDL shipped in resources/FDL validates against the core.

Downstream implementers use the sample corpus as a conformance suite (issue #55),
so every ordinary sample must pass the core's schema and semantic validation.
The only files allowed to fail are the two fixtures that exist to be invalid.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fdl.errors import FDLError
from fdl.testing.base import BaseFDLTestCase

from fdl import read_from_file

RESOURCES = BaseFDLTestCase.get_resources_folder()

# Fixtures that are invalid on purpose: one is not JSON, the other is JSON but not an FDL.
KNOWN_INVALID = {"corrupt_fdl.fdl", "not_fdl.fdl"}

ALL_SAMPLES = sorted(RESOURCES.rglob("*.fdl"))
VALID_SAMPLES = [p for p in ALL_SAMPLES if p.name not in KNOWN_INVALID]
INVALID_SAMPLES = [p for p in ALL_SAMPLES if p.name in KNOWN_INVALID]


def _ids(paths: list[Path]) -> list[str]:
    return [p.relative_to(RESOURCES).as_posix() for p in paths]


def test_sample_corpus_is_present():
    # Guards against an empty glob silently passing the parametrized tests below.
    assert len(VALID_SAMPLES) > 100, f"sample corpus not found under {RESOURCES}"
    assert len(INVALID_SAMPLES) == len(KNOWN_INVALID)


@pytest.mark.parametrize("path", VALID_SAMPLES, ids=_ids(VALID_SAMPLES))
def test_sample_fdl_validates(path: Path):
    read_from_file(path, validate=True)


@pytest.mark.parametrize("path", INVALID_SAMPLES, ids=_ids(INVALID_SAMPLES))
def test_known_invalid_fixture_is_rejected(path: Path):
    # corrupt_fdl.fdl is not JSON and fails in the parser (ValueError);
    # not_fdl.fdl parses but fails schema validation (FDLValidationError).
    with pytest.raises((FDLError, ValueError)):
        read_from_file(path, validate=True)
