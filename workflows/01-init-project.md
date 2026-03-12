# Workflow 01: Initialize Project

**Goal**: Initialize Otomate for a target project — scan its repository structure, auto-detect project details, generate a complete `otomate.config.yml`, and copy the full Otomate system into the project's `.otomate/` directory.

**Trigger**: "Initialize Otomate", "Set up Otomate", "Init project", "Init project at {path}"

**Agents**: Orchestrator → Code Agent, Project Context Agent

**Time**: ~10 minutes (mostly interactive)

## Input

The developer provides a **reference to the project folder** they want to initialize. This workflow can be run from OUTSIDE the target project.

```
REQUIRED: project_path — absolute or relative path to the target project folder

Examples:
  "Init project at /home/dev/my-awesome-api"
  "Initialize Otomate for ../my-awesome-api"
  "Set up Otomate" (defaults to current working directory)

IF no path provided:
  → Ask: "Which project folder do you want to initialize?
          Provide the path (absolute or relative) or press enter for current directory."
  → Default: current working directory
```

## Phase 0: PRE-FLIGHT — Check Initialization Status

Before doing anything else, check if the target project has already been initialized.

```
STEP 1 — Validate project path:
  IF path does not exist:
    → STOP: "The path '{project_path}' does not exist. Please provide a valid project path."
  IF path is not a directory:
    → STOP: "The path '{project_path}' is not a directory."
  IF path is not a git repository (no .git/ folder):
    → WARN: "This directory is not a git repository. Some auto-detection features
             (commit patterns, branch naming) will be limited."
    → Ask: "Continue anyway?"

STEP 2 — Check for existing initialization:
  Look for: {project_path}/.otomate/ directory

  IF .otomate/ EXISTS:
    → Check: {project_path}/.otomate/VERSION
    → Read current version from .otomate/VERSION
    → Read latest version from {otomate_source}/VERSION

    IF versions match:
      → INFORM: "This project is already initialized with Otomate v{version}.
                 Config file: {project_path}/otomate.config.yml
                 Otomate files: {project_path}/.otomate/

                 If you want to update Otomate to the latest version, use:
                 'Update Otomate' workflow instead.

                 If you want to RE-INITIALIZE (overwrite existing config), say:
                 'Force re-initialize Otomate'"
      → STOP (unless developer says force re-initialize)

    IF versions differ:
      → INFORM: "This project has Otomate v{current_version} installed.
                 Latest available version is v{latest_version}.
                 Use 'Update Otomate' to upgrade.
                 Use 'Force re-initialize' to start fresh (will overwrite config)."
      → STOP (unless developer says force re-initialize)

  IF .otomate/ DOES NOT EXIST:
    → Continue to Phase 1 (fresh initialization)

STEP 3 — Handle force re-initialize:
  IF developer requests force re-initialize:
    → WARN: "This will overwrite your existing otomate.config.yml and .otomate/ directory.
             Any customizations you've made to these files will be lost."
    → 🚦 HITL GATE: "Are you sure you want to re-initialize? (yes/no)"
    → IF yes: Continue to Phase 1
    → IF no: STOP
```

## Phase 1: SCAN REPOSITORY

Code Agent reads key files from the **target project** to detect project characteristics:

### Language Detection

```
Check for file extensions and package files:
  - TypeScript: .ts, .tsx files + tsconfig.json
  - JavaScript: .js, .jsx files + package.json (no TypeScript)
  - Java: .java files + pom.xml or build.gradle
  - Python: .py files + requirements.txt or pyproject.toml
  - Go: .go files + go.mod
  - Rust: .rs files + Cargo.toml
  - C#: .csproj, .sln files

Action: Identify primary language
Output: language = "typescript" | "javascript" | "java" | etc.
```

### Framework Detection

```
For TypeScript/JavaScript:
  - NestJS: nest-cli.json, @nestjs imports
  - Express: express in package.json, main server setup
  - Next.js: next.config.js, pages/ directory
  - React: react in package.json, .tsx components
  - Angular: angular.json, @angular imports

For Java:
  - Spring Boot: pom.xml with spring-boot-starter, @SpringBootApplication
  - Spring: gradle build with spring plugins
  - Maven: pom.xml structure

For Python:
  - Django: django in requirements, manage.py
  - Flask: flask in requirements, app.py or wsgi
  - FastAPI: fastapi in requirements

Action: Identify framework
Output: framework = "nestjs" | "spring-boot" | "django" | etc.
```

### Package Manager Detection

```
Check for lock files:
  - npm: package-lock.json
  - yarn: yarn.lock
  - pnpm: pnpm-lock.yaml
  - maven: pom.xml
  - gradle: gradle lock files
  - pip: requirements.txt or Pipfile.lock
  - poetry: poetry.lock
  - cargo: Cargo.lock

Action: Identify package manager
Output: package_manager = "npm" | "maven" | "pip" | etc.
```

### Testing Framework Detection

```
Check config files and imports:
  - jest: jest.config.js, jest.setup.js
  - mocha: .mocharc.json or mocha config
  - pytest: pytest.ini, conftest.py
  - junit: test config in pom.xml
  - unittest: standard Python testing

Action: Identify test framework
Output: test_framework = "jest" | "pytest" | etc.
```

### Linter & Formatter Detection

```
Check for config files:
  - ESLint: .eslintrc.js, .eslintrc.json
  - Prettier: .prettierrc, .prettierrc.json
  - Pylint: .pylintrc
  - Black: pyproject.toml with [tool.black]
  - Checkstyle: checkstyle.xml (Java)

Action: Identify linting tools
Output: linter = "eslint", formatter = "prettier"
```

### Architecture Detection

```
Scan folder structure to map layers:
  TypeScript/NestJS typical:
    src/
      controllers/ → controller layer
      services/ → business logic layer
      repositories/ → data access layer
      entities/ → domain models
      middleware/ → cross-cutting concerns

  Java/Spring typical:
    src/main/java/
      controller/ → controllers
      service/ → services
      repository/ → repositories
      entity/ → entities
      config/ → configuration

  Python/Django typical:
    app/
      views.py → views/controllers
      models.py → entities
      serializers.py → DTOs

Action: Map folder structure to layers
Output: architecture.layers with paths and descriptions
```

### CI/CD Detection

```
Check for:
  - Jenkinsfile: Jenkins configuration
  - .gitlab-ci.yml: GitLab CI configuration
  - .github/workflows: GitHub Actions
  - sonar-project.properties: SonarQube configuration
  - Dockerfile, docker-compose.yml: Docker configuration

Action: Identify CI/CD tools
Output: jenkins.job_name, sonarqube.project_key, etc.
```

## Phase 2: DETECT CONVENTIONS

### Commit Message Pattern

```
Action: Read last 10 commits via GitLab Agent
  Call: search_in_repository(search_term=".*")
  Extract commit messages

Analyze pattern:
  - "PROJ-123: feat: add avatar" → Jira prefix + conventional commits
  - "Add user authentication" → Free-form
  - "fix(auth): handle edge case" → Conventional commits only
  - "#456 Update docs" → Issue number prefix

Output: commit_message.pattern
Default if unclear: "{{key}}: {{title}}\n\n{{description}}"
```

### Branch Naming Convention

```
Action: List existing branches via GitLab Agent
  Analyze names: feature/PROJ-123, fix/PROJ-456, release/v1.0

Pattern detection:
  - feature/, fix/, hotfix/, release/ prefixes
  - Jira key inclusion
  - Slug formatting

Output: branching prefixes
Default: feature/, fix/, hotfix/
```

### Code Style Analysis

```
Read sample code files:
  - Class naming: PascalCase vs camelCase vs snake_case
  - Function naming: camelCase vs snake_case
  - File naming: kebab-case vs snake_case
  - Constant naming: UPPER_SNAKE_CASE vs PascalCase

Compare with linter config (.eslintrc, .pylintrc):
  Extract naming rules

Output: coding_standards.naming conventions
```

## Phase 3: DETECT TOOL CONFIGURATION

### Jira Detection

```
From commit messages:
  Extract Jira project keys: PROJ-123 → project key "PROJ"

If found: Jira is used
  Suggest: "Your commits reference PROJ. Is this the Jira project key?"

From Jenkinsfile/CI config:
  Look for JIRA_PROJECT_KEY environment variable

Action: Extract project key
Output: jira.project_key = "PROJ"

Note: Jira board ID and custom field IDs must be provided manually
```

### GitLab Detection

```
From git remote URL:
  git remote get-url origin
  Parse: https://gitlab.com/orgname/project-name.git
  Extract: project_id from GitLab project settings

Action: Extract project ID (must be numeric)
Output: gitlab.project_id = 12345

Note: User must provide numeric project ID from GitLab UI
```

### Jenkins Detection

```
Check for Jenkinsfile:
  Extract: job name, pipeline stages, environment variables

From CI/CD variables:
  Look for JENKINS_URL, JENKINS_JOB_NAME

Action: Extract job name
Output: jenkins.job_name = "my-awesome-api-build"
```

### SonarQube Detection

```
Check for sonar-project.properties:
  Extract: sonar.projectKey, sonar.sources

From CI pipeline:
  Look for sonar-scanner commands

Action: Extract project key
Output: sonarqube.project_key = "com.org:project"
```

### Confluence Detection

```
From CI/CD variables or config:
  Look for CONFLUENCE_SPACE_KEY

If found:
  → Confluence is likely used
  → Space key can be detected

Note: Page IDs must be provided manually
```

## Phase 4: PRESENT DRAFT CONFIG

Generate complete `otomate.config.yml` and show to developer:

```yaml
# Otomate version that generated this config
otomate_version: "1.0.0"

project:
  name: "my-awesome-api"          ✓ Auto-detected
  description: "REST API..."      ✓ From README.md
  language: "typescript"          ✓ Auto-detected
  framework: "nestjs"             ✓ Auto-detected
  package_manager: "npm"          ✓ Auto-detected

architecture:
  pattern: "clean architecture"   ✓ From folder structure
  layers: [...]                   ✓ Auto-detected

jira:
  project_key: "PROJ"             ✓ From commits
  # board_id: ???                 ⚠ NEEDS INPUT
  # custom field IDs: ???         ⚠ NEEDS INPUT

gitlab:
  project_id: 12345               ⚠ NEEDS INPUT (numeric ID)
  default_branch: "develop"       ✓ Detected

jenkins:
  job_name: "my-awesome-api"      ✓ From Jenkinsfile

sonarqube:
  project_key: "com.org:api"      ✓ From sonar-project.properties

confluence:
  space_key: "ENG"                ⚠ NEEDS INPUT
  # release_notes_parent_page_id  ⚠ NEEDS INPUT
```

### Highlight Missing Fields

Show clearly which sections need developer input:

```
✓ AUTO-DETECTED (8 fields)
⚠ NEEDS MANUAL INPUT (6 fields):
  - jira.board_id: Find in Jira board settings
  - jira.story_point_field: Check Jira project custom fields
  - gitlab.project_id: From GitLab project URL
  - confluence.space_key: From Confluence
  - confluence.release_notes_parent_page_id: Parent page for release notes
  - sonarqube.base_url: SonarQube instance URL

This is NORMAL. Some values can only come from knowing your tools.
```

## Phase 5: 🚦 HITL GATE — Developer Reviews

```
Show developer:
  ← Draft otomate.config.yml
  ← Highlighted sections needing input

Ask: "Does this look right?"

Developer can:
  1. Approve and let me fill in missing values
  2. Correct auto-detected values
  3. Ask questions about any field
  4. Show me where to find missing values

Support multi-round refinement:
  Developer: "The project key is wrong, it should be MYAPP"
  Agent: "Got it, changing PROJ → MYAPP"
  Agent: "For Jira board ID, where should I look?"
  Developer: "Go to https://jira/software/c/projects/MYAPP/boards"
  ...
```

## Phase 6: SAVE CONFIGURATION & INSTALL OTOMATE

```
STEP 1 — Finalize config:
  Ask developer for remaining missing values
  Fill in all required fields
  Add otomate_version field with current version from {otomate_source}/VERSION

STEP 2 — Write otomate.config.yml:
  Save to: {project_path}/otomate.config.yml

STEP 3 — Copy Otomate system into .otomate/ folder:
  Source: {otomate_source}/ (the Otomate repository root)
  Destination: {project_path}/.otomate/

  Copy the following directories and files:
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
    - .git/ directory
    - otomate.config.yml (this is project-specific, already written to project root)
    - .gitattributes (project may have its own)
    - Any temporary or build files

STEP 4 — Write VERSION file:
  Write {otomate_source}/VERSION content to {project_path}/.otomate/VERSION
  This stamps the installed version so the update workflow can compare later.

STEP 5 — Add to .gitignore (suggest):
  Check if {project_path}/.gitignore exists
  Suggest adding:
    # Otomate config (may contain project-specific values)
    # otomate.config.yml

  Note: .otomate/ directory SHOULD be committed so the team shares the same workflows.
  But otomate.config.yml may be project-specific with values that differ per-developer.

STEP 6 — Verify setup:
  Confirm: otomate.config.yml exists at {project_path}/otomate.config.yml
  Confirm: .otomate/ folder structure is complete at {project_path}/.otomate/
  Confirm: .otomate/VERSION matches source VERSION
  Confirm: All required config fields are populated

Show developer:
  ✓ Otomate v{version} is initialized!
  ✓ Config saved to: {project_path}/otomate.config.yml
  ✓ Otomate system installed to: {project_path}/.otomate/
  ✓ Version: {version}
  ✓ Agents loaded: {list}
  ✓ Workflows available: {count}

  Next steps:
    - "Plan epics": Load requirements from Confluence
    - "Implement task": Pick a Jira ticket and start coding
    - "Fix pipeline": Debug a failed build
    - "Update Otomate": Update to latest version when available
```

## Error Handling

### If repo has no detectable structure

```
Sometimes a repo is non-standard or very new.

Action:
  1. Generate MINIMAL config with placeholders
  2. Show: "I couldn't detect all details. Please fill in the blanks:"
  3. Provide clear instructions for each missing field
  4. Save minimal config and offer to refine later
```

### If key files can't be read

```
Example: Jenkinsfile doesn't exist, or .eslintrc not found

Action:
  1. Skip that section
  2. Note clearly: "Couldn't find Jenkinsfile"
  3. Suggest: "Either this project doesn't use it, or it's named differently"
  4. Ask: "Do you use Jenkins for CI/CD?"
  5. Proceed with available information
```

### If Git info is unavailable

```
Example: Repository URL can't be extracted

Action:
  1. Ask developer directly: "What's your GitLab project ID?"
  2. Or: "What's the repository URL?"
  3. Extract needed info from their input
  4. Continue
```

### If project path is invalid

```
Action:
  1. Show: "The path '{project_path}' does not exist or is not accessible."
  2. Ask: "Please provide a valid path to your project directory."
  3. Suggest: Use absolute paths for clarity (e.g., /home/dev/my-project)
```

### If .otomate copy fails

```
Action:
  1. Show: "Failed to copy Otomate files to {project_path}/.otomate/"
  2. Show: Specific error (permission denied, disk full, etc.)
  3. Suggest: "Try manually: cp -r {otomate_source}/* {project_path}/.otomate/"
  4. Offer: "Continue without .otomate/ copy? (config will still be created)"
```

## Success Criteria

✓ Config file is complete and valid
✓ All required fields are populated
✓ Optional fields have sensible defaults
✓ Developer understands what each field means
✓ Developer feels confident about the configuration
✓ .otomate/ directory is fully populated with latest Otomate version
✓ VERSION file is stamped in .otomate/
✓ Next workflow can proceed without additional setup

---

**Duration**: 5-10 minutes (mostly auto-detection + 2-3 minutes Q&A)

**What It Creates**:
- `otomate.config.yml` — project-specific configuration
- `.otomate/` — complete Otomate system (agents, workflows, templates, docs, skills)
- `.otomate/VERSION` — installed version stamp

**Next Workflow**: Any of the remaining workflows (02-13)

**Related**:
- docs/onboarding.md (user guide)
- config/otomate.config.example.yml (template)
- Workflow 13: Update (to upgrade .otomate/ to latest version)
