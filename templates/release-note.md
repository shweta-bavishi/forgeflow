# Release Note Template

Confluence release note template. Generated content will be converted to Confluence HTML.

---

# Release Note — {{VERSION}} — {{DATE}}

## Overview

{{RELEASE_SUMMARY}}

High-level summary of what's in this release (2-3 sentences).

Example:
"This release brings significant improvements to user profile management and adds two-factor authentication support.
We've also resolved several critical bugs and improved API performance by up to 60%.
This is a recommended update for all users."

---

## What's New

### New Features

| Jira Key | Feature | Description |
|----------|---------|-------------|
| {{JIRA_KEY}} | {{FEATURE_TITLE}} | {{DESCRIPTION}} |
| PROJ-123 | Avatar Upload | Users can upload custom profile avatars with automatic compression |
| PROJ-124 | User Profiles | Enhanced profile editing with real-time validation |
| PROJ-125 | Two-Factor Auth | Added 2FA support for enhanced account security |

### Bug Fixes

| Jira Key | Issue | Impact |
|----------|-------|--------|
| {{JIRA_KEY}} | {{BUG_TITLE}} | {{IMPACT}} |
| PROJ-200 | Login Page Crash | Fixed null pointer exception when email field is empty |
| PROJ-201 | Session Handling | Properly handle expired sessions in middleware |
| PROJ-202 | Password Reset | Fixed email template rendering in password reset flow |

### Improvements & Performance

| Jira Key | Improvement | Details |
|----------|-------------|---------|
| {{JIRA_KEY}} | {{TITLE}} | {{DETAILS}} |
| PROJ-300 | Database Optimization | Reduced user profile load time by 60% |
| PROJ-301 | API Caching | Added Redis caching for frequently accessed endpoints |
| PROJ-302 | Error Messages | More helpful error messages for API consumers |

---

## ⚠️ Breaking Changes

**IMPORTANT**: The following changes require updates to your client code or configuration:

### Change 1: {{BREAKING_CHANGE_TITLE}}

**What changed:**
- **Old**: {{OLD_BEHAVIOR}}
- **New**: {{NEW_BEHAVIOR}}

**Why**: {{REASON}}

**Migration guide:**

{{MIGRATION_INSTRUCTIONS}}

Example:

### Change 1: API Endpoint Renamed

**What changed:**
- **Old**: `GET /api/users/me`
- **New**: `GET /api/users/current`

**Why**: Better semantic clarity. The new endpoint name makes it obvious this returns the currently authenticated user.

**Migration guide:**

Update your client code to use the new endpoint:

```javascript
// Before (old endpoint)
const user = await fetch('/api/users/me').then(r => r.json());

// After (new endpoint)
const user = await fetch('/api/users/current').then(r => r.json());
```

No other changes needed. The response format and data structure remain identical.

---

## 🔒 Security & Compliance

Security improvements and fixes in this release:

- **Fixed**: {{SECURITY_FIX_DESCRIPTION}}
- **Improved**: {{SECURITY_IMPROVEMENT_DESCRIPTION}}
- **Updated**: {{SECURITY_UPDATE_DESCRIPTION}}

Examples:
- **Fixed**: CSRF vulnerability in form submissions (CVE-XXXX-XXXXX)
- **Improved**: Authentication flow now includes rate limiting (5 attempts per minute)
- **Updated**: All dependencies patched to latest secure versions

---

## 📊 Known Issues

Issues or limitations you should be aware of:

| Issue | Severity | Status | Workaround |
|-------|----------|--------|-----------|
| {{ISSUE}} | {{SEVERITY}} | {{STATUS}} | {{WORKAROUND}} |
| Avatar editing not implemented | Medium | Planned for v{{NEXT_VERSION}} | Edit profile manually for now |
| Mobile sync delays 5-10s | Low | Investigating | Refresh screen if changes don't appear |
| Bulk export timeout (>10K records) | High | Planned fix v{{NEXT_VERSION}} | Export in smaller batches |

---

## 🚀 Upgrade Instructions

### Prerequisites

- Node.js 20+ (required for image processing)
- {{REQUIRED_PACKAGES}}

### Step 1: Pull Latest Code

```bash
git fetch origin
git checkout {{VERSION}}
# OR
git pull origin {{VERSION}}
```

### Step 2: Install Dependencies

```bash
npm install
```

If you encounter dependency conflicts:
```bash
npm install --legacy-peer-deps  # For Node 16
```

### Step 3: Run Database Migrations

If applicable:
```bash
npm run migrate
```

Check for migration instructions in MIGRATION.md file.

### Step 4: Verify Installation

```bash
npm run health-check
# Expected: All checks pass ✓
```

### Step 5: Start Service

```bash
npm start
# OR for production:
npm run start:prod
```

### Docker Users

```bash
docker pull {{DOCKER_REGISTRY}}/{{APP_NAME}}:{{VERSION}}
docker run -e NODE_ENV=production {{DOCKER_REGISTRY}}/{{APP_NAME}}:{{VERSION}}
```

---

## 📝 Documentation Updates

Updated or new documentation available:

- [API Reference]({{API_DOC_LINK}}) — Updated endpoints
- [Installation Guide]({{INSTALL_GUIDE_LINK}}) — Setup instructions
- [Migration Guide]({{MIGRATION_GUIDE_LINK}}) — Breaking changes guide
- [Security Guide]({{SECURITY_GUIDE_LINK}}) — 2FA setup and best practices

---

## 🙏 Contributors

Thank you to our contributors for this release:

| Contributor | Commits | Changes |
|-------------|---------|---------|
| @alice | 7 | Avatar feature implementation |
| @bob | 5 | Bug fixes and testing |
| @charlie | 3 | Documentation and UI improvements |

Special thanks to our testing team and community members for bug reports.

---

## 📥 Downloads & Artifacts

- **GitHub Release**: [v{{VERSION}} Release Page]({{GITHUB_RELEASE_URL}})
- **Docker Image**: `{{DOCKER_REGISTRY}}/{{APP_NAME}}:{{VERSION}}`
- **NPM Package**: [@yourorg/{{PACKAGE_NAME}}]({{NPM_PACKAGE_URL}})

---

## 🔗 Related Resources

- [Previous Release: v{{PREVIOUS_VERSION}}]({{PREVIOUS_RELEASE_NOTE}})
- [GitHub Commit Log]({{COMMIT_LOG_URL}})
- [Issue Tracker]({{ISSUE_TRACKER_URL}})
- [Support]({{SUPPORT_URL}})

---

## Feedback & Support

Have questions or issues?

- **Report Bugs**: [GitHub Issues]({{GITHUB_ISSUES_URL}})
- **Ask Questions**: [Discussions]({{DISCUSSIONS_URL}})
- **Email Support**: support@your-org.com
- **Documentation**: [Docs]({{DOCS_URL}})

---

**Release Date**: {{DATE}}
**Release Manager**: {{MANAGER_NAME}}
**Maintenance Until**: {{MAINTENANCE_END_DATE}} (Estimated)

---

*Generated by Otomate — Multi-Agent Development Workflow Orchestrator*
