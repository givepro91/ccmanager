## TypeScript Rules (auto-loaded for src/**/*.ts)

- Use `import type` for type-only imports
- No `any` — use `unknown` + type narrowing
- Prefer `interface` over `type` for object shapes
- Always use explicit return types on exported functions
- Use `node:` prefix for Node.js built-in imports (e.g., `node:fs/promises`)
- Prefer `const` assertions and `satisfies` operator where applicable
- Error handling: catch `unknown`, narrow with `instanceof`
