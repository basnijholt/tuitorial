alias t := test
alias e := example

test:
    uv sync
    uv run pytest

example:
    uv run python example.py
