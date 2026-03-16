# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Tests for ClipID and FileSequence handle wrapper types."""

from __future__ import annotations

import json

import pytest

try:
    from fdl_ffi import is_available

    HAS_CORE = is_available()
except ImportError:
    HAS_CORE = False

pytestmark = pytest.mark.skipif(not HAS_CORE, reason="fdl_core library not available")


def _parse_with_clip_id(clip_id_dict: dict):
    """Parse a minimal FDL with a given clip_id on the first context."""
    from fdl import FDL

    fdl_data = {
        "uuid": "4ff5d6b1-aaf2-48fd-a947-2d61e45d676a",
        "version": {"major": 2, "minor": 0},
        "fdl_creator": "ASC FDL Tools",
        "framing_intents": [],
        "contexts": [
            {
                "label": "test_clipid",
                "clip_id": clip_id_dict,
                "canvases": [],
            }
        ],
        "canvas_templates": [],
    }
    return FDL.parse(json.dumps(fdl_data).encode())


def test_deserializing_clip_id():
    from fdl.clip_id import ClipID

    result = _parse_with_clip_id({"clip_name": "ABX_001_110_911", "file": "ABX_001_110_911.mov"})
    clip = result.contexts[0].clip_id
    assert isinstance(clip, ClipID)
    assert clip.clip_name == "ABX_001_110_911"
    assert clip.file == "ABX_001_110_911.mov"
    assert clip.sequence is None
    result.close()


def test_deserializing_file_sequence():
    from fdl.file_sequence import FileSequence

    result = _parse_with_clip_id(
        {
            "clip_name": "ABX_001_110_911",
            "sequence": {"value": "ABX_001_110_911.####.exr", "idx": "#", "min": 0, "max": 100},
        }
    )
    clip = result.contexts[0].clip_id
    seq = clip.sequence
    assert isinstance(seq, FileSequence)
    assert seq.value == "ABX_001_110_911.####.exr"
    assert seq.idx == "#"
    assert seq.min == 0
    assert seq.max == 100
    result.close()


def test_clip_id_properties():
    result = _parse_with_clip_id(
        {
            "clip_name": "A002_C307_0523JT",
            "sequence": {"value": "A002_C307_0523JT.####.exr", "idx": "#", "min": 0, "max": 100},
        }
    )
    cid = result.contexts[0].clip_id
    assert cid.clip_name == "A002_C307_0523JT"
    assert cid.file is None
    assert cid.sequence is not None
    assert cid.sequence.value == "A002_C307_0523JT.####.exr"
    result.close()


def test_clip_id_as_dict():
    result = _parse_with_clip_id({"clip_name": "A001", "file": "A001C001.ari"})
    cid = result.contexts[0].clip_id
    d = cid.as_dict()
    assert d["clip_name"] == "A001"
    assert d["file"] == "A001C001.ari"
    assert "sequence" not in d
    result.close()


def test_set_clip_id_via_dict():
    """Set clip_id using a dict on the context property setter."""
    from fdl import FDL

    fdl_data = {
        "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "version": {"major": 2, "minor": 0},
        "fdl_creator": "test",
        "framing_intents": [],
        "contexts": [{"label": "Source", "canvases": []}],
        "canvas_templates": [],
    }
    doc = FDL.parse(json.dumps(fdl_data).encode())
    ctx = doc.contexts[0]
    assert ctx.clip_id is None

    ctx.clip_id = {"clip_name": "A001", "file": "A001C001.ari"}
    cid = ctx.clip_id
    assert cid is not None
    assert cid.clip_name == "A001"
    assert cid.file == "A001C001.ari"
    doc.close()
