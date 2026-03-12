# Workflow 01: Initialize Project

**Goal**: Scan a repository structure, auto-detect project details, and generate a complete `otomate.config.yml` file tailored to the project.

**Trigger**: "Initialize Otomate", "Set up Otomate", "Init project"

**Agents**: Orchestrator → Code Agent, Project Context Agent

**Time**: ~10 minutes (mostly interactive)

## Phase 1: SCAN REPOSITORY

Code Agent reads key files to detect project characteristics:

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

## Phase 6: SAVE CONFIGURATION

```
STEP 1 — Finalize config:
  Ask developer for remaining missing values
  Fill in all required fields

STEP 2 — Write otomate.config.yml:
  Save to project root: otomate.config.yml

STEP 3 — Create .otomate/ folder structure:
  mkdir .otomate/
  Copy agents/ folder from template
  Copy workflows/ folder from template
  Copy templates/ folder from template
  Copy config/ folder from template (config ref, tools reference)

STEP 4 — Add to .gitignore:
  Check if otomate.config.yml should be in .gitignore
  (Yes if it contains secrets or is project-specific)

STEP 5 — Verify setup:
  Confirm: otomate.config.yml exists in root
  Confirm: .otomate/ folder structure is complete
  Confirm: All required fields are populated

Show developer:
  ✓ Otomate is initialized!
  ✓ Config saved to: otomate.config.yml
  ✓ Agents loaded: {list}
  ✓ Next: Try a workflow!

  Example next steps:
    - "Plan epics": Load requirements from Confluence
    - "Implement task": Pick a Jira ticket and start coding
    - "Fix pipeline": Debug a failed build
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

## Success Criteria

✓ Config file is complete and valid
✓ All required fields are populated
✓ Optional fields have sensible defaults
✓ Developer understands what each field means
✓ Developer feels confident about the configuration
✓ Next workflow can proceed without additional setup

---

**Duration**: 5-10 minutes (mostly auto-detection + 2-3 minutes Q&A)

**What It Creates**: `otomate.config.yml` + `.otomate/` directory structure

**Next Workflow**: Any of the 7 remaining workflows (02-08)

**Related**: docs/onboarding.md (user guide), config/otomate.config.example.yml (template)
