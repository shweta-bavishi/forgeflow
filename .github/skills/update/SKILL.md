---
name: update
description: "Update Otomate to the latest version. Checks the version installed in the project's .otomate/ directory, compares it against the latest available version, and if outdated, copies the latest Otomate files while preserving the project's otomate.config.yml. Use when developer says 'update otomate', 'upgrade otomate', 'check for updates', 'update .otomate', 'is otomate up to date'."
---

# Skill: Update Otomate

Check the installed Otomate version in the project and update to the latest version if outdated. Preserves project-specific configuration.

## Input

```
OPTIONAL: project_path — path to the target project folder

IF path provided → use that path
IF no path → default to current working directory

Store: otomate_source = the directory containing the latest Otomate installation
       (where VERSION, agents/, workflows/, etc. live)
```

## Phase 1: VERSION CHECK

```
STEP 1 — Find .otomate/ directory:
  Look for: {project_path}/.otomate/

  IF NOT FOUND:
    → STOP: "Otomate is not installed in this project.
             Run 'Initialize Otomate' first."
    → Offer to run init-project workflow

STEP 2 — Read versions:
  Installed: {project_path}/.otomate/VERSION → installed_version
    IF no VERSION file → set installed_version = "0.0.0"
  Latest: {otomate_source}/VERSION → latest_version
    IF no VERSION file → STOP: "Cannot determine latest version."

STEP 3 — Compare:
  IF installed_version == latest_version:
    → "Otomate is up to date! v{installed_version}"
    → STOP

  IF installed_version != latest_version:
    → Continue to Phase 2
```

## Phase 2: PRESENT UPDATE PLAN

```
Show what will be updated:

📦 Update Available: v{installed_version} → v{latest_version}

WILL UPDATE (replaced with latest):
  .otomate/agents/       .otomate/workflows/
  .otomate/templates/    .otomate/config/
  .otomate/docs/         .otomate/scripts/
  .otomate/.github/      .otomate/VERSION
  .otomate/README.md     .otomate/SETUP.md
  .otomate/ARCHITECTURE.md

WILL NOT TOUCH:
  otomate.config.yml (your project config — preserved)
  Everything outside .otomate/

⚠ Manual customizations inside .otomate/ will be overwritten.
```

## Phase 3: 🚦 HITL GATE — Approve Update

```
Ask: "Proceed with update to v{latest_version}? (yes / no / back up first)"

IF "back up first":
  → Suggest backup command
  → Wait for confirmation

IF "no" → STOP

IF "yes" → Continue to Phase 4
```

## Phase 4: PERFORM UPDATE

```
STEP 1 — Remove old Otomate content from .otomate/:
  Remove: agents/, workflows/, templates/, config/, docs/,
          scripts/, .github/, VERSION, README.md, SETUP.md,
          ARCHITECTURE.md

STEP 2 — Copy latest files:
  Source: {otomate_source}/
  Destination: {project_path}/.otomate/

  Copy:
    agents/         workflows/      templates/
    config/         docs/           scripts/
    .github/        VERSION         README.md
    SETUP.md        ARCHITECTURE.md

  DO NOT copy: .git/, otomate.config.yml, .gitattributes

STEP 3 — Update otomate_version in otomate.config.yml:
  Read config → update otomate_version field → write back
  IF field doesn't exist → add it at the top
```

## Phase 5: VERIFY & REPORT

```
STEP 1 — Verify:
  ✓ .otomate/VERSION == latest_version
  ✓ .otomate/agents/ exists with files
  ✓ .otomate/workflows/ exists with files
  ✓ .otomate/.github/skills/ exists with files

STEP 2 — Check for new config fields:
  IF new required fields exist in latest version that aren't in project config:
    → WARN: list new fields with descriptions and example values

STEP 3 — Summary:
  ✅ Updated: v{installed_version} → v{latest_version}
  ✓ All Otomate files updated
  ✓ otomate.config.yml preserved
  {if new fields} ⚠ New config fields available — see above
```

## Error Handling

```
No .otomate/ → suggest init-project workflow
Missing source VERSION → stop, suggest re-cloning otomate
Copy failure → show what succeeded/failed, offer retry or manual copy
Config incompatibility → warn, suggest re-init or manual field updates
Invalid project path → ask for valid path
```
