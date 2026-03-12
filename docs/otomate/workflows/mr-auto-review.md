# Workflow: MR Auto-Review

**Trigger:** "Review my MR", "Auto-review MR !{id}", "Is my MR ready for review?"

## What It Does

Performs a structured 6-dimension review of a merge request: standards compliance, architecture compliance, test coverage, quality gate, Jira alignment, and code quality. Produces a severity-rated report and optionally posts it as an MR comment.

## How to Use

1. Say: **"Review my MR"** or **"Auto-review MR !456"**
2. Otomate fetches MR data (diff, commits, pipeline, Jira link)
3. Runs 6-dimension analysis
4. Presents review report with verdict
5. Choose: post to MR, edit findings, fix issues, or keep for reference

## Review Dimensions

| Dimension | What It Checks |
|-----------|---------------|
| Standards Compliance | Naming, forbidden patterns, JSDoc, formatting |
| Architecture Compliance | Layer placement, dependency direction |
| Test Coverage | Test file existence, coverage threshold |
| Quality Gate | SonarQube status, new issues |
| Jira Alignment | Jira reference, scope, acceptance criteria |
| Code Quality | Logic errors, security, performance, dead code |

## Severity Levels

- 🔴 **BLOCKER** — Must fix before merge
- 🟡 **WARNING** — Should fix
- 🟢 **OK** — No issues
- ℹ️ **INFO** — Suggestion

## Verdicts

- 🚫 **NOT READY** — Has blockers
- ⚠️ **NEEDS ATTENTION** — Warnings only
- ✅ **READY FOR REVIEW** — All OK

## HITL Gates

1. Review report before posting to MR

## MCP Tools Used

`review_merge_request`, `review_and_comment_mr`, `post_mr_review_comment`, `get_sonar_quality_gate_status`, `get_sonar_project_issues`, `get_project_uncovered_lines`, `get_jira_issue_detail`, `get_file_content`

## Duration

~10-20 minutes
