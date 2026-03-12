# Troubleshooting Guide

Common issues and their solutions.

## Configuration Issues

### "Config file not found"

**Cause**: `otomate.config.yml` is missing from project root.

**Fix**:
1. Run: "Initialize Otomate" in Copilot Chat
2. Or copy `config/otomate.config.example.yml` to project root as `otomate.config.yml`
3. Fill in your project details

### "Config file has YAML syntax errors"

**Cause**: Invalid YAML formatting (wrong indentation, missing colons, etc.)

**Fix**:
1. Check indentation (use 2 spaces, never tabs)
2. Ensure all string values with special characters are quoted
3. Validate YAML syntax online
4. Check for missing colons after keys

### "Config has placeholder values"

**Cause**: Fields still have template values like "YOUR-PROJECT-KEY".

**Fix**: Replace all placeholder values with actual project data. See `docs/configuration.md` for guidance on finding each value.

## MCP Tool Issues

### "Tool not found: get_jira_issue"

**Cause**: MCP server not configured or not running.

**Fix**:
1. Check IDE settings for MCP server configuration
2. Restart IDE
3. Verify ce-mcp package is installed
4. See `docs/mcp-setup.md` for detailed setup

### "Authentication failed" (any tool)

**Cause**: API token is missing, expired, or has wrong permissions.

**Fix**:
1. Verify environment variable is set (e.g., `echo $JIRA_TOKEN`)
2. Check token hasn't expired
3. Verify token has required scopes:
   - Jira: Read/Write issues
   - GitLab: API, read_repository, write_repository
   - Confluence: Read/Write pages
   - Jenkins: Read builds
   - SonarQube: Execute analysis, browse

### "Rate limited" (429 error)

**Cause**: Too many API requests in short time.

**Fix**: Otomate agents auto-retry with backoff. If persistent:
1. Wait 2-3 minutes
2. Check if other tools are using the same API token
3. Contact admin to increase rate limits

### "Connection refused" / "Timeout"

**Cause**: Service is down, network issue, or firewall blocking.

**Fix**:
1. Check if service is accessible: `curl https://jira.your-org.com`
2. Verify VPN connection (if required)
3. Check proxy settings
4. Try again in a few minutes

## Workflow Issues

### "Copilot doesn't recognize the workflow"

**Cause**: Agent/workflow files not loaded or not in expected location.

**Fix**:
1. Verify `.otomate/` directory exists in project root
2. Check that agent .md files are present in `agents/`
3. Check that workflow .md files are present in `workflows/`
4. Restart Copilot Chat session

### "Workflow stops mid-execution"

**Cause**: Tool call failed, context limit reached, or session timeout.

**Fix**:
1. Check the error message (usually indicates which tool failed)
2. If auth error: fix credentials and retry
3. If timeout: retry the workflow
4. If context limit: start a new conversation and continue from where it stopped

### "Wrong workflow triggered"

**Cause**: Ambiguous intent or keyword overlap.

**Fix**: Be more specific:
- Instead of "fix this" → "fix pipeline for PROJ-123"
- Instead of "plan" → "plan dev tasks for PROJ-100"
- Instead of "release" → "create release note for v2.4.1"

## Jira Issues

### "Issue type not found"

**Cause**: Issue type name in config doesn't match Jira project.

**Fix**:
1. Run: `get_jira_project_info` to see valid types
2. Update `jira.epic_issue_type`, `jira.story_issue_type`, etc. in config
3. Common names: "Epic", "Story", "Task", "Bug" (case-sensitive)

### "Custom field not found"

**Cause**: `story_point_field` or `sprint_field` ID is wrong.

**Fix**:
1. Go to Jira > Project Settings > Fields
2. Find the custom field
3. Copy the field ID (e.g., "customfield_10021")
4. Update config

### "Status transition not available"

**Cause**: Trying to transition to a status that isn't reachable from current status.

**Fix**:
1. Check current issue status
2. Check available transitions (depends on workflow configuration in Jira)
3. May need intermediate transition (To Do > In Progress > In Review)

## GitLab Issues

### "Project not found"

**Cause**: `gitlab.project_id` is wrong or token lacks access.

**Fix**:
1. Go to GitLab project > Settings > General
2. Copy the numeric "Project ID"
3. Update config
4. Verify token has access to this project

### "Branch already exists"

**Cause**: Branch was created in a previous attempt.

**Fix**: Otomate will ask: "Use existing branch or create new?"
- Use existing: code will be committed to existing branch
- Create new: provide a different branch name

### "Merge conflict"

**Cause**: Branch has diverged from target.

**Fix**:
1. Rebase your branch on develop: `git rebase develop`
2. Resolve conflicts in IDE
3. Push updated branch
4. MR will be updated automatically

## Jenkins Issues

### "Build not found"

**Cause**: Job name or build number is wrong.

**Fix**:
1. Verify job name in Jenkins (case-sensitive)
2. Check build number exists
3. Use: `jenkins_list_jobs` to find available jobs

### "Console log is empty"

**Cause**: Build hasn't started yet or log is not accessible.

**Fix**:
1. Wait for build to start
2. Check Jenkins permissions (token needs read access)
3. Try `jenkins_get_build_status` first to verify build exists

## SonarQube Issues

### "Project not found"

**Cause**: `sonarqube.project_key` is wrong.

**Fix**:
1. Check SonarQube > Administration > Project Key
2. Or use: `get_sonar_project_and_nexus_iq_application_by_gitlab` to auto-discover
3. Update config

### "No issues found"

**Cause**: SonarQube scan hasn't run yet.

**Fix**:
1. Trigger a SonarQube scan (usually happens in CI pipeline)
2. Wait for scan to complete
3. Retry the sonar-fix workflow

## Code Generation Issues

### "Generated code doesn't match project style"

**Cause**: Config is missing coding standards or Code Agent hasn't read enough examples.

**Fix**:
1. Update `coding_standards` in config with specific rules
2. Point Code Agent to reference files: "Follow pattern from src/services/user.service.ts"
3. Provide more detailed naming conventions

### "Generated code has compilation errors"

**Cause**: Code Agent made assumptions about imports or types.

**Fix**:
1. Review the code during HITL gate
2. Point out the error: "The import for UserRepository is wrong"
3. Code Agent will fix and re-present

### "Tests are incomplete"

**Cause**: Acceptance criteria in Jira are vague.

**Fix**:
1. Add specific acceptance criteria to Jira task
2. Or tell Code Agent: "Add tests for edge cases: empty input, null values, large files"

## General Tips

1. **Start fresh**: If a workflow is stuck, start a new Copilot Chat conversation
2. **Be specific**: More context = better results
3. **Check config first**: Most issues trace back to config problems
4. **Read error messages**: Otomate provides specific guidance in errors
5. **Update regularly**: Keep MCP server and Otomate files up to date

---

**Still stuck?** Open an issue with:
- Error message
- Which workflow you were running
- Config excerpt (mask secrets)
- Steps to reproduce
