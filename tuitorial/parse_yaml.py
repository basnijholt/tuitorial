"""Module for parsing a YAML configuration file to run a tuitorial."""

import os
import re
from pathlib import Path

import yaml
from rich.style import Style

from tuitorial import Chapter, Focus, ImageStep, Step, TitleSlide, TuitorialApp
from tuitorial.helpers import create_bullet_point_chapter


def _parse_focus(focus_data: dict) -> Focus:  # noqa: PLR0911
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
        case "line_containing":
            return Focus.line_containing(
                focus_data["pattern"],
                style=style,
                lines_before=focus_data.get("lines_before", 0),
                lines_after=focus_data.get("lines_after", 0),
                regex=focus_data.get("regex", False),
                match_index=focus_data.get("match_index"),
            )
        case "syntax":
            return Focus.syntax(
                lexer=focus_data.get("lexer", "python"),
                theme=focus_data.get("theme"),
                line_numbers=focus_data.get("line_numbers", False),
                start_line=focus_data.get("start_line"),
                end_line=focus_data.get("end_line"),
            )
        case "markdown":
            return Focus.markdown()
        case _:
            msg = f"Unknown focus type: {focus_type}"
            raise ValueError(msg)


def _parse_step(step_data: dict) -> Step | ImageStep:
    """Parses a single step from the YAML data."""
    description = step_data["description"]

    if "image" in step_data:
        # It's an ImageStep
        image = step_data["image"]
        width = step_data.get("width")
        height = step_data.get("height")
        halign = step_data.get("halign")
        return ImageStep(description, image, width, height, halign)
    # It's a regular Step
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


def parse_yaml_config(yaml_file: str | Path) -> tuple[list[Chapter], TitleSlide | None]:
    """Parses a YAML configuration file and returns a list of Chapter objects."""
    with open(yaml_file) as f:  # noqa: PTH123
        config = yaml.safe_load(f)

    chapters = [_parse_chapter(chapter_data) for chapter_data in config["chapters"]]
    title_slide = TitleSlide(**config["title_slide"]) if "title_slide" in config else None
    return chapters, title_slide


def run_from_yaml(yaml_file: str | Path) -> None:  # pragma: no cover
    """Parses a YAML config and runs the tutorial."""
    chapters, title_slide = parse_yaml_config(yaml_file)
    app = TuitorialApp(chapters, title_slide)
    app.run()


def cli() -> None:  # pragma: no cover
    """Run the tutorial from a YAML file."""
    import argparse

    parser = argparse.ArgumentParser(description="Run a tuitorial from a YAML file.")
    parser.add_argument("yaml_file", help="Path to the YAML configuration file.", type=Path)
    args = parser.parse_args()
    os.chdir(args.yaml_file.parent)
    run_from_yaml(args.yaml_file.name)
