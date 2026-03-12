# MCP Tools Reference — ForgeFlow Complete Tool Inventory

This document catalogs all 113 MCP tools available from the ce-mcp server that ForgeFlow can use. Tools are organized by domain and include usage notes.

## GitLab Tools (19 tools)

All GitLab operations use the GitLab API via these MCP tools.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `get_project_info` | Get GitLab project detailed information (name, ID, description, visibility, etc.) | Start of any workflow requiring project metadata; needed before creating MRs |
| `get_file_content` | Get file content from project repository | Reading source files for code analysis, configuration files, etc. |
| `commit_and_push_file` | Commit file changes directly to GitLab repository (no MR) | Committing fixes to existing branches; committing config changes |
| `commit_file_and_create_mr` | **RECOMMENDED** — Commit file AND create Merge Request in one call (implicitly creates branch) | Standard code workflow: implement → commit → create MR in one step |
| `create_merge_request` | Create Merge Request (when MR needs to be created separately from commits) | Less common; use `commit_file_and_create_mr` instead |
| `list_project_merge_requests` | List all Merge Requests in the project | Finding an MR to review, check, or release |
| `list_project_issues` | List all project Issues | Discovering GitLab-native issues (less common in Jira-first setups) |
| `get_project_pipelines` | Get project CI/CD Pipelines (list of executions with status) | Checking pipeline status before releasing; diagnosing failed pipelines |
| `search_in_repository` | Search for keywords/patterns in repository code | Finding usage of specific functions, constants, or patterns |
| `search_gitlab_projects` | Search for GitLab projects by name/keyword | Discovering projects; less commonly used |
| `list_user_projects` | List user's projects | Discovering available projects for user context |
| `list_project_merge_requests` | List MRs with filters (status, author, etc.) | Filtering MRs by status; finding open MRs |
| `review_merge_request` | Review MR comprehensively (extracts: changes, commits, approvals, pipeline status) | Analyzing an MR before release; quality checks |
| `review_and_comment_mr` | Review MR AND post results as comment in one call (all-in-one) | Code review workflows; posting findings back to MR |
| `post_mr_review_comment` | Post review results as comment to MR | Adding feedback comments after analysis |
| `get_gitlab_ci_guide` | Get GitLab CI Pipeline Templates usage guide | Learning about available CI/CD templates |
| `generate_gitlab_ci_config` | Generate GitLab CI configuration file (.gitlab-ci.yml) | Creating or updating CI/CD pipeline definitions |
| `explain_gitlab_ci_parameter` | Explain specific GitLab CI configuration parameters | Understanding what a specific CI parameter does |
| `list_available_templates` | List all available GitLab CI template files | Discovering reusable CI/CD template patterns |

### GitLab Usage Patterns

**Pattern: Implementing and Creating MR (used in implement-dev-task, fix-pipeline, sonar-fix workflows)**
```
1. get_file_content → read existing file for context
2. [Code Agent generates changes]
3. commit_file_and_create_mr → commit + create MR in one atomic operation
   (Note: This implicitly creates branch; no separate branch creation tool exists)
```

**Pattern: Code Review**
```
1. review_merge_request → analyze MR comprehensively
2. review_and_comment_mr → post findings as comment in MR
   OR post_mr_review_comment → post manual findings
```

**Critical Note**: GitLab MCP tools do NOT include explicit tools for:
- Branch creation (use `commit_file_and_create_mr` which creates branches implicitly)
- Merge operation (use GitLab UI or manual CLI)
- Cherry-pick (use GitLab UI or manual CLI)
- Tag creation (use GitLab UI or manual CLI)

For these operations, workflows must guide the developer or use the Release Ticket tools.

---

## Jira Tools (12 tools)

All Jira operations for issue management and tracking.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `get_jira_issue` | Get Jira issue details (sync operation) | Quick fetch of issue basic info (title, status, assignee) |
| `get_jira_issue_detail` | Get **comprehensive** Jira issue details (more data than `get_jira_issue`) | When you need full issue context: description, acceptance criteria, comments, links |
| `get_jira_project_info` | Get detailed Jira project information (issue types, field config, etc.) | **REQUIRED** before creating any issues; fetches valid issue types and field IDs |
| `create_jira_issue` | Create a Jira issue (sync operation) | Creating tasks, stories, bugs; **requires calling `get_jira_project_info` first** |
| `create_jira_subtask` | Create a Jira Subtask under a parent issue | Breaking down complex tasks into subtasks |
| `create_epic_with_issues` | Create Epic AND optionally create child issues (Stories/Tasks) in one call | **POWERFUL tool for plan-epics and plan-dev-tasks workflows** — use this instead of creating epic + issues separately |
| `update_jira_issue` | Update an existing Jira issue (status, fields, etc.) | Transitioning issues (To Do → In Progress → Done); updating story points; closing issues |
| `search_jira_issues` | Search Jira issues using JQL (Jira Query Language) | Finding issues matching criteria; discovering related issues |
| `link_issues` | Create a link between two Jira issues (Relates, Blocks, Is-blocked-by, etc.) | Linking parent → child, epic → story, task → task dependencies |
| `move_issue_to_sprint` | Move a Jira issue to a specific sprint | Adding issues to upcoming sprints during planning |
| `list_jira_projects` | List accessible Jira projects (sync) | Discovering available projects |
| `get_project_sprints` | Get all sprints for a project (across all boards) | Listing available sprints for planning |

### Jira Usage Patterns

**Critical Pattern: Creating Issues (ALWAYS follow this order)**
```
1. get_jira_project_info (REQUIRED FIRST)
   → Fetches: valid issue types, field configuration, custom field IDs
2. create_jira_issue or create_epic_with_issues
   → Now you have validated issue types and field names
```

**Pattern: Creating Epic with Child Stories (plan-epics workflow)**
```
1. get_jira_project_info
2. create_epic_with_issues
   → Single call that creates: Epic + all linked child Stories/Tasks
   → Much more efficient than creating epic then linking issues separately
```

**Pattern: Transitioning Issues**
```
1. get_jira_issue_detail (to see current status and available transitions)
2. update_jira_issue with transition field
   → Respect config.jira.statuses for valid status names
```

**Dependency Linking**
```
link_issues parameters:
- issue_key_1, issue_key_2
- link_type: "Relates" / "Blocks" / "is-blocked-by" / "relates to"
```

---

## Confluence Tools (9 tools)

All Confluence operations for documentation and requirements management.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `get_confluence_page` | Get Confluence page details by ID or title | Fetching a single page; minimal overhead |
| `get_confluence_page_full_content` | Get **complete** page content without truncation | **REQUIRED for plan-epics workflow** — use this instead of `get_confluence_page` when parsing detailed requirements |
| `get_confluence_space_pages` | Get pages in a Confluence space (paginated list) | Discovering pages in a space; listing requirements |
| `get_page_children` | Get all child pages under a specific Confluence page | Finding sub-pages under a requirements page; hierarchical discovery |
| `create_confluence_page` | Create Confluence page | Creating release note pages; creating new documentation |
| `update_confluence_page` | Update Confluence page content | Updating existing requirements pages; appending new sections |
| `search_confluence_by_label` | Search Confluence content by label | **DEPRECATED** — avoid; use direct page access or space pages instead |
| `search_confluence_pages` | Search Confluence pages | **DEPRECATED** — use `get_confluence_space_pages` or direct page ID access |
| `list_confluence_spaces` | List Confluence spaces | Discovering available spaces in Confluence |

### Confluence Usage Patterns

**Pattern: Parsing Requirements (plan-epics workflow)**
```
1. get_confluence_page_full_content (NOT get_confluence_page)
   → Fetches complete HTML body without truncation
2. Parse HTML structure:
   - H2/H3 headings → feature areas / stories
   - Bullet lists → acceptance criteria
   - Tables → data specifications
3. get_page_children (optional)
   → Discover child pages for additional context
```

**Pattern: Creating Release Notes**
```
1. create_confluence_page
   → Create new child page under: config.confluence.release_notes_parent_page_id
   → Use templates/release-note.md as content template
   → Title: "Release Note — v{version} — {date}"
```

**Critical Note**: Confluence page content is HTML. When updating pages, ForgeFlow must:
- Fetch current version to avoid conflicts
- Increment version number on update
- Render structured data back to Confluence HTML format

---

## Jenkins Tools (6 tools)

All Jenkins CI/CD operations for build and deployment diagnosis.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `jenkins_get_build_status` | Get detailed status/results of a specific Jenkins build | Checking which stage failed, duration, result of a specific build |
| `jenkins_get_console_text` | Get Jenkins build console text/log output | **PRIMARY diagnosis tool** — extract error messages, stack traces, logs |
| `jenkins_get_job_status` | Get comprehensive job status (health, config, recent builds) | Understanding overall job health, trend, configuration |
| `jenkins_list_jobs` | List and discover all Jenkins deployment jobs | Finding the right job when not specified |
| `teach_schedule_jenkins_build` | Provide instructions for scheduling a Jenkins build | Guiding developer on how to trigger/schedule a build (NO direct trigger tool exists) |
| `get_jenkins_deploy_url_in_acto` | Query Jenkins Deploy URL from ServiceNow CMDB using GitLab project | Finding deployment information from service catalog |

### Jenkins Usage Patterns

**Pattern: Diagnosing Pipeline Failure (fix-pipeline workflow)**
```
1. jenkins_get_job_status → overview of job health
2. jenkins_get_build_status → specific failed build metadata
3. jenkins_get_console_text → PRIMARY diagnosis source (error logs, stack traces)
4. get_file_content (GitLab) → read relevant source files for context
5. [Jenkins Agent applies error catalog to diagnose]
6. [Code Agent reads affected code]
```

**Critical Note**: There is NO direct "trigger build" tool. For scheduling builds:
- Use `teach_schedule_jenkins_build` to provide guidance
- Instruct developer to trigger via Jenkins UI or CLI
- Workflows cannot auto-trigger Jenkins builds

---

## SonarQube Tools (7 tools)

All SonarQube operations for code quality and security analysis.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `get_sonar_project_issues` | Get SonarQube project issue list (all issues with details) | **PRIMARY tool** — fetches all code issues with severity, rule, file, line |
| `get_sonar_project_measures` | Get SonarQube project quality metrics (coverage, duplicates, etc.) | Checking overall code quality metrics |
| `get_sonar_quality_gate_status` | Get SonarQube project quality gate status | Checking if project passes/fails quality gate |
| `list_sonar_quality_profiles` | List available code quality profiles | Discovering available profiles |
| `search_sonar_projects` | Search for projects in SonarQube | Finding the right SonarQube project |
| `get_project_uncovered_lines` | Get uncovered lines for all files in a project | Identifying untested code; coverage analysis |
| `get_sonar_project_and_nexus_iq_application_by_gitlab` | Auto-discover SonarQube project from GitLab CI/CD variables | Finding SonarQube project key if not in config |

### SonarQube Usage Patterns

**Pattern: Analyzing Quality Issues (sonar-fix workflow)**
```
1. get_sonar_project_issues → fetch all issues
2. get_sonar_quality_gate_status → check gate (before and after fixes)
3. [SonarQube Agent categorizes issues by fixability]
4. [Code Agent generates fixes for auto-fixable issues]
5. [Verify: re-run get_sonar_quality_gate_status to show impact]
```

**Issue Categorization** (built into sonar-agent.md):
- **AUTO-FIXABLE**: null checks (S2259), unused imports (S1128), empty catch (S108), resource not closed (S2093)
- **AGENT-ASSISTED**: cognitive complexity (S3776), duplicated code (S1192), security hotspots
- **MANUAL**: architecture issues, complex design violations

---

## Release & Deployment Tools (4 tools)

Release management and deployment tracking.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `create_new_release_ticket` | Create new Release Ticket (Step 1 of 2-step release) | Starting a release process; creating release ticket |
| `confirm_existing_release_ticket` | Confirm created Release Ticket (Step 2 of 2-step release) | Finalizing a release after approvals |
| `create_release_from_history` | Create Release Ticket from commit history (ONE-STEP, recommended) | **PREFERRED for create-release-build workflow** — replaces separate create/confirm steps |
| `get_ticket_history` | Query release request historical records | Auditing past releases; understanding release patterns |

### Release & Deployment Usage Patterns

**Pattern: Creating Release (create-release-build workflow)**
```
OPTION A (RECOMMENDED — One Step):
1. create_release_from_history
   → Auto-generates release ticket from commit history
   → Simpler, fewer steps

OPTION B (Two Steps):
1. create_new_release_ticket (Step 1)
2. confirm_existing_release_ticket (Step 2)
   → More control, explicit approval between steps
```

---

## Nexus IQ Tools (7 tools)

Software composition analysis and dependency security. **Primary tools for the Security Agent** in Workflow 10 (Security Audit).

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `get_nexusiq_application` | Get Nexus IQ application details (name, ID, organization) | Start of security audit — get application metadata |
| `get_nexusiq_component_details` | Get **detailed** component info (CVEs, fixed versions, CVSS scores, affected ranges) | **PRIMARY diagnosis tool** — per-component vulnerability analysis |
| `get_nexusiq_report_policy_violations` | Get all policy violations from a scan report (security, license, quality) | **PRIMARY data source** — lists all violations with threat levels |
| `search_nexusiq_components` | Search Nexus IQ components by name/coordinates | Finding specific components when exact identifier is unknown |
| `list_nexusiq_application_reports` | List scan reports for a Nexus IQ application (with dates) | Finding the MOST RECENT scan report to analyze |
| `list_nexusiq_applications` | List all Nexus IQ applications | Discovering the correct application when not configured |
| `list_nexusiq_organizations` | List Nexus IQ organizations | Discovering organizational structure; rarely needed |

### Nexus IQ Usage Patterns

**Pattern: Security Audit (Workflow 10)**
```
1. get_nexusiq_application → get application metadata
   OR get_sonar_project_and_nexus_iq_application_by_gitlab → auto-discover
2. list_nexusiq_application_reports → find latest scan report
3. get_nexusiq_report_policy_violations → get all violations
4. FOR EACH violation:
   a. get_nexusiq_component_details → get CVE details, fixed version
   b. get_file_content (GitLab) → read dependency file for current version
   c. search_in_repository (GitLab) → check if component is imported (reachability)
5. [Security Agent assesses reachability and remediation strategy]
```

**Pattern: Component Investigation**
```
1. search_nexusiq_components(name) → find component
2. get_nexusiq_component_details(identifier) → get full vulnerability data
```

---

## NPC2 / Terraform Tools (6 tools)

Infrastructure-as-code and deployment configuration management.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `generate_npc2_terraform_template` | Generate deployment.yaml or config-management.yaml | Creating infrastructure-as-code templates |
| `get_npc2_capability_documentation` | Get detailed documentation for a NPC2 capability | Understanding deployment capabilities |
| `list_npc2_capabilities` | List all NPC2 capabilities for Terraform config | Discovering available capabilities |
| `search_npc2_capabilities` | Search NPC2 capabilities by keyword | Finding specific capabilities |
| `validate_npc2_configuration` | Validate an NPC2 deployment.yaml configuration | Checking configuration validity before deployment |
| `extract_cmdb_from_project` | Extract CMDB app instance names from NPC2 project | Discovering deployed instances |

**Usage**: For infrastructure-as-code workflows. Not used in core 8 workflows but available for infrastructure automation.

---

## Ansible Tools (3 tools)

Infrastructure automation and orchestration.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `generate_jenkins_pipeline_with_ansible` | Generate Jenkins pipeline with Ansible roles | Creating automation-driven CI/CD pipelines |
| `generate_requirements_yml` | Generate Ansible requirements.yml file | Creating Ansible dependency files |
| `explain_ansible_galaxy_usage` | Explain ansible.galaxy() and ansible.galaxyAll() usage | Understanding Ansible Galaxy integration |

**Usage**: For infrastructure automation workflows. Not used in core 8 workflows.

---

## Zephyr (Test Management) Tools (2 tools)

Test case and test execution management. **Primary tools for the Test Agent** in Workflow 11 (Generate Test Plan).

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `create_zephyr_test` | Create a Zephyr Test issue in Jira with full test case details | **PRIMARY** — creating test cases linked to stories/epics |
| `update_zephyr_test` | Update an existing Zephyr Test issue (status, results, steps) | Updating test execution results, modifying test steps |

### Zephyr Usage Patterns

**Pattern: Generate Test Plan (Workflow 11)**
```
1. get_jira_issue_detail → fetch acceptance criteria from source story
2. search_jira_issues → check for existing linked tests (avoid duplicates)
3. [Test Agent derives test cases from criteria]
4. FOR EACH approved test case:
   a. create_zephyr_test → create test issue with full details
   b. link_issues → link test to source story ("Tests" link type)
5. [Report: created test keys with links]
```

**Pattern: Update Test Results**
```
1. update_zephyr_test(test_key, status="PASS/FAIL", results={...})
```

**Fallback**: If `create_zephyr_test` fails (Zephyr not configured), fall back to `create_jira_subtask` with test details in the description.

---

## LTM (Load Balancer) Tools (1 tool)

Load balancing configuration management.

| Tool | Purpose | When to Use |
|------|---------|-----------|
| `list_ltm_load_balancer_types` | List all available LTM Load Balancer sub-types | Discovering load balancer configurations |

**Usage**: For infrastructure-as-code workflows involving load balancer configuration.

---

## Tool Availability & Verification

To verify that all required MCP tools are available:

1. **Check MCP Server Configuration** in your IDE settings
   - Ensure ce-mcp server is registered
   - Verify credentials are configured (tokens, API keys)

2. **Test Tool Availability**
   - Start a conversation with ForgeFlow Orchestrator
   - Agent will verify required tools are present
   - Missing tools will be reported clearly

3. **Common Issues**
   - Tool not found → verify MCP server configuration
   - Authentication error → check credentials in Copilot Chat secrets
   - Rate limiting → implement retry logic in workflows (tools handle this)

---

## Tool Selection Strategy for Workflows

| Workflow | Primary Tools | Secondary Tools |
|----------|---------------|-----------------|
| 01-init-project | GitLab (get_file_content), Code Agent | None |
| 02-plan-epics | Confluence (get_page_full_content), Jira (create_epic_with_issues) | GitLab (get_file_content) |
| 03-plan-dev-tasks | Jira (get_jira_issue_detail, create_jira_issue), Code Agent | GitLab (get_file_content) |
| 04-implement-dev-task | GitLab (commit_file_and_create_mr), Code Agent | Jira (update_jira_issue) |
| 05-fix-pipeline | Jenkins (get_console_text, get_build_status), GitLab, Code Agent | Jira (create issue or link) |
| 06-sonar-fix | SonarQube (get_sonar_project_issues), Code Agent, GitLab | Jira (update) |
| 07-create-release-build | GitLab (review_merge_request), Release (create_release_from_history), Jira (update_jira_issue) | Jenkins (verify pipeline) |
| 08-create-release-note | Confluence (create_confluence_page), Jira (search), GitLab (get commits) | None |
| 09-mr-auto-review | GitLab (review_merge_request, review_and_comment_mr), SonarQube, Code Agent | Jira (get_jira_issue_detail) |
| 10-security-audit | Nexus IQ (all 7 tools), SonarQube (security issues), GitLab (get_file_content, search) | Jira (create_jira_issue), GitLab (commit_file_and_create_mr) |
| 11-generate-test-plan | Zephyr (create_zephyr_test), Jira (get_jira_issue_detail, search, link_issues) | GitLab (search_in_repository, get_file_content) |

---

## Adding New Tools to ForgeFlow

To integrate a new MCP tool:

1. **Identify the agent** that should handle it (Jira Agent for Jira tools, etc.)
2. **Add to mcp-tools-reference.md** in the appropriate section
3. **Update the agent's tool list** with the new tool name and description
4. **Create usage patterns** showing how/when to use it
5. **Update workflows** that should use the new tool
6. **Test** in a conversation with Copilot Chat

---

## Credential Management

All MCP tools require authentication. Do NOT hardcode credentials:

- **Jira**: Set `JIRA_TOKEN` environment variable or Copilot Chat secret
- **GitLab**: Set `GITLAB_TOKEN` environment variable or Copilot Chat secret
- **Confluence**: Set `CONFLUENCE_TOKEN` environment variable or Copilot Chat secret
- **Jenkins**: Set `JENKINS_USER` and `JENKINS_TOKEN` environment variables
- **SonarQube**: Set `SONARQUBE_TOKEN` environment variable or Copilot Chat secret
- **Nexus IQ**: Set `NEXUSIQ_TOKEN` environment variable or Copilot Chat secret

For security, use Copilot Chat's integrated credential management rather than environment variables in production.
