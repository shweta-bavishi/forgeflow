# Otomate Configuration Reference

Complete reference for `otomate.config.yml`.

## Config File Location

The config file must be at the **project root**: `./otomate.config.yml`

Otomate will not execute any workflow (except `init-project`) without this file.

## Section Reference

### `project` (REQUIRED)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Short project identifier | `"my-awesome-api"` |
| `description` | string | Human-readable description | `"REST API for user profiles"` |
| `team` | string | Team name | `"backend-squad"` |
| `language` | string | Primary language | `"typescript"` / `"java"` / `"python"` / `"go"` |
| `framework` | string | Framework used | `"nestjs"` / `"spring-boot"` / `"django"` |
| `runtime` | string | Runtime + version | `"node.js 20"` |
| `package_manager` | string | Package manager | `"npm"` / `"maven"` / `"pip"` |
| `repository_url` | string | Git repository URL | `"https://gitlab.com/org/repo.git"` |

### `architecture`

| Field | Type | Description |
|-------|------|-------------|
| `pattern` | string | Architecture pattern (`"clean architecture"`, `"MVC"`, `"hexagonal"`) |
| `layers` | list | Layer definitions with `name`, `path`, `description` |
| `key_files` | list | Important files agents should read for context |

### `coding_standards`

| Field | Type | Description |
|-------|------|-------------|
| `style_guide` | string | Style guide reference (e.g., `"Airbnb TypeScript"`) |
| `linter` | string | Linter tool (`"eslint"`, `"pylint"`) |
| `linter_config` | string | Linter config file path |
| `formatter` | string | Formatter tool (`"prettier"`, `"black"`) |
| `test_framework` | string | Test framework (`"jest"`, `"pytest"`, `"junit"`) |
| `test_pattern` | string | Glob pattern for test files |
| `coverage_threshold` | number | Minimum coverage % (e.g., `80`) |
| `naming` | object | Naming conventions for files, classes, functions, etc. |
| `rules` | list | Project-specific coding rules |

### `jira` (REQUIRED)

| Field | Type | Description |
|-------|------|-------------|
| `project_key` | string | Jira project key (e.g., `"PROJ"`) |
| `board_id` | number | Board ID for sprint operations |
| `epic_issue_type` | string | Epic issue type name |
| `story_issue_type` | string | Story issue type name |
| `task_issue_type` | string | Task issue type name |
| `story_point_field` | string | Custom field ID for story points |
| `sprint_field` | string | Custom field ID for sprint |
| `statuses` | object | Status names: `todo`, `in_progress`, `in_review`, `qa`, `done` |
| `labels` | list | Default labels for Otomate-created issues |

### `gitlab` (REQUIRED)

| Field | Type | Description |
|-------|------|-------------|
| `project_id` | number | Numeric GitLab project ID |
| `default_branch` | string | Default dev branch (`"develop"` or `"main"`) |
| `release_branch_pattern` | string | Release branch pattern |
| `branching` | object | Branch prefixes: `feature_prefix`, `bugfix_prefix`, etc. |
| `merge_request` | object | MR defaults: `target_branch`, `squash_commits`, `delete_source_branch` |
| `commit_message` | object | Commit message pattern with `{{key}}`, `{{title}}`, `{{description}}` |

### `confluence`

| Field | Type | Description |
|-------|------|-------------|
| `space_key` | string | Confluence space key |
| `release_notes_parent_page_id` | number | Parent page for release notes |
| `requirements_page_id` | number | Requirements page (optional) |

### `jenkins`

| Field | Type | Description |
|-------|------|-------------|
| `job_name` | string | Build/test job name |
| `deploy_job_name` | string | Deploy job name |
| `base_url` | string | Jenkins instance URL |

### `sonarqube`

| Field | Type | Description |
|-------|------|-------------|
| `project_key` | string | SonarQube project key |
| `quality_gate` | string | Quality gate name |
| `base_url` | string | SonarQube instance URL |

### `nexusiq`

| Field | Type | Description |
|-------|------|-------------|
| `application_name` | string | Nexus IQ application name |
| `organization` | string | Nexus IQ organization (optional) |

### `zephyr`

| Field | Type | Description |
|-------|------|-------------|
| `test_issue_type` | string | Issue type for test cases |
| `test_link_type` | string | Link type connecting tests to stories |
| `labels` | list | Labels for generated tests |

### `auto_review`

| Field | Type | Description |
|-------|------|-------------|
| `dimensions` | object | Enable/disable review dimensions |
| `coverage_threshold` | number | Coverage threshold for review |
| `auto_post` | boolean | Auto-post review (recommend: `false`) |
| `forbidden_patterns` | list | Patterns to flag in code review |

### `approval_gates`

| Field | Type | Description |
|-------|------|-------------|
| `always_require_approval` | list | Actions that always need HITL approval |
| `can_auto_approve_if` | list | Actions that can auto-approve under conditions |

### `integrations`

| Field | Type | Description |
|-------|------|-------------|
| `jira.url` | string | Jira instance URL |
| `gitlab.url` | string | GitLab instance URL |
| `confluence.url` | string | Confluence instance URL |
| `jenkins.url` | string | Jenkins instance URL |
| `sonarqube.url` | string | SonarQube instance URL |
| `nexusiq.url` | string | Nexus IQ instance URL |

**Note:** Never commit actual credentials. Use environment variables or Copilot Chat secrets.
