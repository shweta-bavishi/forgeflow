# Otomate — Multi-Agent Development Workflow Orchestrator

A powerful, config-driven system for automating the complete software development lifecycle using AI-powered agents and Model Context Protocol (MCP) tools.

## What is Otomate?

Otomate is a collection of **markdown-based agents and workflows** that run inside your IDE's Copilot Chat (VS Code/JetBrains). It orchestrates complex development tasks across Jira, GitLab, Confluence, Jenkins, and SonarQube without requiring any executable code or server infrastructure.

### Key Features

🚀 **11 Complete Workflows**
- Initialize project with auto-detection
- Plan epics from Confluence requirements
- Break epics into dev tasks
- Implement tasks with full code generation
- Fix pipeline failures with diagnostics
- Resolve SonarQube quality issues
- Create release builds with validation
- Generate and publish release notes
- **Auto-review merge requests** with 6-dimension analysis
- **Security audit** with Nexus IQ + SonarQube vulnerability analysis
- **Generate test plans** with Zephyr test case creation

🤖 **10 Specialized Agents**
Each agent is an expert in its domain with deep knowledge of patterns, conventions, and best practices:
- **Orchestrator** — Routes requests to workflows
- **Project Context** — Loads and provides project configuration
- **Code Agent** — Analyzes code and generates new implementations
- **Jira Agent** — Manages issue creation and tracking
- **GitLab Agent** — Handles commits, branches, and merge requests
- **Confluence Agent** — Parses requirements and publishes documentation
- **Jenkins Agent** — Diagnoses pipeline failures
- **SonarQube Agent** — Analyzes and fixes code quality issues
- **Security Agent** — Dependency vulnerability analysis and remediation
- **Test Agent** — Translates requirements into structured test cases

🔧 **113 MCP Tools**
Pre-configured access to Jira, GitLab, Confluence, Jenkins, SonarQube, and more. Every workflow uses these tools to interact with your development infrastructure.

⚙️ **Fully Config-Driven**
Single `otomate.config.yml` file defines your entire project setup. Change config, not code. Same Otomate works across all your projects.

🚦 **Human-in-the-Loop (HITL)**
Every critical action requires developer approval. No surprises. Workflows guide you through decision points with clear options.

## Quick Start (5 minutes)

### 1. Prerequisites

✓ Copilot Chat enabled in VS Code or JetBrains IDE
✓ MCP server configured with access to your tools (Jira, GitLab, etc.)
✓ Credentials set up (JIRA_TOKEN, GITLAB_TOKEN, etc.)

### 2. Install Otomate

Copy the complete `.otomate/` directory into your project root:

```bash
git clone https://github.com/your-org/otomate.git
cp -r otomate/. your-project/.otomate/
```

Or use the init workflow (see below).

### 3. Initialize Your Project

In Copilot Chat, say:

```
Initialize Otomate
```

Otomate will:
1. Scan your repository
2. Detect language, framework, architecture
3. Auto-fill config with detected values
4. Ask for missing credentials/IDs
5. Create `otomate.config.yml`

### 4. Try Your First Workflow

```
Plan epics from Confluence page {page_id}
```

Or:

```
Implement PROJ-123
```

Done! You're using Otomate.

## The 11 Workflows

| Workflow | Trigger | Output | Time |
|----------|---------|--------|------|
| **01 — Init Project** | "Initialize Otomate" | Config file + .otomate/ directory | 5-10 min |
| **02 — Plan Epics** | "Plan epics from Confluence {url}" | Jira epics + updated Confluence | 15 min |
| **03 — Plan Dev Tasks** | "Plan dev tasks for {EPIC-KEY}" | Jira tasks with technical specs | 20 min |
| **04 — Implement Dev Task** | "Implement {JIRA-KEY}" | Code files + Git branch + MR | 45 min |
| **05 — Fix Pipeline** | "Fix pipeline" | Diagnosis + fix branch + MR | 30 min |
| **06 — Sonar Fix** | "Fix sonar issues" | Quality fixes + MR | 30 min |
| **07 — Create Release** | "Release v{version}" | Merged to develop + tagged | 20 min |
| **08 — Release Note** | "Create release note for v{version}" | Confluence documentation | 15 min |
| **09 — MR Auto-Review** | "Review my MR" | 6-dimension review + MR comment | 15-25 min |
| **10 — Security Audit** | "Run security audit" | Vulnerability report + fix MR/Jira | 20-40 min |
| **11 — Generate Test Plan** | "Generate test plan for {KEY}" | Zephyr test cases linked to stories | 15-30 min |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Copilot Chat                         │
│              (Your IDE's LLM Interface)                 │
└────────────────────┬────────────────────────────────────┘
                     │
     ┌───────────────┴────────────────────┐
     │                                    │
┌────▼──────────────────┐     ┌──────────▼─────────────┐
│  Orchestrator Agent   │     │  Specialized Agents    │
│  (Router + Manager)   │────→│  - Code Agent          │
└───────────────────────┘     │  - Jira Agent          │
                              │  - GitLab Agent        │
                              │  - Confluence Agent    │
                              │  - Jenkins Agent       │
                              │  - SonarQube Agent     │
                              │  - Security Agent      │
                              │  - Test Agent          │
                              └──────────┬─────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
             ┌──────▼────┐        ┌──────▼────┐       ┌──────▼────┐
             │   Jira    │        │   GitLab   │       │ Confluence │
             │ (Issues)  │        │   (Code)   │       │  (Docs)    │
             └───────────┘        └────────────┘       └────────────┘
                    │                    │                    │
             ┌──────▼────┐        ┌──────▼────┐       ┌──────▼────┐
             │  Jenkins   │        │ SonarQube  │       │Confluence │
             │ (Pipeline) │        │ (Quality)  │       │ (Release) │
             └────────────┘        └────────────┘       └────────────┘
```

## How It Works

### Example: Implement a Task

**Developer**: "Implement PROJ-123"

```
1. Orchestrator routes to 04-implement-dev-task workflow
2. Jira Agent fetches task details
3. Code Agent:
   - Reads existing project code
   - Understands patterns
   - Creates implementation plan
4. Developer reviews & approves plan
5. Code Agent generates:
   - Controllers, services, repositories
   - Unit tests, integration tests
   - Type definitions, error handling
6. Developer reviews code
7. GitLab Agent creates branch & MR
8. Jira Agent updates issue status
9. Developer merges MR when ready
```

**Result**: Production-ready code, tests, and open MR — no manual file creation or boilerplate.

## Configuration

Every project needs one file: `otomate.config.yml`

```yaml
project:
  name: my-awesome-api
  language: typescript
  framework: nestjs
  package_manager: npm

jira:
  project_key: PROJ
  board_id: 123
  story_point_field: customfield_10021

gitlab:
  project_id: 12345
  default_branch: develop

confluence:
  space_key: ENG
  release_notes_parent_page_id: 98765

jenkins:
  job_name: my-awesome-api-build

sonarqube:
  project_key: com.org:my-awesome-api
```

Run the **Init Project** workflow to auto-generate this.

## Project Structure

```
otomate/
├── README.md (you're here)
├── SETUP.md (detailed setup guide)
├── ARCHITECTURE.md (technical design)
│
├── agents/
│   ├── otomate-orchestrator.md
│   ├── project-context-agent.md
│   ├── code-agent.md
│   ├── jira-agent.md
│   ├── gitlab-agent.md
│   ├── confluence-agent.md
│   ├── jenkins-agent.md
│   ├── sonar-agent.md
│   ├── security-agent.md
│   └── test-agent.md
│
├── workflows/
│   ├── 01-init-project.md
│   ├── 02-plan-epics.md
│   ├── 03-plan-dev-tasks.md
│   ├── 04-implement-dev-task.md
│   ├── 05-fix-pipeline.md
│   ├── 06-sonar-fix.md
│   ├── 07-create-release-build.md
│   ├── 08-create-release-note.md
│   ├── 09-mr-auto-review.md
│   ├── 10-security-audit.md
│   └── 11-generate-test-plan.md
│
├── templates/
│   ├── mr-description.md
│   ├── changelog.md
│   ├── release-note.md
│   └── scaffolds/
│       └── typescript/
│           ├── controller.hbs
│           ├── service.hbs
│           ├── repository.hbs
│           ├── entity.hbs
│           └── test.hbs
│
├── config/
│   ├── otomate.config.example.yml
│   └── mcp-tools-reference.md
│
├── scripts/
│   └── mcp_connector.py          (sample MCP client)
│
└── docs/
    ├── configuration.md
    ├── mcp-setup.md
    ├── onboarding.md
    ├── troubleshooting.md
    ├── contributing.md
    ├── workflows/                 (one guide per workflow)
    │   ├── init-project.md
    │   ├── plan-epics.md
    │   ├── ...
    │   ├── mr-auto-review.md
    │   ├── security-audit.md
    │   └── generate-test-plan.md
    └── agents/                    (agent design references)
        ├── security-agent.md
        └── test-agent.md
```

## Key Concepts

### Agentic Design
- Agents have **decision-making authority**
- No fixed step-by-step scripts
- Agents reason about context and adapt
- If unsure → ask developer, don't assume

### Human-in-the-Loop (HITL)
- Every merge, release, or destructive action needs approval
- Clear information provided at approval gates
- Developer always knows what's happening next

### Token Optimization
- Config loaded once per session
- Agents don't duplicate work
- Minimal context overhead
- Fast iterations

### Config-Driven
- Zero hardcoded project details
- Change config → works across projects
- Supports any language/framework/tool combo

## Limitations & Future

### Current Limitations

❌ Cannot directly trigger Jenkins builds (must be manual)
❌ Cannot auto-merge MRs (must merge via GitLab UI/CLI)
❌ Cannot cherry-pick or create tags (must be manual via git CLI)
❌ Requires Copilot Chat in IDE (not standalone CLI)

### Why These Limitations?

By design. Otomate prioritizes **safety** over full automation:
- Manual merge approval prevents accidents
- Developer stays in control of releases
- Reversible operations are the only automated ones

### Future Enhancements

✅ Direct Jenkins build triggering
✅ Automated MR merging (with pre-checks)
✅ Extended language scaffolds (Java, Python, Go)
✅ Custom workflow templates
✅ Advanced code analysis and refactoring

## Getting Help

📚 **Documentation**
- [Setup Guide](SETUP.md) — Installation & configuration
- [Architecture](ARCHITECTURE.md) — Design deep-dive
- [Workflow Guides](docs/workflows/) — Step-by-step for each workflow
- [Configuration Reference](docs/configuration.md) — All config options
- [Troubleshooting](docs/troubleshooting.md) — Common issues & fixes

🤔 **Questions?**
- Check [docs/onboarding.md](docs/onboarding.md) for first-time setup
- See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues
- Open an issue: [GitHub Issues](https://github.com/your-org/otomate/issues)

💬 **Community**
- Discussions: [GitHub Discussions](https://github.com/your-org/otomate/discussions)
- Slack: #otomate channel
- Office hours: [Calendar link]

## Contributing

Want to extend Otomate?

1. Add new workflow in `workflows/XX-workflow-name.md`
2. Create specialist agent in `agents/new-agent.md`
3. Update agents/agents that interact with your agent
4. Document in `docs/workflows/`
5. Add to orchestrator trigger patterns

See [docs/contributing.md](docs/contributing.md) for detailed guide.

## License

Otomate is open source. See LICENSE file.

## Credits

Created by the Development Infrastructure team.

**Key Contributors**:
- Architecture & design
- Agent implementation
- Workflow design
- Documentation

---

**Ready to get started?** → [SETUP.md](SETUP.md)

**Want to learn more?** → [ARCHITECTURE.md](ARCHITECTURE.md)

**Jump right in?** → Initialize your project now: "Initialize Otomate"

---

*Otomate — Automate your development lifecycle with AI-powered agents*
