# ©AngelaMos | 2026
# Dockerfile

FROM golang:1.26.10-bookworm AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /api ./cmd/api
RUN install -d -m 700 -o 65532 -g 65532 /runtime-keys

FROM builder AS development
CMD ["go", "run", "./cmd/api"]

FROM gcr.io/distroless/static-debian12:nonroot AS production
COPY --from=builder /api /api
COPY --from=builder /build/config.yaml /config.yaml
COPY --from=builder /build/migrations /migrations
COPY --from=builder --chown=65532:65532 /runtime-keys /keys
WORKDIR /
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/api"]
