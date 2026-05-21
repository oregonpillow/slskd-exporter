"""CLI entrypoint for slskd-exporter using Typer."""

import logging
import signal
import threading

import typer
from prometheus_client import CollectorRegistry, start_http_server

from slskd_exporter.collector import SlskdCollector

app = typer.Typer(
    name="slskd-exporter",
    help="Prometheus exporter for the slskd Soulseek daemon REST API.",
    add_completion=False,
)

logger = logging.getLogger("slskd_exporter")


@app.command()
def serve(
    host: str = typer.Option(
        "http://localhost:5030",
        "--host",
        "-h",
        help="Base URL of the slskd instance (e.g. http://localhost:5030).",
        envvar="SLSKD_HOST",
    ),
    api_key: str = typer.Option(
        "",
        "--api-key",
        "-k",
        help="API key for the slskd instance (optional, only needed if authentication is enabled).",
        envvar="SLSKD_API_KEY",
    ),
    port: int = typer.Option(
        9099,
        "--port",
        "-p",
        help="Port to expose Prometheus metrics on.",
        envvar="SLSKD_EXPORTER_PORT",
    ),
    interval: int = typer.Option(
        30,
        "--interval",
        "-i",
        help="Scrape interval (seconds).",
        envvar="SLSKD_EXPORTER_INTERVAL",
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        "-l",
        help="Logging level (DEBUG, INFO, WARNING, ERROR).",
        envvar="SLSKD_EXPORTER_LOG_LEVEL",
    ),
) -> None:
    """Start the slskd Prometheus exporter."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    registry = CollectorRegistry()
    collector = SlskdCollector(base_url=host, api_key=api_key)
    registry.register(collector)

    logger.info("Starting slskd-exporter on :%d (interval=%ds)", port, interval)
    logger.info("Scraping slskd at %s", host)

    start_http_server(port, registry=registry)
    logger.info("Exporter is running - Ctrl+C to stop")

    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())

    try:
        while not stop.is_set():
            stop.wait(interval)
    except KeyboardInterrupt:
        pass

    logger.info("Shutting down")


def main() -> None:
    """Package entrypoint."""
    app()


if __name__ == "__main__":
    main()
