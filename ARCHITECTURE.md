# Otomate Architecture

Technical architecture document covering multi-agent design, orchestration, workflow execution, and extensibility.

## Design Philosophy

Otomate follows three core principles:

1. **Agentic, not procedural** — Agents make decisions based on context, not fixed scripts
2. **Config-driven, not hardcoded** — Zero project-specific details in agent code
3. **Safe by default** — Every destructive action requires human approval

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        IDE / Copilot Chat                       │
│                    (LLM Interface — the brain)                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Natural language
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                            │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │  Intent   │→│ Workflow  │→│   HITL     │→│   Results     │  │
│  │  Parser   │  │  Router  │  │   Manager  │  │  Aggregator   │  │
│  └──────────┘  └──────────┘  └───────────┘  └───────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Delegates to
          ┌────────────────┼────────────────────┐
          ▼                ▼                    ▼
┌──────────────┐  ┌──────────────┐    ┌──────────────┐
│ Project Ctx  │  │  Specialist  │    │   Workflow    │
│    Agent     │  │   Agents     │    │   Files       │
│              │  │              │    │              │
│ Loads config │  │ Code Agent   │    │ 01-init      │
│ once/session │  │ Jira Agent   │    │ 02-epics     │
│ Provides to  │  │ GitLab Agent │    │ 03-tasks     │
│ all agents   │  │ Confluence   │    │ 04-implement │
│              │  │ Jenkins      │    │ 05-pipeline  │
│              │  │ SonarQube    │    │ 06-sonar     │
└──────┬───────┘  └──────┬───────┘    │ 07-release   │
       │                 │            │ 08-notes     │
       │                 │            └──────────────┘
       ▼                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                     MCP TOOL LAYER (113 tools)                  │
│                                                                  │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ │
│  │  Jira   │ │ GitLab  │ │Confluence│ │ Jenkins │ │  Sonar  │ │
│  │ 12 tools│ │ 19 tools│ │  9 tools │ │ 6 tools │ │ 7 tools │ │
│  └─────────┘ └─────────┘ └──────────┘ └─────────┘ └─────────┘ │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ │
│  │ Release │ │Nexus IQ │ │NPC2/Terra│ │ Ansible │ │Zephyr+  │ │
│  │ 4 tools │ │ 7 tools │ │  6 tools │ │ 3 tools │ │LTM 3    │ │
│  └─────────┘ └─────────┘ └──────────┘ └─────────┘ └─────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Agent Responsibilities

| Agent | Responsibility | Model Hint | Stateful? |
|-------|---------------|------------|-----------|
| Orchestrator | Route intent, manage HITL, aggregate results | FAST | Session memory |
| Project Context | Load config, validate, distribute context | FAST | Cached config |
| Code Agent | Analyze code, generate implementations, write tests | MOST_CAPABLE | Pattern memory |
| Jira Agent | Create/update issues, manage lifecycle | FAST | None |
| GitLab Agent | Commit code, create MRs, review changes | FAST | None |
| Confluence Agent | Parse requirements, create documentation | CAPABLE | None |
| Jenkins Agent | Diagnose pipeline failures | CAPABLE | Error catalog |
| SonarQube Agent | Analyze quality issues, categorize fixes | CAPABLE | Rule knowledge |

## How Orchestration Works

### Intent Resolution

```
Developer Input → Orchestrator
                    │
                    ├─ Keyword match? → Route to workflow
                    ├─ Ambiguous? → Ask clarifying question
                    ├─ Multi-workflow? → Break into sequence
                    └─ Unknown? → Explain available options
```

### Workflow Execution Model

Each workflow follows a phased execution model:

```
Phase 1: GATHER    → Collect data from tools (Jira, GitLab, etc.)
Phase 2: ANALYZE   → Code Agent / specialist agent processes data
Phase 3: PRESENT   → Show results to developer
Phase 4: 🚦 GATE   → Developer approves / modifies / rejects
Phase 5: EXECUTE   → Perform actions (create issues, commit code, etc.)
Phase 6: VERIFY    → Confirm actions succeeded
Phase 7: REPORT    → Summarize results and next steps
```

Not every workflow has all phases. Some have multiple GATE phases.

### HITL Gate Design

Human-in-the-loop gates exist for safety:

```
ALWAYS require approval:
  - Pushing code to remote
  - Creating Jira issues (batches)
  - Merging to develop/release
  - Creating release tags
  - Publishing Confluence pages
  - Transitioning Jira issues to "Done"

CAN auto-approve (if configured):
  - Auto-fixable sonar issues
  - Low-risk pipeline fixes
  - Config validation results

Gate provides:
  - What will happen
  - Why approval is needed
  - Consequences of proceeding
  - Ability to modify before proceeding
```

## Data Flow

### Configuration Loading

```
otomate.config.yml
        │
        ▼
  Project Context Agent
  (reads once, caches)
        │
        ├──→ Code Agent (architecture, standards)
        ├──→ Jira Agent (project_key, statuses)
        ├──→ GitLab Agent (project_id, branching)
        ├──→ Confluence Agent (space_key, page IDs)
        ├──→ Jenkins Agent (job_name)
        └──→ SonarQube Agent (project_key)
```

### Cross-Agent Communication

Agents don't talk to each other directly. Communication flows through workflows:

```
Workflow 04 (Implement Task):
  1. Jira Agent → fetches task → passes data to
  2. Code Agent → generates code → passes files to
  3. GitLab Agent → commits and creates MR → passes MR link to
  4. Jira Agent → updates issue with MR link
```

## Model Selection Strategy

Three tiers match task complexity:

```
FAST (lightweight LLM):
  - Config parsing
  - Tool call orchestration
  - Simple routing decisions
  - API-heavy operations
  Used by: Orchestrator, Project Context, Jira Agent, GitLab Agent

CAPABLE (medium LLM):
  - Content analysis (Confluence parsing)
  - Log parsing (Jenkins diagnosis)
  - Pattern matching (SonarQube categorization)
  - Moderate reasoning
  Used by: Confluence Agent, Jenkins Agent, SonarQube Agent

MOST_CAPABLE (strongest LLM):
  - Code generation
  - Architecture analysis
  - Complex reasoning
  - Test generation
  Used by: Code Agent
```

## Token Optimization

### Strategy 1: Load Once, Reference Many

```
Config loaded by Project Context Agent (once per session)
All other agents reference cached config
No duplicate config reads
```

### Strategy 2: Selective File Reading

```
Code Agent reads only:
  - Files in affected architecture layers
  - 2-3 examples per layer (not entire codebase)
  - Config files for patterns

NOT:
  - Every file in the project
  - Entire git history
  - All test files
```

### Strategy 3: Compact Output Formats

```
Agent output uses structured YAML/tables instead of prose:
  Instead of: "The project uses TypeScript with NestJS framework..."
  Use:
    language: typescript
    framework: nestjs
    pattern: clean architecture
```

### Strategy 4: Progressive Detail Loading

```
Phase 1: Load minimal context (config summary)
Phase 2: Load relevant context (affected files only)
Phase 3: Load deep context (if needed for complex analysis)

Each phase adds context only when needed
```

## Error Handling Architecture

### Three-Level Error Strategy

```
Level 1: TRY
  Execute the tool call normally

Level 2: FALLBACK
  If tool fails, try alternative approach:
  - Different tool (get_jira_issue → get_jira_issue_detail)
  - Different parameters (branch: develop → branch: main)
  - Cached data (use previously fetched info)

Level 3: ASK
  If fallback fails, ask developer:
  - Show the error
  - Explain what was attempted
  - Offer options (retry, skip, manual)
```

### Error Propagation

```
Tool Error → Agent catches → Classifies error type
  │
  ├─ Transient (network, timeout) → Retry with backoff
  ├─ Auth (401, 403) → Stop, ask for credentials
  ├─ Validation (400) → Show error, ask for correct input
  ├─ Not Found (404) → Ask for correct identifier
  └─ Unknown → Show raw error, ask developer
```

## Security Model

### Credential Management

```
Credentials are NEVER stored in:
  - otomate.config.yml
  - Agent .md files
  - Workflow .md files

Credentials are stored in:
  - Environment variables (JIRA_TOKEN, GITLAB_TOKEN, etc.)
  - IDE secret storage (Copilot Chat secrets)
  - MCP server configuration
```

### Access Control

```
Otomate respects existing tool permissions:
  - If Jira token has read-only access → create_jira_issue fails gracefully
  - If GitLab token lacks MR permissions → commit_file_and_create_mr fails
  - Agents never attempt to escalate privileges
```

## Extensibility

### Adding a New Agent

1. Create `agents/new-agent.md` following agent design patterns
2. Define: GOAL, responsibilities, tools, decision trees, error handling
3. Update orchestrator to know about the new agent
4. Reference from relevant workflows

### Adding a New Workflow

1. Create `workflows/XX-workflow-name.md`
2. Define: phases, agents involved, HITL gates
3. Add trigger patterns to orchestrator
4. Create user-facing docs in `docs/workflows/`

### Adding Tools

1. Add to `config/mcp-tools-reference.md`
2. Update relevant agent's tool list
3. Create usage patterns
4. Test in conversation

### Adding Language Scaffolds

1. Create `templates/scaffolds/{language}/` directory
2. Add Handlebars templates (controller.hbs, service.hbs, etc.)
3. Update config scaffolds section
4. Code Agent will use templates when generating files

## Known Limitations

| Limitation | Reason | Workaround |
|-----------|--------|------------|
| No auto-merge MR | No MCP merge tool | Developer merges via GitLab UI |
| No cherry-pick | No MCP cherry-pick tool | Developer uses git CLI |
| No tag creation | No MCP tag tool | Developer uses git CLI |
| No Jenkins trigger | No MCP trigger tool | Developer triggers via Jenkins UI |
| No branch deletion | No MCP delete tool | Developer cleans up in GitLab |
| No issue deletion | No MCP delete tool | Developer manages in Jira UI |
| Single-project config | Config is per-project | Copy config to each project |

## File Organization Rationale

```
agents/     → Agent behavior specifications (read by LLM)
workflows/  → Step-by-step workflow definitions (read by LLM)
templates/  → Code generation templates (read by Code Agent)
config/     → Configuration and tool reference (read by Project Context Agent)
docs/       → Human-readable documentation (read by developers)
```

Separation keeps concerns clean:
- LLM reads agents/ and workflows/
- Code Agent reads templates/
- Developers read docs/
- Config drives everything

---

**Related**: README.md (overview), SETUP.md (installation), docs/ (detailed guides)
