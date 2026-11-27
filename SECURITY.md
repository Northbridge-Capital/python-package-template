# Security

<!-- Describe what this package does with credentials, network access and user input, and what
it deliberately does not do. Replace this comment with that paragraph. -->

## Reporting a vulnerability

Please report vulnerabilities **privately** through GitHub: open the repository's
[Security tab](https://github.com/Northbridge-Capital/REPLACE_ME/security) and choose
"Report a vulnerability". Do not open a public issue. Include the affected version and steps to
reproduce, and never include real credentials or data.

## Supported versions

Only the latest release receives fixes while the project is `0.x`.

## Supply chain

Releases are built and published by GitHub Actions through PyPI trusted publishing, with no
stored token, and carry PyPI's build attestations. Workflow actions are pinned to commit SHAs and
the workflows are audited by `zizmor` on every pull request.
