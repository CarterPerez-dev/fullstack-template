<!-- ©AngelaMos | 2026 -->
<!-- template-operations.md -->

# Template operations and release

The source checkout is `/home/yoshi/dev/templates`, configured for
`CarterPerez-dev/Fullstack-setup`. The local `template` symlink reads this checkout.
An installed release reads its embedded manifest and downloads a single pinned
variant archive. A generated application has no synchronization relationship with
either source; fix recurring problems in this repository and regenerate a clean
test project before releasing the fix.

As of November 8, the current priority is the web/backend templates and public
distribution. Carter has deferred React Native Docker/device verification and
stopped the repeated manual Docker matrix loop. The existing commands below
remain available; they are not another requested manual assignment. Preserve
the recorded passing results and disclose unexecuted combined-stack/browser
checks when describing release readiness. The current scope and evidence are in
`docs/plans/2026-10-25-template-release-audit.md`.

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
This variant targets iOS and Android. Its SecureStore authentication has no browser
storage adapter; use a web variant for a browser application.

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

Dependency candidates were refreshed on November 1, with a client audit follow-up
on November 2. Start with:

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
a passing test matrix. Client resolution refreshes nested dependencies with
`pnpm update --depth Infinity --lockfile-only --no-save`, preserving declared
ranges and exact pins. It then runs `pnpm install --resolution-only` with strict
peer checks; pnpm's update step alone can report a peer warning without failing.
Inspect the resulting diffs before proceeding.

Missing pinned tool versions may be downloaded into the managers' caches.
Corepack uses each client's declared pnpm version; its update banner does not
change that pin. Go downloads its selected toolchain alongside existing versions.
The resolver fails on peer conflicts and prints a group-specific resume command
when interrupted. A cancelled run preserves lockfiles from completed projects.

On November 2, the first complete fresh-install run finished all 13 projects.
Five Python and two Go projects passed. The Go audits found no affected calls,
but reported one required-module advisory, later identified as GO-2026-5932 in
unused OpenPGP packages. PostgreSQL cases skipped in that dependency-only run.
The subsequent Zod 4.6.6 follow-up passed all five web
clients' fresh installations, builds, regressions, and production audits, with
no known vulnerabilities reported. Native's first SDK 58 resolution failed on
an old Metro runtime peer; its later type check also exposed a Tamagui input
declaration mismatch. Metro is now explicit, and a recorded declaration patch
fixes the type error. Native's deep dependency refresh also required migrating
Biome's configuration and recognizing its four existing card text components.
The fresh report at `/tmp/template-dependency-check-ar8prrrn` passes installation,
Expo alignment, lint/types, all 14 authentication/storage cases, and both exports.
Its audit reduced 34 findings to two moderate advisories in glob and minimatch,
with no high or critical findings. Repairing only the reported CLI path exposed
other Expo parents sharing the old versions in the next audit.

The manifest now scopes patched dependency overrides to all five affected Expo
parents, including fingerprint's direct minimatch dependency. The genuine lock
resolves every production reference to glob 14.0.3 and minimatch 11.0.4. Eleven
tooling compatibility cases were added. The final native report at
`/tmp/template-dependency-check-dt4bpkh_/report.json` passes fresh strict installation,
Expo alignment, lint/types, all 25 regressions, both exports, and a production
audit with zero advisories. Its recorded inputs match the checkout. Native binary
and device testing remain separate. No repeat dependency run is required unless
its inputs change or a new advisory requires investigation.

Native's Tamagui 1.144.1 patch changes only its input instance declaration. It is
part of the generated project, copied into Docker before dependency installation,
and applied by pnpm. Reassess or remove it when upgrading Tamagui; a missing or
inapplicable patch must fail installation. Do not disable strict peer checks to
get through a migration. pnpm may write a lock before reporting a resolver error,
and a subsequent frozen install may skip peer resolution. Chain the commands
with `&&` when verifying an upgrade:

```bash
just resolve-dependencies native && just check-dependencies native
```

Validate fresh installations after resolving the locks:

```bash
just dependency-check-plan
just check-dependencies
just check-dependencies web
```

The check command copies selected projects into a fresh temporary directory,
excluding installed environments, caches, and private files with the generator's
filters. It performs locked installs, applicable lint/types/build/local regression
checks, and production dependency audits. Missing packages and audit tools are
downloaded. Source environments and lockfiles are preserved, and any change to a
copied manifest, lock, or dependency patch fails that project. Use `python`,
`web`, `native`, or `go` to select a group. A failure stops that project's commands while later projects
continue. Ctrl-C stops the active process and retains completed results.
Native also checks Expo package alignment and exports iOS and Android bundles.
Those exports do not build or install native binaries.
Its tooling regressions exercise Expo's actual file discovery, routing, native
project paths, workspace matching, fingerprint ignores, and cancellation behavior.
The generated native project's `DEPENDENCIES.md` records why the scoped overrides
exist and when to remove them.

Client audits use `pnpm audit --prod --json` locally and in CI. Full advisory
details are retained in the log, and any reported severity fails the check.
This replaces the earlier high-only threshold, which also hid moderate and low
advisory details in its output. Do not disable checks or ignore advisories to
turn a failing dependency graph into a passing release result.

Projects, logs, and a JSON report remain under the printed
`template-dependency-check-*` directory for inspection. The report records
the exact manifest, lock, and dependency patch hashes for each project. This
command intentionally does not connect to a PostgreSQL test database or start application services;
Go's database cases skip. Python runs the isolated HTTP/lifespan regressions.
Run the full PostgreSQL and Docker gates separately after compatibility checks.
The script's explicit `--offline` mode uses cached packages and skips dependency
audits, so its result cannot satisfy the audit gate.

By default, the terminal shows commands and results while full child output goes
to the log. To stream it as well, run
`python3 -B tests/release/check_dependencies.py web --verbose`. A lost terminal
scrollback does not prevent inspection of the saved logs and report. New
verification workspaces live in `.template-checks` beside the source checkout,
on its filesystem instead of the system temporary directory. Override this with
`TEMPLATE_CHECK_ROOT=/path/on/disk` outside the checkout. Child processes also
use that workspace for temporary files. Each workspace is private and needs at
least 2 GiB free to start; the generated matrix checks again before each case.
Reports are replaced atomically so a partial write cannot truncate earlier
results. Older reports retained in `/tmp` still need preservation before reboot
or temporary-directory cleanup.

```bash
just check-template
just check-postgres
just check-postgres go
just check-generated
just check-generated fastapi-stack development
just check-generated go-stack production
```

`just check-postgres` starts one disposable PostgreSQL 18 container on a random
high loopback port. Each of the three Python and two Go backends gets its own
database and a clean source copy. It runs their full test suites, dedicated
Python session/portfolio regressions, Python migrations, and verbose Go
vulnerability scans. Use `python` or `go` to select a group. No live environment
files are loaded. Projects, logs, input hashes, and the report remain under the
printed `template-postgres-check-*` directory; the fixture container and its
volume are removed afterward. The Go scan still needs network access even when
module downloads are cached.

The generated runtime script creates random projects in a private temporary
directory and removes only each project's containers and volumes. It checks builds, service readiness,
database/Redis connections, frontend documents, and combined-stack proxy routes.
It does not prove browser login, device behavior, backup/restore, or production TLS.
The default runs all 15 cases and reports every failure. It refreshes build base
images, validates the disposable Docker namespaces before starting or cleaning
anything, and uses generated environment values without ambient shell overrides.
Projects, rendered configuration, command/service logs, per-case results, and the
report remain under the printed `template-runtime-check-*` directory.
Rendered configuration stays outside Docker build contexts. Ctrl-C cancels the
active command, attempts cleanup, and retains the interrupted case's result.
Both commands check Docker access before creating fixtures. The PostgreSQL tests
remain separate from the generated startup matrix, locally and in CI.

Run them in order with `just check-postgres && just check-generated`. Full command
output goes to the saved logs. Retained fixtures contain generated credentials;
keep the private workspace intact when investigating a failure.

The November 2 PostgreSQL report at
`/tmp/template-postgres-check-b9yqm2b5/report.json` passed all five backends:
160 Python tests, all three migration chains, and both Go race suites including
their database cases. The generated runtime report at
`/tmp/template-runtime-check-i3uuqrn5/report.json` records seven passes. Go
development exited 137 while compiling under an inherited 256 MiB production
limit. Native's package installation exhausted `/tmp`, preventing its result
file from being saved. Both cases need reruns; the three combined stacks had not
started. Go development now has a 2 GiB limit, `go run -p=2`, and a two-minute
health-check startup grace period for cold compilation in both copies.

Resume only failed or unrecorded cases from that report:

```bash
just resume-generated /tmp/template-runtime-check-i3uuqrn5/report.json
```

This selects eight cases, generates fresh projects, and keeps the seven earlier
passes as references in the new report. The old report and workspaces are not
modified. Use `python3 -B tests/release/check_generated.py all all --resume
/path/to/report.json --plan` to inspect selection without Docker. Resume does
not revalidate source changes behind earlier passes; rerun any changed passed
variant explicitly and run the complete matrix from the final release commit.

Recent dependency evidence and candidate upgrade targets are recorded in
`docs/research/2026-11-01-python-upgrade.md`,
`docs/research/2026-11-01-go-infra-upgrade.md`, and
`docs/research/2026-11-01-web-native-upgrade.md`, with the latest client findings in
`docs/research/2026-11-02-client-audit-follow-up.md`. These are not resolved
lockfiles. Run registry-backed resolution and fresh locked installations before
treating any candidate as the release graph. Use a patched Node runtime as
specified by the research; satisfying Expo's engine range alone is insufficient.

For manual backend test runs outside the helper, set `TEST_POSTGRES_URL` to a disposable PostgreSQL database.
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
