# Merge Request Description Template

Use this template for all MR descriptions created by ForgeFlow. Replace placeholders with actual data.

---

## Summary

{{SUMMARY_OF_CHANGES}}

Brief 2-3 sentence overview of what this MR does and why it's important.

Example:
"This MR implements the avatar upload feature, allowing users to upload custom profile images.
Images are automatically validated for size and type, then compressed to 300x300px for optimal storage and display."

---

## Linked Jira Issues

**{{JIRA_KEY}}: {{ISSUE_TITLE}}**
[Link to Jira](https://jira.your-org.com/browse/{{JIRA_KEY}})

List all related issues:
- PROJ-123: Avatar Upload
- PROJ-124: User Profile Updates

---

## Acceptance Criteria

Checklist of acceptance criteria from the Jira task:

- [ ] Criterion 1: Users can upload image files
- [ ] Criterion 2: System validates file size < 5MB
- [ ] Criterion 3: Images are automatically compressed to 300x300px
- [ ] Criterion 4: Avatar URL is returned in response
- [ ] Criterion 5: Error messages are clear and helpful

---

## Files Changed

Summary of which files are affected:

**Created:**
- src/controllers/avatar.controller.ts
- src/services/avatar.service.ts
- src/dto/upload-avatar.dto.ts
- src/entities/avatar.entity.ts
- tests/avatar.service.spec.ts

**Modified:**
- src/app.module.ts (registered new providers)
- src/users/user.entity.ts (added avatarUrl field)

Total: +303 lines, -5 lines across 7 files

---

## Test Plan

How to verify this MR works:

### Unit Tests
```bash
npm test -- avatar.service.spec.ts
# Expected: All 6 tests pass
```

### Integration / Manual Testing
1. POST /users/1/avatar with valid image (JPG, <5MB)
   - Expected: 200 OK, returns avatarUrl
2. POST /users/1/avatar with file > 5MB
   - Expected: 400 Bad Request, "File too large"
3. POST /users/1/avatar with non-image file
   - Expected: 400 Bad Request, "Invalid file type"
4. GET /users/1 → Check avatarUrl field
   - Expected: Avatar URL is present and accessible

### Screenshots/Demo
[If this is a UI change, include screenshots]

---

## Performance Impact

Any performance considerations or optimizations:

- Image compression uses sharp library (optimized C++ bindings)
- File size validation is pre-compression (fast)
- Avatar metadata cached in Redis (if applicable)
- No performance regression expected

---

## Security Considerations

Any security implications:

- ✓ File type validation (only JPG, PNG, WebP)
- ✓ File size limit (prevents disk exhaustion)
- ✓ Filename sanitization (prevents path traversal)
- ✓ Access control (users can only upload their own avatars)
- ✓ CORS headers configured

---

## Breaking Changes

Any changes that break existing APIs or behavior:

None. This feature is purely additive.

[If there are breaking changes, list them with migration guide]

---

## Dependencies & Library Changes

Any new dependencies added:

```json
{
  "sharp": "^0.32.0",      // Image compression
  "multer": "^1.4.5-lts1"   // File upload handling
}
```

Run: `npm install` to get latest versions

---

## Reviewer Notes

Any specific things reviewers should focus on:

1. Check image compression logic in avatar.service.ts (line 45-67)
2. Verify error handling covers all edge cases
3. Ensure tests have adequate coverage (target: 80%+)
4. Check that file cleanup is working (temp files deleted)

---

## Deployment Notes

Any deployment or environment setup needed:

- Create /uploads/avatars/ directory (must exist before deployment)
- Ensure Node.js 20+ is running (sharp requires Node 14+, but we target 20)
- No database migrations required
- No environment variables need updating

---

## Related Docs

Links to relevant documentation:

- [Avatar API Specification](https://docs.your-org.com/avatar-api)
- [File Upload Best Practices](https://docs.your-org.com/uploads)
- [Image Processing Guidelines](https://docs.your-org.com/images)

---

## Checklist

Before merging, ensure:

- [ ] All tests pass (npm test)
- [ ] Linter passes (npm run lint)
- [ ] Code coverage is adequate (>80%)
- [ ] No console.log statements in production code
- [ ] JSDoc comments added to public methods
- [ ] TypeScript types are complete (no any types)
- [ ] Backwards compatible (no breaking changes)
- [ ] Reviewed by at least {{REQUIRED_REVIEWS}} approvers

---

**Created via ForgeFlow** — Multi-Agent Development Workflow Orchestrator
