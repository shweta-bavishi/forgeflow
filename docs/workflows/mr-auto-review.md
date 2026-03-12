# Workflow 09 — MR Auto-Review

> Performs a comprehensive, multi-dimensional automated review of a Merge Request before human reviewers look at it. Catches issues early, saves reviewer time, and reduces review cycles.

---

## When to Use

- You've finished implementing a feature and want to self-check before requesting review.
- You want to catch standards violations, missing tests, or quality issues before a human reviewer points them out.
- Your team wants a consistent review checklist applied to every MR.

## Prerequisites

| Requirement | Details |
|---|---|
| Open MR | An open merge request in GitLab |
| Config loaded | `forgeflow.config.yml` with `coding_standards`, `architecture`, and `auto_review` sections |
| SonarQube (optional) | For quality gate and coverage checks |
| Jira (optional) | For acceptance criteria alignment checks |

## How to Trigger

```
@forgeflow review my MR
```

Or with a specific MR ID:

```
@forgeflow auto-review MR !142
```

Or to check readiness:

```
@forgeflow is my MR ready for review?
```

## What Happens

### 6 Review Dimensions

The auto-review evaluates your MR across six dimensions:

| Dimension | What It Checks | Severity |
|---|---|---|
| **Standards Compliance** | Naming conventions, forbidden patterns (console.log, TODO), import ordering | 🟡 WARNING |
| **Architecture Compliance** | Layer violations, dependency direction, module structure | 🔴 BLOCKER |
| **Test Coverage** | Missing test files for new code, coverage threshold, uncovered paths | 🔴 BLOCKER |
| **Quality Gate** | SonarQube gate status, new issues, technical debt | 🔴 BLOCKER |
| **Jira Alignment** | MR references Jira, changes match acceptance criteria, scope creep | 🟡 WARNING |
| **Code Quality** | Logic errors, missing error handling, security issues, performance | 🔴/🟡 varies |

### Verdict

- **✅ READY FOR REVIEW** — All dimensions pass
- **⚠️ NEEDS ATTENTION** — Warnings found, no blockers
- **🚫 NOT READY** — Blockers found, must fix before merging

### HITL Gate

Before the review is posted as an MR comment, you see the full report and choose:

1. **Post it** — Adds the review as a comment on the MR
2. **Edit first** — Modify findings (remove false positives, adjust severity)
3. **Fix and re-review** — Address issues first, then run again
4. **Don't post** — Keep the review for personal reference only

### Follow-Up Actions

Based on findings, the workflow offers:

- Fix sonar issues → triggers Workflow 06
- Generate missing tests → Code Agent creates stubs
- Update MR description with Jira link
- Diagnose pipeline failure → triggers Workflow 05

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `review_merge_request` | Fetch comprehensive MR data (diff, metadata) |
| `review_and_comment_mr` | Post review as MR comment |
| `post_mr_review_comment` | Post review comment separately |
| `get_file_content` | Read files for deeper analysis |
| `get_project_pipelines` | Check pipeline status |
| `search_in_repository` | Check consistency with existing code |
| `get_sonar_quality_gate_status` | Quality gate check |
| `get_sonar_project_issues` | New issues introduced |
| `get_sonar_project_measures` | Coverage metrics |
| `get_project_uncovered_lines` | Untested code in changed files |
| `get_jira_issue_detail` | Acceptance criteria for alignment check |

## Example Review Output

```
🔍 ForgeFlow Auto-Review: MR !142

Add user avatar upload endpoint
Branch: feature/PROJ-123-avatar → develop | Files: 5 | Lines: +245 -12
Linked Jira: PROJ-123 — User avatar upload

Verdict: ⚠️ NEEDS ATTENTION

📋 Standards Compliance 🟡
  - "console.log" found in avatar.service.ts:34

🏗️ Architecture Compliance 🟢
  - All files in correct layers

🧪 Test Coverage 🟡
  - Coverage 76% (threshold: 80%)
  - avatar.service.spec.ts exists but missing error case tests

🛡️ Quality Gate 🟢
  - Gate: PASS

📋 Jira Alignment 🟢
  - All 3 acceptance criteria addressed

💻 Code Quality 🟡
  - Missing try/catch around file upload in avatar.service.ts:45
  - Magic number "5242880" should be a named constant (MAX_FILE_SIZE)

🎯 Action Items:
  1. Remove console.log from avatar.service.ts:34
  2. Add error handling around file upload
  3. Extract file size limit to a constant
  4. Add error case tests to increase coverage
```

## Tips

- Run this **before** requesting human review — it catches the easy stuff so reviewers can focus on logic and design.
- If a dimension has no data (e.g., SonarQube not configured), it's skipped, not failed.
- The review is calibrated to be helpful, not pedantic. If you see too many false positives, check your `auto_review.forbidden_patterns` config.
- For large MRs (50+ files), consider splitting into smaller MRs first.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "No open MRs found" | Branch not pushed or MR not created | Push branch and create MR first |
| Review misses Jira alignment | Branch name doesn't follow naming convention | Use the pattern: `feature/PROJ-123-description` |
| False positives in standards check | Config `coding_standards` too strict or mismatched | Adjust `auto_review.forbidden_patterns` in config |
| Quality gate dimension skipped | SonarQube not configured or scan not run | Configure `sonarqube.project_key` and ensure scan runs in CI |
| Review is too large to post | MR is massive | Split into smaller MRs; the review will be more focused |
