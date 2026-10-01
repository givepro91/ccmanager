# ccmanager

> Manage and sync Claude Code configurations across multiple projects.

A CLI that keeps one hub of shared Claude Code configuration (`CLAUDE.md`, rules, hooks, commands, settings) and pushes it into every project you register. Everything is local filesystem; no network calls.

> **Status (2026-10):** personal tool, `0.1.0`, not published to npm. The `ccmanager` name on npm belongs to a different project, so install from source.

## Install

```bash
git clone https://github.com/givepro91/ccmanager.git
cd ccmanager
npm install
npm run build
npm link        # exposes `ccm`
```

## Commands

| Command | What it does |
|---------|--------------|
| `ccm init` | Create the hub at `~/.ccm/` |
| `ccm add <path>` | Register a project |
| `ccm sync` | Push shared configs from the hub into every registered project |
| `ccm status` | List managed projects and their current config state |

## Concepts

- **Hub** (`~/.ccm/`) holds the shared configs and the project registry.
- **Project** is any directory with Claude Code config (`CLAUDE.md`, `.claude/`).
- **Sync** writes hub files into projects. It never overwrites without `--force` and prefers merging.

## Design rules

- Zero config to start: `ccm init && ccm add .` works on its own.
- Non-destructive by default.
- Offline-first. No network calls.
- Minimal dependencies, stdlib over packages.

## Development

```bash
npm run dev        # tsup watch
npm run test       # vitest
npm run typecheck  # tsc --noEmit
npm run lint
```

Node.js 18+, TypeScript 5 (strict), tsup (ESM), vitest, commander.

## License

MIT
