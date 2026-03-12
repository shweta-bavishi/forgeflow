# Contributing to Otomate

## How Otomate Is Structured

Otomate consists of three types of files:

| Type | Location | How Copilot Uses It |
|------|----------|-------------------|
| Agents | `.github/agents/*.agent.md` | Appear in Copilot dropdown |
| Skills | `.github/skills/*/SKILL.md` | Auto-loaded when prompt matches description |
| Instructions | `.github/instructions/*.instructions.md` | Always injected based on `applyTo` |

## Adding a New Workflow (Skill)

1. **Create skill directory:** `.github/skills/{skill-name}/`
2. **Create `SKILL.md`** with YAML frontmatter:
   ```yaml
   ---
   name: my-new-skill
   description: "Clear description that matches developer intent for auto-discovery."
   ---
   ```
3. **Write workflow body** with phases, decision trees, MCP tool calls, HITL gates
4. **Update orchestrator** (`otomate.agent.md`): add trigger pattern to the routing table
5. **Update context instructions** (`otomate-context.instructions.md`): add tool selection entry
6. **Create workflow doc** in `docs/otomate/workflows/`

### Skill Best Practices

- Description must be specific enough for VS Code to auto-match prompts
- Use exact MCP tool names from the ce-mcp inventory
- Include HITL gates before any destructive action
- Include error handling for every tool call
- Follow TRY → FALLBACK → ASK pattern

## Adding a New Agent

1. **Create agent file:** `.github/agents/{name}.agent.md`
2. **Define frontmatter:** name, description, tools, model, handoffs
3. **Add handoff** from orchestrator to new agent
4. **Write agent body** with role, decision trees, knowledge base

### Agent Guidelines

- Agents should be domain-specific (code, review, security, etc.)
- Use handoffs for cross-agent collaboration
- Keep agent count low (4-6 max) for token efficiency

## Modifying Existing Workflows

1. Find the skill: `.github/skills/{name}/SKILL.md`
2. Edit phases, tool calls, or decision trees
3. Test in Copilot Chat by triggering the workflow
4. Update the workflow doc if behavior changed

## Adding a New MCP Tool

1. Verify the tool exists in `ce-mcp` server
2. Add to `otomate-context.instructions.md` under the correct domain section
3. Add usage patterns showing when/how to call it
4. Update the tool selection table
5. Update any skills that should use the new tool

## Config Changes

1. Add new field to `otomate.config.yml`
2. Update `docs/otomate/configuration.md` with field reference
3. Update `init-project` skill if the field can be auto-detected
4. Update any skills that read the new field

## Testing Changes

1. Open VS Code with Copilot Chat
2. Select the Otomate agent
3. Trigger the modified workflow with a test prompt
4. Verify: correct skill loads, correct tools called, HITL gates appear
5. Test error scenarios (missing config, tool failures)
