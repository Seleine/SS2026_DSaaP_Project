# Contributing to SS2026_DSaaP_Project
Thank you for your interest in contributing to this project.
This document explains how to get involved, report issues, and submit changes to the Investigating Cat Movement Patterns analysis pipeline.

## Code of Conduct
Please be respectful and constructive in all interactions.
We welcome contributors of all backgrounds and experience levels.

## How Can I Contribute?
### Reporting Bugs
If you encounter unexpected behaviour (e.g. incorrect KDE output, crashes, wrong file paths), please open an issue and include:

- A clear, descriptive title
- Steps to reproduce the problem
- Your operating system and Python version (check .python-version)
- Any relevant error messages or tracebacks
- Sample data if possible (make sure no sensitive location data is included)

### Suggesting Enhancements
Have an idea to improve the analysis pipeline, add a new movement classifier, or support additional GPS formats?
Open an issue with the label enhancement and describe:

- What you'd like to see
- Why it would be useful
- Any implementation ideas you have in mind

### Submitting Pull Requests

- Fork the repository and clone your fork locally.
- Create a new branch from main.
- Make your changes.
- Run the tests to make sure nothing is broken.
- Open a pull request against main with a clear description of what you changed and why.

## Development Setup
See the README for full installation and setup instructions.

## Pull Request Process

- Make sure your branch is up to date with `main` before opening a PR.
- Ensure all existing tests pass (`uv run pytest tests/`).
- Add or update tests if your change affects analysis logic.
- Fill in the PR description with a summary of changes and any related issue numbers.
- A project maintainer will review your PR and may request changes before merging.

## License
By contributing to this project, you agree that your contributions will be licensed under the MIT License that covers this project.