# Otomate Onboarding Guide

Welcome! This guide walks you through using Otomate for the first time.

## What is Otomate?

Otomate is an AI-powered assistant that automates your development workflow. It runs inside your IDE's Copilot Chat and can:

- Plan epics and tasks from requirements
- Generate production-ready code
- Create branches, commits, and merge requests
- Diagnose and fix pipeline failures
- Fix code quality issues
- Create releases and documentation

## Your First 10 Minutes

### 1. Initialize Your Project (2 minutes)

Open Copilot Chat and say:

```
Initialize Otomate
```

Otomate will scan your repository, detect your technology stack, and create a configuration file. Review it and fill in any missing values (like Jira project key or GitLab project ID).

### 2. Try Planning Tasks (3 minutes)

If you have an epic in Jira:

```
Plan dev tasks for PROJ-100
```

Otomate will read the epic, analyze your codebase, and create a detailed breakdown of development tasks.

### 3. Implement a Task (5 minutes)

Pick a task and say:

```
Implement PROJ-123
```

Otomate will:
1. Read the task requirements
2. Show you an implementation plan
3. Generate complete code files
4. Ask for your review
5. Create a branch and merge request

## Available Workflows

### Workflow 1: Initialize Project
```
"Initialize Otomate"
```
Scans repo, creates config file. Run once per project.

### Workflow 2: Plan Epics
```
"Plan epics from Confluence page 12345"
```
Parses requirements page, creates Jira epics.

### Workflow 3: Plan Dev Tasks
```
"Plan dev tasks for PROJ-100"
```
Breaks an epic into detailed development tasks.

### Workflow 4: Implement Dev Task
```
"Implement PROJ-123"
```
Generates code, tests, creates branch and MR.

### Workflow 5: Fix Pipeline
```
"Fix pipeline"
```
Diagnoses Jenkins build failures, suggests fixes.

### Workflow 6: Fix Sonar Issues
```
"Fix sonar issues"
```
Analyzes SonarQube report, generates quality fixes.

### Workflow 7: Create Release Build
```
"Create release build for MR !42"
```
Validates MR, guides merge and tag creation.

### Workflow 8: Create Release Note
```
"Create release note for v2.4.1"
```
Generates and publishes Confluence release note.

## Tips for Best Results

### Be Specific
- Good: "Implement PROJ-123"
- Better: "Implement PROJ-123, follow the pattern in user.service.ts"

### Review Plans Carefully
Otomate shows you a plan before executing. Take time to review — modifications here save rework later.

### Use Natural Language
You don't need exact trigger phrases. Otomate understands variations:
- "Pick up PROJ-123" = "Implement PROJ-123"
- "Debug the build" = "Fix pipeline"
- "Help with code quality" = "Fix sonar issues"

### Keep Config Updated
When your project changes (new architecture layers, different naming conventions), update `otomate.config.yml` to get better code generation.

### Ask for Help
If stuck, just say: "Help" and Otomate will show available options.

## FAQ

**Q: Does Otomate push code automatically?**
No. Every push requires your explicit approval. Otomate always asks before pushing.

**Q: Can Otomate break my code?**
Otomate generates code but never modifies your local files directly. It commits to GitLab via API. You always review before merging.

**Q: What if the generated code is wrong?**
Tell Otomate what's wrong. It will iterate: "The error handling needs to use our custom exception class." Otomate will adjust.

**Q: Does it work with my language/framework?**
Otomate supports any language and framework. Code generation quality is best for TypeScript/NestJS (built-in templates), but it adapts to any project by reading your existing code patterns.

**Q: Can I use it for just one workflow?**
Absolutely. Use only the workflows you need. Each is independent.

**Q: What data does Otomate access?**
Only what's in your config and what the MCP tools provide. It reads Jira issues, GitLab repos, Confluence pages, Jenkins logs, and SonarQube reports — all through your authenticated API tokens.

## Next Steps

1. Run all 8 workflows at least once to see what they do
2. Customize `otomate.config.yml` for your team's conventions
3. Share Otomate with your team
4. Add custom scaffold templates for your project patterns
5. Provide feedback to improve Otomate

---

**Need help?** See troubleshooting.md | **Want to extend?** See contributing.md
