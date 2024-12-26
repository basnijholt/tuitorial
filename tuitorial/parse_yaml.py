"""Module for parsing a YAML configuration file to run a tuitorial."""

import re

import yaml
from rich.style import Style

from tuitorial import Chapter, Focus, Step, TutorialApp
from tuitorial.helpers import create_bullet_point_chapter


def _parse_focus(focus_data: dict) -> Focus:
    """Parses a single focus item from the YAML data."""
    focus_type = focus_data["type"]
    style = Style.parse(focus_data.get("style", "yellow bold"))
    word_boundary = focus_data.get("word_boundary", False)
    from_start_of_line = focus_data.get("from_start_of_line", False)

    match focus_type:
        case "literal":
            return Focus.literal(focus_data["pattern"], style=style, word_boundary=word_boundary)
        case "regex":
            # Ensure the pattern is compiled for Focus.regex
            return Focus.regex(re.compile(focus_data["pattern"]), style=style)
        case "line":
            return Focus.line(focus_data["pattern"], style=style)
        case "range":
            return Focus.range(focus_data["start"], focus_data["end"], style=style)
        case "startswith":
            return Focus.startswith(
                focus_data["pattern"],
                style=style,
                from_start_of_line=from_start_of_line,
            )
        case "between":
            return Focus.between(
                focus_data["start_pattern"],
                focus_data["end_pattern"],
                style=style,
                inclusive=focus_data.get("inclusive", True),
                multiline=focus_data.get("multiline", True),
                match_index=focus_data.get("match_index"),
                greedy=focus_data.get("greedy", False),
            )
        case _:
            msg = f"Unknown focus type: {focus_type}"
            raise ValueError(msg)


def _parse_step(step_data: dict) -> Step:
    """Parses a single step from the YAML data."""
    description = step_data["description"]
    focus_list = [_parse_focus(focus_data) for focus_data in step_data.get("focus", [])]
    return Step(description, focus_list)


def _parse_chapter(chapter_data: dict) -> Chapter:
    """Parses a single chapter from the YAML data."""
    title = chapter_data["title"]
    code = ""
    steps = []

    if "code_file" in chapter_data:
        with open(chapter_data["code_file"]) as code_file:  # noqa: PTH123
            code = code_file.read()
    elif "code" in chapter_data:
        code = chapter_data["code"]

    if chapter_data.get("type") == "bullet_points":
        return create_bullet_point_chapter(
            title,
            chapter_data["bullet_points"],
            extras=chapter_data.get("extras", []),
            marker=chapter_data.get("marker", "-"),
            style=Style.parse(chapter_data.get("style", "cyan bold")),
        )

    # Only parse steps if not a bullet_points type
    if "steps" in chapter_data:
        steps = [_parse_step(step_data) for step_data in chapter_data["steps"]]

    return Chapter(title, code, steps)


def parse_yaml_config(yaml_file: str) -> list[Chapter]:
    """Parses a YAML configuration file and returns a list of Chapter objects."""
    with open(yaml_file) as f:  # noqa: PTH123
        config = yaml.safe_load(f)

    return [_parse_chapter(chapter_data) for chapter_data in config["chapters"]]


def run_tutorial_from_yaml(yaml_file: str) -> None:
    """Parses a YAML config and runs the tutorial."""
    chapters = parse_yaml_config(yaml_file)
    app = TutorialApp(chapters)
    app.run()


def cli() -> None:
    """Run the tutorial from a YAML file."""
    import argparse

    parser = argparse.ArgumentParser(description="Run a tuitorial from a YAML file.")
    parser.add_argument("yaml_file", help="Path to the YAML configuration file.")
    args = parser.parse_args()
    run_tutorial_from_yaml(args.yaml_file)
