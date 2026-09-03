FROM node:22-bookworm-slim AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
ARG NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
ARG FRONTEND_PORT=3000
ARG FRONTEND_HOSTNAME=0.0.0.0
ENV NEXT_PUBLIC_BACKEND_BASE_URL=${NEXT_PUBLIC_BACKEND_BASE_URL}
ENV PORT=${FRONTEND_PORT}
ENV HOSTNAME=${FRONTEND_HOSTNAME}
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM node:22-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ARG NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8000
ARG FRONTEND_PORT=3000
ARG FRONTEND_HOSTNAME=0.0.0.0
ENV NEXT_PUBLIC_BACKEND_BASE_URL=${NEXT_PUBLIC_BACKEND_BASE_URL}
ENV PORT=${FRONTEND_PORT}
ENV HOSTNAME=${FRONTEND_HOSTNAME}

RUN groupadd --system --gid 1001 nodejs
RUN useradd --system --uid 1001 --gid nodejs --home-dir /app nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE ${FRONTEND_PORT}

CMD ["node", "server.js"]
