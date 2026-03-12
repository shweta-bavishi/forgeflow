# Workflow 10 — Security Audit

> Performs a comprehensive security and dependency audit using Nexus IQ scan data and SonarQube security hotspots. Produces a prioritized remediation plan and optionally creates fix MRs or Jira issues.

---

## When to Use

- Before a release, to verify no critical vulnerabilities ship to production.
- After a Nexus IQ scan reports policy violations.
- When you want to understand your project's dependency security posture.
- During regular security hygiene checks (monthly / quarterly).

## Prerequisites

| Requirement | Details |
|---|---|
| Nexus IQ (recommended) | Application registered and at least one scan completed |
| SonarQube (recommended) | Project scanned with security rules enabled |
| Config loaded | `nexusiq.application_name` and/or `sonarqube.project_key` |
| At least one data source | Either Nexus IQ or SonarQube must be available |

## How to Trigger

```
@forgeflow run security audit
```

Or more specific:

```
@forgeflow check vulnerabilities
@forgeflow audit dependencies
@forgeflow are we safe to release?
```

## What Happens

### Phase 1 — Application Discovery

The Security Agent locates the Nexus IQ application automatically:
1. Checks `nexusiq.application_name` in config
2. Auto-discovers via `get_sonar_project_and_nexus_iq_application_by_gitlab`
3. Searches `list_nexusiq_applications` by project name
4. Falls back to SonarQube-only audit if no Nexus IQ available

### Phase 2 — Data Collection

| Source | Data Collected |
|---|---|
| Nexus IQ | Latest scan report, all policy violations with threat levels |
| SonarQube | Security issues, hotspots, quality gate status |
| GitLab | Dependency files (package.json, pom.xml, etc.) |

### Phase 3 — Vulnerability Analysis

For each vulnerability:
- **Component details**: CVE IDs, CVSS scores, fixed versions
- **Current version**: Confirmed from your dependency file
- **Reachability**: Is the vulnerable component actually imported/used in your code?
- **Remediation strategy**: UPGRADE, REPLACE, MITIGATE, or ACCEPT

### Phase 4 — Audit Report

A structured report is presented with:
- Executive summary (overall risk level)
- Vulnerability table (component, current version, fixed version, severity, reachability)
- SonarQube hotspots (file, line, assessment)
- Prioritized remediation plan
- Metrics (total, by severity, reachable vs. not)

### Phase 5 — HITL Review

You review the findings and can:
- Adjust severity levels
- Mark false positives
- Change remediation strategies
- Select which items to act on

### Phase 6 — Remediation Actions

Four options:

| Option | What It Does |
|---|---|
| **A — Fix MR** | Creates an MR with dependency version bumps (patch/minor) |
| **B — Jira issues** | Creates Jira issues for each finding needing work |
| **C — Both** | MR for easy upgrades + Jira for complex ones |
| **D — Report only** | No action taken, just the report |

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_nexusiq_application` | Application metadata |
| `list_nexusiq_application_reports` | Find latest scan |
| `get_nexusiq_report_policy_violations` | All violations |
| `get_nexusiq_component_details` | CVE details per component |
| `search_nexusiq_components` | Component lookup |
| `get_sonar_project_issues` | Security issues and hotspots |
| `get_sonar_quality_gate_status` | Overall quality status |
| `get_file_content` | Read dependency files |
| `search_in_repository` | Reachability analysis |
| `commit_file_and_create_mr` | Create fix MR |
| `create_jira_issue` | Create remediation issues |
| `link_issues` | Link related security issues |

## Example Report Summary

```
🔒 Security Audit Report

Project: my-awesome-api
Scan Date: 2026-03-10
Overall Risk: 🟡 MODERATE

Executive Summary:
  Found 12 dependency vulnerabilities (2 Critical, 3 High, 5 Medium, 2 Low).
  2 critical vulnerabilities are reachable in code — fix immediately.
  3 SonarQube security hotspots reviewed (1 true positive, 2 false positives).

Remediation Plan:
  Priority 1: Upgrade lodash 4.17.15 → 4.17.21 (fixes CVE-2021-23337, reachable)
  Priority 2: Upgrade express 4.17.1 → 4.18.2 (fixes CVE-2022-24999, reachable)
  Priority 3: 3 HIGH issues planned for next sprint
  Accepted: 2 LOW issues (not reachable)

Actions available:
  A) Create fix MR for lodash + express upgrades
  B) Create Jira issues for all findings
  C) Both
  D) Report only
```

## Tips

- **Reachability matters**: A CRITICAL vulnerability that's not reachable is lower priority than a HIGH one that is.
- **Group by component**: One upgrade often fixes multiple CVEs — the audit groups these for you.
- **Major version bumps**: Flagged as breaking change risk. Plan these carefully rather than auto-upgrading.
- **Run regularly**: Monthly audits catch new CVEs before they become urgent at release time.
- **Partial data is fine**: If Nexus IQ is unavailable, SonarQube-only audit is still valuable.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "Nexus IQ application not found" | Application name mismatch or not registered | Check `nexusiq.application_name` in config; register the app in Nexus IQ |
| "No scan reports" | No Nexus IQ scan has been run | Trigger a scan in your CI pipeline or Nexus IQ UI |
| Reachability shows "MAYBE" for everything | Transitive dependencies can't be traced by import search | Manual review needed; focus on directly imported components |
| Fix MR breaks the build | Major version upgrade introduced breaking changes | Use Option C (MR for safe upgrades + Jira for complex ones) |
| Auth failure | Nexus IQ or SonarQube token invalid | Check credentials; see docs/mcp-setup.md |
