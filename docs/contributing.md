# Contributing to Helix

Welcome and thank you for considering contributing to Helix! This document provides guidelines and instructions for contributing to the Helix project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please treat all contributors with respect and professionalism.

## Getting Started

1. **Fork and Clone**: Fork the repository on GitHub and clone your fork locally.
2. **Setup Development Environment**: Follow the instructions in `docs/getting_started.md` to set up both the backend (FastAPI) and frontend (Next.js) locally.
3. **Branching Strategy**: Create a new branch for your feature or bug fix:
   - `feature/your-feature-name`
   - `bugfix/issue-description`
   - `docs/what-you-are-documenting`

## Development Workflow

- **Issues**: Before starting work on a major feature, please check the issue tracker to see if someone is already working on it, or open a new issue to discuss your proposed changes.
- **Commits**: Write clear and descriptive commit messages.
- **Testing**: Ensure all tests pass. For the backend, run `make test`.
- **Linting & Formatting**: Run `make lint` and `make format` to ensure your code follows the project's stylistic guidelines (using `ruff` and `black` for Python, `eslint` for Next.js).

## Pull Requests

1. **Push Changes**: Push your branch to your forked repository.
2. **Open a PR**: Open a Pull Request against the `main` branch of the official Helix repository.
3. **Description**: Provide a clear description of the problem your PR solves or the feature it adds. Link any relevant issues.
4. **Review**: A maintainer will review your PR, request changes if necessary, and merge it when it's ready.

## Documentation

- **MkDocs Portal**: Our documentation uses MkDocs Material. It's hosted at `https://uni-coder-harsh.github.io/Helix/`.
- **Updating Docs**: When you make changes to the codebase, please update the corresponding documentation inside the `docs/` folder.
- **Architecture Changes**: Significant architectural changes should be proposed using an Architecture Decision Record (ADR) under `docs/adr/`.

Thank you for contributing to Helix!
