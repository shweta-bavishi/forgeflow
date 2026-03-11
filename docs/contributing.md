# Contributing to ForgeFlow

How to extend ForgeFlow with new agents, workflows, templates, and improvements.

## Architecture Overview

Before contributing, understand the structure:

```
agents/     → Agent behavior specs (read by LLM at runtime)
workflows/  → Workflow step definitions (read by LLM at runtime)
templates/  → Code generation templates (used by Code Agent)
config/     → Configuration and tool reference
docs/       → Human-readable documentation
```

## Adding a New Workflow

### 1. Create Workflow File

Create `workflows/XX-workflow-name.md` with:

```markdown
# Workflow XX: Workflow Name

**Goal**: What this workflow accomplishes
**Trigger**: "example trigger phrases"
**Agents**: Orchestrator → Agent1, Agent2, Agent3
**Time**: ~N minutes

## Phase 1: GATHER
[Collect data from tools]

## Phase 2: ANALYZE
[Process data with agents]

## Phase 3: PRESENT
[Show results to developer]

## Phase 4: 🚦 HITL GATE
[Developer approves/modifies]

## Phase 5: EXECUTE
[Perform actions]

## Error Handling
[What to do when things go wrong]

## Success Criteria
[How to know the workflow succeeded]
```

### 2. Follow Agentic Design Patterns

Every workflow must follow these principles:

- **Goal-oriented**: "Your GOAL is..." not "Step 1: Do X"
- **Decision trees**: Include conditional logic
- **Error recovery**: TRY → FALLBACK → ASK pattern
- **HITL gates**: Explicit approval points for destructive actions
- **Self-verification**: Verify results after multi-step actions
- **Negative instructions**: What NOT to do

### 3. Update Orchestrator

Add trigger patterns to `agents/forgeflow-orchestrator.md`:

```markdown
| "Your trigger phrase" | XX-workflow-name | trigger, keywords |
```

### 4. Document the Workflow

Create `docs/workflows/workflow-name.md` with:
- What it does (plain English)
- How to trigger it
- Prerequisites
- Step-by-step walkthrough
- Common issues

## Adding a New Agent

### 1. Create Agent File

Create `agents/new-agent.md` with this structure:

```markdown
# Agent Name

**Role**: What this agent does
**Scope**: Which workflows use it

## Your GOAL
[Primary objective]

## Core Responsibilities
[Numbered list]

## MCP Tools Available
[List exact tool names from ce-mcp server]

## Decision Trees
[Conditional logic for all operations]

## Error Handling
[TRY → FALLBACK → ASK for each operation]

## Success Criteria
[How to measure success]
```

### 2. Define Tool Interactions

List exact MCP tool names and when to use each:

```markdown
## Tools
- `tool_name` — Purpose | When to use
```

### 3. Include Error Catalog

For diagnostic agents, include error patterns:

```markdown
Pattern: "error message regex"
  Diagnosis: What this means
  Fix: How to fix it
  Confidence: HIGH/MEDIUM/LOW
```

## Adding Scaffold Templates

### 1. Create Language Directory

```bash
mkdir templates/scaffolds/{language}/
```

### 2. Create Handlebars Templates

Use Handlebars syntax for placeholders:

```handlebars
{{pascalCase name}}  → UserService
{{camelCase name}}   → userService
{{kebabCase name}}   → user-service
{{lowerCase name}}   → user service
{{name}}             → raw name
{{jiraKey}}          → PROJ-123
{{description}}      → from Jira
```

### 3. Update Config

Add template mappings to `forgeflow.config.example.yml`:

```yaml
scaffolds:
  python:
    - name: "service"
      template: "templates/scaffolds/python/service.hbs"
      output_pattern: "src/services/{{snake name}}_service.py"
```

## Modifying Existing Workflows

1. Read the current workflow file
2. Understand the phase structure
3. Make targeted changes (don't rewrite entire file)
4. Test in a conversation
5. Update docs if behavior changed

## Updating the Error Catalog

Jenkins Agent's error catalog (`agents/jenkins-agent.md`) is extensible:

```markdown
Pattern: "new error regex"
  Severity: BLOCKING/HIGH/MEDIUM/LOW
  Diagnosis: What this means
  Root Cause: Why it happens
  Fix: How to fix it
  Keywords: Related terms
```

Add new patterns based on real-world failures you encounter.

## Testing Changes

1. Open a project with ForgeFlow configured
2. Start a Copilot Chat conversation
3. Trigger the modified workflow
4. Verify each phase works correctly
5. Test error paths (what if tool fails?)
6. Test HITL gates (approve, modify, reject)

## Style Guide for .md Files

- Use consistent heading levels (H1 for title, H2 for sections, H3 for subsections)
- Use code blocks for tool calls and examples
- Use tables for structured data
- Include "What NOT to do" sections
- End with success criteria and metadata (related workflows, agents, tools)

## Pull Request Guidelines

1. Describe what changed and why
2. List affected agents/workflows
3. Include test evidence (conversation screenshots or logs)
4. Update relevant docs
5. Get review from at least one team member

---

**Questions?** Open a discussion or reach out to the ForgeFlow maintainers.
