<!-- ©AngelaMos | 2026 -->
<!-- template-operations.md -->

# Template operations and release

The source checkout is `/home/yoshi/dev/templates`, configured for
`CarterPerez-dev/Fullstack-setup`. The local `template` symlink reads this checkout.
An installed release reads its embedded manifest and downloads a single pinned
variant archive. A generated application has no synchronization relationship with
either source; fix recurring problems in this repository and regenerate a clean
test project before releasing the fix.

## Development and production

Generate outside this repository, enter the generated directory, then inspect
`just --list`. Use `just dev-up` for the Python stacks and no-auth frontend,
`just dev` for the standalone Go API, and the root `justfile` for Go + React.
Every Compose invocation must use its matching `--env-file`. Production and
development have distinct literal Compose namespaces and generated credentials.

`--install` optionally installs host dependencies with `uv` or `pnpm` using locked
versions. It reports failures and preserves the generated project for diagnosis.
Docker startup performs its own dependency installation. Services run in Docker;
the generator does not start them or contact an existing application database.

Production browser refresh cookies require HTTPS. The Go web client explicitly
requests HttpOnly cookies with `X-Auth-Transport: cookie`. Native/JSON clients
receive refresh tokens in the response body. The standalone React and Expo
variants currently implement the FastAPI contract, not the Go contract.

For Expo on a physical device, set `DEV_HOST` to the development computer's LAN
address and `EXPO_PUBLIC_API_URL` to a backend URL reachable from that device.
`localhost` on a phone refers to the phone. Expo public variables belong in the
client bundle and must never contain credentials. Production API URLs must be
HTTPS. Run Metro through the generated Docker recipe; native signing and device
installation still require the platform's normal build workflow.

## Administrator enrollment

Public FastAPI and Go registrations create ordinary users. Portfolio public
registration is disabled. `ADMIN_EMAIL` does not grant a public signup an elevated
role. Create an owner explicitly from the trusted server console after startup
and migrations.

For a Python stack:

```bash
docker compose --env-file .env.development -f dev.compose.yml exec backend python -m admin --email owner@example.com
```

For the standalone Python API use service `api` instead of `backend`. The command
prompts twice without echoing the password. For production select `.env` and
`compose.yml`. Password-manager automation can use `--password-stdin` with
Compose `exec -T`. Do not put passwords in command arguments or shell history.

For Go, the `migrate` service uses the application image and database environment.
After the initial schema has been applied, feed a password through standard input:

```bash
IFS= read -r -s -p 'New administrator password: ' template_admin_password
printf '\n'
printf '%s\n' "$template_admin_password" | docker compose --env-file .env.development -f dev.compose.yml run --rm -T migrate -create-admin owner@example.com
unset template_admin_password
```

That example is for Bash. The password is not a command argument. Account creation
refuses duplicate addresses; it does not promote or overwrite an existing account.

## Session behavior

Refresh rotation consumes one token and creates one successor in a transaction.
Replaying a consumed token revokes its family, including a successor created by a
concurrent request. Clients serialize refresh requests inside one process. Separate
tabs/devices that reuse the same token can therefore trigger a sign-in requirement.

Password changes atomically replace the verified hash and advance the stored token
version. A stale password rehash cannot overwrite a newer password. Logout-all
advances the version as well. Access-token verification consults current user
state, and refresh tokens retain the version under which they were issued.
Go profile, role, and tier changes write only the requested column, so changing a
display name cannot restore a role or tier from a stale account snapshot.
Single-session logout revokes refresh capability; already-issued access tokens
can remain valid until their short expiry. It is not an immediate access-token
blacklist operation.

Python request sessions finish their commit before sending a successful response.
Clients share a refresh attempt within one local session. Login/logout changes
that session's version, so delayed responses and retries cannot update or execute
as a replacement session. A failed business request after successful refresh does
not by itself discard the session. Native secure-store operations run in order,
and explicit logout reports failed credential deletion. Browser cookie ordering
across tabs and actual device storage behavior still require platform validation.

Go JSON request bodies are limited to 1 MiB, including streamed bodies. Concurrent
password work has a 128 MiB admission budget; saturation returns HTTP 503 with
`Retry-After: 1`. This limits active Argon2 work, not total process memory. Measure
the application under its actual container memory limit before increasing it.

Application rate limits use the connection address, not unsigned JWT subjects or
arbitrary forwarded headers. Define a trusted ingress and its per-client limits
for a deployment. Go currently treats the direct proxy as one client; Python uses
the ASGI server's trusted client-address handling. Do not enable universal proxy
trust on an API reachable directly by untrusted clients.

## Database changes

New PostgreSQL 18 projects mount `/var/lib/postgresql`. Do not fix an existing
deployment by deleting its volume. Back up, prove restore, and perform a deliberate
version/layout migration separately.

Go migrations live in `migrations/NNN_description.sql`. They run under a database
advisory lock and transaction, record checksums, and reject modified/reordered
applied history. SQL files must not include their own transaction control.
Rollback requires an explicit forward repair or restore. An old unmanaged Go
database needs a reviewed adoption migration; the initial schema is for a fresh
database and deliberately does not silently accept preexisting tables.

FastAPI includes an Alembic migration adding refresh-token versions. Old tokens
default to version zero and may require users with higher versions to sign in.
Exercise migrations against a restored disposable database before deployment.

Portfolio migration `d74b10ce893f` adds true-only unique singleton keys to profile
and settings and media references with `ON DELETE SET NULL`. Existing duplicate
singletons or dangling references require a reviewed data repair; the migration
will not silently remove them.

Portfolio uploads persist file contents before committing metadata. Insert failure
removes the new file, while uncertain commit failure preserves it for reconciliation.
Media deletion commits before removing the file; failed cleanup logs
`media_cleanup_required` with its storage filename. Back up uploads with the
database. Automated orphan reconciliation and crash recovery remain release work.

## Go signing keys

Key initialization publishes complete files without replacing existing keys. It
stores the private key first, derives a missing public key from it, and validates
that an existing pair matches. Interrupted temporary PEM files are excluded from
template packaging. A damaged private key or an old public-only pair requires
restoring the matching private key; startup refuses to silently change identity.
Keep a protected backup of signing keys alongside the database recovery procedure.
JWT key IDs derive from the public key's SHA-256 thumbprint, so restarting with
the same key preserves the identifier published in JWKS.

## Local verification

Dependency candidates were refreshed on November 1. Start with:

```bash
just dependency-plan
just resolve-dependencies
```

The resolver runs pinned uv 0.13.6 through `uvx`, checks the effective pnpm
10.34.9 version, and selects Go 1.26.10 for the reviewed module tuple. It resolves
five Python projects, five web clients, the native client's currently declared
graph, and both Go modules. Use `python`, `web`, `native`, or `go` as the recipe's
argument to resume one group. It stops on failure and retains output in the
printed `/tmp/template-dependency-resolution-*` directory. Package managers
update manifests/locks; this command does not establish a fresh installation or
a passing test matrix. Inspect the resulting diffs before proceeding.

As of the November 1 preparation, Python/web manifests are ahead of their old
locks, both minimal examples need newly generated `uv.lock` files, and Go modules
still need the selected upgrades resolved. Frozen installs cannot pass until
this step succeeds. The native manifest has shared tooling/Axios/Babel updates
but still uses SDK 54; the coordinated supported-SDK migration remains required.

```bash
just check-template
just check-generated
just check-generated fastapi-stack development
just check-generated go-stack production
```

The runtime script creates a random project in a temporary directory and removes
only that project's containers and volumes. It checks builds, service readiness,
database/Redis connections, frontend documents, and combined-stack proxy routes.
It does not prove browser login, device behavior, backup/restore, or production TLS.
The default runs all 15 cases and reports every failure. Docker access is checked
before creating a project. The PostgreSQL backend test jobs in CI remain separate
from this startup matrix.

Recent dependency evidence and candidate upgrade targets are recorded in
`docs/research/2026-11-01-python-upgrade.md`,
`docs/research/2026-11-01-go-infra-upgrade.md`, and
`docs/research/2026-11-01-web-native-upgrade.md`. These are not resolved lockfiles. Run
registry-backed resolution and fresh locked installations before treating any
candidate as the release graph.

Set `TEST_POSTGRES_URL` to a disposable PostgreSQL database for backend tests.
Python configuration also requires `DATABASE_URL`, `SECRET_KEY`, and a development
`ENVIRONMENT`; use disposable fixture values as the CI workflow does.
Python expects a `postgresql+asyncpg://` URL; Go expects `postgres://`. Tests create
random isolated schemas and remove those schemas afterward. Portfolio requires
PostgreSQL because its models use JSONB. The dedicated Python session tests in
`tests/release/test_python_security.py` run outside the regular conftest so their
commit/rollback and concurrency checks exercise independent sessions.

The CI workflow checks all variants and blocks its packaging job on lint, types,
builds, real PostgreSQL tests, dependency audits, generated Docker startup, and
Expo export. Browser/device validation remains an additional release gate.

## Publishing

1. Review the audit's unresolved findings, update vulnerable locked dependencies,
   and pass the complete CI matrix plus browser and device checks.
2. Review the dirty checkout and stage only intended source changes. Preserve the
   preexisting work. Verify the live remote and reconcile its history without
   discarding local changes or force-pushing.
3. Build from a clean reviewed commit with
   `just package v0.1.0 /tmp/template-v0.1.0`. Development `--allow-dirty` artifacts
   are explicitly marked and must never be published.
4. Publish the version tag and all eight archives, `template.pyz`, `release.json`,
   `checksums.txt`, `install.sh`, and `uninstall.sh` to the matching GitHub release.
   Make the release immutable where supported.
5. Serve the exact installer bytes at
   `https://angelamos.com/template/install.sh`. The website source convention is
   `~/dev/design/001/frontend/public/template/install.sh`. Hosting and deployment
   require their own verified change; documentation does not deploy a URL.
6. Fetch that exact public URL into a fresh isolated installation, verify the
   installed version and source revision, generate each variant, and run its
   checks. Test update, checksum failure, unrelated-command protection, and
   uninstall as well.

The installer can configure PATH for future shells, but a piped child process
cannot change its parent shell's environment. It prefers an existing writable PATH
directory and reports an activation command when a new directory is necessary.
Do not describe that case as immediate parent-shell activation.
