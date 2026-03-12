# Workflow: Security Audit

**Trigger:** "Run security audit", "Check vulnerabilities", "Audit dependencies"

## What It Does

Performs a comprehensive security audit using Nexus IQ (dependency vulnerabilities) and SonarQube (security hotspots). Assesses reachability for each vulnerability, produces a prioritized remediation plan, and optionally creates fix MRs or Jira issues.

## How to Use

1. Say: **"Run security audit"**
2. Otomate discovers your Nexus IQ application and fetches scan data
3. Analyzes each vulnerability: CVEs, reachability, remediation strategy
4. Presents audit report with prioritized findings
5. Choose: create fix MR, create Jira issues, both, or report only

## HITL Gates

1. Review audit findings (can adjust severity, mark false positives)
2. Approve remediation actions before creation

## Remediation Options

| Option | What Happens |
|--------|-------------|
| Fix MR | Dependency version bumps committed as MR |
| Jira Issues | Per-finding issues with CVE details |
| Both | Safe upgrades → MR, complex ones → Jira |
| Report Only | No action taken |

## Overall Risk Levels

- 🔴 **CRITICAL** — Critical + reachable vulnerability found
- 🟡 **MODERATE** — High + reachable (no criticals)
- 🟢 **LOW** — Only medium/low or not reachable

## MCP Tools Used

`get_nexusiq_application`, `get_nexusiq_component_details`, `get_nexusiq_report_policy_violations`, `list_nexusiq_application_reports`, `get_sonar_project_issues`, `get_sonar_quality_gate_status`, `get_file_content`, `search_in_repository`, `commit_file_and_create_mr`, `create_jira_issue`, `link_issues`

## Graceful Degradation

If Nexus IQ is unavailable, Otomate automatically falls back to a SonarQube-only audit.

## Duration

~20-40 minutes (depends on vulnerability count)
