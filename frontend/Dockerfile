# ---------- base ----------
FROM node:20-alpine AS base

WORKDIR /app

# ---------- deps ----------
FROM base AS deps

COPY package.json package-lock.json* ./

RUN npm ci

# ---------- dev ----------
FROM deps AS dev

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
