# AI Learning Studio

A modular laboratory for learning the full stack of modern AI systems—from running open-source
LLMs locally to wiring retrieval, agents, MCP tooling, evaluation, and deployment. The project is
structured so each milestone teaches a new concept while adding genuinely useful capabilities.

## Repository layout

```
.
├── docs/                # Journals, milestone notes, and conceptual write-ups
├── notebooks/           # Experiment notebooks and exploratory analyses
├── src/ai_learning_studio/
│   ├── __init__.py      # Package metadata and exports
│   ├── cli.py           # CLI helper for exploring the learning roadmap
│   └── planning.py      # Parses milestone docs into structured phases
└── tests/               # Test harness (currently using unittest)
```

## Quickstart

1. Create and activate a Python 3.10+ virtual environment.
2. Install the project in editable mode along with dev dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Explore the learning roadmap (generated from the markdown milestone files):
   ```bash
   python -m ai_learning_studio.cli --list
   python -m ai_learning_studio.cli --phase 3
   python -m ai_learning_studio.cli --next --after 0
   ```
   To automatically run `git fetch`/`git pull` before loading the phases, opt in by setting
   `AI_LEARNING_STUDIO_AUTO_PULL=1`. The CLI will only run these commands when executed inside a
   Git repository. For private repositories make sure your Git credential helper or personal access
   token is configured so `git pull` can authenticate without prompting; never commit long-lived
   tokens to source control or shell history.
4. Run the smoke tests:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

## Roadmap summary

The roadmap is sourced directly from the markdown files in `docs/milestones/`, so keeping those
notes up-to-date automatically keeps the CLI aligned with the repository. The current milestones
include:

- **Milestone 00 – Project Scaffolding**
- **Milestone 01 – LLM Fundamentals**
- **Milestone 02 – Data Ingestion & Preprocessing**
- **Milestone 03 – Retrieval-Augmented Generation**
- **Milestone 04 – Agentic Flows & Tooling**
- **Milestone 05 – Model Context Protocol**
- **Milestone 06 – Evaluation & Safety**
- **Milestone 07 – Interface & UX**
- **Milestone 08 – Deployment & Scaling**

Each milestone documents its objective plus a working checklist of experiments or deliverables.

## What's next?

After completing the scaffolding milestone, run:

```bash
python -m ai_learning_studio.cli --next --after 0
```

The CLI will highlight the upcoming phase—whatever is next in `docs/milestones/`—and the concrete experiments to tackle. For instance, `docs/milestones/01_llm_fundamentals.md` contains the detailed playbook for diving into local language models.

### Custom milestone locations

If you want to experiment with an alternative set of milestones (for example in a fork or during testing), point the CLI to a different directory by setting the `AI_LEARNING_STUDIO_MILESTONES_DIR` environment variable before running commands.

## Contributing

This is a personal learning project, but contributions and suggestions are welcome. Please open an
issue or pull request describing proposed changes or new learning experiments.
