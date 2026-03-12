# Workflow: Create Workflow

**Trigger:** "Create a new workflow", "I want to automate...", "Can Otomate do...", "Add a workflow for...", "Build a custom workflow", "Extend Otomate to..."

## What It Does

A meta-workflow that lets you describe an automation need in natural language, then:
1. Analyzes feasibility against all 113 available MCP tools
2. If NOT feasible — explains what's missing and suggests alternatives
3. If feasible — designs the workflow, generates a production-ready SKILL.md, and commits it via MR

## How to Use

1. Say: **"Create a new workflow that updates Jiras after a deployment"**
2. Otomate asks clarifying questions (trigger, input, output, systems, HITL gates)
3. Presents a **feasibility analysis** with per-step assessment
4. You review and approve the feasibility verdict
5. Otomate presents a **workflow design** with phases, tools, and limitations
6. You review, iterate, and approve the design
7. Otomate generates the complete SKILL.md
8. You review the generated file
9. Otomate commits it and creates an MR

## HITL Gates

- **Approve feasibility assessment** — before designing the workflow
- **Approve workflow design** — before generating the SKILL.md
- **Approve file creation** — before committing and creating the MR

## MCP Tools Used

`list_available_skills_tool`, `get_file_content`, `commit_file_and_create_mr`, `commit_and_push_file`, plus any discovery tools needed to validate requirements (`list_jira_projects`, `jenkins_list_jobs`, etc.)

## Duration

~10-20 minutes (depends on requirement complexity and iteration rounds)

## Example: Feasible Workflow

```
Developer: "Create a workflow that checks SonarQube quality and creates
            Jira issues for critical violations"

Otomate: "Feasibility: ✅ FULLY FEASIBLE
  - get_sonar_project_issues → fetch violations ✅
  - LLM analysis → filter critical ones 🔧
  - create_jira_issue → create Jira per violation ✅
  Shall I design this workflow?"
```

## Example: Not Feasible Workflow

```
Developer: "Create a workflow that auto-deploys when all tests pass"

Otomate: "Feasibility: ❌ NOT FEASIBLE
  - Listening for test results requires webhooks (not available)
  - Triggering Jenkins deploys not possible (read-only)
  
  Alternative: A manual-trigger workflow that checks latest build
  status and guides you through the deployment process."
```

## Tips

- **Be specific** about trigger, input, output, and which systems are involved
- **Event-driven triggers** (webhooks, cron) are not possible — workflows are always developer-triggered
- **Partially feasible** workflows are still valuable — 80% automation + 20% guided manual steps
- Generated skills are committed via MR — you can edit them before merge

## Next Steps

After the MR is merged, test the new workflow by selecting Otomate in Copilot Chat and using one of the trigger phrases.
