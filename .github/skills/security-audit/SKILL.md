---
name: security-audit
description: "Run comprehensive security and dependency audit using Nexus IQ and SonarQube. Analyzes vulnerabilities with reachability assessment, creates prioritized remediation plan, and optionally creates fix MRs or Jira issues."
---

# Skill: Security Audit

Perform a comprehensive security audit using Nexus IQ and SonarQube, assess vulnerability reachability, and produce an actionable remediation plan.

## Phase 1: IDENTIFY APPLICATION

```
STEP 1 — Config lookup:
  IF config.nexusiq.application_name set:
    Call: get_nexusiq_application(application_name)
    Found → Phase 2

STEP 2 — Auto-discover:
  Call: get_sonar_project_and_nexus_iq_application_by_gitlab(config.gitlab.project_id)
  Found → Phase 2

STEP 3 — Search:
  Call: list_nexusiq_applications()
  Match against config.project.name
  One match → confirm with developer
  Multiple → present list, ask to choose

FALLBACK — No Nexus IQ:
  "Nexus IQ not found. Proceeding with SonarQube-only audit."
```

## Phase 2: FETCH SCAN DATA

### Nexus IQ Data

```
Call: list_nexusiq_application_reports(application_id)
  → Pick MOST RECENT report by date
  → No reports: "Trigger a scan first." Offer SonarQube-only.

Call: get_nexusiq_report_policy_violations(report_id)
  → All violations: component, policy type, threat level
```

### SonarQube Security Data

```
Call: get_sonar_project_issues(project_key, types="VULNERABILITY,SECURITY_HOTSPOT")
Call: get_sonar_quality_gate_status(project_key)
```

### Dependency File

```
Based on config.project.language:
  Node.js → get_file_content("package.json")
  Java    → get_file_content("pom.xml")
  Python  → get_file_content("requirements.txt")
  Go      → get_file_content("go.mod")
  .NET    → search_in_repository("*.csproj")
```

## Phase 3: ANALYZE VULNERABILITIES

```
FOR EACH Nexus IQ policy violation:

  STEP 1 — Component details:
    Call: get_nexusiq_component_details(component_id)
    Extract: CVEs, CVSS scores, fixed versions, affected ranges

  STEP 2 — Confirm version in project:
    Cross-ref with dependency file
    NOT in affected range → false positive, skip

  STEP 3 — Assess reachability:
    Call: search_in_repository("import.*{component}" or "require('{component}')")
    Directly imported → ✅ REACHABLE (HIGH priority)
    Not imported (transitive) → ❓ MAYBE (MEDIUM)
    Imported but vulnerable function unused → ❌ UNLIKELY (LOWER)

  STEP 4 — Remediation strategy:
    Fixed version, same major → UPGRADE (safe)
    Fixed version, different major → UPGRADE (⚠️ breaking)
    No fix, alternative exists → REPLACE
    No fix, no alternative → MITIGATE or ACCEPT

  STEP 5 — Group by component:
    Multiple CVEs → one upgrade action
```

### SonarQube Security Hotspots

```
FOR EACH hotspot:
  Call: get_file_content(file_path)
  Read flagged line + context

  True positive → add to remediation plan
  False positive → note, suggest marking "Safe" in SonarQube
  Uncertain → flag as ℹ️ INFO for developer review
```

## Phase 4: GENERATE AUDIT REPORT

```
## 🔒 Security Audit Report

**Project:** {name}
**Scan Date:** {date}
**Overall Risk:** {🔴 CRITICAL | 🟡 MODERATE | 🟢 LOW}

### Executive Summary
{2-3 sentences: total vulns, critical count, action needed}

### Dependency Vulnerabilities (Nexus IQ)
| # | Component | Current | Fixed | Severity | CVEs | Reachable | Action |
|---|-----------|---------|-------|----------|------|-----------|--------|

### Security Hotspots (SonarQube)
| # | File | Line | Issue | Severity | Assessment |
|---|------|------|-------|----------|------------|

### Remediation Plan (Prioritized)
Priority 1 — CRITICAL: {details}
Priority 2 — HIGH: {details}
Priority 3 — MEDIUM: {details}
Priority 4 — ACCEPT: {rationale}

### Metrics
Total: {N} | Critical: {N} | High: {N} | Medium: {N} | Low: {N}
Reachable: {N} | Not reachable: {N} | Auto-fixable: {N} | Manual: {N}
```

### Overall Risk

```
ANY critical + reachable → 🔴 CRITICAL
ANY high + reachable (no critical) → 🟡 MODERATE
Only medium/low or not reachable → 🟢 LOW
```

## Phase 5: 🚦 HITL GATE — Review Findings

```
Developer reviews audit report
Can: adjust severity, mark false positives, change strategy
```

## Phase 6: OFFER REMEDIATION

```
OPTION A — Fix MR: version bumps → commit_file_and_create_mr
OPTION B — Jira Issues: per-finding issues → create_jira_issue + link_issues
OPTION C — Both: safe upgrades → MR, complex → Jira
OPTION D — Report only: no action
```

## Phase 7: 🚦 HITL GATE — Approve Actions

```
Show: "Create MR with {N} upgrades + {M} Jira issues. Proceed?"
```

## Phase 8: EXECUTE

```
Fix MR:
  Call: get_file_content(dep_file) → update versions → commit_file_and_create_mr
  Branch: security/dependency-updates-{date}

Jira Issues:
  Call: get_jira_project_info → create_jira_issue per finding → link_issues
  Priority mapped from severity, labels: ["security", "otomate-generated"]
```

## Phase 9: SUMMARY

```
✓ MR created: !{id} — {N} dependency upgrades
✓ Jira issues: {list}
→ Remaining: {ACCEPT/MITIGATE items}
→ Next: merge MR, re-scan, address Jira items in sprint
```

## Error Handling

```
Nexus IQ unavailable → SonarQube-only (still valuable)
No reports → inform, offer SonarQube-only
Auth failure → point to docs, do NOT retry
Dep file not found → try alternatives, skip reachability
Partial failures → continue with available data, report skipped items
```
