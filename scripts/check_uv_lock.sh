#!/usr/bin/env bash
# Check that uv.lock contains only public registry URLs.
# Used as a pre-commit hook to prevent private/corporate indexes leaking in.
BAD=$(grep -E "https?://" uv.lock | grep -v "pypi.org" | grep -v "files.pythonhosted.org" | grep -v "github.com" | head -5)
if [ -n "$BAD" ]; then
    echo "ERROR: uv.lock contains non-public URLs:"
    echo "$BAD"
    echo "Run: python scripts/uv_lock.py"
    exit 1
fi
