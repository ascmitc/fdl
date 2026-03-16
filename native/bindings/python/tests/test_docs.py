# SPDX-FileCopyrightText: 2024-present American Society Of Cinematographers
# SPDX-License-Identifier: Apache-2.0
import pathlib

import pytest
from mktestdocs import check_md_file

SKIP_FILES = {
    "FDL_Template_Implementer_Guide.md",
    "FDL_Apply_Template_Logic.md",
    "fdl_imaging.md",  # examples require image/FDL files on disk
    "fdl_frameline_generator.md",  # examples require FDL files on disk
}

_DOCS_DIR = pathlib.Path(__file__).parents[4] / "docs"


@pytest.mark.parametrize("fpath", _DOCS_DIR.glob("**/*.md"), ids=lambda p: str(p.relative_to(_DOCS_DIR)))
def test_all_docs(fpath):
    if fpath.name in SKIP_FILES:
        pytest.skip(f"{fpath.name}: not yet implemented")
    check_md_file(fpath=fpath, memory=False)
