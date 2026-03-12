# Workflow 13: Update Otomate

**Goal**: Check the installed Otomate version in a project's `.otomate/` directory and, if it is not the latest version, update all Otomate files to the latest version while preserving the project-specific `otomate.config.yml`.

**Trigger**: "Update Otomate", "Upgrade Otomate", "Check for Otomate updates", "Update .otomate"

**Agents**: Orchestrator → Project Context Agent

**Time**: ~2-5 minutes

## Input

```
OPTIONAL: project_path — path to the target project folder

IF developer provides a path:
  → Use that path as the target project
  Examples: "Update Otomate at /home/dev/my-api", "Update Otomate in ../my-api"

IF no path provided:
  → Default: current working directory
  → Look for .otomate/ in current directory
```

## Phase 1: VERSION CHECK

```
STEP 1 — Locate the project's .otomate/ directory:
  Look for: {project_path}/.otomate/

  IF .otomate/ DOES NOT EXIST:
    → STOP: "Otomate is not installed in this project.
             No .otomate/ directory found at {project_path}.
             Run 'Initialize Otomate' first to set up this project."
    → Offer: "Would you like to initialize Otomate for this project?"

STEP 2 — Read installed version:
  Read: {project_path}/.otomate/VERSION → installed_version

  IF VERSION file does not exist:
    → WARN: "No VERSION file found in .otomate/. This project may have been
             initialized with an older version of Otomate before versioning was added."
    → Set: installed_version = "0.0.0" (treat as oldest possible)

STEP 3 — Read latest available version:
  Read: {otomate_source}/VERSION → latest_version

  IF VERSION file does not exist in source:
    → STOP: "Cannot determine latest Otomate version. VERSION file missing
             from Otomate source at {otomate_source}."

STEP 4 — Compare versions:
  IF installed_version == latest_version:
    → INFORM: "Otomate is already up to date!
               Installed version: v{installed_version}
               Latest version: v{latest_version}
               No update needed."
    → STOP

  IF installed_version != latest_version:
    → Continue to Phase 2
```

## Phase 2: PRESENT UPDATE PLAN

```
Show developer what will happen:

  📦 Otomate Update Available
  ─────────────────────────────
  Installed version: v{installed_version}
  Latest version:    v{latest_version}

  What will be UPDATED (replaced with latest):
    .otomate/agents/         — Agent definitions
    .otomate/workflows/      — Workflow definitions
    .otomate/templates/      — Code & doc templates
    .otomate/config/         — Configuration reference & tool inventory
    .otomate/docs/           — Documentation
    .otomate/scripts/        — Utility scripts
    .otomate/.github/        — Copilot agents, skills, instructions
    .otomate/VERSION         — Version stamp
    .otomate/README.md       — Project README
    .otomate/SETUP.md        — Setup guide
    .otomate/ARCHITECTURE.md — Architecture docs

  What will NOT be touched:
    otomate.config.yml       — Your project-specific configuration (PRESERVED)
    .git/                    — Git history (NOT touched)
    Any files outside .otomate/ — Your code is safe

  ⚠ WARNING: Any manual customizations you've made to files inside
     .otomate/ will be overwritten. If you've customized agents or
     workflows, back them up first.
```

## Phase 3: 🚦 HITL GATE — Approve Update

```
Ask: "Do you want to proceed with the update?

Options:
  1. Yes, update to v{latest_version}
  2. No, keep current version
  3. Let me back up my customizations first"

IF developer says "back up first":
  → Suggest: "Copy your customized files to a backup location:
              cp -r {project_path}/.otomate/ {project_path}/.otomate-backup-v{installed_version}/
              Then say 'proceed with update' when ready."
  → WAIT for developer to confirm

IF developer says "no":
  → STOP: "Update cancelled. You're still on v{installed_version}."

IF developer says "yes":
  → Continue to Phase 4
```

## Phase 4: PERFORM UPDATE

```
STEP 1 — Remove old .otomate/ contents:
  Remove the following directories/files from {project_path}/.otomate/:
    agents/
    workflows/
    templates/
    config/
    docs/
    scripts/
    .github/
    VERSION
    README.md
    SETUP.md
    ARCHITECTURE.md

  DO NOT remove:
    Any files the developer may have added that don't exist in source
    (be cautious — only remove known Otomate directories)

STEP 2 — Copy latest Otomate files:
  Source: {otomate_source}/
  Destination: {project_path}/.otomate/

  Copy:
    {otomate_source}/agents/           → {project_path}/.otomate/agents/
    {otomate_source}/workflows/        → {project_path}/.otomate/workflows/
    {otomate_source}/templates/        → {project_path}/.otomate/templates/
    {otomate_source}/config/           → {project_path}/.otomate/config/
    {otomate_source}/docs/             → {project_path}/.otomate/docs/
    {otomate_source}/scripts/          → {project_path}/.otomate/scripts/
    {otomate_source}/.github/          → {project_path}/.otomate/.github/
    {otomate_source}/VERSION           → {project_path}/.otomate/VERSION
    {otomate_source}/README.md         → {project_path}/.otomate/README.md
    {otomate_source}/SETUP.md          → {project_path}/.otomate/SETUP.md
    {otomate_source}/ARCHITECTURE.md   → {project_path}/.otomate/ARCHITECTURE.md

  DO NOT copy:
    .git/
    otomate.config.yml
    .gitattributes

STEP 3 — Update otomate_version in config:
  Read: {project_path}/otomate.config.yml
  Update: otomate_version field to {latest_version}
  Write: updated config back

  IF otomate_version field doesn't exist in config:
    → Add it at the top of the config file:
      otomate_version: "{latest_version}"
```

## Phase 5: VERIFY UPDATE

```
STEP 1 — Verify file structure:
  Confirm: .otomate/VERSION contains {latest_version}
  Confirm: .otomate/agents/ directory exists and has files
  Confirm: .otomate/workflows/ directory exists and has files
  Confirm: .otomate/templates/ directory exists and has files
  Confirm: .otomate/.github/skills/ directory exists and has files

STEP 2 — Verify config compatibility:
  Read: {project_path}/otomate.config.yml
  Check: Are there any NEW required config fields in the latest version
         that don't exist in the project's config?

  IF new required fields found:
    → WARN: "The latest version introduces new config fields:
             {list of new fields with descriptions}
             Please add these to your otomate.config.yml."
    → Show: Example values for each new field

  IF no new fields:
    → All good, config is compatible

STEP 3 — Show update summary:
  ✅ Otomate updated successfully!
  ─────────────────────────────
  Previous version: v{installed_version}
  Current version:  v{latest_version}

  Updated:
    ✓ Agents: {count} agent definitions
    ✓ Workflows: {count} workflow definitions
    ✓ Templates: code & doc templates
    ✓ Skills: {count} Copilot skills
    ✓ Documentation: latest guides

  Preserved:
    ✓ otomate.config.yml (your project config — untouched)

  {IF new config fields}
  ⚠ ACTION NEEDED:
    New config fields available. See above for details.
  {END IF}

  You're now running Otomate v{latest_version}!
```

## Error Handling

### If .otomate/ directory doesn't exist

```
→ STOP: "Otomate is not installed in this project."
→ Offer: "Run 'Initialize Otomate' to set up this project."
```

### If source VERSION file is missing

```
→ STOP: "Cannot determine latest version. Otomate source may be corrupted."
→ Suggest: "Re-clone the Otomate repository and try again."
```

### If copy fails mid-update

```
→ WARN: "Update failed during file copy: {error}"
→ Show: Which files were successfully copied and which failed
→ Suggest: "Your .otomate/ directory may be in an inconsistent state.
            Options:
            1. Retry the update
            2. Manually copy from {otomate_source}/
            3. Re-initialize: 'Force re-initialize Otomate'"
```

### If config has incompatible changes

```
→ WARN: "Your otomate.config.yml uses a format from v{installed_version}
         that may not be fully compatible with v{latest_version}."
→ Show: Specific incompatibilities
→ Suggest: "Run 'Initialize Otomate' with force to regenerate config,
            or manually update the listed fields."
```

### If project path is invalid

```
→ STOP: "The path '{project_path}' does not exist or is not accessible."
→ Ask: "Please provide a valid path to your project directory."
```

## What NOT to Do

- ❌ NEVER modify otomate.config.yml content (only update otomate_version field)
- ❌ NEVER delete files outside .otomate/ directory
- ❌ NEVER proceed without developer approval (always HITL gate before update)
- ❌ NEVER skip the version check (always compare before updating)
- ❌ NEVER copy .git/ directory from source
- ❌ NEVER overwrite otomate.config.yml with the template version

## Success Criteria

✓ Version check correctly identifies outdated installations
✓ Update copies all latest files without data loss
✓ Project config (otomate.config.yml) is preserved
✓ VERSION stamp is updated in .otomate/
✓ otomate_version field in config is updated
✓ Developer is warned about any new config fields
✓ Developer can safely roll back if needed

---

**Duration**: 2-5 minutes

**What It Does**: Updates `.otomate/` directory with latest Otomate files

**What It Preserves**: `otomate.config.yml` (project-specific config)

**Related**:
- Workflow 01: Init Project (for fresh installations)
- VERSION file (source of truth for latest version)
