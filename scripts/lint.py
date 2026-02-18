#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
"""Run all CI lint checks locally, mirroring .github/workflows/main.yml lint job.

Usage:
    python scripts/lint.py              # run all checks
    python scripts/lint.py --fail-fast  # stop on first failure
    python scripts/lint.py --step clang-tidy  # run just one step
    python scripts/lint.py --list       # list available steps
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CLANG_FORMAT_DIRS = [
    "native/core/src",
    "native/core/include",
    "native/core/tests",
    "native/bindings/cpp/",
]
CLANG_FORMAT_EXTENSIONS = (".cpp", ".h", ".hpp")

WARNING_RE = re.compile(r"^(.+?):(\d+):(\d+): (warning|error): (.+) \[(.+)\]$")

OUR_CODE_PREFIXES = ("native/core/src/", "native/core/include/")


def find_clang_format_files() -> list[str]:
    """Find all C/C++ files matching the CI glob pattern."""
    files = []
    for d in CLANG_FORMAT_DIRS:
        root = REPO_ROOT / d
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix in CLANG_FORMAT_EXTENSIONS:
                files.append(str(path))
    return sorted(files)


def filter_clang_tidy_output(output: str) -> tuple[list[str], int]:
    """Split clang-tidy output into our-code warnings and dependency warning count."""
    our_warnings = []
    dep_count = 0
    for line in output.splitlines():
        m = WARNING_RE.match(line)
        if not m:
            continue
        filepath = m.group(1)
        # Make path relative to repo root for consistent matching
        try:
            rel = str(Path(filepath).resolve().relative_to(REPO_ROOT))
        except ValueError:
            rel = filepath
        if any(rel.startswith(p) for p in OUR_CODE_PREFIXES):
            our_warnings.append(line)
        else:
            dep_count += 1
    return our_warnings, dep_count


class LintStep:
    """A single lint check."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def check_tools(self) -> str | None:
        """Return an error message if required tools are missing, else None."""
        return None

    def run(self, log_dir: Path) -> tuple[bool, str]:
        """Run the check. Returns (passed, detail_message)."""
        raise NotImplementedError


class RuffCheck(LintStep):
    def __init__(self):
        super().__init__("ruff-check", "Python lint (ruff check)")

    def check_tools(self) -> str | None:
        if not shutil.which("uvx"):
            return "uvx not found — install uv: https://docs.astral.sh/uv/"
        return None

    def run(self, log_dir: Path) -> tuple[bool, str]:
        r = subprocess.run(
            ["uvx", "ruff", "check", "."],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        (log_dir / "ruff-check.txt").write_text(r.stdout + r.stderr)
        return r.returncode == 0, ""


class RuffFormat(LintStep):
    def __init__(self):
        super().__init__("ruff-format", "Python format (ruff format --check)")

    def check_tools(self) -> str | None:
        if not shutil.which("uvx"):
            return "uvx not found — install uv: https://docs.astral.sh/uv/"
        return None

    def run(self, log_dir: Path) -> tuple[bool, str]:
        r = subprocess.run(
            ["uvx", "ruff", "format", "--check", "."],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        (log_dir / "ruff-format.txt").write_text(r.stdout + r.stderr)
        return r.returncode == 0, ""


class ClangFormat(LintStep):
    def __init__(self):
        super().__init__("clang-format", "C++ format (clang-format --Werror)")

    def check_tools(self) -> str | None:
        if not shutil.which("clang-format"):
            return "clang-format not found — install: brew install llvm"
        return None

    def run(self, log_dir: Path) -> tuple[bool, str]:
        files = find_clang_format_files()
        if not files:
            return True, "no files found"
        r = subprocess.run(
            ["clang-format", "--dry-run", "--Werror", *files],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        (log_dir / "clang-format.txt").write_text(r.stdout + r.stderr)
        return r.returncode == 0, ""


class CodegenDrift(LintStep):
    def __init__(self):
        super().__init__("codegen-drift", "Codegen drift check")

    def check_tools(self) -> str | None:
        script = REPO_ROOT / "scripts" / "run_codegen.py"
        if not script.exists():
            return f"{script} not found"
        return None

    def run(self, log_dir: Path) -> tuple[bool, str]:
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "run_codegen.py"), "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        (log_dir / "codegen-drift.txt").write_text(r.stdout + r.stderr)
        return r.returncode == 0, ""


class ClangTidy(LintStep):
    def __init__(self):
        super().__init__("clang-tidy", "C++ lint (clang-tidy)")

    def check_tools(self) -> str | None:
        if not shutil.which("run-clang-tidy"):
            return "run-clang-tidy not found — install: brew install llvm"
        if not shutil.which("cmake"):
            return "cmake not found — install: brew install cmake"
        return None

    def _ensure_compile_commands(self) -> bool:
        """Ensure compile_commands.json exists. Returns True if available."""
        cc_json = REPO_ROOT / "native" / "core" / "build" / "compile_commands.json"
        cmake_file = REPO_ROOT / "native" / "core" / "CMakeLists.txt"

        need_configure = not cc_json.exists()
        if cc_json.exists() and cmake_file.exists():
            if cmake_file.stat().st_mtime > cc_json.stat().st_mtime:
                need_configure = True

        if need_configure:
            r = subprocess.run(
                [
                    "cmake",
                    "-S",
                    "native/core",
                    "-B",
                    "native/core/build",
                    "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
                    "-DFDL_BUILD_TESTS=OFF",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                return False
        return True

    def run(self, log_dir: Path) -> tuple[bool, str]:
        if not self._ensure_compile_commands():
            return False, "CMake configure failed"

        cpu_count = os.cpu_count() or 1
        r = subprocess.run(
            [
                "run-clang-tidy",
                f"-p={REPO_ROOT / 'native' / 'core' / 'build'}",
                f"-j{cpu_count}",
                str(REPO_ROOT / "native" / "core" / "src") + "/",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        combined = r.stdout + r.stderr
        (log_dir / "clang-tidy.txt").write_text(combined)

        our_warnings, dep_count = filter_clang_tidy_output(combined)
        detail = ""
        if dep_count > 0:
            detail = f"{dep_count} dependency warnings filtered"

        if our_warnings:
            msg_parts = [f"{len(our_warnings)} warnings in our code"]
            if dep_count > 0:
                msg_parts.append(f"{dep_count} dependency warnings filtered")
            # Print the actual warnings for immediate visibility
            print()
            for w in our_warnings:
                print(f"    {w}")
            return False, ", ".join(msg_parts)

        return True, detail


ALL_STEPS: list[LintStep] = [
    RuffCheck(),
    RuffFormat(),
    ClangFormat(),
    CodegenDrift(),
    ClangTidy(),
]

STEP_NAMES = [s.name for s in ALL_STEPS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    parser.add_argument("--step", choices=STEP_NAMES, help="Run only the named step")
    parser.add_argument("--list", action="store_true", help="List available steps and exit")
    args = parser.parse_args()

    if args.list:
        for s in ALL_STEPS:
            print(f"  {s.name:<16} {s.description}")
        return 0

    steps = ALL_STEPS
    if args.step:
        steps = [s for s in ALL_STEPS if s.name == args.step]

    log_dir = Path(tempfile.mkdtemp(prefix="fdl-lint-"))

    results: list[tuple[str, str, str]] = []  # (name, status, detail)
    failed = 0

    print(f"\n=== FDL Lint ({len(steps)} checks) ===\n")

    for step in steps:
        missing = step.check_tools()
        if missing:
            status = "SKIP"
            detail = missing
            print(f"  {step.name:<16} ... SKIP ({missing})")
            results.append((step.name, status, detail))
            continue

        print(f"  {step.name:<16} ... ", end="", flush=True)
        passed, detail = step.run(log_dir)

        if passed:
            status = "PASS"
            suffix = f" ({detail})" if detail else ""
            print(f"PASS{suffix}")
        else:
            status = "FAIL"
            failed += 1
            suffix = f" ({detail})" if detail else ""
            print(f"FAIL{suffix}")

        results.append((step.name, status, detail))

        if not passed and args.fail_fast:
            break

    print(f"\nLogs: {log_dir}/")

    if failed:
        print(f"\n{failed} of {len(steps)} checks failed.")
        # Show log file hints for failures
        for name, status, _ in results:
            if status == "FAIL":
                print(f"  See {log_dir}/{name}.txt")
        return 1

    print(f"\nAll {len(steps)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
