# Otomate — AI-Powered Development Workflow Orchestrator

Otomate is a multi-agent development workflow system built on VS Code Copilot's native customization features. It automates the complete software development lifecycle using 113 MCP tools from the `ce-mcp` server.

## Architecture

Otomate uses VS Code Copilot's **native agent, skill, and instruction** mechanism:

- **4 Custom Agents** (`.github/agents/`) — Appear in Copilot agent dropdown
- **12 Workflow Skills** (`.github/skills/`) — Auto-discovered and loaded on-demand
- **3 Custom Instructions** (`.github/instructions/`) — Always-on context rules
- **1 Global Instructions** (`.github/copilot-instructions.md`) — Standard Copilot config

### Agents

| Agent | File | Role |
|-------|------|------|
| Otomate | `otomate.agent.md` | Orchestrator — routes intent to skills, manages HITL gates |
| Otomate Code | `otomate-code.agent.md` | Code analysis, generation, testing, refactoring |
| Otomate Review | `otomate-review.agent.md` | 6-dimension MR auto-review |
| Otomate Security | `otomate-security.agent.md` | Nexus IQ + SonarQube security audits |

### Workflows (Skills)

| # | Skill | Trigger | What It Does |
|---|-------|---------|-------------|
| 1 | init-project | "Initialize Otomate" | Scans repo, generates config |
| 2 | plan-epics | "Plan epics from Confluence" | Parses requirements → Jira epics |
| 3 | plan-dev-tasks | "Plan dev tasks for PROJ-100" | Breaks epic → implementation tasks |
| 4 | implement-dev-task | "Implement PROJ-123" | Code generation → MR |
| 5 | fix-pipeline | "Fix pipeline" | Diagnose + fix CI/CD failure |
| 6 | sonar-fix | "Fix sonar issues" | Auto-fix quality gate issues |
| 7 | release-build | "Create release" | Validate + release workflow |
| 8 | release-note | "Create release note" | Generate + publish to Confluence |
| 9 | mr-auto-review | "Review my MR" | 6-dimension review + comment |
| 10 | security-audit | "Run security audit" | Nexus IQ + SonarQube audit |
| 11 | generate-test-plan | "Generate tests for PROJ-123" | Acceptance criteria → Zephyr tests |
| 12 | create-workflow | "Create a new workflow" | Describe automation → feasibility analysis → generate SKILL.md |

### MCP Tool Domains (113 tools)

| Domain | Tools | Primary Use |
|--------|-------|-------------|
| GitLab | 19 | Code, branches, MRs, pipelines |
| Jira | 12 | Issues, epics, sprints |
| Confluence | 9 | Pages, requirements, release notes |
| Jenkins | 6 | Build status, logs, diagnosis |
| SonarQube | 7 | Quality gate, issues, coverage |
| Nexus IQ | 7 | Vulnerability scanning |
| Release | 4 | Release tickets |
| NPC2/Terraform | 6 | Infrastructure-as-code |
| Ansible | 3 | Automation pipelines |
| Zephyr | 2 | Test management |
| LTM | 1 | Load balancer config |

## Quick Start

1. Open your project in VS Code with Copilot Chat
2. Select the **Otomate** agent from the Copilot dropdown
3. Say: **"Initialize Otomate"**
4. Otomate scans your repo and generates `otomate.config.yml`
5. Start using any of the 11 workflows

## Key Design Principles

- **Config-driven**: `otomate.config.yml` drives all project-specific behavior
- **Human-in-the-loop**: Every destructive action requires explicit approval
- **Agentic**: Goal-oriented decision trees, not linear checklists
- **TRY → FALLBACK → ASK**: Resilient error handling for every tool call
- **Token-optimized**: Skills load on-demand (only when prompt matches)

## Project Structure

```
.github/
  agents/
    otomate.agent.md            # Orchestrator agent
    otomate-code.agent.md       # Code specialist
    otomate-review.agent.md     # Review specialist
    otomate-security.agent.md   # Security specialist
  skills/
    init-project/SKILL.md
    plan-epics/SKILL.md
    plan-dev-tasks/SKILL.md
    implement-dev-task/
      SKILL.md
      scaffolds/                  # Handlebars code templates
        controller.hbs
        service.hbs
        repository.hbs
        entity.hbs
        test.hbs
    fix-pipeline/SKILL.md
    sonar-fix/SKILL.md
    release-build/SKILL.md
    release-note/
      SKILL.md
      release-template.md
    mr-auto-review/SKILL.md
    security-audit/SKILL.md
    generate-test-plan/SKILL.md
    create-workflow/SKILL.md
  instructions/
    otomate-context.instructions.md   # Always-on context (applyTo: **)
    coding-standards.instructions.md    # Source-only (applyTo: src/**)
    hitl-rules.instructions.md          # Always-on HITL rules (applyTo: **)
  copilot-instructions.md              # Global Copilot instructions
otomate.config.yml                    # Project configuration
templates/
  mr-description.md                    # MR description template
  changelog.md                         # Changelog template
  release-note.md                      # Release note template
docs/otomate/                        # Documentation
```

## Documentation

- [SETUP.md](SETUP.md) — Installation and configuration
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design and agent architecture
- [configuration.md](configuration.md) — Config file reference
- [troubleshooting.md](troubleshooting.md) — Common issues and solutions
- [contributing.md](contributing.md) — How to extend Otomate
- [workflows/](workflows/) — Per-workflow user guides
