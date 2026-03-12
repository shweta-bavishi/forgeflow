# Otomate Setup Guide

Complete installation and configuration guide for Otomate in your project.

## Prerequisites

Before starting, ensure you have:

- ✓ VS Code or JetBrains IDE with Copilot Chat extension
- ✓ Access to development tools: Jira, GitLab, Jenkins, SonarQube, Confluence
- ✓ API tokens/credentials for each tool
- ✓ Git repository already initialized
- ✓ Node.js 16+ (for TypeScript projects)

## Step 1: Add MCP Server Configuration

Otomate requires MCP tools. Configure your IDE to use the ce-mcp server:

### VS Code

Edit `.vscode/settings.json`:
```json
{
  "claude": {
    "mcp_servers": {
      "ce-mcp": {
        "command": "npx",
        "args": ["@your-org/ce-mcp"],
        "env": {
          "JIRA_URL": "https://jira.your-org.com",
          "GITLAB_URL": "https://gitlab.com",
          "CONFLUENCE_URL": "https://confluence.your-org.com"
        }
      }
    }
  }
}
```

### JetBrains

Settings → Tools → Claude Code → MCP Servers → Add:
- Server: ce-mcp
- URL: npx @your-org/ce-mcp
- Enable: ✓

## Step 2: Set Environment Variables

Store credentials in environment:

```bash
# Jira
export JIRA_TOKEN="jira_api_token_here"
export JIRA_URL="https://jira.your-org.com"

# GitLab
export GITLAB_TOKEN="gitlab_personal_access_token"
export GITLAB_URL="https://gitlab.com"

# Confluence
export CONFLUENCE_TOKEN="confluence_api_token"
export CONFLUENCE_URL="https://confluence.your-org.com"

# Jenkins
export JENKINS_USER="jenkins_username"
export JENKINS_TOKEN="jenkins_api_token"
export JENKINS_URL="https://jenkins.your-org.com"

# SonarQube
export SONARQUBE_TOKEN="sonarqube_token"
export SONARQUBE_URL="https://sonarqube.your-org.com"
```

Or add to `.env` file (never commit):
```
JIRA_TOKEN=xxx
GITLAB_TOKEN=xxx
...
```

## Step 3: Copy Otomate to Project

### Option A: Manual Copy

```bash
mkdir -p your-project/.otomate
cp -r otomate/{agents,workflows,templates,config} your-project/.otomate/
```

### Option B: Use Init Workflow (Recommended)

1. Open your project in IDE
2. Open Copilot Chat
3. Say: **"Initialize Otomate"**
4. Follow prompts

Otomate will scan your project and create config.

## Step 4: Create otomate.config.yml

In your project root, create `otomate.config.yml`:

```yaml
# Copy from config/otomate.config.example.yml and customize:

project:
  name: "my-awesome-api"
  language: "typescript"
  framework: "nestjs"
  package_manager: "npm"

jira:
  project_key: "PROJ"
  board_id: 123  # From Jira board URL
  story_point_field: "customfield_10021"

gitlab:
  project_id: 12345  # Numeric ID from GitLab project settings
  default_branch: "develop"

confluence:
  space_key: "ENG"
  release_notes_parent_page_id: 12345678

jenkins:
  job_name: "my-awesome-api-build"

sonarqube:
  project_key: "com.org:my-awesome-api"
```

### Find Missing Values

**Jira board_id**:
- Go to https://jira.your-org.com/software/c/projects/PROJ/boards
- Board URL has ID: `.../boards/123`

**Jira custom field IDs**:
- Go to Jira → Project Settings → Fields
- Hover over "Story Points" field
- Copy field ID from URL or field configuration

**GitLab project_id**:
- Go to project → Settings → General
- Copy "Project ID"

**Confluence page ID**:
- Go to page → Edit
- URL shows: `.../spaces/ENG/pages/12345678/...`

**SonarQube project_key**:
- Go to SonarQube project → Administration → Project Information
- Copy "Project Key"

## Step 5: Verify Setup

Test that all tools are accessible:

### In Copilot Chat:

```
Verify Otomate setup
```

Or manually:

```
Try: Get Jira project PROJ → Should return project info
Try: Get GitLab project 12345 → Should return project details
Try: Get Confluence space ENG → Should list pages
Try: Get Jenkins job my-awesome-api-build → Should return job info
Try: Get SonarQube project com.org:my-awesome-api → Should return metrics
```

If any fail:
- Check credentials in environment
- Verify URLs are correct in config
- Check MCP server is running
- See troubleshooting below

## Step 6: Test with First Workflow

Try the simplest workflow:

```
Implement PROJ-123
```

Or if you have Confluence requirements:

```
Plan epics from Confluence page {page_id}
```

This will:
1. Fetch task/page details
2. Show implementation plan
3. Ask for approval
4. Generate code and open MR

**If this works**: ✓ Otomate is ready!

## Troubleshooting

### MCP Tools Not Found

**Error**: "Tool get_jira_issue not found"

**Solution**:
1. Verify MCP server is configured (see Step 1)
2. Restart IDE
3. Check MCP server is running: `npx @your-org/ce-mcp`

### Authentication Failed

**Error**: "Authentication failed" or "Permission denied"

**Solution**:
1. Verify environment variables are set
2. Check tokens are not expired
3. Verify token has necessary scopes:
   - Jira: read issues, create issues, edit issues
   - GitLab: read code, create MR, commit
   - Confluence: read pages, create pages
   - Jenkins: read builds
   - SonarQube: read metrics

### Config File Not Found

**Error**: "otomate.config.yml not found"

**Solution**:
1. Create config in project root (see Step 4)
2. Or run: "Initialize Otomate" to auto-generate

### Workflow Fails

**Error**: Workflow stops with error

**Solution**:
1. Check error message for specific issue
2. See [docs/troubleshooting.md](docs/troubleshooting.md)
3. Or open GitHub issue with:
   - Error message
   - Which workflow
   - Config excerpt (mask secrets)

## Next Steps

1. ✓ Setup complete!
2. Read [docs/onboarding.md](docs/onboarding.md) for user guide
3. Try each workflow one by one
4. Customize agents for your team's patterns
5. Add to team documentation

## Team Setup

To roll out to your team:

1. **Distribute**: Share otomate/ directory
2. **Document**: Link to README.md and SETUP.md
3. **Train**: Walk through first workflow together
4. **Customize**: Update config for your org
5. **Iterate**: Collect feedback, improve agents

See [docs/contributing.md](docs/contributing.md) for extending Otomate.

---

**Issues?** Check [docs/troubleshooting.md](docs/troubleshooting.md)

**Next:** [ReadME.md](README.md) for overview or start using Otomate now!
