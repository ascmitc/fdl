# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Thread-safety tests for fdl Python bindings.

Verifies that:
- String buffer aliasing is resolved (single-threaded regression)
- Concurrent reads on same document are safe
- Concurrent mutations on same document are safe
- Independent documents on separate threads don't interfere
- OwnedHandle.close() double-close is safe
- Library loading is thread-safe
- Rounding strategy get/set is thread-safe
- Concurrent template apply works

Requires: libfdl_core built and discoverable.
"""

from __future__ import annotations

import json
import threading

import pytest

try:
    from fdl_ffi import is_available

    HAS_CORE = is_available()
except ImportError:
    HAS_CORE = False

pytestmark = [
    pytest.mark.skipif(not HAS_CORE, reason="fdl_core library not available"),
    pytest.mark.thread_safety,
]

_MINIMAL_FDL = {
    "uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "version": {"major": 2, "minor": 0},
    "fdl_creator": "test-creator",
    "default_framing_intent": "FI_01",
    "framing_intents": [
        {
            "id": "FI_01",
            "label": "Default Intent",
            "aspect_ratio": {"width": 16, "height": 9},
            "protection": 0.0,
        }
    ],
    "contexts": [
        {
            "label": "Source Context",
            "context_creator": "test-ctx-creator",
            "canvases": [
                {
                    "id": "CV_01",
                    "label": "Source Canvas",
                    "source_canvas_id": "CV_01",
                    "dimensions": {"width": 3840, "height": 2160},
                    "anamorphic_squeeze": 1.0,
                    "framing_decisions": [
                        {
                            "id": "CV_01-FI_01",
                            "label": "Default FD",
                            "framing_intent_id": "FI_01",
                            "dimensions": {"width": 3840.0, "height": 2160.0},
                            "anchor_point": {"x": 0.0, "y": 0.0},
                        }
                    ],
                }
            ],
        }
    ],
    "canvas_templates": [],
}

_MINIMAL_JSON = json.dumps(_MINIMAL_FDL).encode()


def _parse_doc():
    """Parse a fresh FDL document from the minimal JSON."""
    from fdl import FDL

    return FDL.parse(_MINIMAL_JSON)


# -----------------------------------------------------------------------
# T1: String buffer aliasing regression (single-threaded)
# -----------------------------------------------------------------------


class TestStringBufferAliasing:
    """Verify that reading multiple string properties from different objects
    in the same scope doesn't cause aliasing (C1 fix regression test)."""

    def test_multiple_accessors_no_aliasing(self):
        doc = _parse_doc()
        try:
            ctx = doc.contexts[0]
            canvas = ctx.canvases[0]
            fd = canvas.framing_decisions[0]

            # Read labels from different object types — these share the
            # key "label" but must return independent values.
            ctx_label = ctx.label
            canvas_label = canvas.label
            fd_label = fd.label

            assert ctx_label == "Source Context"
            assert canvas_label == "Source Canvas"
            assert fd_label == "Default FD"

            # Also verify IDs don't alias
            canvas_id = canvas.id
            fd_id = fd.id
            assert canvas_id == "CV_01"
            assert fd_id == "CV_01-FI_01"
        finally:
            doc.close()

    def test_doc_level_accessors_no_aliasing(self):
        doc = _parse_doc()
        try:
            uuid = doc.uuid
            creator = doc.fdl_creator
            default_fi = doc.default_framing_intent

            assert uuid == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
            assert creator == "test-creator"
            assert default_fi == "FI_01"
        finally:
            doc.close()


# -----------------------------------------------------------------------
# T2: Concurrent reads on same document
# -----------------------------------------------------------------------


class TestConcurrentReads:
    def test_concurrent_reads_same_doc(self):
        doc = _parse_doc()
        results = []
        lock = threading.Lock()
        errors = []

        def reader(thread_id):
            try:
                for _ in range(100):
                    uuid = doc.uuid
                    creator = doc.fdl_creator
                    default_fi = doc.default_framing_intent
                    ctx = doc.contexts[0]
                    ctx_label = ctx.label
                    canvas = ctx.canvases[0]
                    canvas_label = canvas.label
                    canvas_id = canvas.id
                    fd = canvas.framing_decisions[0]
                    fd_label = fd.label
                    fd_dims = fd.dimensions
                    with lock:
                        results.append(
                            (
                                uuid,
                                creator,
                                default_fi,
                                ctx_label,
                                canvas_label,
                                canvas_id,
                                fd_label,
                                fd_dims.width,
                                fd_dims.height,
                            )
                        )
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        threads = [threading.Thread(target=reader, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        doc.close()

        assert not errors, f"Thread errors: {errors}"
        assert len(results) == 800  # 8 threads * 100 iterations

        expected = (
            "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "test-creator",
            "FI_01",
            "Source Context",
            "Source Canvas",
            "CV_01",
            "Default FD",
            3840.0,
            2160.0,
        )
        for r in results:
            assert r == expected, f"Data corruption detected: {r}"


# -----------------------------------------------------------------------
# T3: Concurrent mutations on same document
# -----------------------------------------------------------------------


class TestConcurrentMutations:
    def test_concurrent_read_write(self):
        from fdl import FDL, DimensionsInt

        doc = FDL.create(
            uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            fdl_creator="test",
            default_framing_intent="FI_01",
        )
        doc.add_framing_intent("FI_01", "Default", DimensionsInt(width=16, height=9), 0.0)

        errors = []
        lock = threading.Lock()

        def reader(thread_id):
            try:
                for _ in range(100):
                    _ = doc.uuid
                    _ = doc.fdl_creator
                    _ = doc.default_framing_intent
                    _ = len(doc.framing_intents)
            except Exception as e:
                with lock:
                    errors.append((thread_id, "reader", e))

        def writer(thread_id):
            try:
                for i in range(20):
                    new_uuid = f"aaaaaaaa-bbbb-cccc-dddd-{thread_id:04d}{i:08d}"
                    doc.uuid = new_uuid
            except Exception as e:
                with lock:
                    errors.append((thread_id, "writer", e))

        threads = []
        for i in range(4):
            threads.append(threading.Thread(target=reader, args=(i,)))
        for i in range(2):
            threads.append(threading.Thread(target=writer, args=(i + 4,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        doc.close()

        assert not errors, f"Thread errors: {errors}"


# -----------------------------------------------------------------------
# T4: Independent documents on separate threads
# -----------------------------------------------------------------------


class TestIndependentDocuments:
    def test_independent_docs_no_interference(self):
        errors = []
        lock = threading.Lock()

        def worker(thread_id):
            try:
                for _ in range(50):
                    doc = _parse_doc()
                    # Read everything
                    assert doc.uuid == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
                    assert doc.fdl_creator == "test-creator"
                    ctx = doc.contexts[0]
                    assert ctx.label == "Source Context"
                    canvas = ctx.canvases[0]
                    assert canvas.id == "CV_01"
                    fd = canvas.framing_decisions[0]
                    assert fd.label == "Default FD"
                    # Serialize and verify
                    json_str = doc.as_json()
                    assert "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" in json_str
                    doc.close()
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"


# -----------------------------------------------------------------------
# T5: OwnedHandle double-close safety
# -----------------------------------------------------------------------


class TestOwnedHandleDoubleClose:
    def test_concurrent_close(self):
        """4 threads all call close() on the same document. Only one should
        actually free; others should be no-ops. No segfault."""
        doc = _parse_doc()
        errors = []
        lock = threading.Lock()

        def closer(thread_id):
            try:
                doc.close()
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        threads = [threading.Thread(target=closer, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        # Verify it's closed
        assert doc._closed is True
        assert doc._handle is None


# -----------------------------------------------------------------------
# T6: Library loading race
# -----------------------------------------------------------------------


class TestLibraryLoadingRace:
    def test_concurrent_get_lib(self):
        """8 threads all call get_lib() simultaneously. All must get the
        same library object."""
        import fdl_ffi

        # Reset the singleton to force re-loading
        original_lib = fdl_ffi._lib
        fdl_ffi._lib = None

        results = []
        lock = threading.Lock()
        errors = []

        def loader(thread_id):
            try:
                lib = fdl_ffi.get_lib()
                with lock:
                    results.append(lib)
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        threads = [threading.Thread(target=loader, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Restore original
        fdl_ffi._lib = original_lib

        assert not errors, f"Thread errors: {errors}"
        assert len(results) == 8
        # All threads should have gotten the same library object
        assert all(r is results[0] for r in results)


# -----------------------------------------------------------------------
# T7: Rounding strategy thread-safety
# -----------------------------------------------------------------------


class TestRoundingStrategyThreadSafety:
    def test_concurrent_get_set_rounding(self):
        from fdl.constants import RoundingEven, RoundingMode

        from fdl import RoundStrategy, get_rounding, set_rounding

        strategies = [
            RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.UP),
            RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
            RoundStrategy(even=RoundingEven.WHOLE, mode=RoundingMode.UP),
            RoundStrategy(even=RoundingEven.WHOLE, mode=RoundingMode.ROUND),
        ]
        errors = []
        lock = threading.Lock()

        def setter(thread_id):
            try:
                strategy = strategies[thread_id % len(strategies)]
                for _ in range(100):
                    set_rounding(strategy)
            except Exception as e:
                with lock:
                    errors.append((thread_id, "setter", e))

        def getter(thread_id):
            try:
                for _ in range(100):
                    rs = get_rounding()
                    # Must be a valid RoundStrategy (not garbage)
                    assert isinstance(rs, RoundStrategy)
                    assert rs.even in (RoundingEven.EVEN, RoundingEven.WHOLE)
                    assert rs.mode in (RoundingMode.UP, RoundingMode.ROUND)
            except Exception as e:
                with lock:
                    errors.append((thread_id, "getter", e))

        threads = []
        for i in range(4):
            threads.append(threading.Thread(target=setter, args=(i,)))
        for i in range(4):
            threads.append(threading.Thread(target=getter, args=(i + 4,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"


# -----------------------------------------------------------------------
# T8: Concurrent template apply
# -----------------------------------------------------------------------


class TestConcurrentTemplateApply:
    def test_concurrent_apply(self):
        from fdl import (
            FDL,
            DimensionsFloat,
            DimensionsInt,
            FitMethod,
            GeometryPath,
            HAlign,
            PointFloat,
            RoundingEven,
            RoundingMode,
            RoundStrategy,
            VAlign,
        )

        errors = []
        lock = threading.Lock()
        results = []

        def apply_template(thread_id):
            try:
                doc = FDL.create(
                    uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                    fdl_creator="test",
                    default_framing_intent="FI_01",
                )
                doc.add_framing_intent("FI_01", "Default", DimensionsInt(width=16, height=9), 0.0)
                ctx = doc.add_context("Source", "test")
                canvas = ctx.add_canvas(
                    "CV_01",
                    "Source Canvas",
                    "CV_01",
                    DimensionsInt(width=3840, height=2160),
                    1.0,
                )
                fd = canvas.add_framing_decision(
                    "CV_01-FI_01",
                    "Default FD",
                    "FI_01",
                    DimensionsFloat(width=3840.0, height=2160.0),
                    PointFloat(x=0.0, y=0.0),
                )
                ct = doc.add_canvas_template(
                    id="CT_01",
                    label="HD Delivery",
                    target_dimensions=DimensionsInt(width=1920, height=1080),
                    target_anamorphic_squeeze=1.0,
                    fit_source=GeometryPath.CANVAS_DIMENSIONS,
                    fit_method=FitMethod.WIDTH,
                    alignment_method_horizontal=HAlign.CENTER,
                    alignment_method_vertical=VAlign.CENTER,
                    round=RoundStrategy(even=RoundingEven.EVEN, mode=RoundingMode.ROUND),
                )

                result = ct.apply(
                    source_canvas=canvas,
                    source_framing=fd,
                    new_canvas_id=f"CV_02_{thread_id}",
                    new_fd_name="HD FD",
                    source_context_label="Source",
                    context_creator="test",
                )

                with lock:
                    results.append(result.canvas.get_custom_attr("scale_factor"))

                result.fdl.close()
                doc.close()
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        threads = [threading.Thread(target=apply_template, args=(i,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        assert len(results) == 4
        for sf in results:
            assert sf == pytest.approx(0.5)
