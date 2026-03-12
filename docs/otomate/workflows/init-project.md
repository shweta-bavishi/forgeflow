# Workflow: Initialize Project

**Trigger:** "Initialize Otomate", "Set up Otomate", "Init project", "Init project at {path}"

## What It Does

Scans a target project's repository structure, auto-detects language, framework, architecture, CI/CD tools, and coding conventions, then generates a complete `otomate.config.yml` and copies the full Otomate system into the project's `.otomate/` directory with version stamping.

## How to Use

### From outside the project (recommended for first-time setup)

1. Select **Otomate** agent in Copilot Chat
2. Say: **"Init project at /path/to/my-project"**
3. Otomate scans the target repo and presents a draft config
4. Review and fill in any fields marked ⚠ NEEDS INPUT
5. Approve → config saved + `.otomate/` installed

### From inside the project

1. Open the project in your IDE
2. Select **Otomate** agent in Copilot Chat
3. Say: **"Initialize Otomate"**
4. Same flow as above, using current directory as target

## What Happens

1. **Pre-flight check**: Validates the path and checks if already initialized
2. **Scan**: Auto-detects project characteristics
3. **Present**: Shows draft config with ✓ detected / ⚠ needs input markers
4. **Review**: You fill in missing values and correct any mistakes
5. **Save**: Creates `otomate.config.yml` at project root
6. **Install**: Copies all Otomate files (agents, workflows, templates, skills, docs) into `.otomate/`
7. **Stamp**: Writes the current version to `.otomate/VERSION`

## Already Initialized?

If the project already has a `.otomate/` directory:

- **Same version**: Otomate tells you it's already initialized and suggests using "Update Otomate" if needed
- **Different version**: Otomate tells you the installed vs latest version and suggests the Update workflow
- **Force re-init**: Say "Force re-initialize Otomate" to overwrite everything (requires confirmation)

## What Gets Detected Automatically

- Language (TypeScript, Java, Python, Go, Rust, C#)
- Framework (NestJS, Spring Boot, Django, Express, etc.)
- Package manager (npm, maven, pip, etc.)
- Test framework (Jest, pytest, JUnit)
- Linter/formatter (ESLint, Prettier, Pylint)
- Architecture layers (from folder structure)
- CI/CD tools (Jenkins, GitLab CI, SonarQube)
- Commit message patterns, branch naming conventions

## What You Need to Provide

- Jira board ID and custom field IDs
- GitLab numeric project ID
- Confluence space key and parent page IDs
- Any non-standard tool configurations

## What Gets Installed

The `.otomate/` directory receives a complete copy of:

| Directory | Contents |
|-----------|----------|
| `.otomate/agents/` | All 10 agent definitions |
| `.otomate/workflows/` | All 13 workflow definitions |
| `.otomate/templates/` | Code scaffolds and doc templates |
| `.otomate/config/` | Config reference and MCP tool inventory |
| `.otomate/docs/` | Full documentation |
| `.otomate/scripts/` | Utility scripts |
| `.otomate/.github/` | Copilot agents, skills, instructions |
| `.otomate/VERSION` | Installed version stamp |

## Versioning

- The `VERSION` file in the Otomate source tracks the current release
- During init, this version is:
  - Written to `.otomate/VERSION` in the target project
  - Recorded as `otomate_version` in `otomate.config.yml`
- Use the **Update** workflow to upgrade later

## MCP Tools Used

`get_file_content`, `search_in_repository`, `get_project_info`

## Duration

~5-10 minutes (mostly interactive Q&A)

## Next Steps

After initialization:
- Use any of the 13 workflows
- Run "Update Otomate" when a new version is available
