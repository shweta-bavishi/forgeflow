# Workflow 10: Security Audit

**Goal**: Perform a comprehensive security and dependency audit using Nexus IQ scan data, SonarQube security hotspots, and code analysis. Produce a prioritized remediation plan and optionally create Jira issues and/or fix MRs.

**Trigger**: "Run security audit", "Check security vulnerabilities", "Audit dependencies", "What vulnerabilities do we have?", "Check Nexus IQ report"

**Agents**: Orchestrator → Security Agent, SonarQube Agent, Code Agent, Jira Agent, GitLab Agent, Project Context Agent

**Time**: ~20-40 minutes (analysis depth depends on number of findings)

## Phase 1: IDENTIFY APPLICATION

### Discover Nexus IQ Application

```
STEP 1 — Check config:
  IF config.nexusiq.application_name is set:
    → Call: get_nexusiq_application(application_name)
    → If found → proceed to Phase 2
    → If not found → STEP 2

STEP 2 — Auto-discover from GitLab:
  Call: get_sonar_project_and_nexus_iq_application_by_gitlab(gitlab_project_id)
  → If found → proceed to Phase 2
  → If not found → STEP 3

STEP 3 — Search by project name:
  Call: list_nexusiq_applications()
  → Match against config.project.name (fuzzy)
  → IF one match → confirm with developer: "Found '{app_name}'. Is this correct?"
  → IF multiple matches → present list, ask developer to choose
  → IF no match → ask: "What is your Nexus IQ application name?"

FALLBACK — No Nexus IQ at all:
  → Inform: "Nexus IQ application not found. Proceeding with SonarQube-only audit."
  → Skip to Phase 2 (SonarQube section only)
```

## Phase 2: FETCH SCAN DATA

### Nexus IQ Data

```
Call: list_nexusiq_application_reports(application_id)
  → Pick MOST RECENT report (by date)
  → If no reports: "No scan reports found. Trigger a Nexus IQ scan first."
    → Offer to continue with SonarQube data only

Call: get_nexusiq_report_policy_violations(report_id)
  → Extract: All policy violations with:
    - Component name and version
    - Policy type (security, license, quality)
    - Threat level (1-10)
    - Constraint violations
```

### SonarQube Security Data

```
Call: get_sonar_project_issues(project_key, types="VULNERABILITY,SECURITY_HOTSPOT")
  → Filter: Only security-related issues
  → Extract: rule, severity, file, line, message, status

Call: get_sonar_quality_gate_status(project_key)
  → Extract: Overall quality status (for context)
```

### Dependency File

```
Based on config.project.language, read the primary dependency file:

  Node.js → get_file_content("package.json")
  Java    → get_file_content("pom.xml")
  Python  → get_file_content("requirements.txt")
  Go      → get_file_content("go.mod")
  .NET    → get_file_content("*.csproj")  (search_in_repository first)

Extract: Current dependency versions for cross-referencing
```

## Phase 3: ANALYZE VULNERABILITIES

### Per Component Analysis

```
FOR EACH policy violation from Nexus IQ:

  STEP 1 — Get component details:
    Call: get_nexusiq_component_details(component_identifier)
    Extract:
      - Component name, group, current version
      - CVE identifiers (CVE-YYYY-NNNNN)
      - CVSS score and vector
      - Fixed version (if available)
      - Affected version range

  STEP 2 — Confirm current version in project:
    → Cross-reference with dependency file from Phase 2
    → Verify: is the version in our project actually in the affected range?
    → If NOT in range → false positive, note and skip

  STEP 3 — Assess reachability:
    Call: search_in_repository(import_pattern_for_component)
      → Search for import/require statements
      → Examples: "import.*{component}", "require('{component}')", "from '{component}'"

    IF component is directly imported in code:
      → Reachable = ✅ YES — HIGH priority
    IF component is NOT imported (transitive dependency):
      → Reachable = ❓ MAYBE — MEDIUM priority
    IF component is imported BUT vulnerable function not used:
      → Reachable = ❌ UNLIKELY — LOWER priority

  STEP 4 — Determine remediation:
    IF fixed version available AND same major:
      → Strategy = UPGRADE (safe patch/minor bump)
    IF fixed version available AND different major:
      → Strategy = UPGRADE (⚠️ breaking change risk)
    IF no fixed version AND alternative exists:
      → Strategy = REPLACE
    IF no fixed version AND no alternative:
      → Strategy = MITIGATE or ACCEPT

  STEP 5 — Group by component:
    IF same component has multiple CVEs:
      → Group: "Upgrading {component} {current} → {fixed} resolves {N} CVEs"
      → Show all CVEs but recommend one action
```

### SonarQube Security Hotspot Analysis

```
FOR EACH security hotspot from SonarQube:

  STEP 1 — Read affected code:
    Call: get_file_content(file_path)
    → Read the flagged line and surrounding context

  STEP 2 — Assess:
    IF true positive (real security issue):
      → Add to remediation plan
      → Recommend specific code fix
    IF false positive (safe in this context):
      → Note as false positive
      → Suggest marking as "Safe" in SonarQube UI
    IF uncertain:
      → Flag for developer review
      → Mark as ℹ️ INFO, not 🔴 BLOCKER
```

## Phase 4: GENERATE AUDIT REPORT

```
## 🔒 Security Audit Report

**Project:** {config.project.name}
**Scan Date:** {date of latest Nexus IQ report}
**Overall Risk:** 🔴 CRITICAL / 🟡 MODERATE / 🟢 LOW

---

### Executive Summary
{2-3 sentences: total vulnerabilities, critical count, recommended action}

### Dependency Vulnerabilities (Nexus IQ)

| # | Component | Current | Fixed | Severity | CVEs | Reachable? | Action |
|---|-----------|---------|-------|----------|------|------------|--------|
| 1 | lodash    | 4.17.15 | 4.17.21 | 🔴 CRITICAL | CVE-2021-23337 | ✅ Yes | UPGRADE |
| 2 | express   | 4.17.1  | 4.18.2  | 🟡 HIGH     | CVE-2022-24999 | ✅ Yes | UPGRADE |
| 3 | moment    | 2.29.1  | -       | 🟡 MEDIUM   | CVE-2022-31129 | ❌ No  | ACCEPT  |

### Security Hotspots (SonarQube)

| # | File | Line | Issue | Severity | Assessment |
|---|------|------|-------|----------|------------|
| 1 | auth.ts | 45 | Hardcoded credential | 🔴 HIGH | True positive |
| 2 | api.ts  | 123 | SQL query construction | 🟡 MEDIUM | False positive (parameterized) |

### Remediation Plan (Prioritized)

**Priority 1 — CRITICAL (fix immediately):**
1. Upgrade {component} {current} → {fixed}
   - Impact: {breaking change assessment}
   - Files affected: {dependency file}
   - Fixes: {CVE list}

**Priority 2 — HIGH (fix this sprint):**
2. {details}

**Priority 3 — MEDIUM (plan for next sprint):**
3. {details}

**Priority 4 — LOW / ACCEPT:**
4. {details with rationale}

### Metrics
- Total vulnerabilities: {N}
- Critical: {N} | High: {N} | Medium: {N} | Low: {N}
- Reachable: {N} | Not reachable: {N}
- Auto-fixable (version bump): {N}
- Needs manual intervention: {N}
```

### Overall Risk Determination

```
IF any CRITICAL + reachable vulnerability:
  → Overall Risk = 🔴 CRITICAL

IF any HIGH + reachable vulnerability (no criticals):
  → Overall Risk = 🟡 MODERATE

IF only MEDIUM/LOW or no reachable vulnerabilities:
  → Overall Risk = 🟢 LOW
```

## Phase 5: 🚦 HITL GATE — Review Audit Findings

```
Show developer the full audit report.

Developer can:
  - Adjust severity assessments ("moment is LOW, not MEDIUM for us")
  - Mark false positives ("that SonarQube hotspot is safe")
  - Change remediation strategy ("don't upgrade express, mitigate instead")
  - Select which items to act on

ASK: "Review the findings above. Would you like to adjust any severity or strategy?"

WAIT for developer confirmation before proceeding to actions.
```

## Phase 6: OFFER REMEDIATION ACTIONS

```
Based on approved findings, present options:

OPTION A — "Create fix MR for dependency upgrades"
  → Read current dependency file via get_file_content
  → Update version numbers for approved upgrades (simple version bumps only)
  → Use commit_file_and_create_mr to commit + create MR
  → MR description includes: CVE details, before/after versions, risk assessment
  → Branch: security/dependency-updates-{date}

OPTION B — "Create Jira issues for remediation"
  → For each finding needing work:
    → create_jira_issue with:
      - Summary: "Security: {CVE/issue} in {component}"
      - Description: Full vulnerability details, impact, fix steps
      - Priority: Mapped from severity (Critical → Highest, High → High, etc.)
      - Labels: ["security", "otomate-generated"]
  → Link related issues via link_issues

OPTION C — "Both — fix MR for easy upgrades + Jira for complex ones"
  → Simple version bumps (patch/minor) → MR
  → Major version upgrades → Jira for planning
  → Replacements or mitigations → Jira for planning

OPTION D — "Just the report (no action)"
  → Save report for reference
  → No MR or Jira created
```

## Phase 7: 🚦 HITL GATE — Approve Actions

```
IF developer chose Option A, B, or C:

  Show summary of what will be created:
    "Ready to:
     - Create MR with {N} dependency upgrades
     - Create {M} Jira issues for complex remediation
     Proceed?"

  WAIT for explicit approval

  IF approved → execute
  IF not approved → ask what to change
```

## Phase 8: EXECUTE ACTIONS

### Create Fix MR (if Option A or C)

```
STEP 1 — Read dependency file:
  Call: get_file_content(dependency_file_path)

STEP 2 — Modify versions:
  Update only approved version bumps
  Keep all other dependencies unchanged

STEP 3 — Commit and create MR:
  Call: commit_file_and_create_mr(
    files: [updated_dependency_file],
    branch: "security/dependency-updates-{date}",
    title: "fix(security): Upgrade {N} vulnerable dependencies",
    description: [audit report summary with CVE details]
  )

STEP 4 — Verify:
  → Confirm MR created
  → Show MR link to developer
```

### Create Jira Issues (if Option B or C)

```
STEP 1 — Prerequisite:
  Call: get_jira_project_info(project_key)

FOR EACH approved finding needing Jira:
  STEP 2 — Create issue:
    Call: create_jira_issue(
      project_key: config.jira.project_key,
      issue_type: config.jira.task_issue_type,
      summary: "Security: {brief description}",
      description: "{full CVE details, impact, fix steps}",
      priority: {mapped from severity},
      labels: ["security", "otomate-generated"]
    )

  STEP 3 — Link related:
    IF multiple issues for related components:
      Call: link_issues(issue_1, issue_2, "Relates")

STEP 4 — Report:
  Show all created issues with links
```

## Phase 9: SUMMARY

```
## Security Audit Complete

**Findings:** {N} vulnerabilities analyzed
**Risk Level:** {overall risk}

**Actions Taken:**
  ✓ MR created: !{mr_id} — {N} dependency upgrades
  ✓ Jira issues created: {list of keys}

**Remaining (manual):**
  → {list of ACCEPT/MITIGATE items}

**Next Steps:**
  1. Review and merge the security fix MR
  2. Run CI/CD to verify no regressions
  3. Re-run Nexus IQ scan after merge to confirm fixes
  4. Address Jira items in upcoming sprints
  5. Schedule next audit in {recommended timeframe}
```

## Error Handling

```
Nexus IQ application not found:
  → Fall back to SonarQube-only audit
  → Partial audit is still valuable

No scan reports available:
  → Inform developer: "No scans found. Trigger a scan and re-run."
  → Offer to continue with SonarQube data only

Authentication failure (401/403):
  → Do NOT retry
  → Point to docs/mcp-setup.md

Dependency file not found:
  → Try alternative locations
  → Skip reachability analysis, note it

search_in_repository returns too many results:
  → Sample first 20 results
  → Note: "Reachability analysis used a sample"

Component details unavailable:
  → Use policy violation data directly (less detail)
  → Note: "Detailed component info unavailable"

Partial tool failures:
  → Continue with available data
  → Show what succeeded and what was skipped
  → "Audit completed with partial data — {tools} were unavailable"
```

## What NOT to Do

- ❌ Don't create MRs or Jira issues without explicit developer approval
- ❌ Don't classify all vulnerabilities as CRITICAL — assess reachability
- ❌ Don't recommend major version upgrades without flagging breaking change risk
- ❌ Don't ignore transitive dependencies — they can still be exploitable
- ❌ Don't skip SonarQube hotspots when Nexus IQ data is available
- ❌ Don't present raw CVE numbers without explaining impact
- ❌ Don't fail the entire audit because one tool is unavailable (graceful degradation)
- ❌ Don't auto-accept risk without checking reachability first

## Success Criteria

✓ All Nexus IQ policy violations analyzed with component details
✓ Reachability assessed for each vulnerability
✓ Multiple CVEs for same component grouped (one action, many fixes)
✓ SonarQube security hotspots included alongside Nexus IQ findings
✓ Remediation plan is prioritized and actionable
✓ Breaking change risks flagged for major version upgrades
✓ Developer reviews and approves all actions before execution
✓ Partial data produces partial (still useful) audit

---

**Duration**: 20-40 minutes (varies with vulnerability count)

**What It Creates**:
- Comprehensive security audit report
- Dependency upgrade MR (optional)
- Jira remediation issues (optional)

**Next Steps**:
- Merge security fix MR
- Address Jira items in sprint planning
- Re-scan after fixes to verify remediation
- Schedule periodic audits

**Related**: Security Agent, SonarQube Agent, Code Agent, GitLab Agent, Jira Agent
