# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
# AUTO-GENERATED from fdl_api.yaml — DO NOT EDIT
"""FDL Core version type."""

from __future__ import annotations


class Version:
    """FDL document version (major, minor)."""

    __slots__ = ("major", "minor")

    def __init__(self, major: int = 2, minor: int = 0) -> None:
        self.major = major
        self.minor = minor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self.major == other.major and self.minor == other.minor

    def __repr__(self) -> str:
        return f"Version(major={self.major!r}, minor={self.minor!r})"
