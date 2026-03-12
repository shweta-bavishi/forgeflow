# Otomate Troubleshooting

## Common Issues

### "Otomate needs to be initialized first"

**Cause:** `otomate.config.yml` not found in project root.
**Fix:** Run the `init-project` workflow: say "Initialize Otomate" to the Otomate agent.

### MCP Tools Not Available

**Cause:** `ce-mcp` server not configured or not running.
**Fix:**
1. Check VS Code MCP server settings
2. Verify `ce-mcp` is registered and running
3. Test with a simple tool call in Copilot Chat

### Authentication Errors (401/403)

**Cause:** Invalid or missing API tokens.
**Fix:**
1. Check environment variables: `JIRA_TOKEN`, `GITLAB_TOKEN`, etc.
2. Or configure Copilot Chat secrets
3. Verify tokens have the required permissions
4. Tokens may have expired — regenerate if needed

### Jira Issue Creation Fails

**Cause:** Missing `get_jira_project_info` call before creation.
**Fix:** Otomate always calls `get_jira_project_info` first. If it still fails:
1. Check `jira.project_key` in config matches your Jira project
2. Verify issue type names match exactly (e.g., "Story" vs "User Story")
3. Check custom field IDs are correct

### Confluence Content Truncated

**Cause:** Using `get_confluence_page` instead of `get_confluence_page_full_content`.
**Fix:** Otomate skills use `get_confluence_page_full_content` by default. If you see truncation, verify the skill is loaded correctly.

### Pipeline Diagnosis Shows No Errors

**Cause:** Jenkins console log may be empty or not yet available.
**Fix:**
1. Wait for the build to complete before diagnosing
2. Check Jenkins job name matches config
3. Try fetching a specific build number instead of "latest"

### Quality Gate Shows PASSED but SonarQube Has Issues

**Cause:** Quality gate conditions may not include all issue types.
**Fix:** Check `sonarqube.quality_gate` in config. Use `get_sonar_project_issues` for the full issue list.

### Nexus IQ Application Not Found

**Cause:** Application name mismatch or not registered.
**Fix:**
1. Set `nexusiq.application_name` in config
2. Or let Otomate auto-discover via `get_sonar_project_and_nexus_iq_application_by_gitlab`
3. Otomate gracefully falls back to SonarQube-only audit

### Code Generation Doesn't Match Project Style

**Cause:** Agent didn't read enough existing code for pattern matching.
**Fix:**
1. Ensure `architecture.key_files` in config lists important files
2. Point the agent to reference code: "Check src/services/user.service.ts for the pattern"
3. Provide feedback in the HITL review gate — the agent will adjust

### MR Creation Fails

**Cause:** Branch may already exist, or GitLab token lacks permissions.
**Fix:**
1. Check if branch already exists — say "Use existing branch" if prompted
2. Verify `GITLAB_TOKEN` has `api` scope
3. Ensure `gitlab.project_id` is the correct numeric ID

### Rate Limiting (429)

**Cause:** Too many API calls in a short period.
**Fix:** Otomate automatically retries with backoff. If persistent:
1. Wait a few minutes before retrying
2. Reduce the scope of the workflow (e.g., fewer issues at once)

## Getting Help

1. Check the relevant workflow guide in `docs/otomate/workflows/`
2. Review the agent file in `.github/agents/` for decision trees
3. Inspect the skill file in `.github/skills/` for exact MCP tool calls
4. Check `otomate.config.yml` for configuration issues
