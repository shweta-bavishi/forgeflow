# Update Prompt: Integrate llm-wiki Strategy into `init-project.md`

> Apply these changes to `forgeflow/cli/prompts/workflows/init-project.md`
> The existing 6-phase structure is PRESERVED. Changes are ADDITIVE only.
> New content is clearly marked so you know exactly where to insert it.

---

## CHANGE 1 — Update the workflow header (lines 1–9)

**Find** the existing header block:
```
# Workflow 01: Initialize Project

**Goal**: Initialize Forgeflow for a target project – auto-scan the repository,
detect project details, present findings for approval, then generate a complete
`forgeflow-config.yml`.

**Trigger**: "Initialize Forgeflow", "Set up Forgeflow", "Init project", ...
**Agents**: Orchestrator → Code Agent, Project Context Agent
**Time**: ~5 minutes (mostly auto-detection + approval)
```

**Replace with** (add strategy declaration and second output file):
```
# Workflow 01: Initialize Project

**Goal**: Initialize Forgeflow for a target project – auto-scan the repository,
detect project details, present findings for approval, then generate a complete
`forgeflow-config.yml` AND a living `project-wiki.md` using the llm-wiki strategy.

**Strategy**: llm-wiki — treat the project as a versioned knowledge base.
Every fact is tagged with a confidence level. Every downstream workflow reads
`project-wiki.md` before acting.

**Trigger**: "Initialize Forgeflow", "Set up Forgeflow", "Init project", ...
**Agents**: Orchestrator → Code Agent, Project Context Agent
**Time**: ~5 minutes (mostly auto-detection + approval)
**Outputs**:
  - `forgeflow-config.yml`       ← machine config (existing)
  - `.forgeflow/project-wiki.md` ← human+LLM knowledge base (NEW)
```

---

## CHANGE 2 — Update CRITICAL RULES (lines 27–30)

**Find** the existing rules block:
```
## CRITICAL RULES

1. **SCAN FIRST, ASK LATER**: Never ask the user for project details that can be
   auto-detected. Always scan first, then present what you found.
2. **EXIT OPTION**: Every choice question MUST include an "Exit" option to cancel.
3. **Config file**: The output is `forgeflow-config.yml` (hyphenated, not dot-separated).
4. **Review before any workflow**: All other workflows must read `forgeflow-config.yml`
   before making any changes to the project.
```

**Replace with**:
```
## CRITICAL RULES

1. **SCAN FIRST, ASK LATER**: Never ask the user for project details that can be
   auto-detected. Always scan first, then present what you found.
2. **EXIT OPTION**: Every choice question MUST include an "Exit" option to cancel.
3. **Config file**: The output is `forgeflow-config.yml` (hyphenated, not dot-separated).
4. **Review before any workflow**: All other workflows must read BOTH
   `forgeflow-config.yml` AND `.forgeflow/project-wiki.md` before acting.
5. **llm-wiki confidence tagging**: Every fact written into `project-wiki.md` MUST
   carry one of: [DETECTED] [INFERRED] [USER-CONFIRMED] [UNKNOWN].
   - [DETECTED]       = read directly from a file or API
   - [INFERRED]       = derived by pattern matching or reasoning
   - [USER-CONFIRMED] = the user approved or corrected it in Phase 3
   - [UNKNOWN]        = could not determine; workflow must not assume
6. **Wiki versioning**: `project-wiki.md` opens with a version header. Init creates
   v1.0. Each subsequent workflow that updates it increments the patch number and
   appends one line to the Changelog section at the bottom.
7. **No secrets in wiki**: Credentials, tokens, and passwords are NEVER written into
   `project-wiki.md`. Reference them as `<SECRET:NAME>` only.
```

---

## CHANGE 3 — Add llm-wiki annotation step inside Phase 1 (after line ~85)

**Find** the end of Phase 1 (the last bullet under STEP 2 — Detect language):
```
  - go.mod → Go
```

**Insert immediately after**:
```
STEP 3 — Tag all Phase 1 findings with confidence level:
  - Mark each detected value as [DETECTED] or [INFERRED]:
      • Values read directly from package.json/pom.xml/go.mod → [DETECTED]
      • Values derived from file patterns (e.g., framework from dependencies) → [INFERRED]
      • GitLab project_id, default_branch from GitLab API → [DETECTED]
      • GitLab path guessed from package.json repository field → [INFERRED]
  - Store tagged findings in memory for Phase 5 wiki generation.
  - Do NOT present these tags to the user yet — just annotate internally.
```

---

## CHANGE 4 — Add llm-wiki annotation step inside Phase 2 (after Jira detection)

**Find** the end of Phase 2 (after "Mark Jira as 'not detected'"):
```
  → Mark Jira as "not detected"
```

**Insert immediately after**:
```
STEP 2 — Tag Jira findings:
  - Jira key found in commit history (3+ occurrences) → [DETECTED]
  - Jira key found in only 1–2 commits → [INFERRED]
  - Jira not found → [UNKNOWN]
  - board_id: always [UNKNOWN] until user provides it → flag as needs-input
```

---

## CHANGE 5 — Upgrade Phase 3 approval table

**Find** the existing Phase 3 table:
```
| Source          | Detected Value    | Found In         |
|-----------------|-------------------|------------------|
| GitLab Project  | org/my-project    | package.json     |
| GitLab ID       | 12345             | GitLab API       |
| Default Branch  | develop           | GitLab API       |
| Jira Project    | FICUIDEV          | Commit history   |
| Language        | TypeScript        | package.json     |
| Framework       | NestJS            | package.json     |
| Test Framework  | Jest              | package.json     |
| Linter          | ESLint            | package.json     |
```

**Replace with** (add Confidence column):
```
| Source          | Detected Value    | Found In         | Confidence        |
|-----------------|-------------------|------------------|-------------------|
| GitLab Project  | org/my-project    | package.json     | [INFERRED]        |
| GitLab ID       | 12345             | GitLab API       | [DETECTED]        |
| Default Branch  | develop           | GitLab API       | [DETECTED]        |
| Jira Project    | FICUIDEV          | Commit history   | [DETECTED]        |
| Language        | TypeScript        | package.json     | [DETECTED]        |
| Framework       | NestJS            | package.json     | [INFERRED]        |
| Test Framework  | Jest              | package.json     | [DETECTED]        |
| Linter          | ESLint            | package.json     | [DETECTED]        |

After the user chooses "Use these values" or "Let me correct":
  - Upgrade all approved/corrected values from [DETECTED]/[INFERRED] → [USER-CONFIRMED]
  - Any field the user fills in manually → [USER-CONFIRMED]
  - Any field still empty → [UNKNOWN]
```

---

## CHANGE 6 — Add domain mapping step inside Phase 4 (after folder scan)

**Find** the end of Phase 4 STEP 2 (architecture pattern detection):
```
Map each detected directory to a layer with name, path, and description.
```

**Insert immediately after**:
```
STEP 2b — Map directories to Domains for the wiki:
  For each detected architectural layer, create a Domain entry:
    domain_id:   D<N>  (D1, D2, D3 ... in order of importance)
    name:        <layer name>
    path:        <directory path from repo root>
    description: <what this layer is responsible for>
    depends_on:  [] ← list other domain_ids this layer calls/reads
    confidence:  [DETECTED | INFERRED]

  Cross-link domains: identify which domains consume each other's output.
  This becomes the Domain Map in the wiki (§4).

  Example output (internal, not shown to user yet):
    D1: Controllers  (src/controllers) → calls D2
    D2: Services     (src/services)    → calls D3
    D3: Repositories (src/repositories)
```

---

## CHANGE 7 — Upgrade Phase 5 to generate BOTH outputs

**Find** the Phase 5 header:
```
## Phase 5: PRESENT FULL DRAFT CONFIG

Generate the complete `forgeflow-config.yml` and show it to the developer.
```

**Replace with**:
```
## Phase 5: PRESENT FULL DRAFT CONFIG + WIKI

Generate both outputs and show them to the developer.

### 5a — Generate `forgeflow-config.yml` (existing format, unchanged)
```

Then **find** the closing `---` at the end of the existing forgeflow-config.yml block and **insert after it**:

```
### 5b — Generate `.forgeflow/project-wiki.md` (NEW — llm-wiki strategy)

Generate the following document and show it to the developer AFTER the config:

---
```markdown
---
wiki_version: 1.0
project: <project.name from config>
initialized_at: <ISO-8601 timestamp>
initialized_by: forgeflow init
strategy: llm-wiki
---

# Project Wiki — <Project Name>

> <one-line description from config>
> All forgeflow workflows read this document before acting.

---

## 0. How To Use This Wiki

This document is maintained by `forgeflow init` and updated by every workflow.
- Workflows READ §1–§8 to understand the project before acting.
- Workflows WRITE to §9 (their own subsection) after completing work.
- Any workflow that changes a fact MUST update the confidence tag and bump wiki_version.
- If this file does not exist, run `forgeflow init` before any other command.

---

## 1. Project Identity
```yaml
name:         <from config>           # [USER-CONFIRMED]
description:  <from config>           # [DETECTED/INFERRED/USER-CONFIRMED]
language:     <from config>           # [DETECTED]
framework:    <from config>           # [INFERRED]
runtime:      <from config>           # [DETECTED]
repository:   <from config>           # [DETECTED/INFERRED]
team:         <from config or UNKNOWN># [USER-CONFIRMED/UNKNOWN]
```

---

## 2. Repository & Structure
```yaml
gitlab_project_path: <value> # [DETECTED/INFERRED]
gitlab_project_id:   <value> # [DETECTED/UNKNOWN]
default_branch:      <value> # [DETECTED/UNKNOWN]
package_manager:     <value> # [DETECTED]
```

Top-level directories:
| Directory  | Purpose                    | Confidence  |
|------------|----------------------------|-------------|
| `src/`     | Application source code    | [DETECTED]  |
| `test/`    | Test suites                | [DETECTED]  |
| `config/`  | Configuration files        | [DETECTED]  |
| `scripts/` | Build and utility scripts  | [DETECTED]  |
<!-- Add all detected directories here -->

Key files detected:
<!-- List all key_files from Phase 4 STEP 3 -->

---

## 3. Architecture
```yaml
pattern:    <modular/layered/component-based/pages/django-apps>  # [INFERRED]
```

### Domain Map
<!-- One entry per domain from Phase 4 STEP 2b -->

**D1 — <Name>**
- Path: `<path>`
- Responsibility: <what it does>
- Depends on: <other domain IDs or none>
- Confidence: [DETECTED/INFERRED]

**D2 — <Name>**
- Path: `<path>`
- Responsibility: <what it does>
- Depends on: <other domain IDs or none>
- Confidence: [DETECTED/INFERRED]

<!-- repeat for all domains -->

---

## 4. Tech Stack & Standards
```yaml
linter:             <value>  # [DETECTED]
formatter:          <value>  # [DETECTED/UNKNOWN]
test_framework:     <value>  # [DETECTED]
coverage_threshold: <value>  # [DETECTED/UNKNOWN]
file_naming:        <value>  # [INFERRED/UNKNOWN]
```

---

## 5. Integrations
```yaml
jira:
  project_key: <value>  # [DETECTED/UNKNOWN]
  board_id:    <value>  # [USER-CONFIRMED/UNKNOWN]
gitlab:
  project_path:   <value>  # [INFERRED]
  project_id:     <value>  # [DETECTED]
  default_branch: <value>  # [DETECTED]
jenkins:
  job_name: <value or UNKNOWN>  # [DETECTED/UNKNOWN]
sonarqube:
  project_key: <value or UNKNOWN>  # [DETECTED/UNKNOWN]
confluence:
  space_key: <value or UNKNOWN>  # [USER-CONFIRMED/UNKNOWN]
```

---

## 6. CI/CD Pipeline
```yaml
platform:      <GitLab CI / Jenkins / GitHub Actions / UNKNOWN>  # [DETECTED/UNKNOWN]
pipeline_file: <path or UNKNOWN>                                  # [DETECTED/UNKNOWN]
```

Detected pipeline stages (from `.gitlab-ci.yml` or `Jenkinsfile`):
<!-- List stages if pipeline file was found, otherwise mark [UNKNOWN] -->

Known [UNKNOWN] gaps that workflows should verify before touching pipeline:
<!-- List any pipeline facts that could not be detected -->

---

## 7. Workflow Intelligence
<!-- This section is the primary reference for all forgeflow workflows -->

### 7.1 — Epic Creation
- Epics should map to Domains in §3.
- Reference at least one Domain ID (D1, D2...) in every epic.
- Verify Jira project_key (§5) is [USER-CONFIRMED] before creating epics.

### 7.2 — Dev Task Planning
- Read §3 Domain Map to understand blast radius before breaking down tasks.
- Check §4 coverage_threshold — tasks must not drop coverage below this.
- If coverage_threshold is [UNKNOWN], ask user before planning test subtasks.

### 7.3 — Code Changes
- Before editing any file, identify its Domain from §3.
- Run linter (`<linter from §4>`) and test framework (`<framework from §4>`) locally.
- Commit format: `<type>(D<N>): <description>` using domain IDs from §3.
- Check §6 for pipeline — ensure your change won't break detected stages.

### 7.4 — MR Review
- Verify: tests added, coverage maintained (§4 threshold), no secrets committed.
- For changes touching 2+ Domains (§3): flag for cross-domain review.
- Pipeline must be green (§6) before approval.

### 7.5 — Pipeline Fix
- Identify the failed stage against §6 known stages.
- Check §5 integrations — failures may be caused by misconfigured Jira/Sonar keys.
- Never disable a stage as a fix — open a chore task instead.

---

## 8. Open Questions

| # | Question                          | Affects          | Status | Added by |
|---|-----------------------------------|------------------|--------|----------|
| 1 | Confirm `jira.board_id`           | Epic creation    | OPEN   | init     |
| 2 | Confirm `confluence.space_key`    | Documentation    | OPEN   | init     |
<!-- Add one row per [UNKNOWN] field from §1–§6 -->

---

## 9. Changelog

| Version | Date       | Workflow | Change Summary                        |
|---------|------------|----------|---------------------------------------|
| 1.0     | <date>     | init     | Wiki created via llm-wiki strategy    |

<!-- Every workflow appends here when it updates this document -->
```
---

After presenting both files, ask:
  1. Save both files
  2. Edit config values first
  3. Edit wiki content first
  4. Exit

IF "Edit wiki content": ask which section to correct, update, re-present wiki only.
IF "Save both": continue to Phase 6.
```

---

## CHANGE 8 — Upgrade Phase 6 save steps

**Find** the existing Phase 6 local project steps:
```
FOR local projects:
  STEP 1 – Write forgeflow-config.yml to project root
  STEP 2 – Create .forgeflow/ directory
  STEP 3 – Write .forgeflow/project-context.md (architecture summary)
  STEP 4 – Add .forgeflow/ to .gitignore if not already there
```

**Replace with**:
```
FOR local projects:
  STEP 1 – Write forgeflow-config.yml to project root
  STEP 2 – Create .forgeflow/ directory (if not exists)
  STEP 3 – Write .forgeflow/project-wiki.md  ← replaces project-context.md
  STEP 4 – Add .forgeflow/ to .gitignore if not already there

  NOTE: project-wiki.md supersedes project-context.md.
  If project-context.md already exists from a previous init, rename it:
    → mv .forgeflow/project-context.md .forgeflow/project-wiki.md
    Then prepend the wiki YAML front-matter block to the top.
```

**Find** the existing Phase 6 remote project steps:
```
FOR remote projects:
  STEP 1 – Write config to ~/.forgeflow/projects/<name>/config.yml
  STEP 2 – Write origin.yml with source URL, branch, sync time
  STEP 3 – Set as active remote project
```

**Replace with**:
```
FOR remote projects:
  STEP 1 – Write config to ~/.forgeflow/projects/<name>/config.yml
  STEP 2 – Write ~/.forgeflow/projects/<name>/project-wiki.md
  STEP 3 – Write origin.yml with source URL, branch, sync time
  STEP 4 – Set as active remote project
```

---

## CHANGE 9 — Update the completion message (after line 310)

**Find** the existing completion message block (whatever is shown after "Show completion:").

**Add** this to the completion output:
```
Show completion:

✅ Forgeflow initialized successfully!

Files written:
  📄 forgeflow-config.yml          ← machine config for all workflows
  📚 .forgeflow/project-wiki.md    ← living project knowledge base

Wiki summary:
  • Domains mapped:    <N>
  • Confidence gaps:   <count> [UNKNOWN] fields → see §8 Open Questions
  • Integrations:      Jira <DETECTED/UNKNOWN>, GitLab <DETECTED>, CI/CD <DETECTED/UNKNOWN>

Next steps:
  1. Fill open questions in §8 of project-wiki.md
  2. Run `forgeflow epic create` to plan your first epic
  3. Run `forgeflow doctor` to validate config

All forgeflow workflows will now read project-wiki.md before acting.
```

---

## CHANGE 10 — Add downstream workflow preamble as a new appendix section

**Append at the very end of `init-project.md`**:

```markdown
---

## Appendix: Preamble for All Other Workflow Files

Copy this block to the TOP of every other workflow prompt file
(epic-create.md, plan-task.md, code-change.md, review-mr.md, fix-pipeline.md):

---
> **⚠️ FORGEFLOW WIKI REQUIREMENT — READ BEFORE ACTING**
>
> Before performing any action in this workflow:
>
> 1. Read `forgeflow-config.yml` from the project root.
> 2. Read `.forgeflow/project-wiki.md` — identify the relevant Domain(s) from §3.
> 3. Check [MUST] constraints and [UNKNOWN] gaps in §8 that affect this workflow.
> 4. Read §7.<N> — the subsection written for THIS workflow.
>
> If `.forgeflow/project-wiki.md` does not exist:
> → STOP. Tell the user: "Run `forgeflow init` first."
>
> If you update any project fact during this workflow:
> → Correct the relevant section in `project-wiki.md`.
> → Update the confidence tag to [USER-CONFIRMED] or [DETECTED].
> → Increment `wiki_version` patch number.
> → Append one line to §9 Changelog.
---
```

---

## Summary of All Changes

| Change | Location in file | What it does |
|--------|-----------------|--------------|
| 1 | Lines 1–9 header | Adds llm-wiki strategy declaration and `project-wiki.md` as second output |
| 2 | CRITICAL RULES | Adds 4 new rules: confidence tagging, wiki versioning, both-files reading, no secrets |
| 3 | End of Phase 1 | Tags all auto-detected values with [DETECTED] or [INFERRED] |
| 4 | End of Phase 2 | Tags Jira detection confidence |
| 5 | Phase 3 table | Adds Confidence column; upgrades tags to [USER-CONFIRMED] on approval |
| 6 | Phase 4 STEP 2 | Maps directories to Domain IDs (D1, D2...) for wiki §3 |
| 7 | Phase 5 | Generates `project-wiki.md` alongside `forgeflow-config.yml` |
| 8 | Phase 6 | Saves `project-wiki.md` instead of `project-context.md`; handles migration |
| 9 | Completion message | Shows wiki summary with domain count and confidence gaps |
| 10 | New appendix | Preamble block to paste into all other workflow prompt files |

**Nothing is removed from the existing workflow. All 6 phases are preserved.**
**The only replacement is `project-context.md` → `project-wiki.md` in Phase 6.**
