![CI](https://github.com/Srishanth57/ai-repo-migrator/actions/workflows/ci.yml/badge.svg)

# AI Repository Migration Agent

An agentic CLI tool that upgrades code through **tested, sandboxed, human-reviewed** changes — not a chatbot that edits files, but a verification loop that makes AI-generated code changes safe to trust.

## The problem this solves

Codebases rot: libraries deprecate, languages evolve, APIs change their signatures. This kind of migration work is tedious, error-prone, and easy to get subtly wrong. An LLM can generate a plausible-looking fix in one shot — but the hard problem isn't generating a fix, it's making that fix **safe to accept without a human re-reading every line**.

This project answers that with three mechanisms:

1. **Sandboxing** — generated code never runs on the host machine. It's tested inside a disposable Docker container.
2. **Test-gating** — a change is only surfaced to a human if it passes the project's existing test suite.
3. **Human-in-the-loop** — even after passing tests, nothing is kept until the user explicitly approves the diff.

This is the same _generate → sandbox-execute → verify → human-approve_ pattern used by production coding agents, scoped down to something buildable and demoable.

## Tech stack

- **Python** — orchestration, CLI
- **Google Gemini API** (`google-genai` SDK) — code generation
- **Docker** — isolated test execution
- **Typer** — CLI interface
- **pytest** — test running (both for the tool itself, and for the target repo being migrated)
- **GitHub Actions** — CI pipeline

## Architecture

```
                     ┌─────────────────────┐
                     │   CLI (Typer)         │  python cli.py run app.py
                     └─────────┬────────────┘
                               │
                     ┌─────────▼────────────┐
                     │  Orchestrator (agent.py) │
                     │  - reads target file      │
                     │  - builds prompt          │
                     │  - calls Gemini             │
                     │  - writes candidate code   │
                     └─────────┬────────────┘
                               │
              ┌────────────────┼─────────────────┐
              ▼                                    ▼
     ┌─────────────────┐                 ┌──────────────────────┐
     │ Gemini API         │                 │ Docker Sandbox Runner │
     │ (llm.py)            │                 │ (sandbox.py)            │
     │ - full-file rewrite │                 │ - copies code to a temp │
     │   given old code +   │                 │   dir                    │
     │   instruction         │                 │ - runs pytest inside a  │
     └─────────────────┘                 │   disposable container   │
                                            └──────────┬──────────┘
                                                       │
                                            ┌──────────▼──────────┐
                                            │ Result Handler          │
                                            │ (agent.py)               │
                                            │ - if tests pass: show    │
                                            │   diff, ask for human    │
                                            │   confirmation             │
                                            │ - if tests fail: feed      │
                                            │   error back to Gemini,    │
                                            │   retry (max 2x)            │
                                            └────────────────────┘
```

### Workflow, step by step

1. `cli.py` parses the command and calls `migrate(filepath, instruction)` in `agent.py`.
2. `agent.py` reads the target file into memory.
3. `llm.py` sends the code + a migration instruction to Gemini and gets back a rewritten version of the file.
4. `agent.py` writes the candidate code to disk.
5. `sandbox.py` copies the surrounding folder into a fresh temp directory, then shells out to `docker run`, mounting that temp directory into a disposable `python:3.11-slim` container and running `pytest` inside it — completely isolated from the host machine.
6. If tests pass, `agent.py` prints a unified diff of the change and prompts the user to approve or reject it.
7. If tests fail, the pytest error output is fed back into the next Gemini call as `error_feedback`, and the loop retries (up to 2 times) before giving up and restoring the original file.

## Project structure

```
ai-repo-migrator/
├── .github/workflows/ci.yml   # GitHub Actions pipeline
├── agent.py                    # orchestration loop
├── llm.py                      # Gemini API calls
├── sandbox.py                  # Docker-based test execution
├── cli.py                      # Typer CLI entrypoint
├── test_llm.py                 # unit tests (mocked Gemini calls)
├── test_sandbox.py             # unit tests (mocked Docker calls)
├── sample_repo/                # example "legacy" repo used for demos
│   ├── app.py
│   └── test_app.py
├── requirements.txt
└── .env                        # GEMINI_API_KEY (not committed)
```

## Setup

**Prerequisites:** Python 3.11+, Docker Desktop, a [Gemini API key](https://aistudio.google.com/apikey).

```powershell
git clone <your-repo-url>
cd ai-repo-migrator
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Make sure Docker Desktop is running before use:

```powershell
docker ps
```

## Usage

```powershell
python cli.py run .\sample_repo\app.py
```

Optionally pass a custom instruction:

```powershell
python cli.py run .\sample_repo\app.py --instruction "Migrate to type-hinted Python 3.11 syntax"
```

The tool will print a diff of the proposed change and ask for confirmation before keeping it:

```
Migrating .\sample_repo\app.py...
--- before
+++ after
- print "Hello, " + name
+ print(f"Hello, {name}")
Apply this change? (y/n): y
✅ Change applied and kept.
```

## Testing & CI/CD

Unit tests mock all external calls (Gemini API, Docker subprocess) so they run fast and deterministically without needing real credentials or a running Docker daemon:

```powershell
pytest -q
```

Every push and pull request to `main` automatically triggers the GitHub Actions pipeline (`.github/workflows/ci.yml`), which installs dependencies and runs the full test suite on a clean Ubuntu runner — catching regressions before they merge.

![CI](https://github.com/YOUR_USERNAME/ai-repo-migrator/actions/workflows/ci.yml/badge.svg)

Branching workflow: feature branches (e.g. `feature/gemini-integration`) → pull request into `main` → CI must pass → merge.

## Limitations & future work

This is an MVP scoped to demonstrate the core verification loop, not a production migration tool. Known limitations, and what a v2 would add:

- **Single-file scope** — currently migrates one file at a time; a full implementation would analyze and update multi-file repos with cross-file dependency awareness.
- **Full-file rewrite instead of true patch application** — the LLM returns a complete rewritten file rather than a minimal diff/patch, which is simpler to implement but less precise for large files.
- **No static analysis pass** — a production version would run linters/type-checkers before and after the LLM call to catch issues Gemini might introduce.
- **No live git integration** — the human confirmation step currently just keeps or reverts the file; it doesn't yet create a commit or branch automatically.
- **Base Docker image, not a custom one** — uses `python:3.11-slim` directly rather than a pre-built custom image with test dependencies baked in, which would speed up repeated runs.

## What this project demonstrates

- Designing and implementing an **agentic verification loop** (generate → sandbox-execute → verify → human-approve), not just calling an LLM API
- **Docker-based sandboxing** for safely executing untrusted, AI-generated code
- **Test-driven gating** of automated changes
- Handling a **live third-party SDK deprecation** mid-project (`google-generativeai` → `google-genai`) without disrupting the overall architecture
- End-to-end **CI/CD practice**: mocked unit tests, GitHub Actions, feature-branch → PR → merge workflow
