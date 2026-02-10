# ---------- base ----------
FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- deps ----------
FROM base AS deps

RUN pip install --no-cache-dir uv

COPY pyproject.toml .

RUN uv pip install --system --no-cache -r pyproject.toml

# ---------- runtime ----------
FROM deps AS runtime

COPY . .

CMD ["sh", "start.sh"]
