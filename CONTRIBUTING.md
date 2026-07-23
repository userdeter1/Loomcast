# Contributing to Loomcast

Welcome to Loomcast! Thanks for taking the time to contribute. Please follow the
guidelines below.

## 1. Local setup and running the tests

Before submitting your changes, install the project with its development
dependencies, enable the pre-commit hooks, and run the test suite:

```bash
# Editable install with dev dependencies
pip install -e ".[dev]"

# Install the pre-commit hooks locally
pre-commit install

# Run the unit tests (integration tests are skipped automatically)
pytest -v

# Run the integration tests manually (requires a running local runtime)
pytest -m integration

# Check code style with Ruff
ruff check .

# Run every pre-commit hook manually
pre-commit run --all-files
```

> **Note**: `pytest` without `-m` skips integration tests automatically, thanks
> to `addopts = "-m 'not integration'"` in `pyproject.toml`.

## 2. Branch naming convention

Please use a descriptive branch name tied to the issue or feature you are
working on:

- Format: `issue-<number>-<short-description>`
- Example: `issue-1-cache-content-addressed` or `issue-4-fix-cli-documentation`

## 3. Pull request workflow

- **Target branch**: all pull requests must target `main`.
- **CI must pass**: the CI workflow (unit tests on Python 3.9 through 3.12, Ruff
  lint, and Gitleaks secret scanning) must be green before a PR can be merged.
- **Code review**: PRs are reviewed by the project maintainer before merging. If
  the project gains more contributors, a CODEOWNERS file may be added to
  formalise cross-review.
- **Documentation updates**: if you add or change a CLI command, update
  `README.md` accordingly.

## 4. Versioning and release procedure

Loomcast follows [Semantic Versioning (SemVer 2.0.0)](https://semver.org/).

When preparing a new release:

1. Update the version number in `pyproject.toml` (`version = "X.Y.Z"`).
2. Document the changes in `CHANGELOG.md` under a new `[X.Y.Z]` section.
3. Open a release PR against `main`.
4. Once the PR is merged, create and push the matching Git tag:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
5. **Automatic publication to TestPyPI**: the `.github/workflows/release.yml`
   workflow runs automatically to build the `sdist` / `wheel` artifacts, create
   the GitHub release, and publish the packages to **TestPyPI**.
6. **Verify the install from TestPyPI**: in a temporary isolated virtual
   environment, test installing the published package:
   ```bash
   python -m venv .venv-test
   # Linux/macOS: source .venv-test/bin/activate
   # Windows:     .venv-test\Scripts\Activate.ps1
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ loomcast
   python -c "import loomcast"
   loomcast --help
   ```
7. **Manual publication to production PyPI**: once the release is validated on
   TestPyPI, trigger the workflow manually from GitHub (*Actions* tab →
   *Release* → *Run workflow* → tick `Publish package to production PyPI`).

## 5. Pinning and updating GitHub Actions (SHA pinning)

Every third-party GitHub Action in `.github/workflows/` must be pinned to a
**full 40-character commit SHA**, for security and immutability (supply chain
security).

When a third-party action needs updating (e.g. `actions/checkout`,
`actions/setup-python`, `softprops/action-gh-release`,
`pypa/gh-action-pypi-publish`):

1. **Identify the new version/tag** you want on the action's official repository.
2. **Resolve the matching full SHA** for that exact tag:
   ```bash
   git ls-remote https://github.com/<owner>/<repo>.git refs/tags/<tag>
   # Example for actions/checkout:
   git ls-remote https://github.com/actions/checkout.git refs/tags/v4
   ```
3. **Update the workflow file** (`ci.yml` or `release.yml`) with the new
   40-character SHA, and update the version comment next to it:
   ```yaml
   uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4
   ```
4. **Test and confirm** that the workflows run successfully on GitHub Actions
   after the SHA update.

## 6. Dependency monitoring (Dependabot) and local hooks (pre-commit)

- **Dependabot**:
  `.github/dependabot.yml` configures two weekly monitoring targets (`pip` for
  `pyproject.toml` and `github-actions` for the workflows). Dependabot opens
  update PRs automatically every week.
  *Merge policy*: auto-merge is not enabled. Every Dependabot PR must be
  reviewed manually and pass the full CI pipeline before being merged into
  `main`.

- **Pre-commit**:
  The local hooks configured in `.pre-commit-config.yaml` run end-of-line
  cleanups, TOML validation, and the Ruff linter/formatter before each local
  commit (`pre-commit run --all-files`). `pytest` is deliberately excluded to
  keep commits fast; full test validation is handled by CI.
