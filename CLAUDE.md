# ccmanager

CLI tool to manage and sync Claude Code configurations across multiple projects.
Central hub for CLAUDE.md, rules, hooks, commands, and settings.

## Language

- All code, comments, docs, and commit messages in **English** (global open source)
- Author communication in Korean is fine

## Tech Stack

| Area | Technology |
|------|-----------|
| Runtime | Node.js 18+ |
| Language | TypeScript 5 (strict mode) |
| Build | tsup (ESM) |
| Test | vitest |
| CLI | commander |
| Lint | eslint |
| Package | npm (published as `ccmanager`) |

## Architecture

```
ccmanager/
├── src/
│   ├── cli.ts              # Entry point, command registration
│   ├── commands/            # CLI command handlers
│   │   ├── init.ts          # `ccm init` - initialize hub
│   │   ├── add.ts           # `ccm add` - register project
│   │   ├── sync.ts          # `ccm sync` - push configs to projects
│   │   └── status.ts        # `ccm status` - show managed projects
│   ├── core/                # Business logic
│   │   ├── config.ts        # Hub config (ccm.yaml) management
│   │   └── sync-engine.ts   # File sync logic
│   └── utils/               # Shared utilities
├── tests/                   # vitest tests
├── package.json
├── tsconfig.json
└── tsup.config.ts
```

## Core Concepts

- **Hub** (`~/.ccm/`): Central directory storing shared configs and project registry
- **Project**: Any directory with Claude Code config (CLAUDE.md, .claude/)
- **Sync**: Push shared configs from hub to registered projects
- **Collect**: Read project's current config state for status display

## CLI Commands

| Command | Description |
|---------|-------------|
| `ccm init` | Initialize hub directory |
| `ccm add <path>` | Register a project |
| `ccm sync` | Sync shared configs to all projects |
| `ccm status` | Show all managed projects |

## Principles

- **Zero config to start**: `ccm init && ccm add .` should just work
- **Non-destructive**: Never overwrite without `--force`, prefer merge
- **Offline-first**: No network calls, everything is local filesystem
- **Minimal dependencies**: stdlib > npm packages
- **Global-ready**: All user-facing strings in English, i18n-friendly

## Development

```bash
npm install
npm run build          # Build with tsup
npm run dev            # Watch mode
npm run test           # Run tests
npm run typecheck      # TypeScript check
npm link               # Install globally for local testing
```

## Git Convention

```
feat: new feature      | fix: bug fix
refactor: restructure  | test: add/update tests
docs: documentation    | chore: config/tooling
```

## Quality Rules

- All exports must have JSDoc
- No `any` types — use `unknown` and narrow
- Every command must have a corresponding test
- `npm run build && npm run test` must pass before commit
- Keep bundle size minimal — check with `du -sh dist/`

## Critical Rules

1. **Never break existing project configs** — sync is additive, not destructive
2. **No network calls** in core logic — this is a local tool
3. **Test every command** — untested code doesn't ship
4. **ESM only** — no CommonJS, no dual builds
