# Workflow 08: Create Release Note

**Goal**: Generate a comprehensive release note from release data and publish to Confluence.

**Trigger**: "Create release note for v{version}", "Publish release notes for v{version}"

**Agents**: Orchestrator → Confluence Agent, Jira Agent, GitLab Agent, Project Context Agent

**Time**: ~15 minutes (gathering data + generation + approval + publishing)

## Phase 1: GATHER RELEASE DATA

### Extract Version & Date

Developer provides version (e.g., v2.4.1)
Use today's date for release date

### Fetch Git Data

```
Call: get_project_pipelines(branch: "release/v2.4")
Extract:
  - Recent commits since previous tag
  - Commit messages and authors

Call: get_file_content("Changelog.md" or similar)
Extract:
  - Any existing changelog
  - Previous release notes for comparison
```

### Fetch Jira Data

```
Call: search_jira_issues(
  jql: "fixVersion = v2.4.1"
)
Extract:
  - All issues in this release
  - Categorize by type:
    - Story (Features)
    - Bug (Bug Fixes)
    - Task/Improvement (Improvements)

Extract:
  - Issue key, title, description
  - Labels (e.g., "breaking-change")
  - Priority
```

### Categorize Changes

```
NEW FEATURES:
  - Issue type = Story
  Examples:
    - PROJ-123: Avatar Upload
    - PROJ-124: User Profiles

BUG FIXES:
  - Issue type = Bug
  Examples:
    - PROJ-200: Login page crash
    - PROJ-201: Invalid session handling

IMPROVEMENTS:
  - Issue type = Task/Improvement
  Examples:
    - PROJ-300: Performance optimization
    - PROJ-301: Documentation update

BREAKING CHANGES:
  - Issues with label: "breaking-change"
  - Or mentioned in descriptions
  Examples:
    - API endpoint /users/me renamed to /users/current
    - Database schema version bumped to v3
```

### Identify Known Issues

```
Search for:
  - Issues still open with this fixVersion
  - Known limitations
  - Defer to next release
Examples:
  - PROJ-400: Avatar editing not yet implemented (v2.5)
  - PROJ-401: Mobile app sync issues (investigating)
```

### Extract Contributors

```
From commits in release:
  - Get commit authors
  - Count commits per author
  - Compile contributor list
Examples:
  - @alice (7 commits)
  - @bob (5 commits)
  - @charlie (2 commits)
```

## Phase 2: GENERATE RELEASE NOTE CONTENT

Load template: `templates/release-note.md`

Fill template variables:

```yaml
{{version}}: "v2.4.1"
{{date}}: "March 11, 2026"
{{summary}}: "Release includes avatar support, user profiles, and critical bug fixes"

{{features_table}}: |
  | Jira Key | Title | Description |
  | PROJ-123 | Avatar Upload | Users can upload custom avatars... |
  | PROJ-124 | User Profiles | Enhanced user profile management... |

{{bugfixes_table}}: |
  | Jira Key | Title |
  | PROJ-200 | Login page crash... |
  | PROJ-201 | Session handling fix... |

{{improvements_table}}: |
  | Jira Key | Title |
  | PROJ-300 | Performance optimization... |

{{breaking_changes}}: |
  ## ⚠️ Breaking Changes

  ### API Endpoint Renamed
  The `/users/me` endpoint has been renamed to `/users/current`
  to better reflect its functionality.

  Migration: Update all client code references:
    - Old: GET /users/me
    - New: GET /users/current

{{known_issues}}: |
  ## Known Issues

  - Avatar editing coming in v2.5 (PROJ-400)
  - Mobile app sync issues being investigated (PROJ-401)

{{contributors}}: |
  ## Contributors
  - @alice (7 commits)
  - @bob (5 commits)
  - @charlie (2 commits)

{{upgrade_instructions}}: |
  ## Upgrade Instructions

  1. Pull latest code: git pull origin release/v2.4
  2. Install dependencies: npm install
  3. Run migrations (if any): npm run migrate
  4. Start service: npm start
  5. Verify: npm run health-check
```

### Generate HTML for Confluence

Convert markdown to Confluence markup:
- Headings → `<h1>`, `<h2>`, etc.
- Tables → `<table>` with rows
- Bold/italic → `<strong>`, `<em>`
- Links → `<a>`
- Lists → `<ul>` / `<ol>`

## Phase 3: 🚦 HITL GATE — Developer Reviews Content

```
Show complete release note preview:

## Release Note — v2.4.1 — March 11, 2026

### Overview
This release includes 5 new features, 4 critical bug fixes, 3 improvements,
and documentation updates. [Full summary]

### New Features
| Jira Key | Title | Description |
| --- | --- | --- |
| PROJ-123 | Avatar Upload | ... |
| ... |

### Bug Fixes
[Similar table]

### Improvements
[Similar table]

### Breaking Changes
[Details]

### Known Issues
[List]

### Contributors
[List with counts]

---

Developer can:
  1. APPROVE "Looks good"
  2. REQUEST CHANGES "Add more detail to feature X"
  3. EDIT TEXT "Change this wording"
  4. ADD SECTIONS "Include performance improvements"

Support multi-round refinement until approved
```

## Phase 4: PREPARE CONFLUENCE PAGE

### Check if Page Exists

```
Target location:
  Space: from config.confluence.space_key
  Parent page: from config.confluence.release_notes_parent_page_id

Call: get_page_children(parent_page_id)
Check if page already exists:
  "Release Note — v2.4.1"

If exists:
  Ask: "Page exists. Update or create new?"
```

### Determine Page Structure

```
Parent page: "Release Notes"
  ├── Child: "Release Note — v2.4.0 — Jan 1, 2026"
  ├── Child: "Release Note — v2.4.1 — Mar 11, 2026" (NEW)
  └── Child: "Release Note — v2.3.5 — Nov 1, 2025"
```

## Phase 5: PUBLISH TO CONFLUENCE

```
Call: create_confluence_page(
  space_key: from config,
  parent_page_id: from config.release_notes_parent_page_id,
  title: "Release Note — v2.4.1 — March 11, 2026",
  body: [generated HTML content]
)

Returns: page_id, page_url

Show developer: "Release note published"
  Link: {url_to_confluence_page}
```

## Phase 6: UPDATE ISSUE LINKS

For each Jira issue in release:

```
Call: update_jira_issue(
  key: issue_key,
  add_comment: "Release note: {confluence_page_url}"
)

Example comment:
  "Released in v2.4.1
   Release Note: https://confluence.com/pages/{page_id}"

Result:
  ✓ PROJ-123: Added release note link
  ✓ PROJ-124: Added release note link
  ✓ PROJ-125: Added release note link
  ...
```

## Phase 7: FINAL SUMMARY

```
## Release Note Published ✓

**Version**: v2.4.1
**Date**: March 11, 2026
**Page**: Release Note — v2.4.1

### Content Summary
- Features: 5 new features documented
- Bug Fixes: 4 critical fixes documented
- Improvements: 3 improvements documented
- Breaking Changes: 1 documented with migration guide
- Known Issues: 2 documented
- Contributors: 3 team members listed

### Confluence Link
https://confluence.com/display/ENG/Release+Note+v2.4.1

### Jiras Updated
Linked release note in 12 issue comments

### Next Steps
1. Share release note with stakeholders
2. Announce release to team
3. Deploy to production (if applicable)
4. Monitor for feedback/issues
```

## Error Handling

### If Confluence space not found

```
→ Check: config.confluence.space_key
→ Ask: What is the correct space key?
→ Retry with correct value
```

### If parent page not found

```
→ Check: config.confluence.release_notes_parent_page_id
→ Ask: Where should release notes go?
→ Create at root or specify parent
```

### If Jira fetch fails

```
→ Proceed with partial data
→ "Couldn't fetch Jiras, but I can create note from git commits"
→ Show what we have
```

### If page already exists

```
→ Ask: "Overwrite or create new version?"
→ If update: Version number incremented automatically
→ If new: Append to title or use alternate name
```

## Content Guidelines

### For Features

```
Good:
  "Users can now upload custom avatars with automatic
   compression to 300x300px. Supported formats: JPG, PNG, WebP.
   File size limited to 5MB."

Bad:
  "Avatar support added"
```

### For Breaking Changes

```
Always include:
  - What changed
  - Why it changed
  - How to migrate/upgrade
  - Any deprecation warnings
```

### For Known Issues

```
Include:
  - What the issue is
  - Impact (severity)
  - When it will be fixed (if known)
  - Workaround (if any)
```

## Success Criteria

✓ All release issues are captured
✓ Changes are categorized correctly
✓ Breaking changes clearly documented with migration steps
✓ Developer reviews and approves content
✓ Confluence page is published at correct location
✓ All issues linked back to release note
✓ Contributors acknowledged

---

**Duration**: 15 minutes

**What It Creates**:
- Confluence release note page
- Links from Jira issues to release note

**Next Steps**:
- Share with stakeholders
- Announce release
- Monitor feedback

**Related**: Confluence Agent, Jira Agent, GitLab Agent

**Template**: templates/release-note.md (used for content generation)
