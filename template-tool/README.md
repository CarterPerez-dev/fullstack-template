<!-- ©AngelaMos | 2026 -->
<!-- README.md -->

# template

One project generator for a local checkout and versioned public downloads.
The public command is a small Python zipapp. It downloads only the requested
template archive and verifies its embedded SHA-256 checksum before extraction.
Python 3.10 or newer is required; no Python package dependencies or rsync are needed.

The public release focuses on web/backend starters. Native remains experimental
with Docker, binary, and device validation deferred. See the
[release audit](../docs/plans/2026-10-25-template-release-audit.md) for recorded
results and integration gaps. Installation requires the GitHub assets and hosted
installer to have been published.

## Local development

```bash
just install
template list
template fastapi billing-service
template fastapi-stack my-app
template go-stack shop --owner your-account
template portfolio my-site
```

`just install` retains the development symlink into this checkout. Changes here
affect subsequent local generation. It refuses to overwrite another installation.

An installed release can explicitly use a checkout:

```bash
template fastapi my-api --source /path/to/fullstack-template
```

With no project name, generation uses the current empty directory. An existing
`.git` directory is preserved. Existing project files are never overwritten;
the old unsafe `--force` flag is no longer supported.

## Public installation after publication

The installer URL is:

```bash
curl -fsSL https://angelamos.com/template/install.sh | bash
template list
template fastapi-stack my-app
```

The installer resolves `latest` to a concrete release tag before downloading.
`--version v0.1.0` pins a specific release. `--prefix DIR` selects a command
directory. Re-running the installer updates an existing release installation
after checksum verification. An existing local development symlink is preserved.

The installer prefers a directory already on PATH. If none is writable, it can
configure the user's shell startup file and prints the exact activation command
for the existing parent shell. A piped child process cannot change its parent's
environment. `--no-modify-path` disables shell configuration changes.

`uninstall.sh --prefix DIR` removes a verified release command while preserving
generated projects and shared PATH configuration.

## Variants

| Command | Source | Contents |
| --- | --- | --- |
| `go` | `backends/go-backend` | Go API |
| `fastapi` | `backends/fastapi` | FastAPI API |
| `open` | `frontends/open` | React without authentication, with Docker |
| `frontend` | `frontends/auth/react-scss` | React authentication client |
| `native` | `frontends/auth/react-native` | Experimental Expo authentication client |
| `fastapi-stack` | `stacks/fastapi-react` | FastAPI and React |
| `go-stack` | `stacks/go-react` | Go and React |
| `portfolio` | `stacks/portfolio` | Editable portfolio |

All eight archives remain available. Native is excluded from the web/backend
release gate; its optional CI workflow input retains the deferred checks.

`template --version` identifies the command. `template info` shows its release
metadata. Every generated project has `.template.json` with its template, source
revision, release version, dirty-source status, and whether port probing was
available. It contains no generated credentials.

## Initialization and safety

- Local generation and release packaging use the same exclusion policy.
- Real `.env` and `.env.*` files are excluded; only `.example` env files are copied.
- Private keys, dependency directories, uploads, caches, and build output are
  excluded. Source symlinks and special files are rejected.
- Archives reject traversal paths, symlinks, hard links, duplicates, special
  entries, oversized content, and unexpected private files before extraction.
- A fresh `.env` is created from each applicable example. Directories with a dev
  Compose definition also receive `.env.development`. Their permissions are 0600.
- New generated secret keys and PostgreSQL/Redis passwords are independent between
  environments. This does not replace each stack's credential/startup validation.
- Assigned host ports fall between 30000 and 60000, with distinct dev/prod values.
  Availability is checked when socket access is permitted. It is an observation,
  not a reservation; restricted environments emit a warning and record the limit.
- `--no-git` skips Git initialization. `--install` runs locked dependency installs;
  failures return nonzero and leave the generated project available for diagnosis.

Scaffolding does not start containers or apply database migrations. Review a
generated project's `just` commands for its lifecycle.

## Verification and packaging

```bash
just check-template
just package v0.1.0 ../.template-checks/template-v0.1.0
```

A normal package build requires a clean checkout and a new output directory
outside the repository. It produces eight archives, `template.pyz`, `release.json`,
the installer and uninstaller, and `checksums.txt`. Archives include the repository
license. Builds from unchanged inputs produce identical bytes.

For an isolated development test only:

```bash
python3 -B template-tool/release.py --version v0.1.0-test --output /tmp/template-test-assets --allow-dirty
bash install.sh --from /tmp/template-test-assets --prefix /tmp/template-test-bin --no-modify-path
/tmp/template-test-bin/template open demo --release-dir /tmp/template-test-assets --no-git
bash uninstall.sh --prefix /tmp/template-test-bin
```

Dirty builds are explicitly identified and rejected by the public installer.
Do not publish development artifacts. `just publish v0.1.0` verifies the live
remote and fast-forwards the current/default branches plus tag atomically. It
waits for GitHub's web/backend release checks and verifies the published assets.
History divergence or a conflicting version stops publication without force.

The maintainer can include installer deployment from the clean Angelamos checkout:

```bash
just publish v0.1.0 /home/yoshi/dev/design/001
```

That additionally pushes the website's current branch, rebuilds/recreates only
nginx, verifies the exact public installer bytes, and performs an isolated public
installation plus FastAPI/React, Go/React, and open-web generation. It preserves
the existing local `template` command. GitHub authentication, registry/network
access, and the website's existing Docker context are required. Use
`python3 -B template-tool/publish.py v0.1.0 --website /path/to/website --plan`
to inspect the steps without network access or writes.
