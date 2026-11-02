<!-- ©AngelaMos | 2026 -->
<!-- 2026-11-01-python-upgrade.md -->

# Python dependency upgrade research, 2026-11-01

Use the candidate constraints below for the first resolved release matrix. The
October 25 report needs three package updates: Pydantic 2.14.2,
pydantic-settings 2.16.2, and python-multipart 0.0.33. The current uv candidate is
0.13.6. These are researched targets, not a resolved or tested dependency graph.
No application files, manifests, locks, or installed packages were changed by
this research task.

The fresh-evidence window is March 1 through November 1, 2026. Package upload
dates, release-note dates, and advisory publication dates are distinguished below.
Tagged source establishes behavior in a dated release; it does not establish when
each implementation detail originated. Older retained dependencies are marked
explicitly. No claim is based on a search crawl date alone.

## Proposed runtime constraints

Apply common requirements to `backends/fastapi`, `stacks/fastapi-react/backend`,
`stacks/portfolio/backend`, and the two `examples/minimal-production/backend`
copies. Redis, SlowAPI, and structlog are present only in the three full backends;
do not introduce them into the minimal examples merely to make manifests match.
All five manifests currently require Python `>=3.12`.

The upper bounds are a proposed initial migration boundary, not security-advisory
requirements. A resolver must produce the complete compatible graph and actual
artifact hashes. Do not copy version strings into `uv.lock` by hand.

| Requirement | Proposed constraint | Primary dated evidence |
| --- | --- | --- |
| FastAPI | `fastapi>=0.162.0,<0.163.0` | [Publisher release history](https://pypi.org/project/fastapi/), October 23, 2026. Use the base distribution; see dependency-surface decision below. |
| Starlette | `starlette>=1.10.0,<1.11.0` | [1.10.0 release](https://github.com/Kludex/starlette/releases/tag/1.10.0), October 24, 2026. Explicit floor is needed because FastAPI metadata permits older affected Starlette. |
| Pydantic | `pydantic>=2.14.2,<2.15.0` | [Publisher changelog and release history](https://pypi.org/project/pydantic/), October 29, 2026. Replaces October 25 candidate 2.14.1. |
| Settings | `pydantic-settings>=2.16.2,<2.17.0` | [Publisher release history](https://pypi.org/project/pydantic-settings/), October 28, 2026. Replaces 2.16.1. |
| Multipart | `python-multipart>=0.0.33,<0.1.0` | [0.0.33 release](https://github.com/Kludex/python-multipart/releases/tag/0.0.33), October 31, 2026. Requires Python >=3.11. |
| SQLAlchemy | `sqlalchemy[asyncio]>=2.0.55,<2.1.0` | [2.0.55 release](https://github.com/sqlalchemy/sqlalchemy/releases/tag/rel_2_0_55), October 16, 2026. Deliberately retains the 2.0 feature line. |
| Alembic | `alembic>=1.20.1,<1.21.0` | [Publisher release history](https://pypi.org/project/alembic/), uploaded October 22, 2026. |
| asyncpg | `asyncpg>=0.32.0,<0.33.0` | [Publisher release history](https://pypi.org/project/asyncpg/), October 6, 2026. |
| Synchronous PostgreSQL driver | `psycopg2-binary>=2.9.13,<3.0.0` | [Publisher release history](https://pypi.org/project/psycopg2-binary/), September 9, 2026. Still required by current database-manager initialization. |
| JWT | `pyjwt>=2.15.1,<2.16.0` | [Publisher release history](https://pypi.org/project/PyJWT/), September 28, 2026. Includes the September parser hardening; see exposure limits below. |
| Password hashing | `pwdlib[argon2]>=0.3.1,<0.4.0` | [0.3.1 release](https://github.com/frankie567/pwdlib/releases/tag/v0.3.1), August 12, 2026. Removes dependency upper pins and improves return typing. |
| Redis client, full backends | `redis>=7.4.1,<8.0.0` | [Publisher release history](https://pypi.org/project/redis/), June 5, 2026. Deliberately retains the 7.x client line. |
| Rate limiting, full backends | `slowapi>=0.1.10,<0.2.0` | [0.1.10 release](https://github.com/laurentS/slowapi/releases/tag/v0.1.10), June 13, 2026. This is a maintenance update, not a claimed security fix. |
| Logging, full backends | `structlog>=26.1.0,<27.0.0` | [26.1.0 release](https://github.com/hynek/structlog/releases/tag/26.1.0), June 6, 2026. Python >=3.10 remains below the application floor. |
| ASGI server | `uvicorn[standard]>=0.54.0,<0.55.0` | [Publisher release history](https://pypi.org/project/uvicorn/), uploaded September 25, 2026. Retains the existing server and reload/accelerator extra. |
| Email validation | `email-validator>=2.3.0,<3.0.0` | [Publisher release history](https://pypi.org/project/email-validator/), August 26, 2025: older compatibility baseline. Make this existing transitive runtime dependency explicit when removing FastAPI's extra. |
| UUID generation | `uuid6>=2025.0.1,<2026.0.0` | [Publisher release history and versioning policy](https://pypi.org/project/uuid6/), July 4, 2025: older retained baseline. The publisher describes versions from 2025.0.0 onward as semantic versions. |

FastAPI 0.162.0 requires Starlette >=0.46.0 and Pydantic >=2.9.0. The proposed
Starlette and Pydantic versions satisfy those declared bounds. Starlette 1.10.0
requires AnyIO >=4,<5 and Python >=3.11. This metadata establishes no known direct
constraint conflict; it does not substitute for resolution or runtime tests.
[FastAPI tagged metadata](https://raw.githubusercontent.com/fastapi/fastapi/0.162.0/pyproject.toml),
[Starlette tagged metadata](https://raw.githubusercontent.com/Kludex/starlette/1.10.0/pyproject.toml).

## Dependency surface and HTTP clients

**Remove `gunicorn` from all five manifests.** Source inventory found it only in
those manifest declarations. Full-backend Docker entrypoints already execute
Uvicorn directly, and both minimal examples also invoke Uvicorn. This is a local
unused-dependency finding, not a vulnerability claim.

**Replace `fastapi[standard]` with base `fastapi` and explicit email validation.**
The 0.162.0 standard extra adds an OpenTelemetry SDK/exporter, CLI packages,
Fastar, both HTTP client distributions, Jinja2, and extra Pydantic types. Runtime
source uses none of those optional facilities. It does use `EmailStr` in schemas
and configuration, so removing the extra without `email-validator` breaks model
construction. Uvicorn, multipart, and settings are already explicit dependencies.
Base FastAPI still requires `opentelemetry-api`; this proposal does not remove all
OpenTelemetry packages. [FastAPI 0.162.0 dependency metadata, October 23](https://raw.githubusercontent.com/fastapi/fastapi/0.162.0/pyproject.toml).

**Keep current direct HTTPX tests on `httpx>=0.28.1,<0.29.0` for this matrix.**
The three `conftest.py` files use `AsyncClient` with `ASGITransport`, and the release
lifecycle tests use the same direct transport. No `TestClient` use was found in
the inspected application or test source. Starlette 1.10's `TestClient` prefers
`httpx2` and retains an HTTPX fallback with a deprecation warning. That change does
not force migration of these independent ASGI transports.
[Starlette 1.10.0 TestClient source, October 24](https://raw.githubusercontent.com/Kludex/starlette/1.10.0/starlette/testclient.py).

HTTPX 0.28.1 is an older retained baseline, released December 6, 2024; the more
recent 1.0.dev releases are prereleases. HTTPX2 2.16.0 was published October 21,
2026. If a future change introduces Starlette/FastAPI `TestClient`, use a reviewed
development requirement such as `httpx2>=2.16.0,<2.17.0`. Adding HTTPX2 is not
required by the current tests and would need its own import/API validation.
[HTTPX publisher history](https://pypi.org/project/httpx/),
[HTTPX2 publisher history](https://pypi.org/project/httpx2/).

**Keep psycopg2-binary while the synchronous engine exists.** Each
`app/core/database.py` constructs `postgresql+psycopg2` via `create_engine` inside
`DatabaseSessionManager.init`, including during normal lifespan startup. The full
backend Alembic implementation is asynchronous, but that does not make the
separately initialized synchronous driver optional. Removing the engine and
synchronous helper API would be a distinct architectural change. Psycopg 2.9.13
also fixes malformed bytea/int64 parsing; 2.9.12 fixed a malformed-interval loop.
The release-note page has no per-entry date, so the table uses PyPI's dated
publication evidence. [Maintainer release notes](https://www.psycopg.org/docs/news.html).

## Security floors and limits of the evidence

| Advisory publication | Verified affected range and first patch | Local relevance |
| --- | --- | --- |
| [Starlette GHSA-82w8-qh3p-5jfq](https://github.com/Kludex/starlette/security/advisories/GHSA-82w8-qh3p-5jfq), June 12, 2026 | >=0.4.1,<1.3.1; fixed 1.3.1 | URL-encoded form limits were ignored. Public OAuth2 password-form routes make framework form parsing relevant. FastAPI's own broad Starlette minimum does not enforce the patched floor. |
| [Multipart GHSA-5rvq-cxj2-64vf](https://github.com/Kludex/python-multipart/security/advisories/GHSA-5rvq-cxj2-64vf), June 4, 2026 | <0.0.30; fixed 0.0.30 | Quadratic semicolon-separated querystring parsing is reachable through the parser class used by Starlette. |
| [Multipart GHSA-v9pg-7xvm-68hf](https://github.com/Kludex/python-multipart/security/advisories/GHSA-v9pg-7xvm-68hf), June 4, 2026 | <0.0.31; fixed 0.0.31 | The maintainer explicitly states Starlette/FastAPI do not call the affected high-level `parse_form` helper. Package version match alone does not establish application reachability. |
| [PyJWT GHSA-42vr-xj54-vc7v](https://github.com/jpadilla/pyjwt/security/advisories/GHSA-42vr-xj54-vc7v), September 23, 2026 | >=2.0.0a1,<=2.14.0; fixed 2.15.0 | Pre-verification payload recursion needs `PyJWKClient` or disabled signature verification. Current application verification uses its configured algorithm and secret. The maintainer limits confirmed impact to a request exception, not an established worker crash or auth bypass. |

The known combined package parser floor remains Starlette 1.3.1 plus multipart
0.0.31; proposed targets exceed it. This refresh rechecked the limiting advisories
above. The broader October 25 advisory inventory remains a separate artifact;
this is not a complete fresh transitive-package vulnerability audit.

Multipart 0.0.33 introduces opt-in `MAX_FIELDS` and `MAX_FIELD_SIZE` for its own
high-level `FormParser`; both default to unlimited and do not apply to multipart
forms. Starlette 1.10.0 instead uses `QuerystringParser` and enforces its own
`max_fields` and `max_part_size` in callbacks before accumulating field data.
Installing multipart 0.0.33 alone therefore does not establish that the application's
form limits work. Test the actual Starlette integration and real server/proxy path.
[Multipart 0.0.33 release, October 31](https://github.com/Kludex/python-multipart/releases/tag/0.0.33),
[Starlette 1.10.0 parser implementation, October 24](https://raw.githubusercontent.com/Kludex/starlette/1.10.0/starlette/formparsers.py).

## Database and application compatibility decisions

SQLAlchemy 2.1.6, published October 21, is newer overall than 2.0.55. Retaining
2.0.55 avoids combining an ORM feature-line migration with the auth, transaction,
and packaging changes already under test. Its October 16 release fixes async
context-manager cancellation and pool cleanup, so the patch has direct relevance
to session ownership and shutdown. Use native `async with` session ownership.
[Publisher history](https://pypi.org/project/SQLAlchemy/),
[2.0.55 cancellation fixes](https://github.com/sqlalchemy/sqlalchemy/releases/tag/rel_2_0_55).

Use the `asyncio` extra explicitly: 2.0.55's base metadata includes greenlet only
for an architecture allowlist, while its `asyncio` extra requires it without that
condition. This is an existing async runtime requirement made portable, not a new
application feature. [2.0.55 packaging metadata](https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/rel_2_0_55/setup.cfg).

Redis 8.1.0 is the newer overall client, published July 30. Redis 8.0 changed the
default wire protocol to RESP3 while preserving legacy Python response shapes by
default; it also changed retry, timeout, and pool defaults. Keeping 7.4.1 is a
controlled compatibility choice. It is not a claim that Redis server 7 cannot
work with client 8. [Publisher history](https://pypi.org/project/redis/),
[Redis 8.0 release, May 28](https://github.com/redis/redis-py/releases/tag/v8.0.0).

Pydantic 2.14.2 changes JSON validation so unused aliases/field names are treated
as extra data consistently with Python validation. Exercise real request bodies,
especially schemas using aliases or `extra="forbid"`, and nullable/omitted profile
fields. [October 29 changelog](https://pypi.org/project/pydantic/).

All three full factories still supplied `root_path="/api"` at research inspection.
FastAPI 0.162 warns that this constructor parameter is deprecated and asks for
server-level configuration. Move the prefix only after tracing nginx stripping,
direct backend routes, OpenAPI servers, redirects, and Uvicorn's root path. A
deprecation is not evidence that current routes are already broken.
[Tagged constructor behavior, October 23](https://raw.githubusercontent.com/fastapi/fastapi/0.162.0/fastapi/applications.py).

## Minimal-production examples still require source repairs

These findings were read in both example copies on November 1, before this
research task made any edits. They are local implementation findings, separate
from the upstream release evidence:

| File within each `examples/minimal-production` directory | Required change |
| --- | --- |
| `backend/app/core/dependencies.py:36` | Set `Depends(get_db_session, scope="function")`, matching the repaired full backends, so a commit failure is observed before a success response is sent. |
| `backend/app/core/database.py:103` | Replace manually owned async sessions and final `await session.close()` with native `async with self._async_sessionmaker() as session`; preserve commit/rollback behavior. |
| `backend/app/factory.py:28` | Put lifespan `yield` inside `try/finally` so `await sessionmanager.close()` executes when lifespan exits exceptionally. |
| `backend/app/__main__.py:15` | Change the Uvicorn import string from `__main__:app` to the importable application module, `app.__main__:app`. |
| `backend/Dockerfile:18` and `docker-compose.yml:39` | Change the same import string and use `exec uvicorn` after successful migration for signal delivery. Keep application import paths consistent with `/app` and the existing `/app/app` module search path. |
| `backend/Dockerfile:11` | Replace the unlocked editable `pip` development installation with the project's pinned uv workflow and an actual resolver-generated lock. The production image should install the runtime dependency set; test tooling belongs in the test environment. |

The minimal factories already omit the unsupported `openapi_version` constructor
argument. They do not currently supply `root_path`, so copying the full factory's
prefix workaround into them is not an appropriate automatic fix. The existing
full-backend lifecycle regression should be extended to exercise both examples,
including commit failure and shutdown cancellation.

## Tooling and acceptance boundary

Pin uv **0.13.6** consistently in the preparation environment and Docker build.
Its notes are dated October 26, 2026; GitHub and PyPI publication occurred October
27. The release adds managed CPython 3.12.16/3.14.10 and other patch versions,
fixes environment-directory handling, and improves resolver resource use. A uv
update does not itself replace an existing interpreter or the Python inside a
Docker base image. Record the exact interpreter and image digest actually tested.
[uv 0.13.6 release](https://github.com/astral-sh/uv/releases/tag/0.13.6),
[publisher history](https://pypi.org/project/uv/).

Next verification is actual `uv lock --upgrade` resolution for every retained
Python project, then clean locked installs using the chosen tool version.
Record the resolved graph, scan transitive dependencies, and run imports,
OpenAPI generation, forms/login/profile/upload contracts, and lifecycle tests.
Then run real PostgreSQL migrations, concurrent refresh/replay tests, portfolio
transactions, and the generated Docker matrix. The source research did not run
those commands or certify compatible wheels for every architecture. Other
development-tool versions were not comprehensively refreshed in this bounded
report; their resolved versions and checks remain part of the dependency phase.
