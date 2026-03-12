"""
Otomate MCP Connector — Sample Python Client
================================================

Connects to the ce-mcp server and invokes MCP tools programmatically.
Reads connection details from `.vscode/mcp.json` in the project root.
Handles corporate proxy environments (Zscaler, etc.) automatically.

Configuration
-------------
Place your MCP server details in `.vscode/mcp.json` at the project root:

    {
        "servers": {
            "ce-mcp": {
                "type": "http",
                "url": "https://your-mcp-server.com",
                "headers": {
                    "gitlab-token": "glpat-xxxxx",
                    "authorization": "Bearer your-token"
                }
            }
        }
    }

The connector also supports the flat format:

    {
        "ce-mcp": {
            "http": "https://your-mcp-server.com",
            "gitlab-token": "glpat-xxxxx",
            "authorization": "Bearer your-token"
        }
    }

Proxy / Zscaler
---------------
The connector auto-detects system proxy settings and handles SSL
certificate verification for corporate environments.  If Zscaler or
another SSL-intercepting proxy is in use, set one of:

    export SSL_CERT_FILE=/path/to/zscaler-ca-bundle.pem
    export REQUESTS_CA_BUNDLE=/path/to/zscaler-ca-bundle.pem
    export NODE_EXTRA_CA_CERTS=/path/to/zscaler-ca-bundle.pem

Or place the CA bundle at any of these paths:
    - /etc/ssl/certs/ca-certificates.crt  (Debian/Ubuntu)
    - /etc/pki/tls/certs/ca-bundle.crt    (RHEL/CentOS)
    - /usr/local/share/ca-certificates/    (macOS custom)

Usage
-----
    python scripts/mcp_connector.py
    python scripts/mcp_connector.py --server ce-mcp
    python scripts/mcp_connector.py --config /path/to/.vscode/mcp.json
    python scripts/mcp_connector.py --list-servers
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("otomate.mcp")

# Default MCP server name to look for in mcp.json
DEFAULT_SERVER_NAME = "ce-mcp"

# Standard locations to search for the CA bundle
_CA_BUNDLE_PATHS = [
    # Explicit env vars (highest priority)
    os.getenv("SSL_CERT_FILE", ""),
    os.getenv("REQUESTS_CA_BUNDLE", ""),
    os.getenv("NODE_EXTRA_CA_CERTS", ""),
    # Common OS paths
    "/etc/ssl/certs/ca-certificates.crt",
    "/etc/pki/tls/certs/ca-bundle.crt",
    "/etc/ssl/cert.pem",
    "/usr/local/etc/openssl/cert.pem",
    "/usr/local/etc/openssl@1.1/cert.pem",
    "/usr/local/etc/openssl@3/cert.pem",
]


def _find_ca_bundle() -> str | None:
    """Return the first existing CA bundle path, or None."""
    for path in _CA_BUNDLE_PATHS:
        if path and os.path.isfile(path):
            return path
    return None


def _build_ssl_context() -> ssl.SSLContext:
    """
    Build an SSL context that works in corporate proxy environments.

    Order of preference:
    1. Custom CA bundle from env vars (SSL_CERT_FILE, REQUESTS_CA_BUNDLE, etc.)
    2. System default certificates
    3. Fallback: unverified context (with warning) — last resort for Zscaler
    """
    ctx = ssl.create_default_context()

    ca_bundle = _find_ca_bundle()
    if ca_bundle:
        try:
            ctx.load_verify_locations(ca_bundle)
            logger.info("SSL: Using CA bundle from %s", ca_bundle)
            return ctx
        except ssl.SSLError as exc:
            logger.warning("SSL: Failed to load CA bundle %s: %s", ca_bundle, exc)

    # Try system defaults
    try:
        ctx.load_default_certs()
        logger.info("SSL: Using system default certificates")
        return ctx
    except Exception:
        pass

    # If nothing else works — check if we can connect at all
    # If SSL verification keeps failing, offer an unverified fallback
    if os.getenv("MCP_SSL_NOVERIFY", "").lower() in ("1", "true", "yes"):
        logger.warning(
            "SSL: ⚠ Certificate verification DISABLED (MCP_SSL_NOVERIFY=1). "
            "This is insecure — use only for debugging."
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    logger.info("SSL: Using default context")
    return ctx


def _build_opener(ssl_context: ssl.SSLContext) -> urllib.request.OpenerDirector:
    """
    Build a urllib opener that respects system proxy settings and uses
    our custom SSL context.  This handles Zscaler and other corporate
    proxies transparently.
    """
    # ProxyHandler with no args reads HTTP_PROXY / HTTPS_PROXY / NO_PROXY
    # from the environment — exactly what corporate networks set up.
    proxy_handler = urllib.request.ProxyHandler()
    https_handler = urllib.request.HTTPSHandler(context=ssl_context)

    opener = urllib.request.build_opener(proxy_handler, https_handler)
    return opener


# ---------------------------------------------------------------------------
# MCP JSON config loader
# ---------------------------------------------------------------------------


def _find_mcp_config(explicit_path: str | None = None) -> pathlib.Path | None:
    """
    Locate `.vscode/mcp.json`.

    Search order:
    1. Explicit path (--config CLI flag)
    2. Current working directory  → .vscode/mcp.json
    3. Walk up parent directories → .vscode/mcp.json  (finds project root)
    """
    if explicit_path:
        p = pathlib.Path(explicit_path)
        if p.is_file():
            return p
        logger.error("Explicit config path does not exist: %s", explicit_path)
        return None

    cwd = pathlib.Path.cwd()
    for directory in [cwd, *cwd.parents]:
        candidate = directory / ".vscode" / "mcp.json"
        if candidate.is_file():
            logger.info("Found mcp.json at %s", candidate)
            return candidate
        # Stop at filesystem root or home directory
        if directory == pathlib.Path.home() or directory == directory.parent:
            break

    logger.warning("Could not find .vscode/mcp.json in any parent directory")
    return None


@dataclass
class MCPServerConfig:
    """Parsed connection details for a single MCP server."""

    name: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 30

    def __post_init__(self) -> None:
        # Normalise URL — strip trailing slash
        self.url = self.url.rstrip("/")


def _parse_mcp_json(path: pathlib.Path) -> dict[str, MCPServerConfig]:
    """
    Parse `.vscode/mcp.json` and return a dict of server-name → MCPServerConfig.

    Supports multiple formats:

    Format A (VS Code native — "servers" wrapper):
        {
            "servers": {
                "ce-mcp": {
                    "type": "http",
                    "url": "https://...",
                    "headers": { "gitlab-token": "...", "authorization": "..." }
                }
            }
        }

    Format B (flat — each key is a server name):
        {
            "ce-mcp": {
                "http": "https://...",
                "gitlab-token": "glpat-...",
                "authorization": "Bearer ..."
            }
        }
    """
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    servers: dict[str, MCPServerConfig] = {}

    # ---- Format A: { "servers": { ... } } ----
    if "servers" in raw and isinstance(raw["servers"], dict):
        for name, entry in raw["servers"].items():
            if not isinstance(entry, dict):
                continue
            url = entry.get("url", "")
            headers = dict(entry.get("headers", {}))
            if url:
                servers[name] = MCPServerConfig(name=name, url=url, headers=headers)
        if servers:
            return servers

    # ---- Format B: flat { "server-name": { "http": "...", ... } } ----
    for name, entry in raw.items():
        if not isinstance(entry, dict):
            continue

        # "http" key holds the server URL
        url = entry.get("http", "") or entry.get("url", "")
        if not url:
            continue

        # Everything except "http" / "url" / "type" is treated as a header
        headers = {
            k: v
            for k, v in entry.items()
            if k not in ("http", "url", "type") and isinstance(v, str)
        }

        servers[name] = MCPServerConfig(name=name, url=url, headers=headers)

    return servers


# ---------------------------------------------------------------------------
# MCP Client
# ---------------------------------------------------------------------------


class MCPClientError(Exception):
    """Raised when an MCP tool call fails."""


@dataclass
class MCPToolResult:
    """Parsed response from an MCP tool invocation."""

    tool_name: str
    success: bool
    data: Any = None
    error: str | None = None
    raw_response: dict = field(default_factory=dict)


class MCPClient:
    """
    MCP client that calls tools exposed by the ce-mcp server via its
    HTTP/JSON-RPC interface.

    Reads connection details from `.vscode/mcp.json` and handles
    corporate proxy / Zscaler environments automatically.
    """

    def __init__(
        self,
        server_config: MCPServerConfig | None = None,
        config_path: str | None = None,
        server_name: str = DEFAULT_SERVER_NAME,
    ) -> None:
        """
        Initialise the client.

        Parameters
        ----------
        server_config:
            Pre-built server config.  If provided, config_path is ignored.
        config_path:
            Explicit path to mcp.json.  If None, auto-discover.
        server_name:
            Which server entry to use from mcp.json (default: "ce-mcp").
        """
        if server_config:
            self.server = server_config
        else:
            self.server = self._load_server(config_path, server_name)

        self._request_id = 0
        self._ssl_context = _build_ssl_context()
        self._opener = _build_opener(self._ssl_context)
        logger.info("MCPClient ready — server: %s (%s)", self.server.name, self.server.url)

    @staticmethod
    def _load_server(config_path: str | None, server_name: str) -> MCPServerConfig:
        """Locate mcp.json, parse it, and return the requested server entry."""
        json_path = _find_mcp_config(config_path)
        if json_path is None:
            logger.error(
                "No .vscode/mcp.json found.  Create one with your MCP server "
                "details or pass --config /path/to/mcp.json"
            )
            sys.exit(1)

        servers = _parse_mcp_json(json_path)
        if not servers:
            logger.error("mcp.json exists but contains no valid server entries")
            sys.exit(1)

        if server_name in servers:
            return servers[server_name]

        # If the requested name isn't found, list what's available
        available = ", ".join(servers.keys())
        logger.error(
            "Server '%s' not found in mcp.json.  Available: %s",
            server_name,
            available,
        )
        # Fall back to first server if only one exists
        if len(servers) == 1:
            only_name = next(iter(servers))
            logger.info("Using the only available server: %s", only_name)
            return servers[only_name]

        sys.exit(1)

    # ----- low-level transport ------------------------------------------------

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _post(self, payload: dict) -> dict:
        """Send a JSON-RPC 2.0 request to the MCP server."""
        body = json.dumps(payload).encode("utf-8")
        url = f"{self.server.url}/rpc"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Merge headers from mcp.json (gitlab-token, authorization, etc.)
        for key, value in self.server.headers.items():
            headers[key] = value

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with self._opener.open(req, timeout=self.server.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            raise MCPClientError(
                f"HTTP {exc.code} from MCP server: {body_text}"
            ) from exc
        except urllib.error.URLError as exc:
            reason = str(exc.reason)

            # Provide actionable hints for common proxy / SSL errors
            hints: list[str] = []
            if "CERTIFICATE_VERIFY_FAILED" in reason or "SSL" in reason.upper():
                hints.append(
                    "SSL certificate verification failed.  This often happens "
                    "with Zscaler or corporate proxies that intercept HTTPS."
                )
                hints.append(
                    "Fix: export SSL_CERT_FILE=/path/to/your-corp-ca-bundle.pem"
                )
                hints.append(
                    "Debug: export MCP_SSL_NOVERIFY=1  (insecure, for testing only)"
                )
            elif "proxy" in reason.lower() or "tunnel" in reason.lower():
                hints.append(
                    "Proxy connection failed.  Check HTTPS_PROXY and NO_PROXY "
                    "environment variables."
                )

            msg = f"Cannot reach MCP server at {url}: {reason}"
            if hints:
                msg += "\n\n" + "\n".join(f"  💡 {h}" for h in hints)

            raise MCPClientError(msg) from exc

    # ----- public API ---------------------------------------------------------

    def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> MCPToolResult:
        """
        Invoke an MCP tool by name.

        Parameters
        ----------
        tool_name:
            One of the 113 ce-mcp tool names, e.g.
            ``get_jira_issue``, ``get_gitlab_file_content``,
            ``search_jira_issues``, ``get_sonarqube_issues``, etc.
        arguments:
            Tool-specific parameters as a dict.

        Returns
        -------
        MCPToolResult with parsed data on success or an error message.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
        }

        logger.info("→ Calling tool: %s  args=%s", tool_name, json.dumps(arguments or {}))

        raw = self._post(payload)

        # JSON-RPC error envelope
        if "error" in raw:
            err_msg = raw["error"].get("message", str(raw["error"]))
            logger.error("← Tool %s failed: %s", tool_name, err_msg)
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                error=err_msg,
                raw_response=raw,
            )

        result_data = raw.get("result", {})
        logger.info("← Tool %s succeeded", tool_name)
        return MCPToolResult(
            tool_name=tool_name,
            success=True,
            data=result_data,
            raw_response=raw,
        )

    def list_tools(self) -> list[dict]:
        """
        Ask the MCP server for its tool catalogue.

        Returns a list of tool descriptors (name, description, inputSchema).
        """
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {},
        }

        raw = self._post(payload)
        tools = raw.get("result", {}).get("tools", [])
        logger.info("Server exposes %d tools", len(tools))
        return tools


# ---------------------------------------------------------------------------
# Sample MCP tool calls
# ---------------------------------------------------------------------------


def sample_get_jira_issue(client: MCPClient) -> None:
    """Fetch a Jira issue by key — simplest possible read operation."""

    result = client.call_tool(
        tool_name="get_jira_issue",
        arguments={"issue_key": "PROJ-101"},
    )

    if result.success:
        print("\n✅ get_jira_issue succeeded:")
        print(json.dumps(result.data, indent=2))
    else:
        print(f"\n❌ get_jira_issue failed: {result.error}")


def sample_search_jira_issues(client: MCPClient) -> None:
    """Run a JQL search — demonstrates a parameterised query."""

    result = client.call_tool(
        tool_name="search_jira_issues",
        arguments={
            "jql": 'project = "PROJ" AND status = "In Progress" ORDER BY updated DESC',
            "max_results": 5,
        },
    )

    if result.success:
        print("\n✅ search_jira_issues succeeded:")
        print(json.dumps(result.data, indent=2))
    else:
        print(f"\n❌ search_jira_issues failed: {result.error}")


def sample_get_gitlab_file(client: MCPClient) -> None:
    """Read a file from a GitLab repository."""

    result = client.call_tool(
        tool_name="get_gitlab_file_content",
        arguments={
            "project_id": "my-group/my-repo",
            "file_path": "src/main.ts",
            "ref": "develop",
        },
    )

    if result.success:
        print("\n✅ get_gitlab_file_content succeeded:")
        content = json.dumps(result.data, indent=2)
        print(content[:200], "..." if len(content) > 200 else "")
    else:
        print(f"\n❌ get_gitlab_file_content failed: {result.error}")


def sample_get_sonarqube_issues(client: MCPClient) -> None:
    """Retrieve SonarQube quality issues for a project."""

    result = client.call_tool(
        tool_name="get_sonarqube_issues",
        arguments={
            "project_key": "com.example:my-service",
            "severities": "CRITICAL,BLOCKER",
            "statuses": "OPEN",
        },
    )

    if result.success:
        print("\n✅ get_sonarqube_issues succeeded:")
        print(json.dumps(result.data, indent=2))
    else:
        print(f"\n❌ get_sonarqube_issues failed: {result.error}")


def sample_list_tools(client: MCPClient) -> None:
    """List all tools the MCP server exposes — useful for discovery."""

    tools = client.list_tools()
    print(f"\n📋 MCP server exposes {len(tools)} tools:")
    for t in tools[:10]:
        print(f"   • {t.get('name', '?'):40s} — {t.get('description', '')[:60]}")
    if len(tools) > 10:
        print(f"   … and {len(tools) - 10} more")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp_connector",
        description="Otomate MCP Connector — connect to ce-mcp and invoke tools",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Explicit path to .vscode/mcp.json (default: auto-discover)",
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_SERVER_NAME,
        help=f"Server name from mcp.json (default: {DEFAULT_SERVER_NAME})",
    )
    parser.add_argument(
        "--list-servers",
        action="store_true",
        help="List all servers in mcp.json and exit",
    )
    parser.add_argument(
        "--tool",
        default=None,
        help="Call a single tool by name (e.g. get_jira_issue)",
    )
    parser.add_argument(
        "--args",
        default="{}",
        help='JSON arguments for --tool (e.g. \'{"issue_key": "PROJ-101"}\')',
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug-level logging",
    )
    return parser


def _cmd_list_servers(config_path: str | None) -> None:
    """Print all servers found in mcp.json."""
    json_path = _find_mcp_config(config_path)
    if json_path is None:
        print("❌ No .vscode/mcp.json found", file=sys.stderr)
        sys.exit(1)

    servers = _parse_mcp_json(json_path)
    if not servers:
        print("⚠ mcp.json exists but contains no valid server entries")
        sys.exit(1)

    print(f"📋 Servers in {json_path}:\n")
    for name, cfg in servers.items():
        print(f"  • {name}")
        print(f"    URL:     {cfg.url}")
        print(f"    Headers: {', '.join(cfg.headers.keys()) or '(none)'}")
        print()


def main() -> None:
    """Entry point — parse CLI args and run."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # ---- list-servers mode ----
    if args.list_servers:
        _cmd_list_servers(args.config)
        return

    print("=" * 60)
    print("  Otomate — MCP Connector")
    print("=" * 60)

    client = MCPClient(config_path=args.config, server_name=args.server)

    # ---- single tool mode ----
    if args.tool:
        try:
            tool_args = json.loads(args.args)
        except json.JSONDecodeError as exc:
            print(f"❌ Invalid JSON in --args: {exc}", file=sys.stderr)
            sys.exit(1)

        result = client.call_tool(args.tool, tool_args)
        if result.success:
            print(f"\n✅ {args.tool} succeeded:")
            print(json.dumps(result.data, indent=2))
        else:
            print(f"\n❌ {args.tool} failed: {result.error}")
        return

    # ---- demo mode: run all sample calls ----
    sample_list_tools(client)
    sample_get_jira_issue(client)
    sample_search_jira_issues(client)
    sample_get_gitlab_file(client)
    sample_get_sonarqube_issues(client)

    print("\n" + "=" * 60)
    print("  All sample calls complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
