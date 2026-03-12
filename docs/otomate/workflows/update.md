# Workflow: Update Otomate

**Trigger:** "Update Otomate", "Upgrade Otomate", "Check for Otomate updates", "Is Otomate up to date?"

## What It Does

Checks the installed Otomate version in your project's `.otomate/` directory, compares it against the latest available version, and if outdated, updates all Otomate files while preserving your project-specific `otomate.config.yml`.

## How to Use

### From inside the project

```
Update Otomate
```

### From outside the project

```
Update Otomate at /path/to/my-project
```

### Just check (no update)

```
Check for Otomate updates
```

## What Happens

1. **Version check**: Reads `.otomate/VERSION` (installed) and compares with source `VERSION` (latest)
2. **If up to date**: Tells you and stops
3. **If outdated**: Shows what will be updated vs preserved
4. **Approval**: You confirm the update (or back up customizations first)
5. **Update**: Replaces `.otomate/` contents with latest files
6. **Config update**: Updates `otomate_version` field in `otomate.config.yml`
7. **Verify**: Confirms everything is in order and warns about any new config fields

## What Gets Updated

| Component | Action |
|-----------|--------|
| `.otomate/agents/` | Replaced with latest |
| `.otomate/workflows/` | Replaced with latest |
| `.otomate/templates/` | Replaced with latest |
| `.otomate/config/` | Replaced with latest |
| `.otomate/docs/` | Replaced with latest |
| `.otomate/scripts/` | Replaced with latest |
| `.otomate/.github/` | Replaced with latest |
| `.otomate/VERSION` | Updated to latest version |

## What Is Preserved

| Component | Action |
|-----------|--------|
| `otomate.config.yml` | **NOT touched** (only `otomate_version` field updated) |
| Your source code | **NOT touched** |
| Everything outside `.otomate/` | **NOT touched** |

## Customization Warning

If you've manually edited files inside `.otomate/` (e.g., customized an agent or workflow), those changes **will be overwritten**. The workflow warns you about this and offers a backup option:

```
cp -r .otomate/ .otomate-backup-v1.0.0/
```

## New Config Fields

When a new Otomate version introduces new config fields, the update workflow will:
1. Detect which fields are new
2. Show you what they are and what they do
3. Provide example values

You'll need to manually add these to your `otomate.config.yml`.

## Not Initialized?

If the project doesn't have a `.otomate/` directory, the update workflow will tell you to run "Initialize Otomate" first.

## HITL Gates

- **Before update**: Must confirm you want to proceed (or back up first)

## Duration

~2-5 minutes

## Example

```
Developer: "Update Otomate"

Otomate: "📦 Update Available
          Installed: v1.0.0
          Latest:    v1.1.0

          Will update: agents, workflows, templates, skills, docs
          Will preserve: otomate.config.yml

          Proceed? (yes / no / back up first)"

Developer: "yes"

Otomate: "✅ Updated to v1.1.0!
          ⚠ New config field available:
            - zephyr.test_cycle_id: ID of default test cycle
          Add this to your otomate.config.yml when ready."
```

## Next Steps

After updating, all workflows will use the latest definitions. No restart needed.
