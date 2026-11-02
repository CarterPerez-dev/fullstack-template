# ©AngelaMos | 2026
# Dockerfile

FROM node:22-slim
RUN corepack enable && corepack prepare pnpm@10.34.9 --activate
WORKDIR /app
COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile
COPY . .
EXPOSE 8081
CMD ["pnpm", "exec", "expo", "start", "--port", "8081", "--lan"]
