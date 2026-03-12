# Workflow: Create Release Build

**Trigger:** "Create release build", "Release v{version}", "Ship MR !{id}"

## What It Does

Validates that an MR is ready for release (approved, pipeline passed, quality gate OK, Jira ready), creates a release ticket, and guides the developer through merge and tagging.

## How to Use

1. Say: **"Create release build for v1.2.0"**
2. Otomate validates: MR approved, pipeline passed, quality gate, Jira status
3. Shows release summary with all checks
4. Approve → release ticket created
5. Manual steps: merge MR in GitLab UI, create git tag

## HITL Gates

1. Approve release after reviewing all checks

## Pre-Release Checks

- MR has approvals
- Pipeline passed
- SonarQube quality gate passed
- Linked Jira issues in correct status
- No unresolved MR discussions

## MCP Tools Used

`review_merge_request`, `list_project_merge_requests`, `get_sonar_quality_gate_status`, `get_jira_issue_detail`, `update_jira_issue`, `create_release_from_history`

## Limitations

Otomate **cannot** auto-merge MRs, create git tags, or trigger deployments. These are guided as manual steps.

## Duration

~10-15 minutes

## Next Steps

"Create release note for v1.2.0" → document the release.
