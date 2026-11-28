"""Every public name appears in the API reference (docs/api.rst)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import package_name as package

API = (Path(__file__).parent.parent / "docs" / "api.rst").read_text()
PUBLIC = sorted(set(package.__all__) - {"__version__"})


@pytest.mark.parametrize("name", PUBLIC)
def test_public_name_is_in_the_api_reference(name: str):
    listed = re.search(rf"^(\s+|\.\. autodata:: ){re.escape(name)}\s*$", API, re.M)
    assert listed, f"add {name} to docs/api.rst"
