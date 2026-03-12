---
name: release-build
description: "Create a release build. Validates MR readiness, checks quality gates and Jira status, creates release ticket, and guides developer through merge and tagging."
---

# Skill: Create Release Build

Validate that an MR is ready for release, check all quality gates, create release ticket, and guide the developer through the merge process.

## Phase 1: IDENTIFY RELEASE TARGET

```
IF developer specifies MR:
  Call: review_merge_request(mr_id)

IF developer specifies version:
  Call: list_project_merge_requests(state="merged", target_branch=config.gitlab.default_branch)
  → Find MR(s) for this version

IF ambiguous:
  Call: list_project_merge_requests(state="approved")
  → Show approved MRs ready for release
  → Ask developer to choose

Extract from MR:
  - Title, description, changed files
  - Pipeline status
  - Approval status
  - Linked Jira issues (from title/description)
  - Source and target branches
```

## Phase 2: PRE-RELEASE CHECKS

```
CHECK 1 — MR approved:
  review_merge_request → approvals count > 0
  IF not approved → "MR needs approval before release"

CHECK 2 — Pipeline passed:
  review_merge_request → pipeline status = "success"
  IF failed → "Pipeline is failing. Run fix-pipeline first?"

CHECK 3 — Quality gate:
  Call: get_sonar_quality_gate_status(config.sonarqube.project_key)
  IF failed → "Quality gate failing. Run sonar-fix first?"

CHECK 4 — Jira status:
  FOR each linked Jira issue:
    Call: get_jira_issue_detail(issue_key)
    Verify: status is "In Review" or "QA" (ready for release)
  IF issues still "In Progress" → "Jira issues not ready for release"

CHECK 5 — No open review threads:
  review_merge_request → unresolved discussions = 0
  IF unresolved → "MR has {N} unresolved discussions"
```

## Phase 3: PRESENT RELEASE SUMMARY

```
## Release Summary

**Version:** v{version}
**MR:** !{mr_id} — {title}
**Branch:** {source} → {target}

### Pre-Release Checks
  ✓ MR approved ({N} approvals)
  ✓ Pipeline passed (build #{build_id})
  ✓ Quality gate: PASSED
  ✓ Jira issues ready: {PROJ-101, PROJ-102}
  ✓ No unresolved discussions

### Changes Included
  Files: {N} changed (+{added} -{removed})
  Jira Issues: {list with titles}

### Release Actions
  1. Create release ticket via Release tools
  2. Merge MR (developer action — via GitLab UI)
  3. Create tag v{version} (developer action — via git CLI)
  4. Update Jira issues to "Done"
```

## Phase 4: 🚦 HITL GATE — Developer Approves Release

```
Developer reviews release summary

Can:
  - Approve: "Go ahead with the release"
  - Delay: "Not yet, need to fix {issue}"
  - Modify: "Change version to v{new_version}"
  - Cancel: "Cancel the release"
```

## Phase 5: CREATE RELEASE

```
PREFERRED — One-step:
  Call: create_release_from_history(
    project_id: config.gitlab.project_id,
    version: version,
    branch: source_branch
  )
  → Creates release ticket from commit history

ALTERNATIVE — Two-step:
  Step 1: create_new_release_ticket(project_id, version, details)
  Step 2: confirm_existing_release_ticket(ticket_id)

MANUAL STEPS (guide developer):
  1. "Merge MR !{id} via GitLab UI" (Otomate cannot auto-merge)
  2. "Create tag: git tag -a v{version} -m 'Release v{version}'"
  3. "Push tag: git push origin v{version}"
```

## Phase 6: UPDATE JIRA

```
FOR each linked Jira issue:
  Call: update_jira_issue(
    key: issue_key,
    transition: config.jira.statuses.done
  )

  Add comment: "Released in v{version}\nMR: !{mr_id}"
```

## Phase 7: SUMMARY

```
✓ Release ticket created
✓ Jira issues updated to "Done": {list}

⚠ MANUAL STEPS REMAINING:
  1. Merge MR !{id} via GitLab UI
  2. Create and push git tag v{version}

→ Next: "Create release note for v{version}?"
```

## Error Handling

```
Pre-release check fails → show which check failed, offer to fix
Release ticket creation fails → show error, offer manual steps
Jira update fails → release still valid, note Jira issue
MR not found → ask for correct MR ID or list available MRs
```

## Limitations

```
Otomate CANNOT:
  - Auto-merge MRs (use GitLab UI)
  - Create git tags (use git CLI)
  - Cherry-pick commits (use git CLI)
  - Trigger deployment pipelines (use Jenkins UI)

For these actions: guide the developer with specific commands/steps
```
