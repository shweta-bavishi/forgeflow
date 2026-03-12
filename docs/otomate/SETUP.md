# Otomate Setup Guide

## Prerequisites

1. **VS Code** with GitHub Copilot Chat extension
2. **MCP Server**: `ce-mcp` server configured and running
3. **Credentials**: API tokens for Jira, GitLab, Confluence, Jenkins, SonarQube (and optionally Nexus IQ)

## Step 1: Install Otomate Files

Copy the Otomate directory structure into your project:

```
.github/
  agents/        → 4 agent files
  skills/        → 11 skill folders
  instructions/  → 3 instruction files
  copilot-instructions.md
```

## Step 2: Configure MCP Server

Ensure `ce-mcp` is registered in your VS Code MCP settings. All 113 tools should be available.

### Verify Tool Availability

In Copilot Chat, select the Otomate agent and say:
```
"Check if MCP tools are available"
```

Otomate will verify connectivity to each tool domain.

## Step 3: Set Up Credentials

Set environment variables or configure Copilot Chat secrets:

| Variable | Purpose | Required For |
|----------|---------|-------------|
| `JIRA_TOKEN` | Jira API access | All Jira operations |
| `GITLAB_TOKEN` | GitLab API access | All GitLab operations |
| `CONFLUENCE_TOKEN` | Confluence API access | Release notes, plan-epics |
| `JENKINS_USER` | Jenkins username | Pipeline diagnosis |
| `JENKINS_TOKEN` | Jenkins API token | Pipeline diagnosis |
| `SONARQUBE_TOKEN` | SonarQube access | Quality gate, sonar-fix |
| `NEXUSIQ_TOKEN` | Nexus IQ access | Security audit (optional) |

## Step 4: Initialize Your Project

1. Open VS Code in your project directory
2. Open Copilot Chat
3. Select **Otomate** from the agent dropdown
4. Say: **"Initialize Otomate"**

Otomate will:
- Scan your repository structure
- Auto-detect language, framework, architecture
- Generate `otomate.config.yml`
- Guide you through filling in manual fields

## Step 5: Verify Setup

After initialization, test with a simple workflow:

```
"What workflows are available?"
```

Otomate should list all 11 workflows with descriptions.

## Configuration File Reference

See [configuration.md](configuration.md) for the complete `otomate.config.yml` schema.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for common setup issues.
