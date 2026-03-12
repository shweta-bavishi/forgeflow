# Configuration Reference

Complete reference for `otomate.config.yml`. Every field explained with type, default, and example.

## File Location

`otomate.config.yml` must be in the **project root directory** (same level as `package.json`, `pom.xml`, etc.).

## Section: project

Project identity and technology stack.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | — | Short project identifier (e.g., "my-awesome-api") |
| `description` | string | No | — | Human-readable project description |
| `team` | string | No | — | Team name responsible for this project |
| `language` | string | Yes | — | Primary language: typescript, java, python, go, rust |
| `framework` | string | Yes | — | Framework: nestjs, spring-boot, django, fastapi, express |
| `runtime` | string | No | — | Runtime version: "node.js 20", "java 17", "python 3.11" |
| `package_manager` | string | Yes | — | Package manager: npm, yarn, pnpm, maven, gradle, pip |
| `repository_url` | string | No | — | Git repository URL |

## Section: architecture

Project architecture details used by Code Agent.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `pattern` | string | No | — | Architecture pattern: "clean architecture", "MVC", "hexagonal" |
| `layers` | array | No | [] | Architecture layers (see below) |
| `key_files` | array | No | [] | Important files for understanding project |

### Layer Definition

Each layer in `architecture.layers`:

```yaml
layers:
  - name: "controllers"        # Layer name
    path: "src/controllers"     # Directory path
    description: "HTTP handlers" # What this layer does
```

## Section: coding_standards

Code conventions enforced by Code Agent.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `style_guide` | string | No | — | Style guide reference (Airbnb, Google, etc.) |
| `linter` | string | No | — | Linter tool name (eslint, pylint, checkstyle) |
| `linter_config` | string | No | — | Linter config file path |
| `formatter` | string | No | — | Formatter tool name (prettier, black) |
| `formatter_config` | string | No | — | Formatter config file path |
| `test_framework` | string | No | — | Test framework (jest, pytest, junit) |
| `test_config` | string | No | — | Test config file path |
| `test_pattern` | string | No | — | Glob pattern for test files |
| `coverage_threshold` | number | No | 80 | Minimum code coverage percentage |
| `naming` | object | No | {} | Naming conventions (see below) |
| `rules` | array | No | [] | Project-specific coding rules as strings |

### Naming Conventions

```yaml
naming:
  files: "kebab-case"            # user-service.ts
  directories: "kebab-case"      # user-service/
  classes: "PascalCase"          # UserService
  functions: "camelCase"         # getUserById
  constants: "UPPER_SNAKE_CASE"  # MAX_FILE_SIZE
  interfaces: "PascalCase"       # IUserRepository
  variables: "camelCase"         # userId
```

## Section: jira

Jira integration configuration.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_key` | string | Yes | — | Jira project key (e.g., "PROJ") |
| `board_id` | number | No | — | Jira board ID for sprint operations |
| `epic_issue_type` | string | No | "Epic" | Issue type name for Epics |
| `story_issue_type` | string | No | "Story" | Issue type name for Stories |
| `task_issue_type` | string | No | "Task" | Issue type name for Tasks |
| `bug_issue_type` | string | No | "Bug" | Issue type name for Bugs |
| `story_point_field` | string | No | — | Custom field ID for story points |
| `sprint_field` | string | No | — | Custom field ID for sprint |
| `statuses` | object | Yes | — | Status name mapping (see below) |
| `labels` | array | No | [] | Default labels for new issues |

### Status Mapping

```yaml
statuses:
  todo: "To Do"           # Initial status
  in_progress: "In Progress"  # Work started
  in_review: "In Review"      # Code review
  qa: "QA"                    # Quality testing
  done: "Done"                # Completed
```

**Finding custom field IDs**: Go to Jira > Project Settings > Fields. Hover over the field name to see the ID in the URL or tooltip.

## Section: gitlab

GitLab integration configuration.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_id` | number | Yes | — | Numeric GitLab project ID |
| `default_branch` | string | No | "develop" | Default development branch |
| `release_branch_pattern` | string | No | "release/v*" | Pattern for release branches |
| `branching` | object | No | — | Branch naming prefixes |
| `merge_request` | object | No | — | MR conventions |
| `commit_message` | object | No | — | Commit message format |

### Branch Naming

```yaml
branching:
  feature_prefix: "feature/"    # feature/PROJ-123-description
  bugfix_prefix: "fix/"         # fix/PROJ-123-description
  hotfix_prefix: "hotfix/"      # hotfix/PROJ-123-description
  release_prefix: "release/v"   # release/v1.2.0
  chore_prefix: "chore/"        # chore/PROJ-123-description
```

### Merge Request Settings

```yaml
merge_request:
  target_branch: "develop"          # Default MR target
  squash_commits: true              # Squash on merge
  delete_source_branch: true        # Delete branch after merge
  auto_remove_source_branch: true   # Auto-cleanup
```

### Commit Message Pattern

```yaml
commit_message:
  pattern: "{{key}}: {{title}}\n\n{{description}}"
```

Placeholders: `{{key}}` = Jira key, `{{title}}` = issue title, `{{description}}` = details

## Section: confluence

Confluence integration configuration.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `space_key` | string | Yes | — | Confluence space key (e.g., "ENG") |
| `release_notes_parent_page_id` | string/number | No | — | Parent page ID for release notes |
| `requirements_page_id` | string/number | No | null | Requirements page ID |
| `template_page_id` | string/number | No | null | Template page ID |

## Section: jenkins

Jenkins integration configuration.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `job_name` | string | Yes | — | Build/test job name |
| `deploy_job_name` | string | No | — | Deployment job name |
| `base_url` | string | No | — | Jenkins instance URL |

## Section: sonarqube

SonarQube integration configuration.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_key` | string | Yes | — | SonarQube project key |
| `quality_gate` | string | No | "Sonar way" | Quality gate name |
| `base_url` | string | No | — | SonarQube instance URL |

## Section: scaffolds

Template mappings for code generation.

```yaml
scaffolds:
  typescript:
    - name: "controller"
      template: "templates/scaffolds/typescript/controller.hbs"
      output_pattern: "src/controllers/{{kebab name}}.controller.ts"
```

## Section: approval_gates

HITL gate configuration.

```yaml
approval_gates:
  always_require_approval:
    - "create_release_build"
    - "push_code_to_remote"
    - "update_jira_status_to_done"
  can_auto_approve_if:
    - "sonar_fix_auto_fixable_issues"
```

## Section: integrations

Tool URLs (credentials go in environment variables).

```yaml
integrations:
  jira:
    url: "https://jira.your-org.com"
  gitlab:
    url: "https://gitlab.com"
  confluence:
    url: "https://confluence.your-org.com"
  jenkins:
    url: "https://jenkins.your-org.com"
  sonarqube:
    url: "https://sonarqube.your-org.com"
```

## Tips

**Multi-project setups**: Each project has its own `otomate.config.yml`. Share common settings via template.

**Minimal config**: Only `project.name`, `project.language`, `jira.project_key`, and `gitlab.project_id` are truly required. Everything else has defaults or is optional.

**Validation**: Run `01-init-project` to auto-detect and validate your config.

---

**Related**: config/otomate.config.example.yml (template), SETUP.md (installation guide)
