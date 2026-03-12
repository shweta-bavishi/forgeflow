# Workflow: Initialize Project

**Trigger:** "Initialize Otomate", "Set up Otomate", "Init project"

## What It Does

Scans your repository structure, auto-detects language, framework, architecture, CI/CD tools, and coding conventions, then generates a complete `otomate.config.yml`.

## How to Use

1. Select **Otomate** agent in Copilot Chat
2. Say: **"Initialize Otomate"**
3. Otomate scans your repo and presents a draft config
4. Review and fill in any fields marked ⚠ NEEDS INPUT
5. Approve → config saved to project root

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

## MCP Tools Used

`get_file_content`, `search_in_repository`, `get_project_info`

## Duration

~5-10 minutes (mostly interactive Q&A)

## Next Steps

After initialization, use any of the 11 workflows.
