<!-- ©AngelaMos | 2026 -->
<!-- 2026-11-01-go-infra-upgrade.md -->

# Go and infrastructure upgrade evidence

Research date: 2026-11-01. Fresh evidence window: 2026-03-01 through
2026-11-01. Release dates and advisory dates qualify; crawl dates do not.
This refresh supplements `2026-10-25-go-infra.md` and supersedes its candidate
versions where listed below.

Use Go **1.26.10**, the coordinated module targets below, PostgreSQL **18.6**,
Redis **7.4.12**, and NGINX stable **1.30.6** as the first upgrade candidate.
The new findings since October 25 are gRPC **1.85.0**, x/net **0.62.0**, and
Redis **7.4.12**. These are verified published versions, not a successfully
resolved or tested application graph. No production file, manifest, lockfile,
image, service, or remote repository was changed by this research task.

## Exact starting point

Both Go manifests still declare `go 1.25.0`; a direct `cmp` of the manifests
passed during this review. The installed command reports
`go version go1.26.5 linux/amd64`. Both production Docker builds select
`golang:1.25-bookworm` and compile with `CGO_ENABLED=0`, then run as UID/GID
65532 in `gcr.io/distroless/static-debian12:nonroot`. CI derives its Go version
from each manifest. Updating only the host executable would leave the build
image and CI policy behind.

The source reviewed uses Chi with `net/http`, sqlx with pgx's `database/sql`
adapter, local ES256 JWKs, go-redis, redis_rate Lua rate limiting, Argon2id, and
an optional outbound OTLP/gRPC exporter. The default server has no TLS/h2c
listener, gRPC server, xDS configuration, remote JWK fetch, or HTML parser.
The Redis Compose service is standalone, authenticated, and has no TLS.
Those are source/configuration observations, not proof about an existing
deployment or user-supplied configuration.

Inspected runtime files include `backends/go-backend/internal/auth/jwt.go`,
`internal/core/{database,redis,telemetry}.go`, `internal/server/server.go`,
`internal/middleware/ratelimit.go`, `internal/config/config.go`, auth/user DTOs,
the Go Docker/Compose definitions, `stacks/go-react/frontend/nginx.conf`,
and `.github/workflows/lint.yml`. The stacked Go manifest matched the standalone
manifest; the eventual upgrade must still compile and test both copies.

## Supported toolchain and coordinated module targets

The official release history lists Go 1.26.10 and 1.27.3 on October 19, 2026,
including the x509 security fix. The download index still lists these supported
series. Go 1.25 is outside the project's two-series support policy after Go
1.27's August release. Select 1.26.10 for the smaller transition; 1.27.3 is a
supported alternative with an additional runtime/database/sql change surface.
[Go release history and support policy](https://go.dev/doc/devel/release),
[official current download metadata](https://go.dev/dl/?mode=json).

| Module | Current | Candidate | Fresh primary evidence and constraint |
| --- | --- | --- | --- |
| `github.com/go-chi/chi/v5` | 5.2.3 | **5.5.0** | [Release, Oct 14](https://github.com/go-chi/chi/releases/tag/v5.5.0). Remain on v5; verify route/middleware behavior. |
| `github.com/go-playground/validator/v10` | 10.23.0 | **10.30.5** | [Release, Sep 20](https://github.com/go-playground/validator/releases/tag/v10.30.5), [tagged manifest](https://raw.githubusercontent.com/go-playground/validator/v10.30.5/go.mod): Go 1.26 minimum. |
| `github.com/jackc/pgx/v5` | 5.7.2 | **5.11.0** | [Release, Sep 7](https://github.com/jackc/pgx/releases/tag/v5.11.0): Go 1.25 minimum; SQL adapter and date/connection parsing changes. |
| `github.com/lestrrat-go/jwx/v3` | 3.0.12 | **3.4.0** | [Release, Oct 23](https://github.com/lestrrat-go/jwx/releases/tag/v3.4.0), [tagged manifest](https://raw.githubusercontent.com/lestrrat-go/jwx/v3.4.0/go.mod): Go 1.25 minimum, resolving the prior report's unknown. |
| `github.com/redis/go-redis/v9` | 9.7.0 | **9.23.0** | [Release, Oct 5](https://github.com/redis/go-redis/releases/tag/v9.23.0): Go 1.26 minimum and a separate pipeline connection pool. |
| OpenTelemetry API, SDK, trace, metric, trace exporter family | 1.33.0 | **1.47.0 together** | [Release, Oct 2](https://github.com/open-telemetry/opentelemetry-go/releases/tag/v1.47.0), [root manifest](https://raw.githubusercontent.com/open-telemetry/opentelemetry-go/v1.47.0/go.mod), [OTLP/gRPC manifest](https://raw.githubusercontent.com/open-telemetry/opentelemetry-go/v1.47.0/exporters/otlp/otlptrace/otlptracegrpc/go.mod): Go 1.26 minimum. |
| `google.golang.org/grpc` | 1.68.1 | **1.85.0** | [Release, Oct 27](https://github.com/grpc/grpc-go/releases/tag/v1.85.0), [tagged manifest](https://raw.githubusercontent.com/grpc/grpc-go/v1.85.0/go.mod): Go 1.26 minimum; includes newer client transport fixes. |
| `golang.org/x/net` | 0.45.0 indirect | **0.62.0** | [Published Oct 27](https://pkg.go.dev/golang.org/x/net), [tagged manifest](https://raw.githubusercontent.com/golang/net/v0.62.0/go.mod): Go 1.26 minimum; supersedes 0.61.0 following HTML security fixes. |
| `golang.org/x/crypto` | 0.43.0 | **0.58.0** | [Published Oct 9](https://pkg.go.dev/golang.org/x/crypto), [tagged manifest](https://raw.githubusercontent.com/golang/crypto/v0.58.0/go.mod): Go 1.26 minimum. |

All of these declared toolchain floors fit Go 1.26.10. That establishes a
candidate tuple, not full dependency compatibility. The exporter declares gRPC
1.83.2 and x/net 0.59.0; gRPC 1.85.0 declares x/net 0.60.0. Request x/net
0.62.0 explicitly so an exporter-only update cannot leave an older networking
module selected. Let the resolver select and checksum indirect dependencies;
do not transplant guessed hashes or manually imitate the upstream `go.sum`.
[Exporter dependency manifest](https://raw.githubusercontent.com/open-telemetry/opentelemetry-go/v1.47.0/exporters/otlp/otlptrace/otlptracegrpc/go.mod),
[gRPC dependency manifest](https://raw.githubusercontent.com/grpc/grpc-go/v1.85.0/go.mod).

The package index shows a contradictory generic "not latest" banner alongside
the displayed versions. The named tags and publication dates are verified;
this report does not use that banner as evidence of a newer release. The module
proxy's `@latest` endpoints were unavailable through the research browser.

Two additional maintenance candidates are available without changing module
majors: koanf/v2 **2.3.8**, released October 7, and x/time **0.16.0**, published
August 19. They are separate from the security-driven minimum above. Koanf's
current release changes merge/copy and decoding edge cases; verify the existing
YAML/default/environment precedence before adopting it. Do not automatically
change provider module paths to a new major.
[Koanf release](https://github.com/knadh/koanf/releases/tag/v2.3.8),
[Koanf manifest, Go 1.23 minimum](https://raw.githubusercontent.com/knadh/koanf/v2.3.8/go.mod),
[x/time publication](https://pkg.go.dev/golang.org/x/time).

## Actual migration surfaces

| Boundary | Source observation and upgrade consequence |
| --- | --- |
| Toolchain | The proposed validator, Redis, OTel, gRPC, and x modules require Go 1.26. A Go 1.25 build cannot satisfy this tuple. Align manifest, Docker builder, CI, and validation toolchain before resolving. |
| PostgreSQL adapter | `database.go` imports pgx/stdlib and calls `sqlx.ConnectContext`. It does not implement `pgx.Rows`. pgx 5.11's added `Rows.TypeMap` requirement therefore does not directly require a local implementation change. Its connection-string and date handling still affect real SQL I/O; test escaped URL passwords, UUIDs, nulls, timestamps, migrations, refresh rotation, and account updates. [Release behavior changes](https://github.com/jackc/pgx/releases/tag/v5.11.0). |
| JWT | The existing `jwt.Sign`, `jwt.Parse`, and `jwt.WithKey` call shapes remain documented in v3.4.0. The release changes NumericDate parsing and signing details. Preserve the existing explicit ES256/issuer/audience validation and stable JWK thumbprint. Test numeric `token_version` extraction, expiration, wrong algorithm/key/issuer/audience, and cached JWKS after restart. A migration to v4 is unnecessary for this tuple. [Versioned v3 API](https://pkg.go.dev/github.com/lestrrat-go/jwx/v3/jwt), [v3.4 release](https://github.com/lestrrat-go/jwx/releases/tag/v3.4.0). |
| Redis and rate limiter | Existing code uses `ParseURL`, `NewClient`, `Ping`, standard pool options, and redis_rate. It does not enable the experimental cache/autopipeline APIs whose fields were removed. The new pipeline pool can affect connection accounting even when the application API compiles. Verify startup, Lua execution, deadlines, limiter contention, and the existing Redis-outage fallback against a real authenticated Redis service. [Redis client release](https://github.com/redis/go-redis/releases/tag/v9.23.0). |
| Validation | Current DTOs use required/email/min/max/omitempty/oneof tags, with `WithRequiredStructEnabled` in handlers. The latest patch's signed-port validation change is not used by those DTOs. The Go floor is a definite change; changed email or Unicode edge behavior across the full version gap still requires request tests. [Validator release](https://github.com/go-playground/validator/releases/tag/v10.30.5). |
| Telemetry | Current code uses `WithEndpoint`, TLS/insecure credentials, batch export, resource host/process data, and shutdown. The gRPC 1.85 client can close connections after prolonged read throttling and changes truncated-message errors. Test collector reconnect, certificate failure, and shutdown flush. [gRPC release](https://github.com/grpc/grpc-go/releases/tag/v1.85.0). |
| Semantic conventions | `telemetry.go` imports `semconv/v1.24.0`. This source review did not establish that path's availability in the proposed OTel download because the targeted source fetch failed. Resolve and compile before claiming zero source changes; any import update needs a resource-attribute compatibility check. |
| Cryptography | This application imports x/crypto/argon2. Updating x/crypto does not justify altering Argon2 memory/time parameters or undoing the existing concurrent-work limit. Exercise stored-hash compatibility and run the container memory/load checks separately. |

No demonstrated source-breaking change beyond the toolchain floor was found in
the inspected call sites. This is intentionally weaker than a successful build:
the proposed graph has not been downloaded or compiled in this session.

## Newly published security boundaries

On October 27, x/net **0.62.0** fixed HTML text-node coalescing with quadratic
allocation/copy behavior and a raw-text rendering namespace issue. The Go
database identifies the parser issue as GO-2026-6860 / CVE-2026-78661 and lists
`html.Parse` variants before 0.62.0. The second fix is recorded in the tagged
maintainer commit as CVE-2026-97045. No application HTML parsing/rendering import
was found here. A module version match alone does not establish exploitability;
run the symbol-aware scan on the resolved graph.
[Go parser advisory, published Oct 27](https://pkg.go.dev/vuln/GO-2026-6860),
[maintainer namespace-rendering fix, committed Oct 27](https://go.googlesource.com/net/+/refs/tags/v0.62.0).

Redis **7.4.12**, released October 26, fixes a heap overflow for cluster-bus
propagation of a PUBLISH/SPUBLISH message larger than 4 GB. The configured
standalone service does not enable that cluster boundary. Use the patched
release as maintenance without describing the template as having a reproduced
cluster exploit. The older Redis 7.4 web release-note page still ends at
7.4.11; the tagged source release notes and official download index establish
the newer release.
[Redis 7.4.12 release](https://github.com/redis/redis/releases/tag/7.4.12),
[tagged release notes](https://raw.githubusercontent.com/redis/redis/7.4.12/00-RELEASENOTES),
[official download index](https://download.redis.io/releases/).

The prior October 25 advisory analysis remains a historical record, not a new
full scan. In particular, do not turn its conditional gRPC server/xDS,
remote-JWK, Redis TLS, or Chi forwarded-header findings into reachable paths
that this application does not configure. Dependency and container scans must
be rerun after resolution; this report is not a clean vulnerability result.

## Images and CI tags

| Surface | Existing configuration | Verified candidate and evidence |
| --- | --- | --- |
| Go builder | `golang:1.25-bookworm` | **`golang:1.26.10-bookworm`** exists in the [official image inventory](https://raw.githubusercontent.com/docker-library/official-images/master/library/golang); language patch dated Oct 19 above. |
| PostgreSQL | `postgres:18-alpine` | **`postgres:18.6-alpine`** is listed in the [official image inventory](https://raw.githubusercontent.com/docker-library/official-images/master/library/postgres). [18.6 release notes, Aug 13](https://www.postgresql.org/docs/release/18.6/) document security fixes and upgrade caveats. Keep the major-18 volume layout and verify on disposable databases. |
| Redis | `redis:7-alpine` | **`redis:7.4.12-alpine`** is listed in the [official image inventory](https://raw.githubusercontent.com/docker-library/official-images/master/library/redis). This preserves the existing major and standalone behavior. |
| Go-stack NGINX | `nginx:1.27-alpine` | **`nginx:1.30.6-alpine`** is listed in the [official image inventory](https://raw.githubusercontent.com/docker-library/official-images/master/library/nginx); [stable release dated Oct 14](https://nginx.org/news.html). Verify SPA routing, `/api/` prefix stripping, request limits, and forwarding headers. |
| Go runtime | `gcr.io/distroless/static-debian12:nonroot` | Exact contents, digest, certificate store, and UID/key-volume behavior are unverified. Retain the runtime model until the built image is scanned and executed. |
| Optional Jaeger | `jaegertracing/all-in-one:1.54` | [Jaeger 2.22.0, Oct 6](https://github.com/jaegertracing/jaeger/releases/tag/v2.22.0), is a migration candidate. It requires configuration/runtime validation; an all-in-one v1 to v2 change is not established by changing a tag string. |

Image inventory files are current, undated operational metadata, not new
research publications. They confirm tag declarations and architectures, not
the digest actually pulled on this host. Record platform/digest and scan the
resulting images during the authorized runtime matrix. No digest is supplied
here, and no Docker command or host configuration change was attempted.

All six action versions already selected in `.github/workflows/lint.yml`
resolve to genuine maintainer releases:

| Existing action tag | Maintainer release date and source |
| --- | --- |
| `actions/checkout@v7.0.1` | [2026-07-20](https://github.com/actions/checkout/releases/tag/v7.0.1) |
| `actions/setup-python@v7.1.0` | [2026-10-22](https://github.com/actions/setup-python/releases/tag/v7.1.0) |
| `actions/setup-go@v7.0.0` | [2026-07-16](https://github.com/actions/setup-go/releases/tag/v7.0.0) |
| `actions/setup-node@v7.1.0` | [2026-10-08](https://github.com/actions/setup-node/releases/tag/v7.1.0) |
| `pnpm/action-setup@v6.1.0` | [2026-09-05](https://github.com/pnpm/action-setup/releases/tag/v6.1.0) |
| `astral-sh/setup-uv@v10.3.2` | [2026-10-22](https://github.com/astral-sh/setup-uv/releases/tag/v10.3.2) |

The setup-go and checkout action manifests select Node 24 as their action
runtime. This is separate from the application's `setup-node` selection.
Release-page authenticity does not prove that this repository's workflow ran.
No full commit SHA was inferred from the abbreviated release display.
[setup-go tagged action manifest](https://raw.githubusercontent.com/actions/setup-go/v7.0.0/action.yml),
[checkout tagged action manifest](https://raw.githubusercontent.com/actions/checkout/v7.0.1/action.yml).

The CI uv **0.13.5** pin is also real: its release notes name October 21,
while GitHub publication is October 22. Preserve this distinction instead of
using a crawler date. The Python report owns the final uv/Python selection.
[uv release and managed-interpreter security notes](https://github.com/astral-sh/uv/releases/tag/0.13.5).

Upgrade the Go vulnerability tool from **1.1.4** to the verified **1.9.0**
candidate when updating CI. The tagged commit is October 10 in its displayed
Pacific offset; the package index publication is October 11. Its manifest
requires Go 1.26. Run it with the same Go version used to build the application,
because source analysis uses that toolchain's build configuration.
[Package publication and scan behavior](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck),
[tagged source commit](https://go.googlesource.com/vuln/+/refs/tags/v1.9.0),
[tool manifest](https://raw.githubusercontent.com/golang/vuln/v1.9.0/go.mod).

## Resolver and verification handoff

The following is a reviewable command set for each Go module once ordinary
registry access works. It was not executed by this research task. It deliberately
selects explicit candidate versions and leaves optional koanf/x/time updates
for a separate reviewed decision.

```sh
GOTOOLCHAIN=go1.26.10 go get go@1.26.10 \
  github.com/go-chi/chi/v5@v5.5.0 \
  github.com/go-playground/validator/v10@v10.30.5 \
  github.com/jackc/pgx/v5@v5.11.0 \
  github.com/lestrrat-go/jwx/v3@v3.4.0 \
  github.com/redis/go-redis/v9@v9.23.0 \
  go.opentelemetry.io/otel@v1.47.0 \
  go.opentelemetry.io/otel/sdk@v1.47.0 \
  go.opentelemetry.io/otel/trace@v1.47.0 \
  go.opentelemetry.io/otel/metric@v1.47.0 \
  go.opentelemetry.io/otel/exporters/otlp/otlptrace@v1.47.0 \
  go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc@v1.47.0 \
  google.golang.org/grpc@v1.85.0 \
  golang.org/x/net@v0.62.0 \
  golang.org/x/crypto@v0.58.0
GOTOOLCHAIN=go1.26.10 go mod tidy
GOTOOLCHAIN=go1.26.10 go mod verify
GOTOOLCHAIN=go1.26.10 go vet ./...
GOTOOLCHAIN=go1.26.10 go test -race -count=1 ./...
GOTOOLCHAIN=go1.26.10 go build ./cmd/api
GOTOOLCHAIN=go1.26.10 go run golang.org/x/vuln/cmd/govulncheck@v1.9.0 ./...
```

Review both resulting manifest/sum diffs and their parity. PostgreSQL tests must
have a disposable `TEST_POSTGRES_URL` and must actually execute, rather than
report skipped cases. Then run the existing Docker-based startup/migration/key
bootstrap tests, authenticated Redis limiter checks, OTLP collector checks,
Argon2 load/memory checks, and Go-stack browser authentication flow. Keep the
project's literal Compose namespaces and arbitrary high host ports.

Remaining unknowns are resolver success, complete indirect graph selection,
compile compatibility including the old semconv path, symbol-aware advisory
results, actual image digests, container/database behavior, and hosted CI
results. None is represented here as passed.

## Older baselines retained explicitly

sqlx **1.4.0** remains the version reached by its maintainer latest-release
endpoint; redis_rate **10.0.1** is dated April 2, 2023, and UUID **1.6.0** is
dated January 23, 2024. These are older baseline/API references, excluded from
the fresh research window. No new replacement library is justified solely by
their age. They still require graph scanning and integration validation.
[sqlx release endpoint](https://github.com/jmoiron/sqlx/releases/latest),
[redis_rate version metadata](https://pkg.go.dev/github.com/go-redis/redis_rate/v10),
[UUID version metadata](https://pkg.go.dev/github.com/google/uuid).
