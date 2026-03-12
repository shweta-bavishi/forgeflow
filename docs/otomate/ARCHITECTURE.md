# Otomate Architecture

## System Overview

Otomate is built on VS Code Copilot's native customization mechanisms. Instead of custom runtime infrastructure, it uses Copilot's agent, skill, and instruction system to orchestrate 113 MCP tools across 11 domains.

```
┌─────────────────────────────────────────────────────┐
│                  VS Code Copilot Chat               │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │           Otomate Orchestrator              │   │
│  │        (.github/agents/otomate.agent.md)    │   │
│  │                                               │   │
│  │  Intent Parsing → Skill Loading → HITL Gates  │   │
│  └──────┬──────────────┬──────────────┬──────────┘   │
│         │              │              │              │
│    ┌────▼────┐   ┌─────▼─────┐  ┌────▼─────┐       │
│    │  Code   │   │  Review   │  │ Security │       │
│    │  Agent  │   │  Agent    │  │  Agent   │       │
│    └────┬────┘   └─────┬─────┘  └────┬─────┘       │
│         │              │              │              │
│  ┌──────▼──────────────▼──────────────▼──────────┐   │
│  │              11 Workflow Skills                │   │
│  │  (.github/skills/*/SKILL.md — loaded on-demand)│   │
│  └──────────────────────┬────────────────────────┘   │
│                         │                            │
│  ┌──────────────────────▼────────────────────────┐   │
│  │          ce-mcp Server (113 Tools)             │   │
│  │  GitLab│Jira│Confluence│Jenkins│SonarQube│...  │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Custom Agents (`.github/agents/`)

Agents appear in the VS Code Copilot dropdown. They use YAML frontmatter:

```yaml
---
name: Otomate
description: "..."
tools: ["ce-mcp"]
model: ["Claude Sonnet 4", "GPT-4o"]
handoffs:
  - label: "Implement Code"
    agent: "otomate-code"
    prompt: "Continue with the implementation plan."
    send: false
---
```

**Agent Responsibilities:**

| Agent | Role | Handoffs To |
|-------|------|------------|
| Otomate (Orchestrator) | Intent parsing, routing, HITL gates | Code, Review, Security |
| Otomate Code | Code analysis, generation, testing | Orchestrator |
| Otomate Review | 6-dimension MR review | Orchestrator, Code |
| Otomate Security | Vulnerability analysis, remediation | Orchestrator, Code |

### 2. Workflow Skills (`.github/skills/`)

Skills are auto-discovered by VS Code from `.github/skills/*/SKILL.md`. They load **only when the user's prompt matches the skill description** — this is the core token optimization mechanism.

```yaml
---
name: implement-dev-task
description: "Implement a Jira development task..."
---
```

Each skill contains the complete workflow instructions: phases, decision trees, MCP tool calls, HITL gates, error handling.

### 3. Custom Instructions (`.github/instructions/`)

Always-on rules injected into every Copilot interaction:

| File | `applyTo` | Purpose |
|------|-----------|---------|
| `otomate-context.instructions.md` | `**` | MCP tool inventory, tool selection patterns, session memory |
| `coding-standards.instructions.md` | `src/**` | Naming conventions, architecture rules, test rules |
| `hitl-rules.instructions.md` | `**` | Approval gate protocol, anti-patterns |

### 4. Configuration (`otomate.config.yml`)

Single config file in project root drives all project-specific behavior:

```
project → identity, language, framework
architecture → layers, patterns, key files
coding_standards → naming, linter, formatter, test framework
jira → project key, board, statuses, fields
gitlab → project ID, branches, MR settings
confluence → space, parent pages
jenkins → job names
sonarqube → project key, quality gate
nexusiq → application name
zephyr → test config
auto_review → dimensions, thresholds
approval_gates → HITL configuration
```

## Token Optimization Strategy

The key architectural decision: **skills load on-demand**.

In the original Otomate architecture (10 agents, 8 workflows loaded simultaneously), every conversation consumed tokens loading all agent and workflow content. In the native Copilot architecture:

1. **Global instructions** (~compact) load always
2. **Custom instructions** (~compact) load based on `applyTo` patterns
3. **Agent body** (~medium) loads when agent is selected
4. **Skill body** (~large) loads **only when prompt matches description**

This means a conversation about fixing a pipeline only loads the `fix-pipeline` SKILL.md — not all 11 workflows.

## Data Flow

### Typical Workflow Execution

```
1. Developer types: "Implement PROJ-123"
                     │
2. Copilot matches → Otomate agent (from dropdown)
                     │
3. Orchestrator: intent parsing
   → Matches "implement" keyword
   → Loads: implement-dev-task skill
                     │
4. Skill Phase 1: get_jira_issue_detail(PROJ-123)
   → Fetches task details from Jira
                     │
5. Skill Phase 2: get_file_content(relevant files)
   → Analyzes existing code patterns
                     │
6. Hand off → Otomate Code agent
   → Generates implementation plan
   → 🚦 HITL GATE: Developer reviews plan
                     │
7. Code Agent: generates files
   → 🚦 HITL GATE: Developer reviews code
                     │
8. Skill Phase 9: commit_file_and_create_mr(...)
   → 🚦 HITL GATE: Developer approves push
   → Creates MR
                     │
9. Skill Phase 10: update_jira_issue(PROJ-123, "In Review")
   → Updates Jira status
                     │
10. Orchestrator: summary + next steps
```

## Error Handling Architecture

Every MCP tool call follows the **TRY → FALLBACK → ASK** pattern:

```
TRY: Primary tool call
  ↓ (success → proceed)
  ↓ (failure →)
FALLBACK: Alternative approach or retry
  ↓ (success → proceed)
  ↓ (failure →)
ASK: Developer for guidance
  → Never silently fail
  → Never retry auth errors
  → Never ignore partial failures
```

## HITL Gate Architecture

Approval gates are defined in `otomate.config.yml` under `approval_gates` and enforced by `hitl-rules.instructions.md`:

```
approval_gates:
  always_require_approval:
    - push_code_to_remote
    - create_merge_request
    - create_release_build
    - post_mr_review_comment
    - create_security_fix_mr
    - create_zephyr_tests
    - update_jira_status_to_done
```

At each gate, the agent must: **PRESENT** → **SHOW** → **ASK** → **WAIT** for explicit approval.

## Security Model

- Credentials are NEVER stored in config (env vars or Copilot secrets only)
- HITL gates prevent unauthorized actions
- No auto-merge, auto-deploy, or auto-trigger capabilities
- All code changes require developer review before push
