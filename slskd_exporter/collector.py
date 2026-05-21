"""Prometheus collector for slskd."""

import logging

import httpx
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

logger = logging.getLogger(__name__)


class SlskdCollector:
    def __init__(self, base_url: str, api_key: str = "") -> None:
        headers = {"accept": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key
        self.client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=15,
        )

    def _get(self, path: str, **params) -> dict | list | None:
        try:
            resp = self.client.get(path, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            logger.exception("Failed to fetch %s", path)
            return None

    # ── /api/v0/application ─────────────────────────────────────────

    def _collect_application(self):
        data = self._get("/api/v0/application")
        if data is None:
            return

        version = data.get("version", {})
        server = data.get("server", {})
        watchdog = data.get("connectionWatchdog", {})
        vpn = data.get("vpn", {})
        relay = data.get("relay", {})
        incoming = data.get("health", {}).get("search", {}).get("incoming", {})
        user = data.get("user", {})
        stats = user.get("statistics", {})
        shares = data.get("shares", {})

        # ── info labels: version + username ──

        info = InfoMetricFamily("slskd", "slskd instance info")
        info.add_metric([], {
            "version": version.get("current", ""),
            "username": user.get("username", ""),
        })
        yield info

        # ── version flags ──

        yield _gauge("slskd_version_is_update_available", "Update available", version.get("isUpdateAvailable"))
        yield _gauge("slskd_version_is_canary", "Canary build", version.get("isCanary"))
        yield _gauge("slskd_version_is_development", "Development build", version.get("isDevelopment"))

        # ── top-level ──

        yield _gauge("slskd_pending_reconnect", "Pending reconnect", data.get("pendingReconnect"))
        yield _gauge("slskd_pending_restart", "Pending restart", data.get("pendingRestart"))

        # ── server ──

        yield _gauge("slskd_server_is_connected", "Server connected", server.get("isConnected"))
        yield _gauge("slskd_server_is_connecting", "Server connecting", server.get("isConnecting"))
        yield _gauge("slskd_server_is_logged_in", "Server logged in", server.get("isLoggedIn"))
        yield _gauge("slskd_server_is_logging_in", "Server logging in", server.get("isLoggingIn"))
        yield _gauge("slskd_server_is_transitioning", "Server transitioning", server.get("isTransitioning"))

        state_info = InfoMetricFamily("slskd_server", "slskd server state")
        state_info.add_metric([], {"state": server.get("state", "")})
        yield state_info

        # ── connection watchdog ──

        yield _gauge("slskd_watchdog_is_enabled", "Watchdog enabled", watchdog.get("isEnabled"))
        yield _gauge("slskd_watchdog_is_attempting_connection", "Watchdog attempting connection", watchdog.get("isAttemptingConnection"))
        yield _gauge("slskd_watchdog_is_awaiting_vpn", "Watchdog awaiting VPN", watchdog.get("isAwaitingVpn"))

        # ── vpn ──

        yield _gauge("slskd_vpn_is_ready", "VPN ready", vpn.get("isReady"))
        yield _gauge("slskd_vpn_is_connected", "VPN connected", vpn.get("isConnected"))

        # ── relay ──

        relay_info = InfoMetricFamily("slskd_relay", "slskd relay state")
        relay_info.add_metric([], {
            "mode": relay.get("mode", ""),
            "controller_state": relay.get("controller", {}).get("state", ""),
        })
        yield relay_info

        # ── search health ──

        yield _gauge("slskd_search_incoming_latency", "Search incoming latency (milliseconds)", incoming.get("latency"))
        yield _gauge("slskd_search_incoming_queue_depth", "Search incoming queue depth (messages)", incoming.get("queueDepth"))
        yield _gauge("slskd_search_incoming_drop_rate", "Search incoming drop rate (ratio)", incoming.get("dropRate"))

        # ── user statistics ──

        yield _gauge("slskd_user_average_speed", "User average speed (bytes/sec)", stats.get("averageSpeed"))
        yield _gauge("slskd_user_directory_count", "User shared directory count", stats.get("directoryCount"))
        yield _gauge("slskd_user_file_count", "User shared file count", stats.get("fileCount"))
        yield _gauge("slskd_user_upload_count", "User total upload count", stats.get("uploadCount"))

        # ── shares ──

        yield _gauge("slskd_shares_scan_pending", "Shares scan pending", shares.get("scanPending"))
        yield _gauge("slskd_shares_scanning", "Shares scanning", shares.get("scanning"))
        yield _gauge("slskd_shares_ready", "Shares ready", shares.get("ready"))
        yield _gauge("slskd_shares_faulted", "Shares faulted", shares.get("faulted"))
        yield _gauge("slskd_shares_cancelled", "Shares cancelled", shares.get("cancelled"))
        yield _gauge("slskd_shares_scan_progress", "Shares scan progress (0.0-1.0)", shares.get("scanProgress"))

    # ── /api/v0/conversations ───────────────────────────────────────

    def _collect_conversations(self):
        data = self._get("/api/v0/conversations", includeInactive="true", unAcknowledgedOnly="false")
        if data is None:
            return

        yield _gauge("slskd_conversations_total", "Total conversations", len(data))

        unacknowledged = sum(c.get("unAcknowledgedMessageCount", 0) for c in data)
        yield _gauge("slskd_conversations_unacknowledged_total", "Total unacknowledged messages", unacknowledged)

    # ── /api/v0/telemetry/reports/transfers/summary ─────────────────

    def _collect_transfers(self):
        data = self._get("/api/v0/telemetry/reports/transfers/summary", start=1)
        if data is None:
            return

        fields = ["totalBytes", "count", "distinctUsers", "averageSpeed", "averageWait", "averageDuration"]

        # metric name mapping so they read nicely in prometheus
        metric_names = {
            "totalBytes": "slskd_transfers_total_bytes",
            "count": "slskd_transfers_count",
            "distinctUsers": "slskd_transfers_distinct_users",
            "averageSpeed": "slskd_transfers_average_speed",
            "averageWait": "slskd_transfers_average_wait",
            "averageDuration": "slskd_transfers_average_duration",
        }

        for field in fields:
            g = GaugeMetricFamily(
                metric_names[field],
                f"Transfer {field}",
                labels=["direction", "status"],
            )
            for direction, statuses in data.items():
                for status, values in statuses.items():
                    g.add_metric(
                        [direction.lower(), status.lower()],
                        float(values.get(field, 0)),
                    )
            yield g

    # ── prometheus_client interface ─────────────────────────────────

    def collect(self):
        yield from self._collect_application()
        yield from self._collect_conversations()
        yield from self._collect_transfers()

    def describe(self):
        # Return empty to indicate metrics are generated dynamically at collect time
        return []


def _gauge(name: str, description: str, value) -> GaugeMetricFamily:
    """Create a simple gauge with a single value. Bools become 1/0."""
    g = GaugeMetricFamily(name, description)
    if isinstance(value, bool):
        g.add_metric([], 1.0 if value else 0.0)
    else:
        g.add_metric([], float(value if value is not None else 0))
    return g
