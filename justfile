alias t := test
alias x := example

test:
    uv sync
    uv run pytest

example:
    uv run tuitorial --watch examples/pipefunc.yaml
