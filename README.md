# AI Learning Studio

## Quickstart

1. Install the project in a virtual environment:
   ```bash
   pip install -e .
   ```
2. Run the planner CLI:
   ```bash
   python -m ai_learning_studio.cli
   ```

### Optional Git auto-sync

Set the `AI_LEARNING_STUDIO_AUTO_PULL` environment variable to opt into automatic Git fetch/pull before each CLI run:

```bash
export AI_LEARNING_STUDIO_AUTO_PULL=1
python -m ai_learning_studio.cli
```

* The helper only runs when the project directory is inside a Git repository. Outside of Git it is skipped silently.
* For private repositories ensure your Git remote is configured to use a credential helper or PAT/SSH key with fetch & pull permissions; the CLI does not manage credentials and will surface authentication errors from Git.
* Leave the variable unset (default) to maintain manual control of Git operations.
