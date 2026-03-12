---
applyTo: "src/**"
---

# Coding Standards — Source File Instructions

These rules apply when generating, editing, or reviewing source code files.

## Code Generation Rules

1. **Read before write**: Always read at least 2-3 existing files in the same layer/directory to understand established patterns before generating new code.
2. **Match conventions exactly**: Follow the project's naming, import style, error handling, and documentation patterns as detected from existing code and `otomate.config.yml`.
3. **No stubs or placeholders**: Every generated file must be complete and production-ready. Never output `// TODO: implement this` for core logic.
4. **Full type safety**: Include all type definitions, interfaces, and generics. No `any` types unless justified.
5. **Error handling is mandatory**: Every service method must handle errors. Every controller must return proper HTTP status codes for error cases.
6. **JSDoc on public methods**: Every public method and class must have JSDoc documentation with `@param`, `@returns`, and `@throws` annotations.
7. **Input validation**: Use framework-appropriate validation (class-validator decorators for NestJS, Pydantic for FastAPI, Bean Validation for Spring).

## Naming Conventions (from config)

| Element | Convention | Example |
|---------|------------|---------|
| Files | kebab-case | `avatar-service.ts`, `user.entity.ts` |
| Directories | kebab-case | `src/user-service/`, `src/auth-guards/` |
| Classes | PascalCase | `UserService`, `AvatarController` |
| Functions | camelCase | `getUserById`, `createAvatarUpload` |
| Constants | UPPER_SNAKE_CASE | `MAX_FILE_SIZE`, `DEFAULT_TIMEOUT` |
| Interfaces | PascalCase | `IUserRepository`, `UserCreateRequest` |
| Variables | camelCase | `userId`, `isActive` |

## Architecture Layer Rules

Dependencies flow downward only:
- Controllers → Services (allowed)
- Services → Repositories (allowed)
- Repositories → Entities (allowed)
- Controllers → Repositories (VIOLATION — always go through services)
- Services → Controllers (VIOLATION — reverse dependency)

## Test Generation Rules

1. Every new source file MUST have a corresponding test file matching `config.coding_standards.test_pattern`.
2. Tests use Arrange-Act-Assert (AAA) pattern.
3. Each test covers ONE behavior.
4. Mock external dependencies (databases, APIs, file systems).
5. Test naming: descriptive `it('should reject files larger than 5MB')`, not `it('test1')`.
6. Cover: happy path, error cases, boundary conditions, edge cases.

## Forbidden Patterns

- `console.log` in production code (use proper logger)
- `debugger` statements
- Hardcoded secrets, tokens, or credentials
- `any` type without comment explaining why
- Empty catch blocks
- Magic numbers without named constants
- Synchronous file I/O in async contexts
