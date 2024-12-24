"""Update environment.yml from pyproject.toml."""

from __future__ import annotations

from typing import TYPE_CHECKING

import tomllib

if TYPE_CHECKING:
    from collections.abc import Iterable

PIP_ONLY_DEPS: set[str] = set()
REPLACE_DEPS: dict[str, str] = {
    "graphviz": "python-graphviz",
}
SKIP_DEPS: set[str] = {"tuitorial"}


def clean_deps(deps: Iterable[str]) -> list[str]:
    """Remove version constraints from dependencies."""
    return [strip_extras(dep.split(";", 1)[0]) for dep in deps]


def generate_pip_deps(deps: list[str]) -> list[str]:
    """Generate pip only dependencies from a list."""
    return [
        REPLACE_DEPS.get(dep, dep) for dep in deps if dep in PIP_ONLY_DEPS and dep not in SKIP_DEPS
    ]


def strip_extras(dep: str) -> str:
    """Strip extras from a dependency."""
    return dep.split("[", 1)[0].strip()


def write_deps(deps: Iterable[str], added_deps: set[str], label: str = "", indent: int = 2) -> str:
    """Write dependencies with optional label."""
    deps_str = ""
    space = " " * indent
    if label:
        deps_str += f"  # {label}\n"
    for dep in deps:
        if dep in added_deps:
            continue
        deps_str += f"{space}- {dep}\n"
        added_deps.add(dep)
    return deps_str


def generate_environment_yml(
    data: dict,
    name: str,
    sections: tuple[str, ...] = ("test", "docs", "plotting"),
    default_packages: tuple[str, ...] = ("python", "pip"),
    filename: str | None = "environment.yml",
    pip_deps: list[str] | None = None,
) -> str:
    """Generate environment.yml from pyproject.toml."""
    if pip_deps is None:
        pip_deps = []
    added_deps: set[str] = set()
    dependencies = clean_deps(data["project"]["dependencies"])
    pip_deps += generate_pip_deps(dependencies)

    env_yaml = "# This file is generated from pyproject.toml using .github/update-environment.py\n"
    env_yaml += f"name: {name}\n\n"
    env_yaml += "channels:\n- conda-forge\n\n"
    env_yaml += "dependencies:\n"

    # Default packages
    env_yaml += write_deps(default_packages, added_deps)

    # Required deps from pyproject.toml
    env_yaml += write_deps(
        [
            REPLACE_DEPS.get(dep, dep)
            for dep in dependencies
            if dep not in PIP_ONLY_DEPS and dep not in SKIP_DEPS
        ],
        added_deps,
        "from pyproject.toml",
    )

    # Optional dependencies
    for group in data["project"]["optional-dependencies"]:
        if group in sections:
            group_deps = clean_deps(data["project"]["optional-dependencies"][group])
            pip_deps += generate_pip_deps(group_deps)
            env_yaml += write_deps(
                [
                    REPLACE_DEPS.get(dep, dep)
                    for dep in group_deps
                    if dep not in PIP_ONLY_DEPS and dep not in SKIP_DEPS
                ],
                added_deps,
                f"optional-dependencies: {group}",
            )

    # PIP only dependencies
    if pip_deps:
        env_yaml += "  - pip:\n"
        # remove duplicates and no label for pip deps
        env_yaml += write_deps(set(pip_deps), added_deps, "", indent=4)

    if filename is not None:
        with open(filename, "w") as f:  # noqa: PTH123
            f.write(env_yaml)

    return env_yaml


if __name__ == "__main__":
    # Load pyproject.toml
    with open("pyproject.toml") as f:  # noqa: PTH123
        data = tomllib.loads(f.read())

    sections = (
        "adaptive",
        "pandas",
        "plotting",
        "profiling",
        "rich",
        "widgets",
        "xarray",
        "zarr",
    )
    # Generate environment.yml
    generate_environment_yml(
        data,
        name="tuitorial",
        sections=("test", *sections),
        filename="environment.yml",
    )

    # Generate environment for Sphinx
    generate_environment_yml(
        data,
        name="tuitorial-sphinx",
        sections=("docs", *sections),
        filename="docs/environment-sphinx.yml",
    )
