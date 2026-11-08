<!-- ©AngelaMos | 2026 -->
<!-- 2026-10-25-template-release-audit.md -->

# Template public release audit and execution record

## Outcome and scope

The major authentication, generation, infrastructure, and dependency repairs are
implemented. The recorded web-client and PostgreSQL backend checks pass. Public
release work remains: commit the current changes, reconcile the remote, publish
the release assets and installer, and accurately disclose integration gaps.

Carter initially selected one coordinated release of all eight variants: `go`, `fastapi`,
`open`, `frontend`, `native`, `fastapi-stack`, `go-stack`, and `portfolio`.
Keep the application architecture opinionated and the starter UI visually neutral.
Carter owns the replacement favicons and the eventual public demo domain.

This is an evolving evidence ledger, not a completed exhaustive audit. Passing
runtime results apply only to the cases recorded below. The initial pass traced the
installed generator, configuration, Docker entrypoints, both authentication
implementations, the web authentication client, mobile API configuration, portfolio
bootstrap/upload paths, and CI. Remaining source, native execution, dependency
advisories, and generated-project integration checks are release work.

Project type: multi-stack application starter and distribution tool. Weight
completeness 60 percent and code quality 40 percent: each advertised command must
produce a project whose client, backend, environment, and deployment agree.

## Current priority and status, November 8

Carter stopped the repeated manual Docker verification loop and explicitly
deprioritized React Native. Defer native Docker/device verification and do not
keep requesting the full runtime matrix as the next assignment. Focus on the
web/backend templates and public distribution. This does not convert unexecuted
cases into passes. The publication follow-up below records the CI scope change.

The five web clients passed fresh installs, lint/types/builds, applicable refresh
regressions, and their November 2 production dependency audits. All five backends
passed real PostgreSQL verification, including 160 Python tests, all three Python
migration chains, and both Go race suites without database skips. Their recorded
manifest and lock hashes still match the checkout as of this status review.

Seven generated Docker cases passed. Go development's memory/startup repair is
implemented but lacks a completed rerun. The combined FastAPI/React, Go/React,
and portfolio runtime cases and real browser authentication flows remain
unverified. Native passed dependency checks, 25 regressions, and both exports;
its Docker/device work is deferred. The latest resumed runtime report,
`/home/yoshi/dev/.template-checks/template-runtime-check-7gq2bxsh/report.json`,
is cancelled with no completed new cases and seven referenced earlier passes.

The shared local/public generator, selective archives, installer, and neutral
starter UI are implemented. The local command still points at this checkout.
Commit `7bd539b` records the subsequent dependency/runtime work. Its hooks passed;
the 36 local tooling tests passed before publication work. The source still
matches the retained dependency reports. Remote reconciliation, publishing, and
hosted-installer verification remain unconfirmed because this runner cannot
resolve GitHub or access the Docker socket.

The publication follow-up adds a tag-triggered release workflow and `just publish`.
Web/backend checks remain required; native checks move to an explicit opt-in
workflow input, including the native Docker case. Native is labeled experimental
in the CLI, README, and release notes. The hosted install/uninstall scripts are
staged in the Angelamos checkout and checked for byte equality with this source.
The publisher verifies remote ancestry, pushes branches/tag atomically without
force, waits for release CI, verifies downloaded assets, and can deploy only the
website's nginx service before testing the real public installation. Prepared
automation and local fixtures do not establish that those remote steps ran.
All 43 local generator/publication/runtime-helper tests pass, including disposable
Git histories for successful synchronization, remote divergence, and existing-tag
protection. Ruff, actionlint, installer checks, and the Angelamos frontend build
pass. The built website contains the exact installer/uninstaller source bytes.

## Continuation status, November 2

Checkpoint `ab28a7c` (`chore: checkpoint template release preparation`) records
the accumulated source, generator, installer, audit, and dependency preparation.
Its five local pre-commit hooks passed. It was committed locally on the existing
branch; no push, tag, release, or website deployment occurred.

Carter ran the dependency resolver in the normal terminal. All five Python
projects now have package-manager-generated locks, including both minimal
examples. The locks select FastAPI 0.162.0, Starlette 1.10.0, Pydantic 2.14.2,
SQLAlchemy 2.0.55, python-multipart 0.0.33, PyJWT 2.15.1, and Uvicorn 0.54.0.
The initial Python and client resolver logs are retained at
`/tmp/template-dependency-resolution-c8tw181g` on this machine. Carter completed
the web and Go follow-up runs. All five web logs finish without peer conflicts
or deprecation warnings at `/tmp/template-dependency-resolution-r16hdrc_`.
Both Go modules completed `go mod tidy` and `go mod verify`; their manifests
and sums match, with logs at `/tmp/template-dependency-resolution-zw6b58pv`.

The web resolution exposed a real peer constraint: `vite-tsconfig-paths` 5.1.4
depends on `tsconfck`, which expects TypeScript 5, while the prepared manifests
select TypeScript 6. All five web clients already have an explicit Vite `@` alias
matching their TypeScript path mapping. The redundant plugin and its dependency
were removed. The unused singular `react-icon` dependency was also removed; it
pulled Babel runtime 5 and deprecated core-js 1. The used plural `react-icons`
package remains. The follow-up resolution removed the redundant plugin, tsconfck,
singular icon package, and core-js 1 from every web lock. All 13 project graphs
resolved before the follow-up Zod and native SDK changes described below.

The resolver now fails on peer-dependency conflicts, explains cached tool
downloads, disables Corepack's interactive download prompt, and handles Ctrl-C
with an exit status of 130 and a group-specific resume command. Short-lived
process checks verified cooperative cancellation, forced cleanup of a process
ignoring SIGINT, and clean CLI cancellation without a traceback. Ruff passes.
Python and native resolution did not need repeating for these web/Go follow-ups.

The normal-terminal fresh-install run completed all 13 projects. Its recovered
report was `/tmp/template-dependency-check-rrb7ryfz/report.json`, completed at
04:49:21 EST on November 2. All recorded manifest and lock hashes matched the
checkout when the results were inspected, before the follow-up repairs.

| Scope | Recovered result |
| --- | --- |
| Five Python projects | Passed locked Python 3.12 installations, applicable lint/types, all 30 HTTP/lifespan regressions, and locked production dependency audits. |
| Two Go modules | Passed download/verification, vet, race tests, binary builds, and govulncheck with Go 1.26.10. Each suite skipped two PostgreSQL tests in this earlier run. The later PostgreSQL run below executes them and identifies the module-only advisory. |
| Five web clients | Passed strict frozen installations, lint, SCSS lint, type/build checks, and all 44 authenticated-client cases. Every project then failed its production audit on Zod 4.1.13. |
| Native SDK 54 baseline | Passed frozen installation, lint/types, 11 authentication cases, three storage-ordering cases, and iOS export. Its production audit reported 130 findings: two critical, 85 high, 36 moderate, and seven low. These counts include tooling/transitive paths and do not establish 130 exploitable application defects. |

Seven projects passed; six stopped at their dependency audits. Two later Konsole
SIGSEGV records occurred at 04:56:20 and 04:56:37 EST. The inspected stack includes
terminal image repainting and Qt allocation. The checks had completed first;
the crash trigger and any causal relationship to their output are unproven.

All six client manifests now select Zod 4.6.6, the reviewed advisory's patched
version. The native manifest prepares Expo 58.0.22 with React 19.3.0, RN 0.88.1,
and the maintainer's coordinated native package tuple. Babel preset 58.0.23
supplies Worklets integration; the redundant explicit Reanimated plugin is
removed. Input refs derive their instance type from the React Native component,
and unused Tamagui config/toast dependencies are removed. Tamagui 1 passes the
SDK 58 type and bundle checks described below; native binary/device behavior
remains unverified. The unsupported native web script is removed; this variant
targets iOS and Android. The earlier SDK 54 success cannot establish SDK 58
compatibility.

The next web resolution completed at `/tmp/template-dependency-resolution-eu53yb30`.
All five web clients then passed every check in
`/tmp/template-dependency-check-_3ik_0un/report.json`, including all 44 auth
regressions and production audits reporting no known vulnerabilities. Their
manifest and lock hashes match the checkout. No web rerun is needed for the
native-only repairs below.

Native resolution at `/tmp/template-dependency-resolution-3a9twahf` wrote a new
SDK 58 lock but failed its peer check: Expo Router requires Metro runtime
`^58.0.16`, while the previously auto-installed runtime remained at `6.1.2`.
The subsequent frozen install skipped resolution and did not rediscover that
peer error. `/tmp/template-dependency-check-52oqr1td/report.json` then stopped
at three TypeScript errors in the input wrappers. Native exports and audit did
not execute. A frozen-install success cannot override the failed resolver.

The manifest now declares Metro runtime `~58.0.16` explicitly. The TypeScript
failure was reproduced with SDK 58 / RN 0.88.1: Tamagui 1's input declarations
use the component type where an instance is required. A recorded pnpm patch
changes that declaration to `React.ComponentRef<typeof NativeTextInput>`;
the wrappers retain the correct native-instance contract. Tamagui packages are
pinned together at 1.144.1, and Docker copies the patch before installation.
The generated `/tmp/template-native-repair` project preserves the patch bytes.
After applying that exact declaration correction to its isolated copy of the
installed dependencies, lint/types and all 14 native auth/storage cases pass.
The patch applies and reverses cleanly in dry-run checks.

The later normal-terminal reports at
`/tmp/template-dependency-check-wfbkibzx/report.json` (06:34:19 EST) and
`/tmp/template-dependency-check-s_pzl5sv/report.json` (06:45:31 EST) matched the
manifest, lock, and patch hashes at that checkpoint.
Both passed strict frozen installation with the recorded patch, Expo package
alignment, lint/types, all 14 authentication/storage cases, and both iOS and
Android exports. Both stopped only at the production dependency audit: one
critical, 24 high, and nine moderate findings. These are dependency advisories,
not demonstrated exploitable paths in the mobile application.

The 25 displayed high/critical findings concern seven packages: shell-quote,
picomatch, @xmldom/xmldom, ws, js-yaml, browserslist, and compression. Reviewed
fixes fit the installed parents' existing dependency ranges. Repeating the old
lock-only install retained vulnerable versions that still satisfied those ranges.
The client resolver now runs `pnpm update --depth Infinity --lockfile-only
--no-save`, followed by strict `pnpm install --resolution-only` validation.
Declared ranges and exact pins stay unchanged. Real offline pnpm fixtures
reproduced the stale lock, refreshed it to a patched version, preserved an exact
pin, and proved that the resolver rejects an incompatible peer after updating.

The local checker and CI now retain full JSON production audits and fail on
findings at any severity. This deliberately strengthens the previous high-only
threshold and exposes the nine moderate findings that its output omitted.
The networked refresh at `/tmp/template-dependency-resolution-4hkntnx_` completed.
Its fresh check at `/tmp/template-dependency-check-x17swp_a` exposed Biome 2.6.4's
new raw-text rule and export ordering. The flagged card components extend native
Text. Biome now recognizes those four names, uses the current configuration
preset/schema, and is pinned to 2.6.4; the export order is corrected. Independent
fixtures still reject raw text inside View and CardFooter. pnpm generated the
corresponding lock change.

The next full run at `/tmp/template-dependency-check-ar8prrrn` passed fresh
installation, Expo alignment, lint/types, all 14 auth/storage cases, and both
exports. Its JSON audit reported only two moderate findings: glob and minimatch,
both published October 27. High and critical findings were zero. A first scoped
CLI override passed six new compatibility cases in
`/tmp/template-dependency-check-m__p733r`, but its audit exposed another parent
sharing the old versions. Audit output had reported a representative path.

The full production graph was then inventoried. Five Expo packages require glob
13, and fingerprint also requires minimatch 10 directly. Exact-parent overrides
now select glob 14.0.3 and minimatch 11.0.4 across all those references. Real pnpm
resolution completed using cached metadata; a traversal of all 695 production
nodes finds only the patched versions of these packages. Eleven compatibility
cases cover the actual Expo consumers and run in the helper and CI. The completed
run at `/tmp/template-dependency-check-dt4bpkh_/report.json` passes fresh strict
installation, Expo alignment, lint/types, all 25 native regressions, both exports,
and the production audit. The audit reports zero findings at every severity
across 696 dependencies. Manifest, lock, patch, Biome configuration, and input
source match the checkout. Native binary/device execution is still unverified.

The five Vite configs now use `import.meta.dirname`, addressing the warning
observed during their actual Vite 8 builds. Refreshed advisory and SDK evidence,
including the distinction between prepared and verified changes, is recorded in
`docs/research/2026-11-02-client-audit-follow-up.md`.

`just check-dependencies` copies each of the 13 projects with the generator's
credential/cache exclusions, installs locked dependencies, runs the applicable
lint/types/build/local regressions, and audits production dependencies. It retains
isolated projects, per-project logs, input hashes, and `report.json` beneath the
printed `/tmp/template-dependency-check-*` directory. Manifests, locks, and
dependency patches must stay byte-identical during verification. Failures are
retained per project and do not hide later projects. Group selection and a command-plan recipe support follow-up
runs. Native checks now include Expo package alignment and both iOS and Android
exports. PostgreSQL, Docker startup, native binary builds, and actual browser or
device checks are outside this command's pass result.

Five helper regressions pass: existing environments/secrets are excluded without
changing the source; a command failure stops that project and retains its log;
a successful command that mutates a copied lock or dependency patch still fails;
and quiet output preserves both child output streams in the log. The checker
prints commands and results by default, with `--verbose` available for full
terminal output. Requirements export also suppresses its redundant stdout copy.
Go audits request verbose details so unreachable module advisories are retained.
CI mirrors the stricter peer checks, Expo alignment, and both native exports.
The scripts pass Ruff and the workflow passes actionlint. Registry DNS remains
unavailable to this runner. A separate offline Go helper attempt failed on
uncached metadata, and a direct verbose scan could not reach `vuln.go.dev`;
neither overrides the completed normal-terminal run.

Both nested minimal examples now have distinct literal Compose namespaces,
generated high ports and credentials, an asyncpg database URL, PostgreSQL 18's
correct volume target, read-only source mounts, non-root backend users, and build
context exclusions. Their instructions use the generated parent environment and
describe the limited authentication scope. They still lack refresh tokens,
logout revocation, password-change token invalidation, and rate limiting; their
historical directory name is not a production-readiness claim.

`just check-template` passes 16 generator tests, five dependency-helper tests,
and 15 runtime-helper tests, plus ShellCheck and Bash syntax checks.
The expanded Compose contract test renders 17 configurations, including both
nested examples, and checks credentials, namespaces, mount targets, and unique
high ports. Rendering does not start Docker containers or execute PostgreSQL.
Native's Metro/patch repair now passes fresh installation, SDK alignment,
lint/types, regressions, both exports, and a clean production audit. A patched
Node runtime, native binary/device checks, and completion of the generated
runtime matrix remain release work.

The normal-terminal PostgreSQL run passed all five backends, retained at
`/tmp/template-postgres-check-b9yqm2b5/report.json`. Each Python FastAPI copy
passed 42 regular tests and seven independent session-security tests. Portfolio
passed 39 regular tests and 23 session/integrity/media cases, totaling 160 Python
tests. All three Alembic migration chains completed. Both Go race suites passed
their PostgreSQL transaction and account-update cases with no skips. Recorded
dependency hashes match the checkout. All copied source files also match except
the two Go Dockerfiles/development Compose definitions repaired after this run.

Verbose Go scans identify the remaining module-only finding as
[GO-2026-5932](https://pkg.go.dev/vuln/GO-2026-5932), published July 7: unmaintained
OpenPGP packages inside `golang.org/x/crypto`. Both scans report zero affected
symbols and zero affected imported packages. The application imports Argon2 from
that module, not OpenPGP. This closes the unidentified-advisory question; no
ignore or dependency substitution was introduced.

The Docker report at `/tmp/template-runtime-check-i3uuqrn5/report.json` preserves
seven passes: Go production, and development/production for FastAPI, open, and
the authenticated web frontend. Go development exited 137 with compiler
processes reporting `signal: killed`. Its rendered configuration confirms that
`extends` inherited the production 256 MiB limit. OOM is the leading diagnosis;
the deleted container's OOM flag and inaccessible kernel journal prevent direct
confirmation. Both Go development variants now override the limit to 2 GiB,
run `go run -p=2`, and allow two minutes of health-check startup grace for cold
compilation. A generated-configuration regression failed on the original
limit in both variants, then passed with the repair. A Docker rerun is pending.

Native timed out while pnpm reported ENOSPC writing `/app/.pnpm-store` through
the generated source bind mount into `/tmp`. Container/volume cleanup completed,
but writing its case result also failed. The matrix stopped before the six
combined-stack cases. Later filesystem inspection shows `/tmp` is a 32 GiB
tmpfs with 17 GiB now available, while the checkout disk has 192 GiB available.
The earlier peak use and what freed it are unknown; no global Docker cleanup
was performed by this agent.

Fresh dependency, PostgreSQL, and runtime workspaces now default to the sibling
`.template-checks` directory, with child temporary files on the same filesystem.
`TEMPLATE_CHECK_ROOT` can select another location outside the source checkout.
Reports use atomic replacement. A full log device no longer prevents the
checker from attempting its owned Compose teardown. New regressions exercise
disk-write failure, cleanup under ENOSPC, and repeated report-based resumption.
`just resume-generated /tmp/template-runtime-check-i3uuqrn5/report.json` selects
the eight failed/unrecorded cases and references the seven prior passes without
modifying old evidence. Resume does not certify that earlier source snapshots
are unchanged; final release CI still needs the complete matrix.

The runner's Docker socket still returns `operation not permitted`. The retained
normal-terminal PostgreSQL and seven Docker passes are verified evidence;
the repaired Go/native cases and combined stacks remain pending execution.

## Continuation status, November 1

Carter authorized the four remaining phases in order: dependency upgrades and
fresh installs; PostgreSQL/generated Docker checks; browser/device and remaining
source review; reviewed commits, remote reconciliation, release and installer
hosting. The first phase is in progress, not complete.

Three bounded research agents refreshed primary-source evidence within March 1
through November 1. Reports are `docs/research/2026-11-01-python-upgrade.md`,
`2026-11-01-web-native-upgrade.md`, and `2026-11-01-go-infra-upgrade.md`. Older
compatibility references and unresolved native/peer requirements are marked.

Preparation now includes:

- Five Python manifests use the reviewed FastAPI/Starlette/parser/ORM targets,
  explicit email validation and SQLAlchemy's async extra, and remove unused
  Gunicorn and FastAPI's broad standard extra. Direct HTTPX tests remain on 0.28.
- Five web manifests select stable Vite/plugin React, React/DOM, Router, Axios,
  and TypeScript candidates. The preview Vite alias and override are removed.
- pnpm 10.34.9 and uv 0.13.6 pins agree across applicable manifests, Dockerfiles,
  and CI. Both Go manifests/builders select Go 1.26.10; the resolver owns the
  coordinated module upgrades and genuine sum generation. CI uses govulncheck
  1.9.0 after the toolchain transition.
- All six TypeScript path configs no longer depend on `baseUrl`; native's path
  mapping is explicitly relative. Native shared tooling/Axios/Babel requirements
  are updated, but SDK 54 and Tamagui 1 remain pending an installed migration
  checkpoint. Do not describe native as upgraded to SDK 58.
- The five Python factories close database resources after normal exit,
  exceptions, injected cancellation, and partial initialization failure. Both
  bundled minimal examples now commit before the HTTP response, own sessions
  through the async context manager, and use the correct Uvicorn module and
  `exec`. Their Docker installs now require actual uv locks and omit development
  extras.
- `just resolve-dependencies` performs package-manager resolution for all 13
  projects, with group selection, effective manager checks, and retained logs.
  `just dependency-plan` prints commands without execution. CI adds lifecycle
  and lint checks for both minimal examples to the package gate.

Verification: the new lifecycle regressions reproduced three missing-cleanup
failures before the fix. All 30 cases then passed across the three main backends
and both minimal examples. These ran in the existing standalone environment:
Python 3.14.2, FastAPI 0.129.0, Starlette 0.52.1, SQLAlchemy 2.0.46, Pydantic
2.12.5, HTTPX 0.28.1. They establish the source repair on that cached graph,
not compatibility with the prepared upgrade graph. Fresh installs and Python
3.12 CI execution remain required.

Both minimal example Ruff checks pass after aligning their intentional generic
repository style exception with the full backends. The changed release scripts
pass Ruff; actionlint and `git diff --check` pass. All five Python manifests and
six client manifest/path configurations parse, and both Go manifests remain
identical. Resolver plans were inspected for all four groups. Cached TypeScript
checks pass for the standalone auth/no-auth clients, both combined-stack clients,
and native. Portfolio's own fresh installation and all checks using the new
dependency graphs remain pending.

Access preflight still fails in this runner: PyPI/npm DNS does not resolve and
the Docker socket returns operation not permitted. Existing caches lack the
complete candidate graph. No lockfiles were hand-edited or claimed resolved.
Python/web manifests are intentionally ahead of their old locks, and both minimal
examples need new locks. Frozen builds are blocked until resolution succeeds.
No remote synchronization, commit, tag, public release, or website deployment
occurred in this continuation.

The two minimal example Compose definitions also retain the old PostgreSQL 18
volume target and standard host ports. Their development-only credentials and
remaining source/runtime boundaries require review before distributing them as
production examples. Main-variant Compose repairs do not cover these nested files.

## Initial repository evidence

- Local path: `/home/yoshi/dev/templates`.
- Installed command: `/home/yoshi/.local/bin/template`, a symlink to
  `template-tool/template` inside this checkout.
- Configured remote: `git@github.com:CarterPerez-dev/Fullstack-setup.git`.
- Current branch: `chore/pnpm-10-pin-sweep`.
- Initial HEAD: `f6adc052423267a3e9ab802abc5fcda96006a191`.
- Initial tracked dirty files: 83. Preserve these changes.
- `template-tool/`, the root `justfile`, and most of `stacks/portfolio/` are
  untracked. Do not mistake an untracked directory for an unpublished Git commit.
- Cached `origin/main`: `0eec274`, dated January 25, 2026. This is a local
  tracking reference, not verified current GitHub state.
- SSH remote lookup failed on local SSH configuration permissions. HTTPS Git and
  GitHub CLI lookup failed on network/DNS access. No push, merge, tag, or deployment
  has occurred.
- Inventory: 539 source/style/script files with 254 distinct byte contents.
  All Go source files in the standalone and combined stacks are byte-identical.
  FastAPI standalone and combined backend Python files differ only in the
  `rate_limit.py` header. This establishes duplication, not full functional parity
  of their infrastructure.

## Implementation and verification status, October 25

The repository is still uncommitted on the original branch and HEAD. No remote
update, tag, GitHub release, website deployment, or live environment mutation was
performed. The initial findings below describe the baseline; this table records
the local repairs and their verification limits.

| Area | Implemented locally | Verification still required |
| --- | --- | --- |
| A01, owner enrollment | Public signup cannot claim administrator status; portfolio signup is closed; explicit Python and Go administrator commands | PostgreSQL enrollment, duplicate refusal, and HTTP authorization |
| A02, Go access authorization | Middleware verifies current user, version, role, and tier | Full browser and database invalidation scenarios |
| A03/A04, refresh lifecycle | User-before-token locks; atomic rotation; replay commits; family logout; versioned refresh tokens and migrations | Real PostgreSQL races, rollback injection, migration rollout |
| A05, rate limits | Removed unverified JWT identity and raw forwarded-header trust | Deployment-specific trusted ingress, outage policy, load checks |
| A06, Go browser contract | Explicit cookie transport, response adapter, correct user/admin endpoints, reload verification | Real browser registration, login, refresh, logout, role changes |
| A07/A08, generation | Shared local/public generator, filtered archives, two environments, credentials, Git ignore rules, high ports, provenance, safe refusal | Fresh installs and application runtime matrix |
| A09/A10, infrastructure | PostgreSQL 18 mounts, authenticated Redis URLs/health checks, optional env normalization | Clean startup, persisted data after recreation, restore checks |
| A11, Go startup | Development API, distroless health mode, runtime key volume, initial schema, checked migration runner, atomic private-first key initialization and pair validation | Docker startup and key-volume recovery as the container UID |
| A12, release checks | All-variant failing CI, PostgreSQL tests, dependency audits, 15 generated Docker cases, packaging dependency gate | Execute CI from the reviewed commit; verify branch protection separately |
| A13, dependency setup | Pinned pnpm and uv tooling, locked startup installs, supported Uvicorn process command | Resolve production dependency advisories and verify fresh frozen installs |
| A14, presentation | Neutral generic landing/shell/forms, working profile/password controls, no fabricated status; portfolio owner login | Rendered desktop/mobile, keyboard, errors, and authenticated interaction |
| A18, portfolio integrity | Database singleton constraints and conflict-safe initialization; media foreign keys; durable file creation; commit-before-delete ordering | PostgreSQL concurrency/migrations, crash reconciliation, media format checks |
| A20, Go resource and key boundaries | 1 MiB JSON limits, bounded password-work admission, validated Argon2 parameters, stable public-key-derived key IDs | Container memory/load checks, restart behavior for external JWKS consumers |
| A21, client session boundaries | Session-bound requests and refreshes; stale-response rejection; guarded logout callbacks; ordered native credential operations | Browser cookie ordering across tabs, device storage/lifecycle behavior |
| A22, Go account updates | Profile, role, and tier updates write only their own column and return current row state | PostgreSQL update, deletion, and concurrency execution |

Completed local checks:

- `just check-template`: 16 tests passed. These include all eight archive-to-project
  paths, 15 Compose configuration renders, credential isolation, archive safety,
  generated dotenv Git exclusions, reproducible bytes, source-copy parity, and
  piped install/reinstall/uninstall. Bash syntax, ShellCheck, and `git diff --check`
  also passed. Native signing-key formats and Tamagui build caches are excluded
  from generated and packaged templates.
- Both Go copies passed `go test -race ./...` and `go vet ./...`; `gofmt -l`
  returned no paths. Nine HTTP-auth/cookie subcases ran per copy. PostgreSQL auth
  and password-transition tests compiled but were skipped without a test database.
- Standalone FastAPI and the FastAPI-stack backend passed Ruff, Pylint, and mypy
  across 39 source files each. Portfolio passed those checks across 47 source files
  using the available standalone backend environment. These are not three fresh
  dependency installations.
- The two non-database forged-JWT rate-limit tests passed. Database-dependent
  FastAPI tests are not counted as passed. Seven additional PostgreSQL security
  scenarios are provided in `tests/release/test_python_security.py`.
- Generic web clients passed lint, SCSS checks, TypeScript, and Vite builds with
  installed dependencies. Some installed tools differ from their locked versions.
  Portfolio lint, SCSS, TypeScript, and Vite passed in a temporary generated copy
  using the available FastAPI frontend dependency tree; one existing array-index
  key warning remains. It still needs its own frozen install.
- Native passed Biome/TypeScript and an offline iOS Expo export of 3,670 modules.
  The export initially failed on an undeclared Babel preset. Its already-locked
  version is now a direct dev dependency. The installed preset was linked from
  the existing local dependency tree for this check, because pnpm could not write
  its global store registration. This is bundle evidence, not device execution.
- `actionlint` passed the rewritten workflow. The generated runtime script's
  command-line path was checked; its Docker execution has not run here.

Environment limits: the generated runtime command stops at `docker info` because
Docker socket access is denied. Local socket binding is also denied. Git/GitHub
network lookup failed, and `uv tree --outdated --locked` failed to resolve PyPI.
pnpm frozen installation fails with `EROFS` while
registering projects under `/home/yoshi/.local/share/pnpm/store/v10/projects`.
The available SQLite async test connection also hung during the earlier run.
The Python CI fixtures now use disposable PostgreSQL schemas when configured;
portfolio explicitly requires PostgreSQL for JSONB. None of these limitations is
a successful integration test, and none proves a live deployment has a defect.

### Follow-up research and repairs, October 25

Three independent research tasks reviewed Python, web/native, and Go/infrastructure
against primary sources dated February 25 through October 25, 2026. The reports
separate patch floors, candidate versions, applicability, and unresolved evidence:

- [Python research](../research/2026-10-25-python.md)
- [Web and native research](../research/2026-10-25-web-native.md)
- [Go and infrastructure research](../research/2026-10-25-go-infra.md)

The researched targets have not been resolved into dependency locks. In addition
to Starlette, the locked multipart parser matches multiple recent advisories.
Go 1.25 is outside the current support window; Expo 54 exceeds its documented
maintenance horizon. A current FastAPI upgrade also requires removing the
unsupported `openapi_version` constructor keyword, now done in all three copies.
Other compatibility work and dependency validation remain explicit release gates.

New local regression evidence:

- Two HTTP lifecycle cases per Python backend pass with the existing standalone
  virtual environment. Before the repair, commit happened after the response,
  and injected commit failure still returned HTTP 201. Session completion is now
  function-scoped and uses the native async session context manager. Ruff,
  single-process Pylint, and mypy pass for the changed backend code.
- Three refresh concurrency cases pass for each of four web auth clients and
  native, 15 cases total. The actual TypeScript interceptor runs with installed
  Axios and controlled adapters/state/storage. Before the fix, a late 401 hung
  and an application 500 after successful refresh caused logout. Portfolio uses
  sibling dependencies for these checks. Cross-tab, logout, browser, and device
  behavior still need their separate tests.
- Five signing-key initialization tests pass with the race detector in each Go
  copy. They cover missing-public-key recovery, repeated initialization, mismatch
  refusal, damaged/private-missing refusal, and concurrent initializers. Complete
  temporary PEM files are published without overwriting existing keys. An old
  public-only pair requires restoring its private key; no identity is invented.
- `just check-template` still passes all 16 cases. `just check-generated` now
  selects all 15 runtime cases by default and reports individual failures.

The runtime matrix was attempted and stopped at its Docker preflight with socket
access denied. A resolver dry run for the proposed FastAPI, Starlette, SQLAlchemy,
and multipart upgrades failed on PyPI DNS access. The session's granular approval
policy rejects sandbox escalation, even though Carter authorized the work; no
supported permission-changing tool was exposed. No runtime case started, and no
dependency-resolution or PostgreSQL success is claimed. Local validation uses
cached packages whose versions differ from the locks.

### Continued local repairs without Docker operations

Carter asked to continue application work while leaving Docker alone. No Docker
command or Docker configuration change was made during this continuation. Carter's
terminal returned HTTP 200 from PyPI, while the agent command environment still
failed DNS resolution. Those are different execution contexts. A read-only uv
resolver preview was requested for the working terminal; no resolver output or
new dependency lock has been received.

- Both Go variants pass the complete available `go test -race ./...` suite,
  `go vet ./...`, and formatting checks after the body, password-memory, and key-ID
  changes. Tests cover known and streamed oversized input, trailing JSON,
  concurrent password admission, invalid stored hash parameters, cached JWKS
  verification after restart, and key replacement. PostgreSQL cases remain skipped.
- All five authenticated clients pass 11 request/refresh/logout cases each,
  55 total. The harness executes the actual TypeScript clients and logout hooks
  with installed Axios and React Query mutation observers. Controlled transport,
  auth state, and native platform adapters make this local concurrency evidence,
  not browser/device execution. Three additional tests run the actual native
  storage wrapper and prove ordered writes/deletes and recovery after a failed
  write. Before the repair, four new client-boundary cases failed in both web
  and native clients.
- Portfolio media tests pass nine failure/success cases. Seven singleton/media
  foreign-key tests are collected but skipped without PostgreSQL. Offline Alembic
  SQL generation succeeds for the new integrity migration. The ordinary async
  media test run hung because Python's event-loop wake-up socket received
  `PermissionError: Operation not permitted` in the agent runtime. A temporary
  test-runner timer allowed the actual filesystem/thread operations to complete;
  no production I/O was replaced with a mock or changed to accommodate the sandbox.
- The generator passes 15 tests and 83 subtests with its one Compose-render test
  deliberately excluded for this continuation. Earlier Compose-render evidence
  remains separate. Shell syntax, ShellCheck, workflow validation, source-copy
  parity, and whitespace checks pass.
- Updated web and native clients pass lint and type checks with cached packages.
  All four authenticated web clients build, and native exports 3,670 iOS modules
  after the session changes. The generated portfolio frontend uses the sibling FastAPI
  dependency tree; its existing array-index-key warning remains. This is not
  evidence of an independent frozen dependency installation.
- Four stale-user update cases failed before the Go account-update repair and
  pass in each copy afterward. Both complete race-test suites, vet, and formatting
  checks pass after this additional repair. The service reproduction uses a
  repository fixture with stale reads; real PostgreSQL field-update and deleted-row
  checks were added but remain unexecuted without the test database.

## Baseline findings

### A01. Public signup can assign the configured administrator role

Severity: CRITICAL. Axis: Code Quality.

Files: `backends/fastapi/app/user/service.py:40`,
`backends/fastapi/app/user/routes.py:37`,
`backends/fastapi/app/core/dependencies.py:135` and duplicated backend code.

Proof: the unauthenticated registration route calls `create_user`; matching
`ADMIN_EMAIL` selects `UserRole.ADMIN`. No ownership challenge is required before
that role can authorize administrative operations. A person who registers the
configured email before the owner can obtain that role.

Proof check: high confidence; conditional on configuring `ADMIN_EMAIL` and the
account not already existing. No exploitation of a deployed service was attempted.

Fix: public registration always creates an ordinary user. Bootstrap administrators
through an explicit local management command, with a password prompt or safe
stdin input, transaction handling, and no password in command arguments/logs.

Verify: public registration with the configured admin email remains unprivileged;
explicit bootstrap succeeds once; subsequent attempts do not overwrite accounts.

### A02. Go access-token revocation is disconnected from authentication

Severity: MAJOR. Axis: Code Quality.

Files: `backends/go-backend/cmd/api/main.go:146`,
`backends/go-backend/internal/middleware/auth.go:36`,
`backends/go-backend/internal/auth/service.go:317`.

Proof: the authenticator receives `jwtManager`, which verifies signatures and
claims. The repository-wide references to `ValidateTokenVersion` and
`IsAccessTokenBlacklisted` are their definitions. Logout-all increments the stored
version, but requests never compare their signed version with the stored version.
Existing access tokens remain accepted until expiry. Roles also come from the
token rather than the current user record.

Proof check: high confidence from call-path tracing; no live request replay run.

Fix: provide the middleware an application-level verifier that validates the JWT,
checks the current user/version, and derives current authorization from the user.
Remove unused blacklist machinery unless it becomes an enforced requirement.

Verify: logout-all, password changes, account deletion, and role demotion invalidate
the relevant old authorization in actual HTTP requests.

### A03. Refresh rotation is not atomic in either backend

Severity: MAJOR. Axis: Code Quality.

Files: `backends/go-backend/internal/auth/service.go:125`,
`backends/go-backend/internal/auth/service.go:385`,
`backends/go-backend/internal/auth/repository.go:111`,
`backends/fastapi/app/auth/service.py:130`,
`backends/fastapi/app/auth/repository.py:26`.

Proof: Go inserts the successor before calling `MarkAsUsed`, then ignores the
conditional update's failure. Two requests can create valid successors from one
token. FastAPI reads without a row lock or conditional consume before revocation
and insertion, permitting concurrent requests to observe the same active token.

Proof check: high confidence from transaction boundaries; needs concurrent
PostgreSQL tests, not SQLite-only tests.

Fix: lock or atomically consume the old token and create its replacement in one
transaction. Preserve replay evidence and define the policy for simultaneous
legitimate refresh requests. Do not describe ignored revocation errors as success.

Verify: concurrent refreshes cannot produce two independently valid token branches;
failure injection rolls back both consumption and successor creation.

### A04. FastAPI replay revocation is rolled back on its error path

Severity: MAJOR. Axis: Code Quality.

Files: `backends/fastapi/app/auth/service.py:139`,
`backends/fastapi/app/auth/repository.py:100`,
`backends/fastapi/app/core/database.py:101`, `backends/fastapi/conftest.py:99`.

Proof: replay detection flushes family revocation and raises `TokenRevokedError`.
The request session manager rolls back on that exception. The test dependency
override only yields a session and does not exercise the production commit/error
boundary, so an HTTP rejection alone does not prove persisted family revocation.

Proof check: high confidence; verify with a fresh database session after the HTTP
response. SQLAlchemy flush is not commit.

Fix: let the security transaction finish before translating its outcome into an
HTTP error. Keep transaction ownership explicit at the service boundary.

Verify: rotate once, replay the consumed token, then attempt the successor in a
new request/session. The successor must be rejected under the chosen replay policy.

### A05. FastAPI rate-limit identity trusts unverified claims

Severity: MAJOR. Axis: Code Quality.

File: `backends/fastapi/app/core/rate_limit.py:25` and its stack copies.

Proof: the limiter decodes bearer tokens with `verify_signature=False` and uses
the supplied subject as its bucket. Untrusted callers can choose different
subjects to change the application limiter's bucket without authenticating.
An independent reverse-proxy limit can reduce exposure but does not repair this.

Proof check: high confidence; this concerns rate-limit bypass, not JWT auth bypass.

Fix: use a trusted client address for pre-authentication limits. Apply a separate
authenticated user limit only after validating identity. Define trusted proxy
handling and explicitly choose behavior when Redis is unavailable.

Verify: forged bearer subjects share the same pre-authentication limit; trusted
proxy addresses and direct connections have documented, tested identities.

### A06. The Go + React stack has incompatible authentication contracts

Severity: MAJOR. Axis: Completeness.

Files: `stacks/go-react/frontend/src/api/hooks/useAuth.ts:68`,
`stacks/go-react/frontend/src/api/types/auth.types.ts:19`,
`stacks/go-react/frontend/src/core/api/api.config.ts:62`,
`backends/go-backend/internal/auth/handler.go:61`.

Proof: the frontend submits a form with `username`, expects top-level
`access_token` plus the FastAPI user shape, and refreshes using a cookie. Go
expects JSON credentials, returns its own response shape, and expects the refresh
token in a JSON body. Pairing these folders does not produce a working auth flow.

Proof check: high confidence; observed source contracts, not an end-to-end run.

Fix: define one browser-facing auth contract or an explicit Go frontend adapter,
including cookies, registration, errors, users, admin operations, and logout.

Verify: browser registration, login, reload recovery, refresh, logout, and role
authorization against the generated Go stack.

### A07. Local generator can propagate real environment files

Severity: MAJOR. Axis: Code Quality.

Files: `template-tool/template:133`, `template-tool/rewrite.py:105`.

Proof: the rsync exclusions name `.env`, `.env.production`, and `.env.*.local` but
not `.env.development` or arbitrary `.env.<environment>`. Real development env files
exist in the template source directories. Copying them can transfer credentials
and machine-specific configuration. File contents were not printed.

Proof check: high confidence; this establishes a copying path, not a confirmed
public credential leak.

Fix: permit only explicit environment examples, reject links and private-key
material, and share the filter between local generation and release packaging.

Verify: fixtures containing development/staging dotenv files, private keys,
symlinks, dependency trees, and build artifacts never appear in generated output
or published archives.

### A08. Clean generation lacks required initialization

Severity: MAJOR. Axis: Completeness.

Files: `template-tool/template:154`, `template-tool/template:174`,
`template-tool/rewrite.py:24`, `stacks/fastapi-react/justfile:179`,
`backends/go-backend/.env.example:13`.

Proof: the generator seeds only `.env`; development recipes require
`.env.development`. Optional dependency failures are discarded with `|| true`.
Go's literal host ports change without updating localhost URLs in its env example;
equal host/container port mappings are deliberately skipped. Keys are excluded
without a replacement bootstrap. Ports are randomized without checking listeners.

Proof check: high confidence from generation/data-flow inspection. Port checks can
only observe current availability, not reserve ports for a future Docker launch.

Fix: stage generation, seed both environments from examples, synchronize endpoints,
generate independent credentials and keys, report dependency failures accurately,
and refuse destructive overwrites. Record source provenance without secrets.

Verify: generate every variant into a clean temporary directory with no private
source env files; validate env interpolation and startup instructions.

### A09. PostgreSQL 18 uses the old volume target

Severity: MAJOR. Axis: Completeness.

Files: `stacks/fastapi-react/compose.yml:79`,
`stacks/fastapi-react/dev.compose.yml:93`,
`backends/go-backend/compose.yml:37` and other PostgreSQL 18 definitions.

Proof: the image is PostgreSQL 18 while the named volume is mounted at
`/var/lib/postgresql/data`. The official image moved its volume to
`/var/lib/postgresql` and data to a versioned subdirectory in 18.
[Official image documentation](https://github.com/docker-library/docs/blob/master/postgres/README.md).

Proof check: high confidence from image documentation and checked-in definitions.
Changing a template is separate from migrating any existing deployment's data.

Fix: correct new-project volume targets. Document a separate migration path for
existing databases; do not delete or relocate live volumes during this work.

Verify: clean startup, insert data, recreate the container, and read the data back.

### A10. Redis credentials, health checks, and default settings disagree

Severity: MAJOR. Axis: Completeness.

Files: `stacks/fastapi-react/.env.example:54`,
`stacks/fastapi-react/compose.yml:116`, `backends/fastapi/app/config.py:126`.

Proof: production enables Redis password authentication but the example Redis URL
omits the password and the health check runs unauthenticated `redis-cli ping`.
Example database/Redis passwords remain predictable placeholders. Empty
`ADMIN_EMAIL` is passed into an optional EmailStr without the empty-to-None
validator that already exists in the portfolio variant.

Proof check: high confidence for Redis mismatch; configuration validation needs
an isolated settings test without the developer's actual environment.

Fix: generate credentials, use authenticated URLs and health checks, reject unsafe
production placeholders, and normalize optional empty settings consistently.

Verify: both generated environments become healthy with generated credentials;
wrong credentials fail cleanly; settings load without a private local dotenv file.

### A11. Go Docker startup is incomplete

Severity: MAJOR. Axis: Completeness.

Files: `backends/go-backend/Dockerfile:21`,
`backends/go-backend/compose.yml:8`, `backends/go-backend/Justfile:68`.

Proof: the production image is distroless but Compose invokes `wget` for health.
The entrypoint defaults to loading `config.yaml`, which is not copied into the
runtime image. Keys are baked into the image from a normally excluded directory.
Compose references `go-api:latest`, whereas the build recipe tags
`go-backend:latest`. Development Compose starts dependencies without the API.

Proof check: high confidence from runtime image contents and actual entrypoint.

Fix: provide a real development API service, build production through Compose,
ship nonsecret config, mount signing keys with readable permissions for the
nonroot process, and add a health-check mode to the application executable.

Verify: generated development and production builds start from fresh files;
runtime images contain no private keys; health checks use installed executables.

### A12. CI reports problems without enforcing a release gate

Severity: MAJOR. Axis: Completeness.

File: `.github/workflows/lint.yml:20`.

Proof: only `backends/fastapi` is checked; lint errors are converted to status text
and continued. There is no final failure assertion, generated-project matrix,
Go test suite, or web test suite found in the initial inventory. FastAPI tests
override the transaction lifecycle with SQLite and do not prove PostgreSQL races.

Proof check: high confidence for current workflow; no claim about external branch
protection settings, which were not retrieved.

Fix: fail on real check failures, run the selected tool versions from lockfiles,
add all-eight generation checks and stack contract tests, and gate packaging on
an explicit clean commit plus passing verification.

Verify: deliberately failing a check fails CI; release artifacts are built from
the same tested commit and include source identity and checksums.

### A13. Docker dependency setup still drifts outside the locally repaired stack

Severity: MAJOR. Axis: Completeness.

Files: `frontends/open/infra/docker/vite.dev:13`,
`frontends/open/dev.compose.yml:42`,
`backends/fastapi/infra/docker/fastapi.prod:16`.

Proof: the no-auth image activates `pnpm@latest`, while package manifests pin
10.29.1. A persistent node_modules volume has no startup reconciliation. The local
FastAPI stack already has targeted fixes, demonstrating divergence across copies.
Python images fetch a moving uv image; production still references deprecated
`uvicorn.workers`.
[Uvicorn migration notice](https://www.uvicorn.org/).

Proof check: high confidence about source drift and deprecation; this is not an
assertion that every moving dependency is currently vulnerable.

Fix: consistent tool versions, frozen dependency installation, noninteractive
startup reconciliation, and a deliberate supported production worker strategy.
Audit resolved dependencies before selecting upgrades.

Verify: rebuild and restart after a dependency change without deleting volumes;
the actual running dependency graph matches the checked-in manifest and lockfile.

### A14. Neutral presentation was implemented by removing usable layout

Severity: MINOR. Axis: Completeness.

Files: `stacks/fastapi-react/frontend/src/pages/landing/landing.module.scss`,
`stacks/fastapi-react/frontend/src/pages/login/login.module.scss`,
`stacks/fastapi-react/frontend/src/pages/register/register.module.scss`.

Proof: the provided screenshots match the empty module styles in the working
tree. The markup retains a large branded sales page, fixed stack claims, and
decorative metadata, while losing spacing, form layout, and navigation hierarchy.

Proof check: high confidence from screenshots plus source. This is a usability
finding, not a request to impose a new brand.

Fix: a quiet starter page with the project name, available working routes, and
plain forms. Use system fonts, restrained grayscale, normal document flow,
accessible focus states, and modest responsive spacing. Keep the public marketing
demo independent from the application's default starter screen.

Verify: desktop/mobile rendering, keyboard navigation, field labels, loading/error
states, and all demo links. Do not call a backend operational without a health result.

## Additional findings and remaining work

### A15. Locked Starlette version has a relevant published denial-of-service advisory

Severity: MAJOR. Axis: Code Quality. Status: OPEN RELEASE BLOCKER.

All three Python lockfiles resolve FastAPI 0.124.0 and Starlette 0.50.0. Their login
routes use `OAuth2PasswordRequestForm`. Starlette's June 12 advisory identifies
unbounded URL-encoded form parsing in versions below 1.3.1. This makes the parsing
path relevant to these APIs; no exploit was sent to a live deployment.
[Maintainer advisory](https://github.com/Kludex/starlette/security/advisories/GHSA-82w8-qh3p-5jfq).

Upgrade FastAPI and its compatible Starlette dependency together, regenerate all
three locks with uv, then run locked installations, migrations, HTTP tests, and
dependency audits. A reverse-proxy body limit alone does not establish remediation.
No production dependency upgrade has been completed in this session.

Axios 1.13.2 also matches a later advisory's version range, but that advisory needs
prior prototype pollution and an interceptor that replaces config while omitting
its own headers. The inspected clients mutate existing config and preserve headers;
reachability of that specific condition is not established. Upgrade and audit the
complete graph rather than labeling every installed old package exploitable.
[Axios maintainer advisory](https://github.com/axios/axios/security/advisories/GHSA-j8rh-479h-cp32).

React Server Components advisories must be assessed against the actual build.
The generic Vite clients render on the client and have no inspected RSC server
entrypoint. A React version number alone is insufficient to claim React2Shell.
[React security notice](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components).

### A16. Password updates race session invalidation and opportunistic rehash

Severity: MAJOR. Axis: Code Quality. Status: IMPLEMENTED, POSTGRESQL CHECKS PENDING.

The Go password path wrote the hash before separately invalidating sessions.
Both implementations could write a rehash based on a stale password read. Python
also incremented a version read into application memory, allowing concurrent
increments to overwrite each other.

All copies now compare the previously verified hash in the database update.
Password changes advance the stored version in the same statement; hash upgrades
preserve the version. Python logout-all uses a database increment. Go session
listing excludes obsolete versions. PostgreSQL tests cover competing password
updates, stale rehash refusal, refresh invalidation, and duplicate owner enrollment.
The SQL and tests compile/typecheck; database execution remains required.

### A17. Native auth and bundling did not match the backend or dependency graph

Severity: MAJOR. Axis: Completeness. Status: IMPLEMENTED, DEVICE CHECKS PENDING.

Native now uses the FastAPI mobile login/refresh/logout endpoints, requires both
tokens, verifies secure-storage writes, avoids retry loops on credential endpoints,
and clears credentials/query data on logout or password change. Persisted query
data is opt-in via `meta.persist`; existing persisted caches are invalidated.

The Babel configuration required `babel-preset-expo`, absent from direct dev
dependencies. It is now declared at the already-locked SDK-compatible version.
Offline iOS export passed after resolving the local module. Fresh frozen install,
physical-device networking, secure-storage failure handling, background recovery,
and logout/refresh races across lifecycle transitions remain verification work.

### A18. Portfolio owner and media boundaries need distinct treatment

Severity: MAJOR. Axis: Code Quality. Status: PARTIAL.

Public owner enrollment is disabled and the public registration screen redirects
to owner login. Management enrollment replaces the race to claim a fresh site.
Media uploads have bounded reads and server-chosen extensions; raw responses add
`nosniff` and a restrictive sandbox CSP.

The baseline singleton repository used select-then-insert without a database
constraint. Profile and settings now have a non-null, unique, true-only singleton
key, with PostgreSQL conflict-safe insertion. Five media references now use
foreign keys with `ON DELETE SET NULL`. Migration `d74b10ce893f` refuses existing
duplicates or dangling references instead of deleting data to make them fit.

Uploads now create files exclusively, flush file/directory state before creating
the database row, and remove files after an insert failure. An uncertain commit
keeps the file because the database may have committed despite a lost response.
Deletion commits its row change before removing the file. Cleanup failures log
the stored filename. This prevents the tested pre-commit deletion failure; it
does not make PostgreSQL and the filesystem one atomic transaction.

Remaining work: execute the seven PostgreSQL cases and migration against a restored
fixture, define crash/orphan reconciliation, and finish format validation. Nine
filesystem failure tests pass with the agent runtime's timer workaround described
above. Cancellation, crash recovery, and real disk/database failures remain limits.

### A19. Remaining architecture and operational review

Severity: MAJOR. Axis: Completeness. Status: OPEN.

The audit has not yet read every distinct source/test file. Remaining concrete
review targets include Go panic-response behavior, obsolete unused blacklist methods,
portfolio crash/orphan recovery, browser cookie ordering and
cross-tab session transitions, and trusted-proxy rate-limit policy. Trace each path
and prove any new finding before
changing it. Existing copied-core parity checks guard drift; they do not establish
that every variant has identical requirements or is correctly abstracted.

The collection still needs a complete resolved-dependency and image audit,
container builds/runtime execution, desktop/mobile rendering, keyboard checks,
real browser auth, native device checks, and restored-database migration tests.
These are explicit outstanding deliverables, not implied successes from lint.

### A20. Go requests and password work need explicit resource admission

Severity: MAJOR. Axis: Code Quality. Status: IMPLEMENTED, LOAD CHECKS PENDING.

Auth and user JSON decoders accepted unbounded bodies. Each password operation
allocated 64 MiB for Argon2 without a concurrency budget, and encoded parameters
were insufficiently bounded before verification. A proxy's body limit does not
protect directly exposed API ports.

Both Go copies now share a 1 MiB decoder that rejects extra JSON values and
oversized streamed bodies. Password operations reserve from a 128 MiB in-flight
work budget; exhausted admission returns HTTP 503 with `Retry-After: 1`. Stored
hash dimensions, lengths, memory, and iteration parameters are validated before
Argon2 runs. Race-detector tests pass. These bounds do not prove the process stays
below its container memory limit: retained allocations, garbage collection, other
work, and actual load still require measurement.

The same review found a new random eight-character JWT key ID on every restart.
It now uses the SHA-256 public-key thumbprint. Cached JWKS verification survives
reloading the same key, while different keys produce different IDs. This fixes
key-discovery reliability; no signature-bypass finding is claimed.

### A21. Delayed client work crossed session boundaries

Severity: MAJOR. Axis: Code Quality. Status: IMPLEMENTED, PLATFORM CHECKS PENDING.

Reproductions showed a late refresh restoring access/refresh state after logout,
an old refresh failure clearing a new session, an old mutation retried with a
different user's token, and stale successful data reaching a replacement session.
Guarding refresh alone was insufficient because logout callbacks also cleared
state after the originating request had become obsolete.

Requests, responses, and refresh attempts now carry a local session version.
Login/logout advances that version; ordinary token rotation preserves it.
Obsolete responses are rejected, replacement sessions have independent refresh
attempts, and logout callbacks check their originating session. Native secure-store
operations execute in call order so a delayed old write cannot finish after a
newer deletion or login write. Explicit logout reports credential-deletion failure.

All 55 client cases and three storage cases pass. HTTP-only browser cookies are
managed outside this JavaScript state boundary; concurrent cookie responses,
multiple tabs, native persistence adapters, and OS keychain behavior still need
their actual platform tests. The repaired client does not add immediate server-side
access-token revocation to single-session logout.

### A22. A Go profile update can overwrite a concurrent role or tier change

Severity: MAJOR. Axis: Code Quality. Status: IMPLEMENTED, POSTGRESQL CHECKS PENDING.

`internal/user/service.go` fetched a whole account, changed one field, and passed
the snapshot to `Repository.Update`. That SQL always wrote name, role, and tier.
A profile request that read an administrator role before a concurrent demotion
could therefore write the old role back. Role and tier updates could also discard
unrelated intervening changes.

Both variants now expose separate name, role, and tier repository methods, each
using one column-specific `UPDATE ... RETURNING` statement. Name omission preserves
the current name, soft-deleted accounts remain unwritable, and the response comes
from the current database row. The service no longer assembles a write from a
stale read. Four controlled stale-read cases per copy pass after failing against
the original service. PostgreSQL SQL behavior and concurrency remain CI gates.

## Distribution decision

Use one generator for local and public consumption. Ship a small Python zipapp
using only the standard library, and one archive per variant. The installed CLI
fetches only the requested archive, verifies it against the release metadata, and
records version, source commit, and template identity in the new project.

Local development must explicitly identify the checkout it uses. Publishing must
require a clean reviewed revision; a local development package must identify dirty
source as such. Never update, reset, or pull inside Carter's working checkout as a
side effect of running `template`.

The installer belongs at `https://angelamos.com/template/install.sh`, following
the requested one-shot installer convention. Hosting is a separate deployment.
Do not claim the URL serves the new installer until its exact response is checked.
The demo's eventual domain is still Carter's decision.

Use pinned release assets. GitHub supports immutable releases and release asset
attestations; checksums alone detect altered bytes but do not establish publisher
identity independently of the download source.
[GitHub release integrity](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).

## Release gates and execution order

1. Preserve and inventory the dirty tree; resolve the live remote state without
   switching branches or sweeping unrelated changes into commits.
2. Implement the shared generator, secret filtering, provenance, package builder,
   installer, and failure-path tests for all eight variants.
3. Repair auth lifecycle and generation/infrastructure contracts. Cover portfolio
   first-owner enrollment/media serving and mobile login/refresh/logout explicitly.
4. Consolidate repeated components or enforce intentional equivalence. Preserve
   app-specific portfolio behavior and documented frontend/backend adapters.
5. Add the neutral UI and verify rendered output while preserving Carter's asset
   changes. Audit all remaining source and dependency versions/advisories.
6. Run generated-project builds and auth tests using the real Docker environment,
   PostgreSQL, and Redis. Run Expo checks plus device/emulator checks where supported.
7. Build release assets from the exact verified commit. Review scoped commits,
   publish the coordinated release, stage the website installer, and verify the
   exact public install command in an isolated installation.

## Self-interrogation

The current strongest findings concern observable wiring and security boundaries.
Do not equate present-day version numbers with quality, or infer vulnerabilities
from age. Access tokens are deliberately excluded from the web persisted store;
do not report them as stored in localStorage. Password-hash mismatch behavior must
be checked against pwdlib rather than assumed from argon2's lower-level API.
Password updates increment the FastAPI token version, but refresh-family lifetime
still needs its own validation. Findings about live compromise, public secrets,
current remote HEAD, and fully passing stacks would exceed the evidence collected.

The initial 14 findings comprised one critical, twelve major, and one minor.
The additional findings above describe dependency, password, native, portfolio,
resource, client-session, account-update, and remaining review work. Implemented
repairs remain subject to the verification limits recorded here. The next
release-critical step is a network-enabled frozen
dependency upgrade and full Docker/PostgreSQL CI run, followed by the remaining
source review and browser/device checks. Remote synchronization and hosting come
after those gates, from a reviewed clean revision.
