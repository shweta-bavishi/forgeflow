# Security Agent — Design Reference

> The Security Agent specializes in dependency vulnerability analysis, policy compliance, and security remediation using Nexus IQ and SonarQube.

---

## Overview

| Property | Value |
|---|---|
| **File** | `agents/security-agent.md` |
| **Model Hint** | CAPABLE |
| **Used In** | Workflow 10 — Security Audit |
| **Primary Tools** | Nexus IQ (7 tools), SonarQube (security-filtered), GitLab (file reading, search) |

## What It Does

The Security Agent thinks like an application security engineer:

1. **Discovers** the Nexus IQ application for the project (auto-discovery or config)
2. **Fetches** the latest scan report and all policy violations
3. **Analyzes** each vulnerability: CVE details, fixed versions, CVSS scores
4. **Assesses reachability**: Is the vulnerable component actually used in the codebase?
5. **Determines remediation**: UPGRADE, PATCH, REPLACE, MITIGATE, or ACCEPT
6. **Groups by component**: One upgrade action resolves multiple CVEs
7. **Flags breaking changes**: Major version bumps are highlighted as risky

## Key Knowledge Areas

### Severity Classification

- **CRITICAL**: KEV-listed, RCE, auth bypass, SQL injection in deps
- **HIGH**: Unauthenticated access, privilege escalation, data exposure
- **MEDIUM**: DoS potential, information disclosure, XSS in deps
- **LOW**: Theoretical, requires unlikely conditions, already mitigated

### Remediation Strategies

- **UPGRADE** (~70%): Newer version fixes the CVE
- **REPLACE** (~10%): Library is abandoned, switch to alternative
- **MITIGATE** (~10%): Add compensating controls (WAF, validation)
- **PATCH** (~5%): Manual workaround when no version fix exists
- **ACCEPT** (~5%): Risk is negligible or unreachable

### Dependency Ecosystem Knowledge

The agent knows where dependency files live for each ecosystem:
- Node.js: `package.json`, `package-lock.json`
- Java: `pom.xml`, `build.gradle`
- Python: `requirements.txt`, `pyproject.toml`
- Go: `go.mod`
- .NET: `*.csproj`

## MCP Tools

| Tool | Role in This Agent |
|---|---|
| `get_nexusiq_application` | Application discovery |
| `get_nexusiq_component_details` | Per-component CVE analysis |
| `get_nexusiq_report_policy_violations` | Primary data source |
| `search_nexusiq_components` | Component lookup |
| `list_nexusiq_application_reports` | Find latest scan |
| `list_nexusiq_applications` | Application search |
| `list_nexusiq_organizations` | Org discovery |
| `get_sonar_project_issues` | Security hotspots |
| `get_sonar_quality_gate_status` | Quality context |
| `get_file_content` | Read dependency files |
| `search_in_repository` | Reachability analysis |
| `get_sonar_project_and_nexus_iq_application_by_gitlab` | Auto-discover app |

## Design Principles

- **Reachability over severity**: A reachable HIGH is more urgent than an unreachable CRITICAL
- **Practical over theoretical**: Recommendations must be actionable
- **Grouped remediation**: One action per component, not per CVE
- **Graceful degradation**: Works with SonarQube-only if Nexus IQ is unavailable
- **Breaking change awareness**: Major version bumps flagged, not silently recommended

## Error Handling

| Error | Behavior |
|---|---|
| Nexus IQ unavailable | Falls back to SonarQube-only audit |
| No scan reports | Informs developer; suggests triggering a scan |
| Auth failure | Points to docs/mcp-setup.md |
| Too many search results | Samples 20; notes partial reachability analysis |
| Dependency file not found | Tries alternatives; skips reachability if not found |
