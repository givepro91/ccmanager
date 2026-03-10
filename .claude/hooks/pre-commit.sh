#!/bin/bash
# Post-commit hook: verify build passes after commit

cd "$(git rev-parse --show-toplevel)" || exit 0

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  echo "WARNING: node_modules not found. Run 'npm install' first."
  exit 0
fi

# Verify TypeScript compilation
npx tsc --noEmit 2>/dev/null
if [ $? -ne 0 ]; then
  echo "WARNING: TypeScript errors detected. Run 'npm run typecheck' to see details."
fi

exit 0
