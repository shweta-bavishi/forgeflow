# Prompt: Add RTK-Style Token Compression to Forgeflow CLI

## Context

You are working on `@nomura/forgeflow` — an AI-powered development workflow orchestrator (Node.js/TypeScript, ESM, Node 18+) that connects an LLM to enterprise tools (Jira, GitLab, Confluence, SonarQube, Jenkins, Nexus IQ, Zephyr) through MCP servers via JSON-RPC 2.0.

The LLM agent loop (`src/core/agent-loop.ts`) iterates up to 30 times per command, sending MCP tool results back to the LLM each cycle. Raw MCP responses are verbose and human-formatted — they contain ANSI escape codes, passing test noise, repeated log lines, full file bodies, and boilerplate that the LLM does not need to reason effectively. A typical `implement` or `fix-pipeline` run can burn 80,000–150,000 tokens just on tool output.

The goal of this task is to implement a **token compression middleware layer** inside Forgeflow, modelled on the open-source RTK (Rust Token Killer) project's filtering strategies, without using any external binary or npm dependency.

---

## Objective

Build a self-contained TypeScript module `src/core/tool-output-compressor.ts` and integrate it into `src/core/mcp-client.ts` so that every MCP tool result is compressed before it reaches the LLM. The compressor must be:

- **Transparent** — the LLM receives correct, semantically equivalent output; only noise is removed
- **Lossless on failures** — errors, stack traces, and failure details are always preserved in full
- **Exit-code safe** — never modify process exit codes or error signals embedded in structured results
- **Zero new runtime dependencies** — pure TypeScript using only Node.js built-ins
- **Configurable per tool** — different MCP tools get different compression strategies

---

## File to Create

### `src/core/tool-output-compressor.ts`

Implement and export the following:

#### 1. `FilterLevel` enum

```typescript
export enum FilterLevel {
  OFF = 'off',           // raw passthrough, no compression
  STANDARD = 'standard', // default: strip noise, keep all signal
  AGGRESSIVE = 'aggressive', // signatures only, strip bodies
}
```

#### 2. `CompressorStrategy` type and strategy map

Define a `CompressorStrategy` as a function signature:

```typescript
type CompressorStrategy = (raw: string, level: FilterLevel) => string;
```

Build a `TOOL_STRATEGY_MAP` that maps MCP tool name patterns to their strategy function. Use the tool name (string) as the key. Support glob-style prefix matching (e.g. `"get_file_*"` matches `get_file_content`, `get_file_diff`).

#### 3. Core utility functions (implement all of these)

**`stripAnsi(text: string): string`**
Remove all ANSI escape sequences (color codes, cursor movement, bold, etc.) using a regex. Pattern: `/\x1b\[[0-9;]*[A-Za-z]|\x1b\][^\x07]*\x07/g`

**`deduplicateLines(text: string, minRepeat?: number): string`**
Collapse repeated consecutive or near-consecutive identical lines into a single line with a count suffix: `"[line repeated 47×]"`. Default threshold `minRepeat = 3`. Preserve line order. Emit the first occurrence followed by the count annotation if repetitions exceed the threshold.

**`truncateMiddle(text: string, maxChars: number, label?: string): string`**
If `text.length > maxChars`, keep the first 40% and last 40% of characters, replace the middle with:
`"\n... [${label ?? 'content'} truncated — ${skippedLines} lines omitted] ...\n"`
Calculate `skippedLines` from newline count in the removed section.

**`extractFailuresOnly(text: string, toolName: string): string`**
Parse test runner output and return only failure-related lines. Keep:
- Lines containing: `FAIL`, `FAILED`, `ERROR`, `error:`, `Error:`, `AssertionError`, `Exception`, `at ` (stack frames), `Expected`, `Received`, `✕`, `✗`, `×`
- The final summary line (e.g. `Tests: 2 failed, 48 passed`)
- Up to 5 lines of context before each failure line (for readability)

Discard:
- Lines containing: `PASS`, `PASSED`, `✓`, `✔`, `ok `, `· ` (passing test dots), progress bars

Append at the top: `"[RTK: filtered to failures only — {passCount} passing tests hidden]\n"`

**`groupErrorsByType(text: string): string`**
For linter/static-analysis output (SonarQube, ESLint-style), group errors by rule ID or error code. Parse lines like `"[rule-id] file.ts:10:5 message"` or `"ERROR: rule-name"`. Output a grouped summary:
```
rule-id: 12 occurrences across 4 files
  → src/service/Foo.ts (3×), src/controller/Bar.ts (9×)
```

**`extractSignaturesOnly(text: string, language: string): string`**
For source code files, strip function/method bodies and return only signatures + top-level structure. Support:
- **TypeScript/JavaScript**: Keep `export`, `function`, `class`, `interface`, `type`, `const`, `async function` declaration lines; strip everything inside `{...}` blocks beyond depth 1
- **Java**: Keep `public/private/protected` method signatures, class declarations, field declarations; strip method bodies
- **Generic fallback**: Return first 60 lines + `"... [body truncated]"`

**`summarizeJiraIssue(json: object): string`**
Convert a full Jira issue JSON object into a compact markdown summary:
```
PROJ-123 [Story] "Title here" — Status: In Progress | SP: 5 | Assignee: akira@example.com
Description: <first 300 chars>
Acceptance Criteria: <first 500 chars>
```
Strip all Jira internal fields (`id`, `self`, `expand`, `renderedFields`, `names`, `schema`, `transitions`, `changelog`, `versionedRepresentations`).

**`summarizeGitLabMR(json: object): string`**
Compact MR representation:
```
!{iid} "{title}" — {state} | {source_branch} → {target_branch}
Author: {author.name} | Approvals: {approved_by} | Conflicts: {has_conflicts}
Description: <first 300 chars>
```

**`summarizePipelineLog(text: string): string`**
For Jenkins console output or GitLab CI logs:
1. Strip timestamps (ISO patterns, `[00:00:00]` prefixes)
2. Strip ANSI codes
3. Deduplicate repeated lines
4. Keep only: lines containing `ERROR`, `WARN`, `FAILED`, `SUCCESS`, `Exception`, `BUILD`, `Stage`, `Pipeline`, `Downloading` (first occurrence only), stack traces
5. Truncate middle if > 4000 chars
6. Prepend: `"[RTK: pipeline log compressed from {originalLines} → {filteredLines} lines]\n"`

**`compressEnvVars(text: string, filterPrefix?: string): string`**
For environment variable dumps, either filter to lines starting with `filterPrefix` or show only the variable names (not values) grouped by prefix:
```
AWS_* (12 vars) | GITLAB_* (4 vars) | NODE_* (3 vars) | [29 others hidden]
```

#### 4. `compressToolResult(toolName: string, raw: string, level?: FilterLevel): string`

The main exported function. It must:

1. Strip ANSI codes unconditionally (always safe)
2. Look up the tool name in `TOOL_STRATEGY_MAP` (exact match first, then prefix match)
3. Apply the matched strategy at the given `FilterLevel`
4. If no strategy matches, fall back to `truncateMiddle(result, 8000)` for anything over 8000 chars
5. Append a one-line compression note at the end if > 20% was removed: `"[compressed: {originalTokenEstimate} → {compressedTokenEstimate} est. tokens]"`
6. Return the compressed string

Token estimate: `Math.ceil(chars / 4)` (rough approximation).

#### 5. `TOOL_STRATEGY_MAP` — strategy assignments

Implement all these mappings:

| Tool name pattern | Strategy |
|---|---|
| `get_jira_issue`, `create_jira_issue`, `update_jira_issue` | `summarizeJiraIssue` on parsed JSON |
| `search_jira_issues`, `list_jira_issues` | summarize each issue in the array, join with newlines |
| `get_merge_request*`, `create_merge_request` | `summarizeGitLabMR` on parsed JSON |
| `get_file_content`, `get_repository_file` | `extractSignaturesOnly` at AGGRESSIVE, `truncateMiddle(12000)` at STANDARD |
| `get_pipeline_status`, `get_build_status` | `summarizePipelineLog` |
| `get_jenkins_console*`, `get_build_log*` | `summarizePipelineLog` |
| `get_sonar_project_issues`, `search_sonar_issues` | `groupErrorsByType` |
| `run_tests`, `execute_tests` | `extractFailuresOnly` |
| `search_confluence*`, `get_confluence_page` | `truncateMiddle(6000, 'confluence content')` |
| `list_*` (any list operation) | `truncateMiddle(4000, 'list results')` |
| `get_diff`, `get_merge_request_diff` | diff-specific: strip context lines (lines starting with ` ` i.e. unchanged), keep only `+`, `-`, `@@` header lines; truncate if > 5000 chars |
| `env`, `get_environment` | `compressEnvVars` |

---

## File to Modify

### `src/core/mcp-client.ts`

Locate the section where `tools/call` results are returned (the JSON-RPC response handler). After parsing the result content, before returning to the caller, add:

```typescript
import { compressToolResult, FilterLevel } from './tool-output-compressor.js';

// Inside the tool result handler:
const rawContent = result.content ?? '';
const rawText = typeof rawContent === 'string'
  ? rawContent
  : JSON.stringify(rawContent, null, 2);

const compressed = compressToolResult(
  toolName,
  rawText,
  this.filterLevel ?? FilterLevel.STANDARD
);

return { ...result, content: compressed };
```

Add a `filterLevel?: FilterLevel` property to the `MCPClient` class constructor options so callers can override per-session.

---

## File to Modify (optional but recommended)

### `src/core/agent-loop.ts`

In `runAgentLoop()`, after `MCPRegistry` executes a tool call and before appending the result to the message history, add a `--compress` flag check:

```typescript
// If global flag --compress is set, apply aggressive filtering
const level = globalFlags.compress ? FilterLevel.AGGRESSIVE : FilterLevel.STANDARD;
```

Wire `level` through to `MCPClient` initialization.

### `src/index.ts` (Commander setup)

Add a global flag:

```typescript
program.option('--compress', 'Enable aggressive token compression on all tool outputs (uses RTK-style filtering)');
```

---

## Testing Requirements

Create `src/core/__tests__/tool-output-compressor.test.ts` using Vitest. Write test cases for:

1. `stripAnsi` — verify ANSI codes are removed, plain text is unchanged
2. `deduplicateLines` — verify repeated lines collapse correctly, threshold respected
3. `extractFailuresOnly` — with a mock `cargo test` output containing 10 passing + 2 failing tests, verify only failures remain
4. `groupErrorsByType` — with a mock SonarQube output of 15 lines across 3 rules, verify grouped output
5. `extractSignaturesOnly` with TypeScript — verify class + function signatures kept, bodies stripped
6. `summarizeJiraIssue` — verify all internal Jira fields stripped, key fields present
7. `compressToolResult` — verify fallback truncation fires at 8001 chars, compression note appended when > 20% saved
8. `summarizePipelineLog` — verify timestamp stripping, deduplication, failure-focus

---

## Constraints and Rules

- **Do not** install any new npm packages. Use only Node.js built-ins (`fs`, `path`, `util`) and TypeScript.
- **Do not** modify `hitl.ts`, `prompt-builder.ts`, or any prompt/agent markdown files.
- **Do not** change MCP tool names, JSON-RPC call structure, or message format sent to the LLM API.
- **Preserve** all JSON structure — if an MCP result is valid JSON, parse it, compress it, and re-serialize as JSON or markdown. Do not return malformed JSON.
- **Always** keep the full content when `FilterLevel.OFF` is set — used for debugging with `--verbose`.
- **Log** compression stats at `--verbose` level: `[compressor] get_file_content: 12,400 → 840 chars (93% saved)`
- The compressor must be **synchronous** — no async functions, no file I/O.
- All string manipulation must handle **UTF-8 correctly** — do not truncate mid-codepoint.

---

## Expected Token Savings by Workflow

| Forgeflow Command | Primary Compressed Tools | Expected Reduction |
|---|---|---|
| `implement` | `get_file_content`, `get_jira_issue`, `get_merge_request_diff` | 60–75% |
| `fix-pipeline` | `get_jenkins_console_output`, `get_build_log` | 80–90% |
| `fix-sonar` | `get_sonar_project_issues` | 65–75% |
| `plan-tasks` | `search_jira_issues`, `get_file_content` | 50–65% |
| `review` | `get_merge_request_diff`, `get_sonar_project_issues` | 60–70% |
| `analyze-logs` | `get_file_content` (log files) | 85–95% |
| `security-audit` | `get_nexus_iq_report`, `list_*` | 55–70% |

---

## Deliverables Checklist

- [ ] `src/core/tool-output-compressor.ts` — fully implemented with all functions and strategy map
- [ ] `src/core/mcp-client.ts` — modified to pipe tool results through compressor
- [ ] `src/core/agent-loop.ts` — wired to pass `FilterLevel` from global flags
- [ ] `src/index.ts` — `--compress` global flag added
- [ ] `src/core/__tests__/tool-output-compressor.test.ts` — all 8 test cases passing
- [ ] `src/types/index.ts` — `FilterLevel` exported from types barrel if needed

Run `npm test` and confirm all new tests pass before considering this task complete.
