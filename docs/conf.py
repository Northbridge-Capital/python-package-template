"""Sphinx configuration for the documentation."""

import html
import importlib.metadata
import inspect
import re
from collections.abc import Generator, Iterator
from typing import get_args, get_origin

from sphinx.util.typing import stringify_annotation

project = "REPLACE_ME"
author = "Northbridge Capital"
copyright = "2026, Northbridge Capital"
release = importlib.metadata.version("REPLACE_ME")
summary = importlib.metadata.metadata("REPLACE_ME")["Summary"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinxext.opengraph",
    "sphinx_copybutton",
]

# Docstrings are NumPy style and carry no types; the signature shows the types.
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
numpydoc_xref_param_type = False
autodoc_typehints = "signature"
autodoc_member_order = "bysource"
# pydantic's own configuration attribute is plumbing, not API.
autodoc_default_options = {"exclude-members": "model_config"}
autosummary_generate = True
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3
exclude_patterns = ["_build"]
templates_path = ["_templates"]

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_favicon = "_static/brand/symbol-tile.svg"
# The published address: canonical links, and the URL link previews point at.
html_baseurl = "https://northbridge-capital.github.io/REPLACE_ME/"
ogp_site_url = html_baseurl
ogp_enable_meta_description = True
ogp_image = "_static/brand/social-card.png"
ogp_image_alt = "Northbridge Capital"
html_title = f"{project} {release}"
html_theme_options = {
    "logo": {
        "image_light": "_static/brand/lockup-on-light.svg",
        "image_dark": "_static/brand/lockup-on-dark.svg",
        "alt_text": "Northbridge Capital",
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/Northbridge-Capital/REPLACE_ME",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/REPLACE_ME/",
            "icon": "fa-brands fa-python",
        },
    ],
    "pygments_light_style": "a11y-high-contrast-light",
    "pygments_dark_style": "a11y-high-contrast-dark",
    "show_toc_level": 2,
    "navigation_with_keys": False,
    "show_prev_next": False,
}

# --- Types in the parameter lists -------------------------------------------------------------
# The docstrings carry no types (the annotation is the single source of truth). This hook adds
# them to the rendered NumPy sections from the annotations, so the lists read ``name : type``.


def _annotations(obj):
    """Return the annotations of ``obj``, evaluated if possible."""
    try:
        return inspect.get_annotations(obj, eval_str=True)
    except Exception:  # an unresolvable forward reference
        return inspect.get_annotations(obj)


def _text(annotation):
    """Return an annotation as readable text, without module prefixes."""
    text = annotation if isinstance(annotation, str) else stringify_annotation(annotation)
    return re.sub(r"\b(?:[a-z_][a-z0-9_]*\.)+([A-Za-z_][A-Za-z0-9_]*)", r"\1", text)


def _add_types(app, what, name, obj, options, lines):
    """Add the annotated types to the Parameters, Attributes and Returns/Yields sections."""
    types, returns, yields = {}, None, None
    if what in {"function", "method"}:
        hints = _annotations(obj)
        types = {key: _text(value) for key, value in hints.items() if key != "return"}
        annotation = hints.get("return")
        if get_origin(annotation) in {Generator, Iterator}:
            yields = _text(get_args(annotation)[0])
        elif annotation is not None and annotation is not type(None):
            returns = _text(annotation)
        sections = {"Parameters": types}
    elif what == "class":
        types = {key: _text(value) for key, value in _annotations(obj).items()}
        for key, member in inspect.getmembers(obj, lambda m: isinstance(m, property)):
            if "return" in _annotations(member.fget):
                types[key] = _text(_annotations(member.fget)["return"])
        sections = {"Attributes": types}
    else:
        return
    result, section, index = [], None, 0
    while index < len(lines):
        line = lines[index]
        result.append(line)
        underlined = (
            bool(line) and index + 1 < len(lines) and re.fullmatch(r"-{3,}", lines[index + 1])
        )
        if underlined:
            section = line
            result.append(lines[index + 1])
            index += 2
            kind = {"Returns": returns, "Yields": yields}.get(section)
            if kind:  # a prose-only description becomes ``type`` plus an indented description
                result.append(kind)
                while index < len(lines) and not (
                    lines[index]
                    and index + 1 < len(lines)
                    and re.fullmatch(r"-{3,}", lines[index + 1])
                ):
                    result.append(("    " + lines[index]) if lines[index] else lines[index])
                    index += 1
            continue
        if section in sections and line and not line.startswith(" ") and line in sections[section]:
            result[-1] = f"{line} : {sections[section][line]}"
        index += 1
    lines[:] = result


def _drop_object_base(app, name, obj, options, bases):
    """Hide the uninformative ``Bases: object`` line."""
    bases[:] = [base for base in bases if base is not object]


def _hide_model_signature(app, what, name, obj, options, signature, return_annotation):
    """Hide a pydantic model's constructor signature: the Attributes section lists its fields."""
    if what == "class" and hasattr(obj, "model_fields"):
        return "", None
    return None


def _head_tags(app, pagename, templatename, context, doctree):
    """Add the icon links to every page, and describe the home page by the package summary."""
    pathto = context["pathto"]
    context["metatags"] = context.get("metatags", "") + (
        f'<link rel="icon" type="image/png" sizes="32x32" '
        f'href="{pathto("_static/brand/icon-tile-32.png", 1)}">\n'
        f'<link rel="apple-touch-icon" sizes="180x180" '
        f'href="{pathto("_static/brand/icon-tile-180.png", 1)}">\n'
    )
    if pagename == "index":  # not the README's badge text
        app.env.metadata[pagename]["og:description"] = summary
        context["metatags"] += f'<meta name="description" content="{html.escape(summary)}">\n'


def setup(app):
    """Register the hooks; the type hook runs before numpydoc reads the sections."""
    app.connect("autodoc-process-docstring", _add_types, priority=400)
    app.connect("autodoc-process-bases", _drop_object_base)
    app.connect("autodoc-process-signature", _hide_model_signature)
    app.connect("html-page-context", _head_tags, priority=400)
