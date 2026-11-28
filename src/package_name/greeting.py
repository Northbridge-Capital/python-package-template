"""A sample public function that follows the docstring convention; replace it with your API."""

from __future__ import annotations


def greet(name: str, *, shout: bool = False) -> str:
    """Return a greeting.

    Parameters
    ----------
    name
        Who to greet.
    shout
        Whether to upper-case the greeting. Default: ``False``.

    Returns
    -------
    The greeting.
    """
    text = f"Hello, {name}!"
    return text.upper() if shout else text
