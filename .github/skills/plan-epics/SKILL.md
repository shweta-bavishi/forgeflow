---
name: plan-epics
description: "Plan epics from a Confluence requirements page. Parses requirements document, extracts feature areas, creates Jira epics with child stories, and updates Confluence with Jira links."
---

# Skill: Plan Epics

Parse a Confluence requirements page, extract feature areas as epics, break them into stories, create everything in Jira, and link back to Confluence.

## Phase 1: FETCH REQUIREMENTS

```
Call: get_confluence_page_full_content(page_id)
  ⚠ MUST use get_confluence_page_full_content, NOT get_confluence_page
  (The short version truncates content — requirements pages are always long)

IF page_id not provided:
  Ask developer: "Confluence page URL or ID?"

IF page has child pages:
  Call: get_page_children(page_id)
  Ask: "Include child pages in the analysis?"

Parse HTML structure:
  - H2/H3 headings → feature areas (potential epics)
  - Bullet lists → acceptance criteria
  - Tables → data specifications
  - Bold text → key requirements
  - Numbered lists → ordered requirements / steps
```

## Phase 2: EXTRACT FEATURES

```
FOR EACH feature area identified:

  Create epic candidate:
    - Epic name (from heading)
    - Epic description (from section content)
    - Child stories (from sub-sections or bullet groups)

  FOR EACH story within epic:
    - Story title (concise action)
    - Acceptance criteria (from bullets)
    - Story points estimate (based on complexity)
    - Priority (from document emphasis or order)

  Map dependencies between epics/stories
```

## Phase 3: PRESENT EPIC PLAN

```
## Proposed Epics from "{page_title}"

### Epic 1: {name}
Description: {summary}
Stories:
  1. {story_title} ({points}pts) — {criteria_count} acceptance criteria
  2. {story_title} ({points}pts) — {criteria_count} acceptance criteria

### Epic 2: {name}
...

Summary: {N} epics, {M} stories, {total} story points

Dependencies:
  Epic 1 → Epic 2 (Epic 2 requires API from Epic 1)
```

## Phase 4: 🚦 HITL GATE — Developer Reviews Plan

```
Developer can:
  - Add/remove epics or stories
  - Modify story points
  - Change priorities
  - Adjust scope
  - Re-word titles or descriptions
  - Add missing acceptance criteria
  - Change dependency mapping

Multi-round refinement until approved
```

## Phase 5: CREATE IN JIRA

```
STEP 1 — Prerequisite:
  Call: get_jira_project_info(config.jira.project_key)
  → Fetch valid issue types and field IDs (REQUIRED before any creation)

STEP 2 — Create epics with stories:
  FOR EACH approved epic:
    Call: create_epic_with_issues(
      project_key: config.jira.project_key,
      epic_name: epic.name,
      epic_description: epic.description,
      issues: [
        { summary: story.title, description: story.description,
          issue_type: config.jira.story_issue_type,
          story_points: story.points }
      ]
    )
    → Single call creates epic + ALL child stories (efficient)

STEP 3 — Link dependencies:
  Call: link_issues(epic_1_key, epic_2_key, "Blocks")

STEP 4 — Assign to sprint (if requested):
  Call: get_project_sprints(config.jira.project_key)
  Call: move_issue_to_sprint(issue_key, sprint_id)
```

## Phase 6: UPDATE CONFLUENCE

```
Call: update_confluence_page(page_id)
  Add Jira links next to each requirement section:
  "→ Jira: PROJ-100 (Epic), PROJ-101, PROJ-102, PROJ-103 (Stories)"

  Preserves existing page content, appends links
```

## Phase 7: SUMMARY

```
✓ Created {N} epics:
  - PROJ-100: {name} ({M} stories, {P} points)
  - PROJ-110: {name} ({M} stories, {P} points)

✓ Created {total} stories across all epics
✓ Linked dependencies
✓ Updated Confluence page with Jira references

→ Next: "Plan dev tasks for PROJ-100?"
```

## Error Handling

```
Page not found → ask for correct page ID/URL
Empty content → inform developer, cannot proceed
Jira creation fails → show error, offer retry or manual
Confluence update fails → Jira epics still valid, note update failure
```
