# python-package-template

Scaffold for a new public Python package at Northbridge Capital. Starting point, not a managed
dependency: everything here is yours to change once you've created a repo from this template.

## Using this template

1. Create a new repo from this template (`gh repo create Northbridge-Capital/<name> --template
   Northbridge-Capital/python-package-template --public`), or provision it via the
   `terraform` repo's `stacks/github/org` so it gets the full public-package governance
   (branch protection, tag protection, `pypi` environment, etc).
2. Clone it, then run:

   ```bash
   scripts/init.sh <repo-name> "<one-line description>"
   ```

   This renames `src/package_name` to your import name, fills in the package name/description/
   URLs across `pyproject.toml`, `CONTRIBUTING.md` and `SECURITY.md`, and deletes nothing for
   you — review the diff.
3. Delete `scripts/init.sh`, fill in the `<!-- -->` placeholder in `SECURITY.md`, write a real
   `README.md`, and start building.

## What's included

- `pyproject.toml`: hatchling build, `ruff` + `basedpyright` configured, `pytest` with coverage.
- `.github/workflows/ci.yml`: lint, type-check, tests (Linux/macOS/Windows, two Python versions),
  lowest-dependency tests, build check, and the `ci-required` job that infrastructure's branch
  protection gates on.
- `.github/workflows/release.yml`: tag `v*` on `main` to build, publish a GitHub Release, and
  publish to PyPI via trusted publishing (no stored token). Also runnable by hand as a dry run.
- `Justfile`: `just sync` / `just lint` / `just test`.
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`: process docs, mostly generic as written.

## What's deliberately not included

This is a one-time scaffold, not something kept in sync afterward. In particular, GitHub repo
governance (branch protection, tag protection, CODEOWNERS, the `pypi` environment, secret
scanning, Dependabot) is managed by Terraform in the `terraform` repo, not by this template —
see that repo's README for the full pattern.
