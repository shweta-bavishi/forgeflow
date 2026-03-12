---
name: init-project
description: "Initialize Otomate for a project. Scans repository structure, auto-detects language, framework, architecture, CI/CD tools, and generates otomate.config.yml."
---

# Skill: Initialize Project

Scan a repository, auto-detect project characteristics, and generate a complete `otomate.config.yml`.

## Phase 1: SCAN REPOSITORY

### Language Detection

```
Check file extensions and package files:
  TypeScript → .ts/.tsx + tsconfig.json
  JavaScript → .js/.jsx + package.json (no TS)
  Java → .java + pom.xml or build.gradle
  Python → .py + requirements.txt or pyproject.toml
  Go → .go + go.mod
  Rust → .rs + Cargo.toml
  C# → .csproj, .sln

Call: get_file_content("package.json") or get_file_content("pom.xml") etc.
Call: search_in_repository("tsconfig") to verify TypeScript
```

### Framework Detection

```
TypeScript/JS: NestJS (nest-cli.json, @nestjs), Express (express in deps),
  Next.js (next.config), React (.tsx components), Angular (angular.json)
Java: Spring Boot (@SpringBootApplication, spring-boot-starter),
  Maven (pom.xml), Gradle (build.gradle)
Python: Django (manage.py, django in deps), Flask (flask in deps),
  FastAPI (fastapi in deps)

Call: get_file_content for framework config files
Call: search_in_repository for framework-specific imports
```

### Package Manager Detection

```
Lock file detection:
  npm → package-lock.json     yarn → yarn.lock
  pnpm → pnpm-lock.yaml       maven → pom.xml
  gradle → gradle.lockfile     pip → requirements.txt
  poetry → poetry.lock         cargo → Cargo.lock
```

### Testing Framework Detection

```
Config file detection:
  jest → jest.config.js        mocha → .mocharc.json
  pytest → pytest.ini, conftest.py  junit → test in pom.xml
```

### Linter & Formatter Detection

```
Config file detection:
  ESLint → .eslintrc.js/.json    Prettier → .prettierrc
  Pylint → .pylintrc              Black → [tool.black] in pyproject.toml
  Checkstyle → checkstyle.xml
```

### Architecture Detection

```
Scan folder structure to map layers:

TypeScript/NestJS:
  src/controllers/ → controller layer
  src/services/ → business logic
  src/repositories/ → data access
  src/entities/ → domain models

Java/Spring:
  src/main/java/controller/ → controllers
  src/main/java/service/ → services
  src/main/java/repository/ → repositories

Python/Django:
  app/views.py → views
  app/models.py → models

Call: search_in_repository to list directory patterns
Call: get_file_content for key files (app.module.ts, main.ts, etc.)
```

### CI/CD Detection

```
Jenkinsfile → Jenkins config
.gitlab-ci.yml → GitLab CI
sonar-project.properties → SonarQube config
Dockerfile → Docker setup

Call: get_file_content for each CI config file found
Extract: job names, project keys, environment variables
```

## Phase 2: DETECT CONVENTIONS

### Commit Message Pattern

```
Analyze recent commit messages for pattern:
  "PROJ-123: feat: add avatar" → Jira prefix + conventional
  "Add user authentication" → Free-form
  "fix(auth): handle edge case" → Conventional commits only

Output: commit_message.pattern
Default: "{{key}}: {{title}}\n\n{{description}}"
```

### Branch Naming Convention

```
Analyze existing branch names for prefixes:
  feature/PROJ-123, fix/PROJ-456, release/v1.0

Output: branching prefixes (feature/, fix/, hotfix/, release/v)
```

### Code Style Analysis

```
Read 3-5 sample source files:
  Detect: class naming (PascalCase), function naming (camelCase),
  file naming (kebab-case), constant naming (UPPER_SNAKE_CASE)

Cross-reference with linter config for confirmation
```

## Phase 3: DETECT TOOL CONFIGURATION

```
Jira: Extract project key from commit messages (PROJ-123 → "PROJ")
GitLab: Extract project ID from remote URL (needs manual confirmation)
Jenkins: Extract job name from Jenkinsfile
SonarQube: Extract project key from sonar-project.properties
Confluence: Extract space key from CI variables (often manual)
```

## Phase 4: PRESENT DRAFT CONFIG

```
Show generated config with status:

project:
  name: "my-awesome-api"          ✓ Auto-detected
  language: "typescript"           ✓ Auto-detected
  framework: "nestjs"              ✓ Auto-detected

jira:
  project_key: "PROJ"             ✓ From commits
  board_id: ???                   ⚠ NEEDS INPUT

gitlab:
  project_id: ???                 ⚠ NEEDS INPUT (numeric ID)
  default_branch: "develop"       ✓ Detected
```

Highlight: ✓ AUTO-DETECTED vs ⚠ NEEDS MANUAL INPUT with guidance for each.

## Phase 5: 🚦 HITL GATE — Developer Reviews

```
Show draft config + missing fields

Developer can:
  1. Approve and fill missing values
  2. Correct auto-detected values
  3. Ask questions about any field
  4. Point to where missing values can be found

Support multi-round refinement until developer is satisfied
```

## Phase 6: SAVE CONFIGURATION

```
1. Finalize config with developer's input
2. Write otomate.config.yml to project root
3. Verify: config exists, all required fields populated
4. Show:
   ✓ Otomate initialized!
   ✓ Config saved to otomate.config.yml
   → Next: try any workflow (plan epics, implement task, etc.)
```

## Error Handling

```
Non-standard repo → generate minimal config with clear placeholders
Key files unreadable → skip section, note clearly, ask developer
Git info unavailable → ask developer directly for project details
```
