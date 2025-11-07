.PHONY: install format lint typecheck test cli

install:
pip install -e .[dev]

format:
black src tests

lint:
ruff check src tests
ruff format --check src tests
ruff check --select I src tests

# Provide a lightweight fallback when ruff is not yet installed.
typecheck:
mypy src

test:
python -m unittest discover -s tests -p "test_*.py"

cli:
python -m ai_learning_studio.cli --list
