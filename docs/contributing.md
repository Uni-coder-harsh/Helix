---
owner: "@harsh"
version: "0.1.0"
status: "Draft"
last_updated: "2026-07-05"
reviewer: "@harsh"
dependencies: []
---

# Contributing Guidelines

Please consult the main [Contributing Guide](file:///home/harsh/Desktop/CodeNova/Helix/CONTRIBUTING.md) at the root of the repository for full details.

## Quick Reference

### Formatting Code
Run the following to format your code:
```bash
ruff check --fix .
black .
mypy .
```

### Pull Request Checklist
Before requesting review, confirm:
1. All lint and format checks pass.
2. The logic is fully documented.
3. The specification is frozen.
4. Your progress is logged in `progress.md`.
