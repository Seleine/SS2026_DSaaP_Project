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

- Make sure formatting and linting is correct (enter `uvx ruff check --fix` and `uvx ruff format` in terminal)
- Make sure your branch is up to date with `main` before opening a PR.
- Ensure all existing tests pass (`uv run pytest tests/`).
- Add or update tests if your change affects analysis logic.
- Fill in the PR description with a summary of changes and any related issue numbers.
- A project maintainer will review your PR and may request changes before merging.


## Docker
If you want to contribute to the project but don't want to set up the development environment locally, you can use Docker.
The Dockerfile is located in the root of the repository and can be used to build a Docker image with all dependencies installed.
To build the Docker image, run the following command in the terminal:

### Set up Docker and build image
To build a new Docker container the Desktop App has to be downloaded from their website:
https://www.docker.com/products/docker-desktop/
The GitHub Account can be used to set up an account.
After downloading and installing the Docker Desktop App, the following command can be used to build the Docker image:
```bash
docker desktop start 
docker build -t cat-movement-analysis .
```

Once the image is built, you can run a container with the following command:

```bash
docker run --rm cat-movement-analysis
```

To enter the container and work on the project files, run:

```bash
docker run --rm -it --entrypoint /bin/bash cat-movement-analysis # enter container
exit # exit container
```

To save and later access the .html output from outside the container enter:

```bash
mkdir plots
docker compose up analysis # run analysis & save output in plots folder
docker compose down # stop container
```

To run tests/ linter/ fomater inside the container, use:

```bash
docker compose run --rm tests # run tests
docker compose run --rm lint
docker compose run --rm format
docker compose run --rm lint-fix
docker compose run --rm format-fix
docker compose down # stop container
```

## License
By contributing to this project, you agree that your contributions will be licensed under the MIT License that covers this project.