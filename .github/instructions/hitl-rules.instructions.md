---
applyTo: "**"
---

# HITL (Human-in-the-Loop) Rules — Always-On

These rules govern when and how to request developer approval during workflow execution. They apply to ALL Otomate agents and skills.

## Approval Gate Protocol

### Actions That ALWAYS Require Approval

Before executing any of these actions, STOP and present a summary to the developer:

1. **Push code to remote** — Show: files changed, line counts, branch name, target branch
2. **Create merge request** — Show: MR title, description, source → target branch, files list
3. **Create release build** — Show: version, included changes, merge target
4. **Publish release notes** — Show: rendered content, target Confluence page
5. **Update Jira status to Done** — Show: issue key, current status → new status
6. **Post MR review comment** — Show: full review content, MR ID
7. **Create security fix MR** — Show: dependency changes, CVE list, breaking change assessment
8. **Create Zephyr test cases** — Show: test case list with names, count, linked issues
9. **Create Jira issues** — Show: issue summaries, types, priorities, count

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
- Never batch multiple destructive actions into one approval (present each separately)
- Never re-execute a rejected action without the developer explicitly asking
- Never claim success if any part of the action failed
- Never modify Jira issues, push code, or post comments without showing the developer exactly what will happen first
- Never create more than 10 Jira issues without confirming the full list
- Never assume "the developer probably wants this" — ask if unsure
