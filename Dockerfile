# Stage 0: Pin uv version
FROM ghcr.io/astral-sh/uv:0.11.18@sha256:78bc42400d77b0678ba95765305c826652ed5431f399257271dda681d0318f03 AS uv-dist

# Stage 1: Export locked dependencies and build wheel
FROM python:3.13.12-slim@sha256:f1927c75e81efd1e091dbd64b6c0ecaa5630b38635a3d1c04034ac636e1f94c8 AS builder

WORKDIR /tmp

COPY --from=uv-dist /uv /uvx /usr/local/bin/

COPY pyproject.toml README.md uv.lock ./
COPY src src/

RUN uv export --no-dev --no-emit-project -o requirements.txt \
 && uv build

# Stage 2: Runtime
FROM python:3.13.12-slim@sha256:f1927c75e81efd1e091dbd64b6c0ecaa5630b38635a3d1c04034ac636e1f94c8

ARG UID=1000
ARG GID=1000
ARG APP_USER=appuser

LABEL org.opencontainers.image.source=https://go.hugobatista.com/gh/joplin-to-obsidian
LABEL security.scan="true"
LABEL maintainer="Hugo Batista <code@hugobatista.com>"

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_ROOT_USER_ACTION=ignore

# Privileged work: package installs, user creation, app directory setup (all before USER)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && rm -rf /var/lib/apt/lists/* \
 && addgroup --system --gid ${GID} ${APP_USER} \
 && adduser --system --uid ${UID} --gid ${GID} --home /app --shell /sbin/nologin ${APP_USER} \
 && mkdir -p /app && chown -R ${APP_USER}:${APP_USER} /app

WORKDIR /app

# Install locked dependencies (leveraging Docker layer cache)
COPY --chown=${UID}:${GID} --from=builder /tmp/requirements.txt ./
RUN pip install --no-cache --upgrade pip \
 && pip install --no-cache --require-hashes -r ./requirements.txt

# Install the app package from the pre-built wheel (no source in final image)
COPY --chown=${UID}:${GID} --from=builder /tmp/dist/*.whl /tmp/
RUN pip install --no-cache /tmp/*.whl && rm /tmp/*.whl

USER ${APP_USER}

HEALTHCHECK --interval=300s --timeout=10s --start-period=5s --retries=3 \
    CMD joplin-to-obsidian --help || exit 1

ENTRYPOINT ["joplin-to-obsidian"]
