# Workflow 01 — Init Project

> Scans an existing repository, detects its technology stack, and generates a `forgeflow.config.yml` tailored to the project.

---

## When to Use

- You are onboarding a **new** project into ForgeFlow for the first time.
- The repository already exists (at least a skeleton) in GitLab.
- You want ForgeFlow to auto-detect the tech stack instead of writing the config from scratch.

## Prerequisites

| Requirement | Details |
|---|---|
| GitLab repo | Repository must be accessible via `get_gitlab_file_content` |
| MCP server | Running and reachable with a valid GitLab token |
| IDE | VS Code or JetBrains with Copilot Chat + MCP configured |

## How to Trigger

In Copilot Chat, say:

```
@forgeflow initialise project my-group/my-service
```

Or simply:

```
@forgeflow init
```

The Orchestrator will route to **Workflow 01** automatically.

## What Happens

### Phase 1 — Repository Scan

The Code Agent reads key files from the repo to detect:

| Signal | Files Inspected |
|---|---|
| Language / runtime | `package.json`, `pom.xml`, `build.gradle`, `go.mod`, `requirements.txt` |
| Framework | Framework-specific markers (NestJS `nest-cli.json`, Spring `application.yml`, etc.) |
| Architecture pattern | Directory structure conventions (`src/modules/`, `src/controllers/`, `src/domain/`) |
| CI/CD pipeline | `.gitlab-ci.yml`, `Jenkinsfile` |
| Testing framework | Jest config, JUnit deps, pytest markers |
| Linting / formatting | `.eslintrc`, `.prettierrc`, `tslint.json` |

### Phase 2 — Config Generation

A draft `forgeflow.config.yml` is assembled using the detected values.  Fields that cannot be inferred (Jira project key, Confluence space, Jenkins job URL) are left with placeholder comments.

### Phase 3 — HITL Review

The generated config is presented to you **before** it is written to the repo.  You can:

- Edit any value.
- Add missing fields (Jira, Confluence, Jenkins details).
- Approve to write the file.

### Phase 4 — Commit

Once approved, the config file is committed to the repository via `commit_file_and_create_mr` on a dedicated branch (e.g. `forgeflow/init-config`).

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `get_gitlab_file_content` | Read repo files for detection |
| `list_project_directory` | Browse directory structure |
| `commit_file_and_create_mr` | Commit the generated config |

## Tips

- Run this workflow **once** per project. After the config exists, update it manually or re-run only if the tech stack changes significantly.
- If detection is inaccurate, correct the config before approving — the rest of ForgeFlow relies on these values.
- You can pre-fill Jira / Confluence / Jenkins values before committing to save a round of manual editing later.

## Example Output

```
✅ Repository scanned: my-group/my-service
   Language:      TypeScript
   Framework:     NestJS 10.x
   Architecture:  Modular monolith (src/modules/)
   CI:            .gitlab-ci.yml (stages: build, test, deploy)
   Testing:       Jest
   Linter:        ESLint + Prettier

📄 Draft forgeflow.config.yml generated.
   ⚠️  Placeholders remaining: jira.project_key, confluence.space_key, jenkins.base_url

🔍 Please review the config below and approve or edit.
```

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "Cannot read file" errors | Token lacks repo read permission | Verify `GITLAB_TOKEN` scopes (read_repository) |
| Wrong language detected | Ambiguous repo (multiple `package.json` + `pom.xml`) | Manually correct in the generated config |
| Config missing sections | New framework not in detection heuristics | Add the missing section manually; consider contributing detection logic |
