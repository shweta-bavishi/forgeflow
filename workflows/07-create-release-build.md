# Workflow 07: Create Release Build

**Goal**: Validate MR readiness, merge to develop, cherry-pick to release branch, create version tag, and update Jiras.

**Trigger**: "Create release build for MR !{id}", "Ship v{version}", "Release {JIRA-KEY}"

**Agents**: Orchestrator → GitLab Agent, Jira Agent, Jenkins Agent, Project Context Agent

**Time**: ~20 minutes (validation + merge + tag + Jira update)

## Phase 1: VALIDATE MR READINESS

GitLab Agent validates all release prerequisites:

```
Call: review_merge_request(mr_iid)
Extract:
  - Files changed, additions/deletions
  - Commits in MR
  - Approvals (count vs required)
  - Pipeline status
  - Discussions (open/resolved)
  - Conflict status

Call: get_project_pipelines(branch)
Extract:
  - Latest pipeline status (PASS/FAIL)
```

### Check All Conditions

```
1. APPROVALS
   Required (from config): {N} approvals
   Current: {M} approvals
   Status: ✓ PASS or ✗ FAIL

2. PIPELINE
   Latest pipeline: {status}
   Status: ✓ PASS or ✗ FAIL

3. CONFLICTS
   Merge conflicts: {count}
   Status: ✓ No conflicts or ✗ Conflicts exist

4. DISCUSSIONS
   Open discussions: {count}
   Status: ✓ All resolved or ✗ Unresolved

5. CODE QUALITY (if available)
   SonarQube quality gate: {status}
   Status: ✓ PASS or ✗ FAIL
```

### If Any Check Fails

```
STOP workflow

Show all failures:
  ✗ Missing {N} approvals
  ✗ Pipeline is failing
  ✗ {N} merge conflicts
  ✗ {N} unresolved discussions

Action: Ask developer to resolve before release
  "Fix these issues first, then we can release"
```

## Phase 2: PRESENT RELEASE SUMMARY

Only show if ALL validations pass:

```
## Release Summary

**MR**: !{number} — {title}
**Source Branch**: feature/PROJ-123-...
**Target**: develop

### Changes
- Files changed: {N}
- Additions: +{lines}
- Deletions: -{lines}

### Linked Jiras
PROJ-123: Avatar Upload
PROJ-124: User Profile
PROJ-125: Avatar Display

### Status Checks
✓ Approvals: {count}/{required}
✓ Pipeline: PASSED
✓ No merge conflicts
✓ All discussions resolved
✓ Quality gate: PASSED (82% coverage)

This MR is READY FOR RELEASE
```

## Phase 3: 🚦 HITL GATE — Approve Merge to Develop

```
Ask developer:
  "Ready to merge to develop?"

Options:
  a) Merge with squash (default from config)
     → Combines all commits into single commit
  b) Merge commit (preserve all commits)
     → Keep individual commit history

Developer selects or accepts default
```

## Phase 4: MERGE TO DEVELOP

⚠️ **LIMITATION**: No direct merge tool available

```
GitLab Agent cannot automatically merge.

Instead:
  1. Show developer MR URL
  2. Guide developer to merge manually:

  "Ready to merge. Please:
   1. Go to: {mr_url}
   2. Click 'Merge' button
   3. Select merge type: {squash/merge commit}
   4. Click 'Merge MR'
   5. Wait for pipeline to complete"

After developer confirms merge:
  Proceed to Phase 5
```

### Alternative: Automated Merge (if desired)

If config allows CI/CD merge automation:
```
Use GitLab API to automatically merge
  (Requires appropriate permissions and configuration)
```

## Phase 5: 🚦 HITL GATE — Approve Cherry-Pick to Release

```
Developer confirms:
  "Ready to cherry-pick to release branch?"

Extract target release branch from config:
  release_branch_pattern: "release/v*"
  Example: "release/v2.4"

Show conflict risk:
  "Release branch may have other commits.
   If conflicts occur, you'll need to resolve manually."
```

## Phase 6: CHERRY-PICK TO RELEASE

⚠️ **LIMITATION**: No cherry-pick tool available

```
GitLab Agent cannot auto cherry-pick.

Instead:
  1. Get merge commit SHA from Phase 4
  2. Guide developer:

  "Cherry-pick the merge commit:
   git fetch origin
   git checkout release/v2.4
   git cherry-pick {merge_commit_sha}

   If conflicts:
     Resolve manually in IDE
     git add .
     git cherry-pick --continue
     git push origin release/v2.4"

Developer confirms cherry-pick complete:
  "Cherry-pick done"
  Proceed to Phase 7
```

## Phase 7: 🚦 HITL GATE — Approve Tag Creation

```
Ask developer for version number:
  "What version? (e.g., v2.4.1)"

Validate format:
  Must match: v{major}.{minor}.{patch}
  Example: v2.4.1 ✓, v2.4 ✗ (missing patch)

Extract changelog:
  From linked Jiras, generate changelog using templates/changelog.md

Show preview:
  ## Release v2.4.1 - March 11, 2026

  ### Features
  - PROJ-123: Avatar upload with compression
  - PROJ-124: User profile enhancements

  ### Bug Fixes
  - PROJ-200: Login page crash fix
  - PROJ-201: Invalid session handling

  ### Breaking Changes
  None

Ask: "Create tag with this changelog?"
```

## Phase 8: CREATE TAG

⚠️ **LIMITATION**: No tag creation tool available

```
GitLab Agent cannot create tags automatically.

Guide developer:
  "Create the release tag:
   git tag -a v2.4.1 -m 'Release v2.4.1

   ## Features
   - Avatar upload
   - User profiles

   ## Bug Fixes
   - Login crash
   - Session handling'

   git push origin v2.4.1"

Developer confirms: "Tag created"
Proceed to Phase 9
```

## Phase 9: UPDATE JIRAS

For each linked Jira issue:

```
Call: update_jira_issue(
  key: issue_key,
  fixVersion: version,  # v2.4.1
  transition: "done"    # from config.jira.statuses
)

Add comment:
  "Released in v2.4.1
   MR: !{mr_number}
   Link: {release_url}"

Result:
  ✓ PROJ-123 → Done (fixVersion: v2.4.1)
  ✓ PROJ-124 → Done (fixVersion: v2.4.1)
  ✓ PROJ-125 → Done (fixVersion: v2.4.1)
```

## Phase 10: SUMMARY

```
## Release Complete ✓

✓ Merged !{mr_number} → develop (squash)
✓ Cherry-picked → release/v2.4
✓ Tagged: v2.4.1
✓ Jiras updated (3 closed, fixVersion: v2.4.1)

### Linked Issues (Now Released)
- PROJ-123: Avatar Upload
- PROJ-124: User Profiles
- PROJ-125: Avatar Display

### Next Steps
1. Announce release to team
2. Run deployment if needed (separate workflow)
3. Monitor for issues in release
4. Start next sprint planning
```

## Error Handling

### If validation fails

```
Show all issues
Guide to remediation
Do NOT proceed to merge
```

### If merge fails

```
Developer guides through GitLab UI
Show specific error if available
Retry or manual intervention
```

### If conflicts during cherry-pick

```
Show: Conflicting files
Guide: "Resolve conflicts in IDE, complete cherry-pick manually"
Don't auto-resolve (too risky)
```

### If Jira update fails

```
Warning: "Jira update failed"
Still proceed with release (Jira is secondary)
Suggest: Update manually or retry later
```

## Manual Release Alternative

If developer prefers full manual control:

```
This workflow guides every step
But developer can do release entirely manually via:
  1. GitLab UI for merge and cherry-pick
  2. Git CLI for tag creation
  3. Jira UI for issue updates

Workflow provides guidance at each step
```

## Success Criteria

✓ All release prerequisites validated
✓ MR is merged to develop
✓ Changes are cherry-picked to release branch
✓ Version tag is created with changelog
✓ All linked Jiras are updated and closed
✓ Release summary is clear and accurate

---

**Duration**: 20 minutes (mostly developer manual actions)

**What It Creates**:
- Merge to develop
- Cherry-pick to release branch
- Git tag with changelog
- Jira issue updates

**Limitations**:
- GitLab merge: manual (developer in GitLab UI)
- Cherry-pick: manual (developer via git CLI)
- Tag creation: manual (developer via git CLI)

**Related**: GitLab Agent, Jira Agent

**Note**: Workflow provides clear guidance at each step, but some operations require developer hands-on due to tool limitations
