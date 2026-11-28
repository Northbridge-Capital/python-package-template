# python-package-template

Scaffold for a new public Python package at Northbridge Capital. Starting point, not a managed
dependency: everything here is yours to change once you've created a repo from this template.

## Using this template

1. Create a new repo from this template (`gh repo create Northbridge-Capital/<name> --template
   Northbridge-Capital/python-package-template --public`), or provision it via the
   `terraform` repo's `stacks/github/org` so it gets the full public-package governance
   (branch protection, tag protection, `pypi` environment, GitHub Pages, etc). A repo created
   some other way needs Pages enabled by hand (Settings, Pages, Source: GitHub Actions), or the
   `Docs` workflow fails.
2. Clone it, then run:

   ```bash
   scripts/init.sh <repo-name> "<one-line description>"
   ```

   This renames `src/package_name` to your import name, fills in the package name/description/
   URLs across `pyproject.toml`, `CONTRIBUTING.md`, `SECURITY.md` and `docs/`, and deletes
   nothing for you — review the diff.
3. Delete `scripts/init.sh`, fill in the `<!-- -->` placeholder in `SECURITY.md`, write a real
   `README.md`, replace the sample `greet` function (and its entry in `docs/api.rst`) with
   your API, and start building. The documentation publishes to
   `https://northbridge-capital.github.io/<name>/`.

## What's included

- `pyproject.toml`: hatchling build, `ruff` + `basedpyright` configured, `pytest` with coverage.
- `.github/workflows/ci.yml`: lint, type-check, tests (Linux/macOS/Windows, two Python versions),
  lowest-dependency tests, build check, and the `ci-required` job that infrastructure's branch
  protection gates on.
- `.github/workflows/release.yml`: tag `v*` on `main` to build, publish a GitHub Release, and
  publish to PyPI via trusted publishing (no stored token). Also runnable by hand as a dry run.
- `docs/` and `.github/workflows/docs.yml`: a Sphinx API reference generated from the
  docstrings (`numpydoc`, `pydata-sphinx-theme`), built strictly in CI and
  published to GitHub Pages on every push to `main`. `tests/test_docstrings.py` and
  `tests/test_api_reference.py` keep the docstrings and `docs/api.rst` complete.
- `.github/dependabot.yml`: weekly version updates for GitHub Actions and Python dependencies,
  with a one-week cooldown.
- `Justfile`: `just sync` / `just lint` / `just test` / `just docs` / `just docs-build`.
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`: process docs, mostly
  generic as written.
- `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`: generic issue/PR forms --
  tighten them once the package has real, package-specific things to ask about.

## What's deliberately not included

This is a one-time scaffold, not something kept in sync afterward. In particular, GitHub repo
governance (branch protection, tag protection, CODEOWNERS, the `pypi` and `github-pages`
environments, GitHub Pages itself, secret scanning, Dependabot security updates) is managed by
Terraform in the `terraform` repo, not by this template —
see that repo's README for the full pattern.
