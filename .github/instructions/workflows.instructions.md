---
applyTo: "**"
---

# Otomate Workflows — Custom Instructions

> [!IMPORTANT]
> **These instructions apply ONLY when the `otomate` agent is selected in Copilot. If any other agent is active, IGNORE this file completely.**

These instructions apply specifically when executing any of the 12 defined Otomate workflows. They enforce best practices, agentic patterns, and safety constraints for each workflow.

## 01. Init Project (`init-project`)
- **Validation**: Ensure `otomate.config.yml` captures the complete technology stack (language, framework, package manager).
- **Paths**: Always use absolute paths or paths explicitly relative to the project root when defining architectural layers.
- **Verification**: Do not create the config without confirming the Git repository structure matches the inferred architecture.

## 02. Plan Epics (`plan-epics`)
- **Traceability**: Every created Jira Epic MUST include a direct link back to the Confluence requirements page in its description.
- **Granularity**: Epics should represent user-facing feature areas, not technical components.
- **Completeness**: Warn the developer if the Confluence page lacks clear acceptance criteria before parsing.

## 03. Plan Dev Tasks (`plan-dev-tasks`)
- **Task Definition**: Every development task MUST include clear Acceptance Criteria, Story Points, and a Definition of Done.
- **Size Limit**: If a task is estimated at more than 8 story points, recommend breaking it down further.
- **Linkage**: All dev tasks must be linked to their parent Epic using the `create_jira_subtask` or `link_issues` tools.

## 04. Implement Dev Task (`implement-dev-task`)
- **Atomic Commits**: Create a Draft Merge Request (MR) as early as possible (`commit_file_and_create_mr`).
- **Traceability**: The MR description MUST reference the Jira task key (e.g., "Closes PROJ-123").
- **Testing**: Never consider an implementation done if the test harness (if applicable based on `otomate.config.yml`) cannot run or is missing coverage.

## 05. Fix Pipeline (`fix-pipeline`)
- **Context Gathering**: Always fetch at least the last 100 lines of console logs (`jenkins_get_console_text`) before diagnosing failures.
- **Root Cause**: Distinctly separate compilation errors, test failures, and environment/dependency issues before proposing a fix.
- **Verification**: Do not declare the issue fixed until `jenkins_get_build_status` returns success on the subsequent run.

## 06. Sonar Fix (`sonar-fix`)
- **Impact Assessment**: Focus on reachability and actual impact. Suggest mitigating false positives by marking them "Safe" rather than blindly rewriting code.
- **Safety**: Do not rewrite core business logic just to satisfy a minor linting rule unless explicitly approved.
- **Verification**: Always verify the fix locally (or by triggering a re-scan) before creating the MR.

## 07. Create Release Build (`release-build`)
- **Dependencies**: Verify all associated MRs are merged and Jira issues are in the "Done" state before creating the release payload.
- **Versioning**: Adhere strictly to Semantic Versioning (SemVer) based on the types of changes included in the release.
- **Traceability**: The release ticket/branch MUST link to all incorporated features and fixes.

## 08. Create Release Note (`release-note`)
- **Structure**: Format notes logically by categorizing into: Features, Bug Fixes, and Chores/Dependencies.
- **Formatting**: Use bolding for issue keys and component names to improve readability.
- **Audience**: Write release notes for human consumption (stakeholders/users) — avoid overly technical jargon where plain language suffices.

## 09. MR Auto-Review (`mr-auto-review`)
- **Comprehensive Checks**: Every review MUST check for: test coverage, security vulnerabilities, adherence to `coding-standards.instructions.md`, and performance implications.
- **Constructive Feedback**: Provide actionable feedback with code examples when suggesting improvements to an MR.
- **Approval**: Never approve an MR that reduces test coverage or introduces reachable security vulnerabilities.

## 10. Security Audit (`security-audit`)
- **Prioritization**: Prioritize vulnerabilities based on Reachability before CVSS score. (A reachable High is more urgent than an unreachable Critical).
- **Remediation**: Always suggest safe dependency upgrades (minor/patch) first. Flag breaking (major) upgrades with a ⚠️ WARNING.
- **Pragmatism**: Suggest mitigation or accepting the risk if no patch is available and the component cannot be replaced.

## 11. Generate Test Plan (`generate-test-plan`)
- **Format**: Ensure test cases conform to the BDD format (Given / When / Then) for clarity, unless the project configures otherwise.
- **Coverage**: Generate both positive (happy path) and negative (error handling, boundary conditions) test cases.
- **Linkage**: Every generated Zephyr test must be explicitly linked to its corresponding Jira requirement (`link_issues`).

## 12. Create Workflow (`create-workflow`)
- **Rigorous Feasibility**: ALWAYS perform a complete feasibility analysis against the 113 MCP tools before attempting to design the `SKILL.md`.
- **Honesty**: Firmly reject and explain why event-driven triggers (webhooks, cron) are not possible.
- **Agentic Patterns**: Ensure the generated `SKILL.md` uses decision trees, TRY → FALLBACK → ASK error handling, and 🚦 HITL gates before executing destructive actions.
