# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Error validation tests for FDL template scenarios 21-22.

Pure FDL tests — verifies proper ValueError exceptions when templates
reference paths that don't exist in the source FDL.
"""

from fdl.testing.template_tests import (
    TestFitSourceValidation,  # noqa: F401
    TestPreserveFromSourceCanvasValidation,  # noqa: F401
)
