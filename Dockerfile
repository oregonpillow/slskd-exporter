FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd --create-home --shell /bin/bash exporter

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY slskd_exporter/ slskd_exporter/
RUN uv sync --frozen --no-dev

RUN chown -R exporter:exporter /app
USER exporter

EXPOSE 9099

ENTRYPOINT ["/app/.venv/bin/slskd-exporter"]
