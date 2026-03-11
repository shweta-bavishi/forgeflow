# Workflow 02: Plan Epics

**Goal**: Parse a Confluence requirements page and create a structured epic breakdown. After developer approval, create Jira epics linked to the requirements.

**Trigger**: "Plan epics from Confluence page {url/id}", "Create epics from requirements"

**Agents**: Orchestrator → Confluence Agent, Jira Agent, Project Context Agent

**Time**: ~15 minutes (parsing + approval + creation)

## Phase 1: FETCH & PARSE

### Identify the Requirements Page

Developer provides either:
- Confluence URL: `https://confluence.com/pages/12345`
- Page ID: `12345`
- Page title: `Q4 Requirements`

If URL → Extract page ID
If title → Search for page in Confluence space

### Fetch Full Content

**CRITICAL**: Use `get_confluence_page_full_content` (not `get_confluence_page`)
- Returns complete content without truncation
- Necessary for parsing detailed requirements

### Parse HTML Structure

```
Look for hierarchy in HTML:
  <h2> "User Authentication" → Epic candidate
    <h3> "Login Implementation" → Story candidate
      <ul><li> "User enters email" → Acceptance criterion
  <h2> "Payment Processing" → Epic candidate
    <h3> "Credit Card Support" → Story candidate
```

### Extract Information

For each potential epic:
- **Name**: From heading text
- **Description**: Paragraph following heading (or generate from context)
- **Priority**: Keywords in content
  - "must have", "critical", "phase 1", "MVP" → HIGH
  - "nice to have", "future", "phase 2" → LOW
- **Acceptance Criteria**: Bullet points under story headings

### Discover Child Pages

Call `get_page_children` to find detailed sub-pages
- May contain additional requirements details
- Extract and incorporate into epic descriptions

## Phase 2: ANALYZE & STRUCTURE

For each identified epic:

```
1. Group related requirements
   - Which stories belong together?
   - Are there sub-features?

2. Determine characteristics:
   - **Epic name**: Concise, business-focused
   - **Epic description**: What value does it deliver?
   - **Estimated stories**: How many stories will this require?
   - **Priority**: High/Medium/Low
   - **Dependencies**: Does epic A block epic B?
   - **Affected components**: From project architecture

3. Validate scope:
   - Is this epic-sized (too big for one sprint)?
   - Are sub-features well-defined?
   - Can stories be independently delivered?
```

## Phase 3: PRESENT TABLE

Show developer formatted table:

```
| # | Epic Name | Description | Est. Stories | Priority | Dependencies |
|----|-----------|-------------|--------------|----------|--------------|
| 1  | User Auth | Login, registration, password reset | 4 | HIGH | None |
| 2  | Avatar Support | Upload, display, delete avatars | 2 | MEDIUM | Requires Epic 1 |
| 3  | Payment Processing | Accept credit card payments | 5 | HIGH | None |

Under each epic, list identified stories:
  Epic 1: User Authentication
    - Login Implementation (3 acceptance criteria)
    - Registration Flow (2 acceptance criteria)
    - Password Reset (2 acceptance criteria)
    - Social Login (OAuth) (2 acceptance criteria)
```

## Phase 4: 🚦 HITL GATE — Developer Approves Epic List

Developer reviews and can:

```
1. EDIT epic names/descriptions
   "User Auth" → "User Authentication & Authorization"

2. MERGE epics
   "Avatar Support" + "Profile Management" → "User Profiles"

3. SPLIT epics
   "Payment Processing" → "Credit Cards" + "PayPal" + "Subscriptions"

4. ADJUST priorities
   "Avatar Support" from MEDIUM → LOW (lower priority)

5. ADD missing epics
   "Reporting" (not in requirements but needed)

6. REMOVE irrelevant epics
   "Nice-to-have feature XYZ" → Remove

7. REORDER
   Change presentation order

Support multi-round refinement:
  Developer: "The avatar epic looks too small"
  Agent: "Should I merge it with user profiles?"
  Developer: "Yes, merge those"
  Agent: [Shows updated list]
  Developer: "Perfect!"
```

## Phase 5: CREATE JIRA EPICS

For each approved epic:

### Prerequisites

```
Call: get_jira_project_info(project_key)
  - Fetch valid issue types
  - Identify Epic issue type name
  - Extract custom field IDs (story_point_field, etc.)
```

### Create Epics & Stories

**BEST PRACTICE**: Use `create_epic_with_issues` (single call creates epic + child stories)

```
Call: create_epic_with_issues(
  epic_name: "User Authentication",
  epic_description: "Enable users to securely log in, register, and reset passwords",
  child_issues: [
    {
      title: "Login Implementation",
      type: "Story",
      description: "Users can log in with email/password"
    },
    {
      title: "Registration Flow",
      type: "Story",
      description: "Users can create new accounts"
    },
    ...
  ]
)
→ Returns: PROJ-100 (epic), PROJ-101, PROJ-102, ... (stories)
```

### Link Dependent Epics

If Epic A blocks Epic B:
```
Call: link_issues(
  key1: "PROJ-100",
  key2: "PROJ-200",
  link_type: "Blocks"
)
```

### Error Handling

If creation fails:
```
- If issue type name wrong: Show available types, ask to confirm
- If custom fields missing: Suggest adding to config, retry
- If permission denied: Check Jira credentials
- If partial failure: Show what succeeded, retry failed items
```

## Phase 6: UPDATE CONFLUENCE

Append section to original requirements page:

```
## Created Epics (via ForgeFlow)

| Jira Key | Epic Name | Priority | Status |
|----------|-----------|----------|--------|
| PROJ-100 | User Authentication | HIGH | To Do |
| PROJ-200 | Avatar Support | MEDIUM | To Do |
| PROJ-300 | Payment Processing | HIGH | To Do |

Created on {date} via ForgeFlow
```

Call: `update_confluence_page` with incremented version

## Output Summary

```
✓ Analyzed Confluence page: {page_title}
✓ Identified {N} epics with {M} total stories
✓ Created {N} Jira epics:
  - PROJ-100: User Authentication (4 stories)
  - PROJ-200: Avatar Support (2 stories)
  - PROJ-300: Payment Processing (5 stories)
✓ Updated Confluence page with epic links

NEXT STEPS:
  1. Plan dev tasks for each epic (03-plan-dev-tasks)
  2. Assign stories to sprints
  3. Start implementation (04-implement-dev-task)
```

## Error Recovery

### If requirements page not found

```
→ Ask: "Do you know the page ID? Check Confluence and provide it."
→ Or: "What is the page title? I'll search for it."
```

### If page structure doesn't match expected format

```
→ Adapt parsing: "I see the page has a different structure."
→ Ask: "How are epics organized? By headings? Tables?"
→ Extract what you can
→ Ask developer to clarify ambiguous sections
```

### If Jira creation fails for some epics

```
→ Show: "Created 2/3 epics successfully"
→ List: Which ones failed and why
→ Offer: Retry failed ones, skip, or create manually
```

## Success Criteria

✓ Requirements page is parsed successfully
✓ Epics are logically grouped and named
✓ Jira epics are created with proper links
✓ Developer approves epic structure before creation
✓ Confluence is updated with epic links
✓ All epics have clear descriptions and priorities

---

**Duration**: 15 minutes

**What It Creates**: Jira epics + updated Confluence page

**Next Workflow**: 03-plan-dev-tasks (break each epic into dev tasks)

**Related**: Confluence Agent, Jira Agent
