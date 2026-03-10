## Testing Rules (auto-loaded for tests/**/*.ts)

- Use vitest (`describe`, `it`, `expect`)
- Test file naming: `{module}.test.ts`
- Each command must have integration tests
- Use temp directories for filesystem tests (cleanup in `afterEach`)
- No mocking filesystem — use real temp dirs for accuracy
- Test both success and error paths
