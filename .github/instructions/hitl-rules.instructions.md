---
applyTo: "**"
---

# HITL (Human-in-the-Loop) Rules — Always-On

These rules govern when and how to request developer approval during workflow execution. They apply to ALL Otomate agents and skills.

## Approval Gate Protocol

### Actions That ALWAYS Require Approval

Before executing any of these actions, STOP and present a summary to the developer:

1. **Write or modify code** — Show: detailed implementation plan (todo list) with step-by-step changes, files to create/modify, and patterns to follow. **No code generation until the plan is approved.**
2. **Push code to remote** — Show: files changed, line counts, branch name, target branch
3. **Create merge request** — Show: MR title, description, source → target branch, files list
4. **Create release build** — Show: version, included changes, merge target
5. **Publish release notes** — Show: rendered content, target Confluence page
6. **Update Jira status to Done** — Show: issue key, current status → new status
7. **Post MR review comment** — Show: full review content, MR ID
8. **Create security fix MR** — Show: dependency changes, CVE list, breaking change assessment
9. **Create Zephyr test cases** — Show: test case list with names, count, linked issues
10. **Create Jira issues** — Show: issue summaries, types, priorities, count. Include implementation plan in each task description.

### Implementation Plan Gate (Mandatory Before Code Changes)

This is a **hard gate** — it applies to ALL workflows that modify code (04, 05, 06, and any future code-modifying workflows).

Before writing, generating, or modifying ANY code:

1. **Analyze** the current codebase state (even if a prior plan exists in Jira)
2. **Present** a detailed implementation plan as a todo list:
   - Each step: specific action, specific file(s), specific pattern to follow
   - Steps ordered by dependency
   - Each step small enough to verify independently
3. **Wait** for developer approval of the plan
4. **Follow** the approved plan step-by-step during implementation
5. **Pause** and re-consult if implementation reveals issues not in the plan

```
## Implementation Plan for {context}

### Todo List
- [ ] 1. {Action} — File: {path} ({CREATE/MODIFY})
- [ ] 2. {Action} — File: {path} ({CREATE/MODIFY})
- [ ] ...

Approve this plan before I start coding? (yes / no / modify)
```

### Approval Gate Format

When presenting an approval gate:

```
WHAT: {Clear description of the action}
WHY: {Why this action is needed}
IMPACT: {What changes, what gets created/modified}
DETAILS: {Specific data — files, line counts, Jira keys, etc.}

Should I proceed? (yes / no / modify)
```

### Developer Responses

- **"yes"** / **"proceed"** / **"go ahead"**: Execute the action, verify success, show results.
- **"no"** / **"stop"** / **"cancel"**: Stop the workflow. Offer alternatives. Do NOT retry the same action.
- **"modify"** / **"change"** / **"adjust"**: Ask what should change. Update the plan. Re-present the modified approval gate.

### Multi-Round Refinement

Support multiple iterations at any approval gate:
1. Developer says "modify" → ask what to change
2. Apply changes → re-present updated gate
3. Repeat until developer approves or cancels
4. Never limit the number of modification rounds

## Error Communication

When something fails:

1. **State what failed**: "The `commit_file_and_create_mr` call failed with: {error}"
2. **State why** (if known): "Authentication token may be invalid"
3. **Offer options**: "1) Retry, 2) Skip this step, 3) Do it manually"
4. **Never hide failures**: If part of a workflow failed, always report it even if the rest succeeded

## Anti-Patterns (Never Do These)

- Never auto-proceed past an approval gate
- Never generate or modify code without presenting an implementation plan first
- Never skip the implementation plan gate — even for "simple" or "obvious" changes
- Never batch multiple destructive actions into one approval (present each separately)
- Never re-execute a rejected action without the developer explicitly asking
- Never claim success if any part of the action failed
- Never modify Jira issues, push code, or post comments without showing the developer exactly what will happen first
- Never create Jira dev tasks without including an implementation plan (todo list) in the description
- Never create more than 10 Jira issues without confirming the full list
- Never assume "the developer probably wants this" — ask if unsure
