alias t := test
alias x := example

test:
    uv sync
    uv run pytest

example:
    uv run python examples/example.py
