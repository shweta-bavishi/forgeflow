# MCP Server Setup Guide

How to configure the MCP (Model Context Protocol) tools that ForgeFlow requires.

## What is MCP?

MCP provides ForgeFlow's agents with access to external tools (Jira, GitLab, Confluence, Jenkins, SonarQube). The ce-mcp server exposes 113 tools that agents call during workflow execution.

## Prerequisites

- IDE with Copilot Chat extension (VS Code or JetBrains)
- Network access to your tools (Jira, GitLab, etc.)
- API tokens for each service

## Step 1: Install MCP Server

```bash
# Install ce-mcp globally
npm install -g @your-org/ce-mcp

# Or use npx (no install needed)
npx @your-org/ce-mcp
```

## Step 2: Configure IDE

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "claude": {
    "mcp_servers": {
      "ce-mcp": {
        "command": "npx",
        "args": ["@your-org/ce-mcp"],
        "env": {
          "JIRA_URL": "https://jira.your-org.com",
          "JIRA_TOKEN": "${env:JIRA_TOKEN}",
          "GITLAB_URL": "https://gitlab.com",
          "GITLAB_TOKEN": "${env:GITLAB_TOKEN}",
          "CONFLUENCE_URL": "https://confluence.your-org.com",
          "CONFLUENCE_TOKEN": "${env:CONFLUENCE_TOKEN}",
          "JENKINS_URL": "https://jenkins.your-org.com",
          "JENKINS_USER": "${env:JENKINS_USER}",
          "JENKINS_TOKEN": "${env:JENKINS_TOKEN}",
          "SONARQUBE_URL": "https://sonarqube.your-org.com",
          "SONARQUBE_TOKEN": "${env:SONARQUBE_TOKEN}"
        }
      }
    }
  }
}
```

### JetBrains

Settings > Tools > Claude Code > MCP Servers > Add:
- Name: ce-mcp
- Command: npx @your-org/ce-mcp
- Environment: (same variables as above)

## Step 3: Set Credentials

### Environment Variables

```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
export JIRA_TOKEN="your_jira_api_token"
export GITLAB_TOKEN="your_gitlab_personal_access_token"
export CONFLUENCE_TOKEN="your_confluence_api_token"
export JENKINS_USER="your_jenkins_username"
export JENKINS_TOKEN="your_jenkins_api_token"
export SONARQUBE_TOKEN="your_sonarqube_token"
```

### Getting API Tokens

**Jira**: Profile > Security > API Tokens > Create Token

**GitLab**: User Settings > Access Tokens > Create Token (scopes: api, read_repository, write_repository)

**Confluence**: Same as Jira (Atlassian uses shared tokens)

**Jenkins**: User > Configure > API Token > Add Token

**SonarQube**: My Account > Security > Generate Token

## Step 4: Verify Tools

In Copilot Chat, test each domain:

```
"Get Jira project PROJ"        → Should return project info
"Get GitLab project 12345"     → Should return project details
"List Confluence spaces"        → Should return space list
"List Jenkins jobs"             → Should return job list
"Search SonarQube projects"    → Should return project list
```

## Tool Inventory

ForgeFlow uses 113 tools across 10 domains:

| Domain | Tools | Key Tools |
|--------|-------|-----------|
| GitLab | 19 | commit_file_and_create_mr, get_file_content |
| Jira | 12 | create_epic_with_issues, get_jira_issue_detail |
| Confluence | 9 | get_confluence_page_full_content, create_confluence_page |
| Jenkins | 6 | jenkins_get_console_text, jenkins_get_build_status |
| SonarQube | 7 | get_sonar_project_issues, get_sonar_quality_gate_status |
| Release | 4 | create_release_from_history |
| Nexus IQ | 7 | Dependency security analysis |
| NPC2/Terraform | 6 | Infrastructure-as-code |
| Ansible | 3 | Automation pipelines |
| Zephyr + LTM | 3 | Test management + load balancing |

See `config/mcp-tools-reference.md` for complete inventory.

## Troubleshooting

### "Tool not found"

1. Verify MCP server is running
2. Restart IDE
3. Check server configuration syntax

### "Authentication failed"

1. Verify token is not expired
2. Check token has correct scopes
3. Ensure URL is correct (https, correct hostname)

### "Connection refused"

1. Check network access to service
2. Verify VPN connection (if required)
3. Check firewall rules

### "Rate limited"

1. ForgeFlow agents retry automatically
2. If persistent: wait 1-2 minutes
3. Check if other automation is using same token

## Adding New Tools

If your organization adds new MCP tools:

1. Update MCP server package
2. Add tool to `config/mcp-tools-reference.md`
3. Update relevant agent's tool list
4. Create usage patterns in agent file
5. Test in a conversation

---

**Related**: config/mcp-tools-reference.md (tool catalog), SETUP.md (installation)
