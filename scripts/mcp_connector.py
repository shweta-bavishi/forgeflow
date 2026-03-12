"""
Otomate MCP Connector — Sample Python Client
================================================

Demonstrates how to connect to the ce-mcp server and invoke MCP tools
programmatically.  This file is a **reference example** — adapt the
transport, authentication, and tool names to your environment.

Usage
-----
    # Set required environment variables first
    export MCP_SERVER_URL="http://localhost:3000"
    export GITLAB_TOKEN="glpat-xxxxx"
    export JIRA_TOKEN="your-jira-api-token"
    export JIRA_EMAIL="you@company.com"

    python scripts/mcp_connector.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
import urllib.request
import urllib.error
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


@dataclass
class MCPConfig:
    """Connection settings for the ce-mcp server."""

    server_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
    gitlab_token: str = os.getenv("GITLAB_TOKEN", "")
    jira_token: str = os.getenv("JIRA_TOKEN", "")
    jira_email: str = os.getenv("JIRA_EMAIL", "")
    timeout_seconds: int = int(os.getenv("MCP_TIMEOUT", "30"))
    # Add additional credentials as needed:
    # confluence_token, jenkins_token, sonarqube_token, etc.


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
    Minimal MCP client that calls tools exposed by the ce-mcp server
    via its HTTP/JSON-RPC interface.

    In a production setup you would typically use the official MCP SDK
    (e.g. ``@anthropic-ai/mcp-sdk``) or an equivalent Python binding.
    This client demonstrates the wire-level protocol so you can
    understand — and debug — what happens under the hood.
    """

    def __init__(self, config: MCPConfig | None = None) -> None:
        self.config = config or MCPConfig()
        self._request_id = 0
        logger.info("MCPClient initialised — server: %s", self.config.server_url)

    # ----- low-level transport ------------------------------------------------

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _post(self, payload: dict) -> dict:
        """Send a JSON-RPC 2.0 request to the MCP server."""
        body = json.dumps(payload).encode("utf-8")
        url = f"{self.config.server_url}/rpc"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Attach auth tokens when available
        if self.config.gitlab_token:
            headers["X-GitLab-Token"] = self.config.gitlab_token
        if self.config.jira_token:
            headers["X-Jira-Token"] = self.config.jira_token
        if self.config.jira_email:
            headers["X-Jira-Email"] = self.config.jira_email

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise MCPClientError(
                f"HTTP {exc.code} from MCP server: {exc.read().decode('utf-8', errors='replace')}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MCPClientError(
                f"Cannot reach MCP server at {url}: {exc.reason}"
            ) from exc

    # ----- public API ---------------------------------------------------------

    def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> MCPToolResult:
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
        # Content may be large — show first 200 chars
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
    for t in tools[:10]:  # show first 10
        print(f"   • {t.get('name', '?'):40s} — {t.get('description', '')[:60]}")
    if len(tools) > 10:
        print(f"   … and {len(tools) - 10} more")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run all sample MCP tool calls."""

    print("=" * 60)
    print("  Otomate — MCP Connector Sample")
    print("=" * 60)

    config = MCPConfig()

    # Quick pre-flight check
    if not config.server_url:
        print("ERROR: MCP_SERVER_URL is not set.", file=sys.stderr)
        sys.exit(1)

    client = MCPClient(config)

    # 1. Discover available tools
    sample_list_tools(client)

    # 2. Jira — single issue fetch
    sample_get_jira_issue(client)

    # 3. Jira — JQL search
    sample_search_jira_issues(client)

    # 4. GitLab — read file content
    sample_get_gitlab_file(client)

    # 5. SonarQube — quality issues
    sample_get_sonarqube_issues(client)

    print("\n" + "=" * 60)
    print("  All sample calls complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
