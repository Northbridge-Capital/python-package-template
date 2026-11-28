# Contributing

Thanks for helping. Bug reports, fixes, docs and features are all welcome; for anything
larger than a small fix, please open an issue first so we can agree on the approach.

## Setup and checks

Requires [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just).

```bash
just sync   # install dependencies
just lint   # ruff, ruff format, basedpyright
just test   # pytest with coverage
```

CI runs the same checks on every pull request (the aggregate `ci-required` job passes only when all
of them do, and is the single check meant for branch protection): lint and types, the documentation build, the tests on Linux, macOS and
Windows across the supported Python range, the tests against the **lowest** dependency versions that
`pyproject.toml` allows, and a build check (`twine check`, clean-environment import).

## Where things are

- `src/`: the package.
- `tests/`: unit tests, including the docstring and API-reference checks.
- `docs/`: the Sphinx documentation; `docs/api.rst` lists the public API.

## Design rules

- **Lean.** Keep the dependency list short; adding a new one needs a real case, not "might be
  useful later." Delete rather than deprecate, and no options kept "just in case".
- **One source of truth.** No logic or constant maintained in two places.
- **Docs move with the code.** README, docstrings, comments and `CHANGELOG.md` (under
  `[Unreleased]`) must be correct in the same pull request.
- **Never print or log credentials.**

## Docstrings

All docstrings in `src/` use the NumPy style. Tests are exempt.

**Public and private.** A name is *public* if the package exports it in `__all__`; everything
else is *private*: names with a `_` prefix, and anything inside a private (`_`-prefixed) module.

**Private functions and classes** get a one-line docstring in imperative mood, ending with a
period, within 100 characters, and no sections. Anything that does not fit on one line (a
rationale, a constraint) goes in a comment above the definition.

```python
def _quote(identifier: str) -> str:
    """Quote an identifier for use in a query."""
```

**Public functions** get a summary line, an optional short description, then these sections in
this order, each omitted when it does not apply:

- **Parameters**: one entry per parameter, in signature order: the name, then an indented
  description. State the default when it is not obvious.
- **Returns**: a prose description of the value. Omitted when the function returns `None`.
  A generator function, including a `@contextmanager`, documents **Yields** instead.
- **Raises**: one entry per exception the function documents, as a package error or a built-in
  exception class name, then when it is raised.

```python
def load(path: Path, *, limit: int | None = None) -> list[str]:
    """Read the lines of a text file.

    Parameters
    ----------
    path
        The file to read.
    limit
        Maximum number of lines. Default: all of them.

    Returns
    -------
    The lines, without their line endings.

    Raises
    ------
    FileNotFoundError
        ``path`` does not exist.
    """
```

**Public classes** get a summary line, an optional short description, then these sections, each
omitted when empty (a bare exception has only its summary):

- **Attributes**: one entry per field or attribute, then one per public property, in
  definition order: the name, then an indented description. Dataclass and pydantic fields are
  documented here, not inline. A property's own docstring is a one-line noun phrase ending
  with a period, with no sections.
- **Methods**: one entry per public method: the name, then an indented one-line description,
  with no signature. Properties, private methods and dunders are left out. The names must
  match the class's public methods, in definition order. Each listed method also has its own
  docstring that follows the function rules above.

```python
class Account:
    """A customer account.

    Attributes
    ----------
    name
        The customer's name.
    balance
        Current balance, in cents.
    is_empty
        Whether the balance is zero.

    Methods
    -------
    deposit
        Add money to the balance.
    """
```

**Style.**

- **No types in docstrings**: the annotation in the signature is the single source of truth.
- Function summaries are imperative ("Read the lines..."); class summaries are noun phrases
  ("A customer account..."). Every description ends with a period.
- Inline code uses double backticks: ``name``.
- Every module has a docstring: a one-line summary, optionally followed by a short paragraph.
- A nested function, if one is ever added, gets a one-liner.

**Enforcement.** CI runs `ruff`'s pydocstyle rules with the `numpy` convention (section
formatting) and `tests/test_docstrings.py` (an AST check, no extra dependency). The test
verifies that every function and class has a docstring, that private ones are one-liners, that
public functions list exactly their parameters in order and have `Returns` (or `Yields`)
exactly when they return (or yield) a value, that `Raises` names only package errors or
built-in exceptions, and that public classes list exactly their fields and properties under
`Attributes` and their public methods under `Methods`.

## Documentation

The API reference is generated with [Sphinx](https://www.sphinx-doc.org/) from the docstrings
and type annotations: `numpydoc` renders the NumPy-style sections in the `pydata-sphinx-theme`.
The README, the changelog and this guide are included as pages; add your own to the `toctree`
in `docs/index.md`. The site is published to GitHub Pages on every push to `main`.

- **Preview** with `just docs` (live reload). `just docs-build` builds it the way CI does:
  warnings are errors.
- **Adding a public name:** list it in `docs/api.rst` under the right heading.
  `tests/test_api_reference.py` fails if a name in `__all__` is missing.
- **Types** are never written in docstrings; `docs/conf.py` adds them to the rendered
  parameter lists from the annotations.
- The Sphinx packages live in the separate `docs` dependency group, so they never affect the
  runtime dependencies.

## Pull requests

1. Fork the repository (or branch, if you are a maintainer) and branch off `main` using
   `feature/…`, `fix/…`, `docs/…` or `chore/…`.
2. Open a pull request against `main`. Branches are merged by **squash**, so the pull request
   title becomes the commit message: make it a short imperative summary.
3. A code owner must approve before merging (`.github/CODEOWNERS`); other reviews are welcome
   but do not satisfy the merge rule. An author cannot approve their own pull request, so a
   code owner should not open the pull request they are meant to approve.

## Releasing

Releases are tags on `main`; consumers pin a tag. Tags matching `v*` are protected: they
cannot be moved or deleted except by organisation admins, so check before you tag, and never
reuse a version.

1. In a pull request, bump `version` in `pyproject.toml`, run `uv lock` (CI uses `--locked`),
   and in `CHANGELOG.md` move the `[Unreleased]` entries under the new version with its date.
   Merge it.
2. Dry-run the release: Actions > **Release** > Run workflow, on `main`. It performs the same
   checks and build as a real release but publishes nothing (tick `testpypi` to also upload the
   build to TestPyPI, once per version). Fix anything it reports; tags cannot be undone, so do
   not skip this.
3. A maintainer tags the merge commit and pushes the tag:

   ```bash
   git switch main && git pull
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```

4. The `Release` workflow checks that the tag is on `main` and equals the `pyproject.toml`
   version, builds the package, and publishes a GitHub Release (that version's `CHANGELOG.md`
   section as the notes, wheel and sdist attached; it fails if the changelog has no section for
   the version). The PyPI upload then waits for a reviewer to approve the `pypi` environment
   (Actions run > Review deployments).
5. Consumers bump their pin to the new version.

### How PyPI publishing is configured

The `Release` workflow publishes with PyPI **trusted publishing** (GitHub's OIDC identity), so no
token or secret is stored anywhere. It relies on two settings outside this repository's code:

- A trusted publisher on the PyPI project: owner `Northbridge-Capital`, repository
  `REPLACE_ME`, workflow `release.yml`, environment `pypi`.
- A GitHub environment named `pypi` on this repository (managed in the infrastructure repo's
  Terraform) with a required reviewer, limited to `main` and `v*` tags.

The `testpypi` dry run uploads to test.pypi.org, which is a separate site with separate accounts;
it needs its own trusted publisher with the same values (not set up yet).

PyPI files are immutable: a version can be uploaded exactly once. If the publish step fails
before uploading (for example a misconfigured publisher), fix the setting and re-run only the
failed job; no new version is needed. If a bad release does get uploaded, yank it and cut a new
version.
