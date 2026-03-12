---
applyTo: "**"
---

# Otomate Context — Always-On Instructions

## Project Context Loading

At the start of every workflow, load project context from `otomate.config.yml`:

1. **Project identity**: name, language, framework, runtime, package manager
2. **Architecture**: pattern, layers (paths + descriptions), key files
3. **Coding standards**: naming conventions, linter, formatter, test framework, coverage threshold
4. **Tool config**: Jira project key + board ID, GitLab project ID + default branch, Jenkins job name, SonarQube project key, Confluence space key
5. **HITL gates**: which actions require approval

Cache this context for the entire session. Do NOT re-read config on every tool call.

## MCP Tool Inventory (ce-mcp server)

### GitLab (19 tools)
`get_project_info`, `get_file_content`, `commit_and_push_file`, `commit_file_and_create_mr`, `create_merge_request`, `list_project_merge_requests`, `list_project_issues`, `get_project_pipelines`, `search_in_repository`, `search_gitlab_projects`, `list_user_projects`, `review_merge_request`, `review_and_comment_mr`, `post_mr_review_comment`, `get_gitlab_ci_guide`, `generate_gitlab_ci_config`, `explain_gitlab_ci_parameter`, `list_available_templates`

### Jira (12 tools)
`get_jira_issue`, `get_jira_issue_detail`, `get_jira_project_info`, `create_jira_issue`, `create_jira_subtask`, `create_epic_with_issues`, `update_jira_issue`, `search_jira_issues`, `link_issues`, `move_issue_to_sprint`, `list_jira_projects`, `get_project_sprints`

### Confluence (9 tools)
`get_confluence_page`, `get_confluence_page_full_content`, `get_confluence_space_pages`, `get_page_children`, `create_confluence_page`, `update_confluence_page`, `search_confluence_by_label`, `search_confluence_pages`, `list_confluence_spaces`

### Jenkins (6 tools)
`jenkins_get_build_status`, `jenkins_get_console_text`, `jenkins_get_job_status`, `jenkins_list_jobs`, `teach_schedule_jenkins_build`, `get_jenkins_deploy_url_in_acto`

### SonarQube (7 tools)
`get_sonar_project_issues`, `get_sonar_project_measures`, `get_sonar_quality_gate_status`, `list_sonar_quality_profiles`, `search_sonar_projects`, `get_project_uncovered_lines`, `get_sonar_project_and_nexus_iq_application_by_gitlab`

### Nexus IQ (7 tools)
`get_nexusiq_application`, `get_nexusiq_component_details`, `get_nexusiq_report_policy_violations`, `search_nexusiq_components`, `list_nexusiq_application_reports`, `list_nexusiq_applications`, `list_nexusiq_organizations`

### Release & Deployment (4 tools)
`create_new_release_ticket`, `confirm_existing_release_ticket`, `create_release_from_history`, `get_ticket_history`

### Zephyr (2 tools)
`create_zephyr_test`, `update_zephyr_test`

### NPC2/Terraform (6 tools)
`generate_npc2_terraform_template`, `get_npc2_capability_documentation`, `list_npc2_capabilities`, `search_npc2_capabilities`, `validate_npc2_configuration`, `extract_cmdb_from_project`

### Ansible (3 tools)
`generate_jenkins_pipeline_with_ansible`, `generate_requirements_yml`, `explain_ansible_galaxy_usage`

### LTM (1 tool)
`list_ltm_load_balancer_types`

## Tool Selection Patterns

| Workflow | Primary Tools | Secondary Tools |
|----------|---------------|-----------------|
| init-project | GitLab (get_file_content, search_in_repository) | — |
| plan-epics | Confluence (get_page_full_content), Jira (create_epic_with_issues) | GitLab (get_file_content) |
| plan-dev-tasks | Jira (get_jira_issue_detail, create_jira_issue) | GitLab (get_file_content) |
| implement-dev-task | GitLab (commit_file_and_create_mr) | Jira (update_jira_issue) |
| fix-pipeline | Jenkins (get_console_text, get_build_status), GitLab | Jira |
| sonar-fix | SonarQube (get_sonar_project_issues), GitLab | Jira |
| release-build | GitLab (review_merge_request), Release (create_release_from_history) | Jenkins, Jira |
| release-note | Confluence (create_confluence_page), Jira (search), GitLab | — |
| mr-auto-review | GitLab (review_merge_request, review_and_comment_mr), SonarQube | Jira |
| security-audit | Nexus IQ (all 7), SonarQube, GitLab | Jira, GitLab |
| generate-test-plan | Zephyr (create_zephyr_test), Jira (get_jira_issue_detail, search, link_issues) | GitLab |

## Session Memory

Within a conversation, remember:
- Project config (read once, reuse)
- Completed workflows and their outputs
- Developer preferences expressed during the session
- Created Jira keys, MR IDs, branch names

Reference previous results: "You just created 3 epics (PROJ-100, PROJ-101, PROJ-102)" rather than re-fetching.
