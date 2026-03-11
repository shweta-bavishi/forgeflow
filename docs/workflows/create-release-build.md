# Workflow 07 — Create Release Build

> Validates merge requests, guides the manual merge/cherry-pick/tag process (due to MCP tool limitations), and updates Jira tickets to reflect the release.

---

## When to Use

- You are preparing a release branch or tag.
- You need to validate which MRs are ready to merge.
- You want Jira tickets updated to "Released" or "Done" status automatically.

## Prerequisites

| Requirement | Details |
|---|---|
| MRs ready | One or more merge requests in "Approved" / "Ready to merge" state |
| Config loaded | `gitlab.project_id`, `jira.project_key`, release settings |
| Jira tickets | Linked to the MRs via branch naming or MR description |

## How to Trigger

```
@forgeflow create release build
```

Or for a specific version:

```
@forgeflow prepare release v2.4.0
```

## What Happens

### Phase 1 — MR Validation

The GitLab Agent checks all open MRs for the target branch:

- Pipeline status (must be green)
- Approval status (must meet minimum approvals)
- Merge conflicts (must be clean)
- SonarQube quality gate (if configured)

A report is generated:

```
Release Readiness — v2.4.0
══════════════════════════

Ready to merge (3):
  ✅ !142  feat/user-auth       Pipeline ✓  Approvals 2/2  No conflicts
  ✅ !145  fix/login-redirect   Pipeline ✓  Approvals 2/2  No conflicts
  ✅ !148  feat/dashboard       Pipeline ✓  Approvals 3/2  No conflicts

Not ready (1):
  ❌ !150  feat/notifications   Pipeline ✗  (test failure in notification.spec.ts)
```

### Phase 2 — ⏸️ HITL: Approve Merge List

You confirm which MRs to include in the release. MRs that are not ready can be excluded.

### Phase 3 — Guided Merge (Manual)

> **Important**: The MCP server does **not** have merge, cherry-pick, or tag tools.

The agent provides step-by-step CLI commands for you to execute:

```bash
# Merge approved MRs (run in your terminal)
git checkout release/v2.4.0
git merge --no-ff origin/feat/user-auth
git merge --no-ff origin/fix/login-redirect
git merge --no-ff origin/feat/dashboard

# Create release tag
git tag -a v2.4.0 -m "Release v2.4.0"
git push origin release/v2.4.0
git push origin v2.4.0
```

For cherry-pick workflows:

```bash
git checkout -b release/v2.4.0 origin/main
git cherry-pick <commit-sha-1>
git cherry-pick <commit-sha-2>
```

### Phase 4 — Release Ticket Creation

The agent uses `create_release_from_history` to generate a release record, gathering:

- All commits included in the release
- Linked Jira tickets
- Changelog entries

### Phase 5 — Jira Updates

For each Jira ticket included in the release:

- Transition to "Done" or "Released" status (`update_jira_issue`)
- Add comment: "Included in release v2.4.0" (`add_jira_comment`)
- Set fix version if the field is configured

### Phase 6 — Jenkins Trigger (Optional)

If configured, triggers the release pipeline: `trigger_jenkins_build`.

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_merge_request_details` | Validate MR status |
| `get_pipeline_status` | Check CI results |
| `create_release_from_history` | Generate release record |
| `update_jira_issue` | Transition tickets to Done/Released |
| `add_jira_comment` | Add release comments to tickets |
| `trigger_jenkins_build` | Start release pipeline |

## Critical Limitation

The ce-mcp server lacks:
- **Merge MR** tool — merge must be done manually or via GitLab UI
- **Cherry-pick** tool — cherry-picks must be done via CLI
- **Create tag** tool — tags must be created via CLI
- **Delete branch** tool — branch cleanup is manual

The workflow compensates by providing exact CLI commands and GitLab UI instructions.

## Tips

- Use consistent branch naming (e.g. `feat/PROJ-101-description`) so the agent can link MRs to Jira tickets automatically.
- Run Workflow 06 (sonar fix) before the release to ensure quality gate passes.
- For hotfix releases, the agent supports cherry-pick workflows — just specify the target branch.
- Keep the `jira.statuses` mapping in config accurate so transitions work correctly.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| MR shows as "not ready" but it's approved | Pipeline hasn't finished or is cached | Wait for pipeline; re-check |
| Jira transition fails | Status name mismatch | Update `jira.statuses` in config to match your Jira workflow |
| Release record missing commits | Commit messages don't reference ticket keys | Use conventional commits with ticket keys (e.g. `PROJ-101: Add feature`) |
| Tag already exists | Version number reused | Choose a new version number |
