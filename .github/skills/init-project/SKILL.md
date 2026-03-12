---
name: init-project
description: "Initialize Otomate for a project. Can be run from outside the target project by providing a project path. Scans repository structure, auto-detects language, framework, architecture, CI/CD tools, generates otomate.config.yml, and copies the complete Otomate system into the project's .otomate/ directory with version stamping."
---

# Skill: Initialize Project

Initialize Otomate for a target project — scan its repository, auto-detect project characteristics, generate `otomate.config.yml`, and install the full Otomate system into `.otomate/`.

## Input

```
REQUIRED: project_path — path to the target project folder

IF developer provides a path:
  → Use that path as the target project
  Examples: "Init project at /home/dev/my-api", "Init ../my-api"

IF no path provided:
  → Ask: "Which project folder do you want to initialize?
          Provide the path or press enter for current directory."
  → Default: current working directory

Store: otomate_source = the directory containing this Otomate installation
       (where VERSION, agents/, workflows/, etc. live)
```

## Phase 0: PRE-FLIGHT — Check Initialization Status

```
STEP 1 — Validate project path:
  IF path does not exist → STOP: "Path does not exist."
  IF path is not a directory → STOP: "Path is not a directory."
  IF no .git/ folder → WARN: "Not a git repo. Some features will be limited. Continue?"

STEP 2 — Check for existing initialization:
  Look for: {project_path}/.otomate/ directory

  IF .otomate/ EXISTS:
    Read: {project_path}/.otomate/VERSION → current_version
    Read: {otomate_source}/VERSION → latest_version

    IF versions match:
      → INFORM: "Already initialized with Otomate v{version}.
                 Use 'Update Otomate' to upgrade, or
                 'Force re-initialize' to start fresh."
      → STOP (unless force re-initialize requested)

    IF versions differ:
      → INFORM: "Otomate v{current_version} installed.
                 Latest is v{latest_version}.
                 Use 'Update Otomate' to upgrade."
      → STOP (unless force re-initialize requested)

  IF .otomate/ DOES NOT EXIST:
    → Continue to Phase 1

STEP 3 — Handle force re-initialize:
  IF developer says "force re-initialize":
    → WARN: "This will overwrite existing config and .otomate/ directory."
    → 🚦 GATE: "Are you sure? (yes/no)"
    → IF yes: Continue to Phase 1
    → IF no: STOP
```

## Phase 1: SCAN REPOSITORY

### Language Detection

```
Check file extensions and package files in {project_path}:
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
Scan folder structure to map layers in {project_path}:

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
Show generated config with status indicators:

# Otomate version
otomate_version: "1.0.0"

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

Highlight: ✓ AUTO-DETECTED vs ⚠ NEEDS MANUAL INPUT with guidance for each.
```

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

## Phase 6: SAVE CONFIGURATION & INSTALL OTOMATE

```
1. Finalize config with developer's input
   Add otomate_version from {otomate_source}/VERSION

2. Write otomate.config.yml to {project_path}/otomate.config.yml

3. Copy full Otomate system to {project_path}/.otomate/:
   Source: {otomate_source}/
   Copy:
     agents/         → .otomate/agents/
     workflows/      → .otomate/workflows/
     templates/      → .otomate/templates/
     config/         → .otomate/config/
     docs/           → .otomate/docs/
     scripts/        → .otomate/scripts/
     .github/        → .otomate/.github/
     VERSION         → .otomate/VERSION
     README.md       → .otomate/README.md
     SETUP.md        → .otomate/SETUP.md
     ARCHITECTURE.md → .otomate/ARCHITECTURE.md

   DO NOT copy: .git/, otomate.config.yml, .gitattributes

4. Stamp version: write VERSION to {project_path}/.otomate/VERSION

5. Suggest .gitignore additions if appropriate

6. Verify:
   ✓ otomate.config.yml exists at project root
   ✓ .otomate/ is complete
   ✓ .otomate/VERSION matches source VERSION
   ✓ All required config fields populated

7. Show:
   ✓ Otomate v{version} initialized!
   ✓ Config: {project_path}/otomate.config.yml
   ✓ System: {project_path}/.otomate/
   → Next: try any workflow
```

## Error Handling

```
Invalid path → STOP with clear message, ask for valid path
Non-standard repo → generate minimal config with placeholders
Key files unreadable → skip section, note clearly, ask developer
Git info unavailable → ask developer directly for project details
Already initialized → inform and suggest 'Update Otomate' or 'Force re-initialize'
Copy failure → show error, offer manual copy instructions
```
