<!-- ©AngelaMos | 2026 -->
<!-- release-notes.md -->

# template

Install a small command that downloads only the application starter you select:

```bash
curl -fsSL https://angelamos.com/template/install.sh | bash
template fastapi-stack my-app
```

The GitHub release also includes `install.sh` for direct installation. Run it with
`--version TAG` to select a specific release, including a prerelease. Hosting the
Angelamos endpoint is a separate deployment from publishing these assets.

Available web/backend starters: `go`, `fastapi`, `open`, `frontend`,
`fastapi-stack`, `go-stack`, and `portfolio`. Generation assigns project names,
high host ports, independent development/production credentials, and source
provenance. The installed command downloads a checksum-verified archive for the
selected starter; it does not clone the repository. Existing project files and
local development installations are preserved.

This release includes the authentication, dependency, infrastructure, and neutral
frontend updates recorded in the repository audit. Release CI checks the
generator, locked web/backend builds and audits, PostgreSQL tests and migrations,
and generated web/backend container startup. These checks do not establish real
browser authentication, production TLS, backup recovery, or deployment readiness
for a particular application.

`native` remains available as an **experimental** Expo starter. Its dependency,
regression, and export results are recorded, but Docker, signed binary, and device
validation are deferred. Native checks are opt-in and do not gate this release.
The bundled `minimal-production` directories are limited authentication examples;
use the main backends for the complete session lifecycle.

See [installation and variants](https://github.com/CarterPerez-dev/fullstack-template/tree/main/template-tool),
[operations](https://github.com/CarterPerez-dev/fullstack-template/blob/main/docs/template-operations.md),
and the [audit record](https://github.com/CarterPerez-dev/fullstack-template/blob/main/docs/plans/2026-10-25-template-release-audit.md)
for scope and evidence.
