# Project: K1 robot soccer, aimed at the real robot

This fork trains Booster K1 football skills that run on the real robot through
`../k1_policy_runner`. Before working on anything, read `knowledge/INDEX.md`;
objectives and standing decisions are in `knowledge/objectives.md` and must not
change without asking the user. The target layout and the evolution-loop design
are in `knowledge/architecture.md`.

Deploy-first rules:

- What a policy observes or outputs (observation slots, action scales, PD, ball
  frame, lost rule, head tracker, speed caps, joint/torque clips, delay) is the
  deployment contract in `knowledge/deployment.md`. A change to it is a runtime
  change: record the matching k1_policy_runner change, pass the parity check, and
  say so in the commit. Rewards and DR inside approved ranges are training-only.
- Do not edit `../k1_policy_runner` from work in this repo.
- Run the safety net (`tests/golden/README.md`) before and after code changes and
  after every merge; a failure means behaviour changed.
- Shared defaults (ball model, reward weights, caps) affect every task built on
  them: change them only deliberately and re-run the safety net.
- Use `.venv/bin/python -m pytest`; evals with `timeout -k 30 N .venv/bin/python ...`.
- Work starts from a task request (`tasks/<name>/request.yaml`: what is asked and
  how it is judged; `rsw request list`); approaches to try are in
  `knowledge/approaches/` by element, with sources and our results (`rsw approaches`).
- Train from a recipe (`experiments/recipes/`), not a bare task: `rsw recipe check`,
  `rsw train RECIPE` (dry run; `--go` to train), `rsw check` for the safety net. The
  deployed kick champion's setup is `kick/kick_stage3_h022.yaml`.

# Development Workflow

**Always use `uv run`, not python**.

```sh

# 1. Make changes.

# 2. Type check.
uv run ty check  # Fast
uv run pyright  # More thorough, but slower

# 3. Run tests.
uv run pytest tests/  # Single suite
uv run pytest tests/<test_file>.py  # Specific file

# 4. Format and lint before committing.
uv run ruff format
uv run ruff check --fix
```

We've bundled common commands into a Makefile for convenience.

```sh
make format     # Format and lint
make type       # Type-check
make check      # make format && make type
make test-fast  # Run tests excluding slow ones
make test       # Run the full test suite
make docs       # Build documentation
```

Always run `make check` before committing. This runs formatting, linting,
and type checking. Do not commit code that fails type checking.

Before creating a PR, ensure all checks pass with `make test`.

When making user-facing changes, add an entry to `docs/source/changelog.rst`
under the "Upcoming version (not yet released)" section using
Added/Changed/Fixed categories. Reference issues with `:issue:\`123\``
(renders as a link to the GitHub issue).

# Commits and PRs

- Put `Fixes #<number>` at the end of the commit message body, not in
  the title.
- PR body should be plain, concise prose. No section headers, checklists,
  or structured templates. Describe the problem, what the change does, and
  any non-obvious tradeoffs. A good PR description reads like a short
  paragraph to a colleague, not a form.
- PR and commit messages are rendered on GitHub, so don't hard-wrap them
  at 88 columns. Let each sentence flow on one line.

Some style guidelines to follow:
- Line length limit is 88 columns. This applies to code, comments, and docstrings.
- Avoid local imports unless they are strictly necessary (e.g. circular imports).
- Tests should follow these principles:
  - Use functions and fixtures; do not use test classes.
  - Favor targeted, efficient tests over exhaustive edge-case coverage.
  - Prefer running individual tests rather than the full test suite to improve iteration speed.
