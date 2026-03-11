# Workflow 06: Sonar Fix

**Goal**: Analyze SonarQube report, categorize issues by fixability, generate fixes for selected issues, and create MR.

**Trigger**: "Fix sonar issues", "Help me pass quality gate", "Resolve sonar report"

**Agents**: Orchestrator → SonarQube Agent, GitLab Agent, Code Agent, Project Context Agent

**Time**: ~30 minutes (analysis + fix generation + MR)

## Phase 1: FETCH & ASSESS

### Get All Issues

```
Call: get_sonar_project_issues(project_key)
Extract:
  - All issues with severity, rule, file, line, message
  - Group by: severity, type (BUG, CODE_SMELL, VULNERABILITY)

Call: get_sonar_quality_gate_status(project_key)
Extract:
  - Status: PASS / FAIL
  - Which conditions failed?
  - Blocker issues count (these block the gate)

Call: get_sonar_project_measures(project_key)
Extract:
  - Test coverage %
  - Duplications %
  - Code smells count
```

### Assess Fixability

SonarQube Agent categorizes each issue:

```
AUTO-FIXABLE (Code Agent can generate fixes):
  - S1128: Unused imports → Delete
  - S2259: Null pointers → Add null check
  - S108: Empty catch → Add logging/throw
  - S1874: Deprecated API → Use new API
  Total: {N} auto-fixable

AGENT-ASSISTED (Requires reasoning, but doable):
  - S3776: Complexity → Refactor method
  - S1192: Duplicated strings → Extract constant
  - S1121: Unused variables → Delete
  Total: {N} agent-assisted

MANUAL (Requires developer decision):
  - S104: File too large → Split file (architecture decision)
  - Security hotspots → Code review needed
  - Test coverage gaps → Write tests
  Total: {N} manual
```

## Phase 2: PRESENT ANALYSIS

```
## SonarQube Analysis

Quality Gate: FAILED (3 blockers prevent pass)

| Severity | Total | Auto-fixable | Agent-assisted | Manual |
|----------|-------|--------------|----------------|--------|
| BLOCKER  | 3     | 2            | 1              | 0      |
| CRITICAL | 7     | 4            | 2              | 1      |
| MAJOR    | 12    | 8            | 3              | 1      |
| MINOR    | 23    | 15           | 5              | 3      |
| TOTAL    | 45    | 29           | 11             | 5      |

Issues by File:
  src/services/user.service.ts: 12 issues (S2259: 4, S1128: 3, S3776: 2, ...)
  src/controllers/auth.controller.ts: 8 issues
  src/repositories/payment.repository.ts: 7 issues

Quality Gate Impact:
  If you fix all 3 BLOCKERS: ✓ Gate will PASS
  If you also fix CRITICAL auto-fixable (4): Coverage improves to 82%

RECOMMENDATION PRIORITY:
  1. Fix 3 BLOCKERS (required for gate pass)
  2. Fix 4 CRITICAL auto-fixable (improves quality)
  3. Fix 8 MAJOR auto-fixable (if time permits)
  4. Skip 5 MANUAL (require developer decision)
```

## Phase 3: 🚦 HITL GATE — Issue Selection

Developer chooses which issues to fix:

```
Which issues should we address?

OPTIONS:
  a) All blockers + all auto-fixable issues (RECOMMENDED)
     → Ensures gate passes + improves coverage
  b) Just blockers + critical auto-fixable
     → Minimal to pass gate
  c) Only auto-fixable issues (safest)
     → No complex refactoring
  d) All auto-fixable + agent-assisted
     → More comprehensive
  e) Pick specific issues manually
     → Fine-grained control

Example:
  Developer: "Do a) - fix all blockers + auto-fixable"
  Agent: "That's 29 issues across 5 files. Proceed?"
```

## Phase 4: GENERATE FIXES

For each selected issue:

### Read Affected File

```
Call: get_file_content(file_path)
Extract:
  - Current code at error line
  - Surrounding context
```

### Generate Fix

```
Code Agent applies fix pattern for this issue type:

EXAMPLE: S2259 (Null pointer)
  Before:
    return user.profile.name;  // Might be null!

  After:
    return user?.profile?.name || 'Unknown';
           OR
    if (user && user.profile) {
      return user.profile.name;
    }
    return 'Unknown';

EXAMPLE: S1128 (Unused import)
  Before:
    import { unused } from './unused';
    import { used } from './used';

  After:
    import { used } from './used';

EXAMPLE: S3776 (Complexity)
  Before:
    if (a) { if (b) { if (c) { ... } } }  // Nested complexity

  After:
    if (!a) return;
    if (!b) return;
    if (!c) return;
    // Main logic here (early return pattern)
```

### Show Before/After

```
For each fix:
  Show: Before → After code
  Explain: Why this fixes the issue
  Reference: Link to sonar-project.properties quality gate

Example:
  File: src/services/user.service.ts
  Line: 45
  Issue: S2259 — Null pointers should not be dereferenced

  Before:
    const name = user.profile.name;

  After:
    const name = user?.profile?.name || 'Unknown';

  This fix: Safely accesses nested properties with optional chaining
```

## Phase 5: 🚦 HITL GATE — Review Fixes

Developer reviews each fix:

```
1. APPROVE individual fix
   "Good"

2. REQUEST changes for specific fix
   "Use if-statement instead of ternary"
   Agent: Updates that fix

3. SKIP individual fix
   "Skip this one, I'll handle it"

4. Proceed
   After reviewing all, developer approves
```

## Phase 6: CREATE BRANCH & COMMIT

```
GitLab Agent creates branch:
  Branch name: fix/sonar-{project}-{date}
  Example: fix/sonar-my-awesome-api-2026-03-11

Commit message:
  "fix: resolve {N} sonar quality issues

   - S2259 ({file}): {fix description}
   - S1128 ({file}): {fix description}
   - S3776 ({file}): {fix description}
   ...

   Quality Gate Impact:
   Before: {gate status before}
   After: {predicted gate status after}"
```

## Phase 7: 🚦 HITL GATE — Approve Push & MR

```
Show summary:
  Files modified: {N}
  Issues fixed: {N}
  Estimated quality gate impact: {PASS or improvements}

Confirmation: "Push and create MR?"
```

## Phase 8: PUSH, MR & VERIFY

```
Call: commit_file_and_create_mr(
  files: [all fixed files],
  branch_name: "fix/sonar-{project}-{date}",
  mr_description: [From template]
)

MR DESCRIPTION:
  ## Summary
  Fixed {N} SonarQube quality issues to improve code quality.

  ## Issues Fixed
  - S2259 in user.service.ts (3 instances): Null pointer dereference
  - S1128 in auth.controller.ts (2 instances): Unused imports
  - S3776 in payment.service.ts (1 instance): Cognitive complexity
  ...

  ## Quality Gate Impact
  Before: {gate status} ({N} blockers, {M}% coverage)
  After: {predicted status} ({X} blockers, {Y}% coverage)

  If all fixes apply correctly → Quality Gate will PASS ✓

  ## Verification
  - Run: npm run sonar (re-scan project)
  - Expected: Quality gate passes
  - Or: Merge and verify in SonarQube UI after scan completes
```

## Phase 9: SUGGEST FOLLOW-UP

```
After MR created:
  1. Code review (if team uses reviews)
  2. Merge to develop
  3. Jenkins pipeline will run SonarQube scan
  4. Check SonarQube UI to confirm quality gate passes
  5. If still failing, run workflow again for remaining issues

Next: "Want to fix the remaining {N} issues?
       Or are we done?"
```

## Error Handling

### If SonarQube project not found

```
→ Try: get_sonar_project_and_nexus_iq_application_by_gitlab
       to auto-discover from GitLab CI variables
→ If still not found: Ask developer for project key
```

### If fix generation fails

```
→ Show which fixes succeeded, which failed
→ Offer: Retry, skip, or manual fix
→ Don't force merge with incomplete fixes
```

### If authentication fails

```
→ Check: SONARQUBE_TOKEN environment variable
→ Guide: docs/mcp-setup.md for credential setup
```

## Special Cases

### If Already Passing Quality Gate

```
Message: "Quality gate is already passing!"
Option: Still fix minor issues?
  - Yes: Fix all auto-fixable issues for better quality
  - No: Quit workflow
```

### If No Auto-Fixable Issues

```
Message: "No auto-fixable issues found"
Option: Review agent-assisted issues?
  - Yes: Show manual issues requiring refactoring
  - No: Done
```

### If Issue Count Very High

```
If > 100 issues:
  Warning: "This will generate a large MR"
  Ask: "Fix all or just blockers+criticals?"
  Recommend: Smaller PRs are better
```

## Success Criteria

✓ Quality gate impact is clear before fixing
✓ Issues are categorized by fixability
✓ Only auto-fixable or approved issues are fixed
✓ Each fix is specific and tested
✓ Developer reviews before committing
✓ MR shows expected quality gate improvement
✓ Confidence in fix correctness is high

---

**Duration**: 30 minutes (analysis + generation + MR)

**What It Creates**:
- Branch with quality fixes
- Merge Request with detailed fix list
- Prediction of quality gate impact

**Next Steps**:
- Merge MR to develop
- Jenkins runs SonarQube scan
- Verify quality gate passes in SonarQube UI

**Related**: SonarQube Agent, Code Agent, GitLab Agent

**Note**: Some issues require developer decision (manual). Cannot auto-fix all issues.
