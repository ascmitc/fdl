# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""
Minimal setup.py to produce platform-specific but Python-version-agnostic wheels.

The fdl package bundles a native shared library (libfdl_core.dylib/so/dll) loaded
via ctypes at runtime.  The wheel must carry a platform tag (macOS/Linux/Windows)
but should NOT be pinned to a specific CPython version — ctypes works identically
across Python 3.10+.

Resulting tag: py3-none-{platform}   (e.g. py3-none-macosx_14_0_arm64)
"""

from setuptools import setup
from setuptools.dist import Distribution

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            # Mark as platform-specific (not 'any') but not Python-version-specific
            self.root_is_pure = False

        def get_tag(self):
            # py3-none-{platform}
            _, _, plat = _bdist_wheel.get_tag(self)
            return "py3", "none", plat

except ImportError:
    # wheel not installed at build time — fall back to platform-tagged dist
    bdist_wheel = None


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


setup(
    distclass=BinaryDistribution,
    cmdclass={"bdist_wheel": bdist_wheel} if bdist_wheel else {},
)
