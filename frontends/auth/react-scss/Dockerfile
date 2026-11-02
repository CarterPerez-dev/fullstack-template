# ©AngelaMos | 2026
# Dockerfile

FROM node:22-slim AS dependencies
RUN corepack enable && corepack prepare pnpm@10.34.9 --activate
WORKDIR /app
COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile
COPY . .

FROM dependencies AS development
CMD ["pnpm", "dev", "--host", "0.0.0.0"]

FROM dependencies AS builder
ARG VITE_APP_TITLE="Your project"
ENV VITE_APP_TITLE=$VITE_APP_TITLE
ENV VITE_API_URL=/api
RUN pnpm build

FROM nginx:1.27-alpine AS production
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 8080
