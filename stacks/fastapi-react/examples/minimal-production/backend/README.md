<!-- ©AngelaMos | 2026 -->
<!-- README.md -->

# Minimal FastAPI example

This bundled development example demonstrates async SQLAlchemy, PostgreSQL,
Alembic migrations, and JWT access-token authentication. Its historical
`minimal-production` directory name does not establish production readiness.
Use the generated project's main backend for its fuller authentication lifecycle.

## Start from a generated project

Run these commands from the generated project's root. Generation creates the
parent `.env.development` with credentials and high host ports. Compose uses that
file for both interpolation and the backend environment; no additional `.env`
copy is needed inside this example.

```bash
docker compose --env-file .env.development \
  -f examples/minimal-production/docker-compose.yml up --build -d

docker compose --env-file .env.development \
  -f examples/minimal-production/docker-compose.yml port backend 8000
```

Use the reported loopback address with `http://` to open `/docs` or `/health`.
Port 8000 is internal to the container. The API and database publish separate
high host ports, and this example has its own Compose namespace and data volume.

The image installs the committed `uv.lock` with uv and runs as an unprivileged
user. Startup applies Alembic migrations before starting Uvicorn. Source is
mounted read-only; edit files on the host and the development reloader sees them.
PostgreSQL 18 persists its data beneath `/var/lib/postgresql` in a named volume.

```bash
docker compose --env-file .env.development \
  -f examples/minimal-production/docker-compose.yml logs --tail 100 backend

docker compose --env-file .env.development \
  -f examples/minimal-production/docker-compose.yml down
```

Stopping with `down` retains the database volume. Keep runtime services in Docker.

## Authentication scope

`POST /v1/users` registers a user. `POST /v1/auth/login` accepts an OAuth2 password
form with the email in `username` and returns an access token. Send it as a Bearer
token to `GET /v1/auth/me` or `POST /v1/users/change-password`.

This example has no refresh-token flow, rate limiting, or token-version
invalidation after a password change. Its `/v1/auth/logout` endpoint is a
placeholder and does not revoke issued tokens; clients must discard their local
token, which otherwise remains valid until expiry. The full stack's frontend
expects the main backend's refresh contract and cannot be pointed at this example
without adapting its authentication client.

The source, dependencies, migrations, and Docker runtime still require their
release checks. Treat this as a limited example when choosing deployment code.
