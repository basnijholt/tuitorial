"""Module for parsing a YAML configuration file to run a tuitorial."""

import asyncio
import contextlib
import inspect
import os
import re
import sys
import tempfile
import traceback
import urllib.request
from pathlib import Path

import rich
import textual.theme
import yaml
from rich.style import Style
from rich.traceback import install
from textual._context import active_app
from textual.app import App
from textual.widgets import TextArea

from tuitorial import Chapter, Focus, ImageStep, Step, TitleSlide, TuitorialApp
from tuitorial.helpers import create_bullet_point_chapter
from tuitorial.highlighting import FocusType

_DEFAULT_STYLE = "yellow bold"


class InvalidYamlError(ValueError):
    """Raised when an invalid YAML configuration is encountered."""


def _validate_focus_data(focus_data: dict) -> None:
    if "type" not in focus_data:
        msg = f"Invalid focus definition: Each focus must have a 'type' key. Found: {focus_data}"
        raise InvalidYamlError(msg)
    focus_type = focus_data["type"]
    method = getattr(Focus, focus_type, None)
    if method is None:
        valid_types = ", ".join(FocusType.__members__)
        msg = f"Invalid focus type: '{focus_type}'. Must be one of: {valid_types}"
        raise InvalidYamlError(msg)
    sig = inspect.signature(method)
    for key in focus_data:
        if key == "type":
            continue
        if key not in sig.parameters:
            allowed = ", ".join(sig.parameters)
            msg = (
                f"Invalid key '{key}' for focus type '{focus_type}'. "
                f"Allowed keys are: {allowed}"
            )
            raise InvalidYamlError(msg)


def _parse_focus(focus_data: dict) -> Focus:  # noqa: PLR0911
    """Parses a single focus item from the YAML data."""
    _validate_focus_data(focus_data)
    focus_type = focus_data["type"]
    style = Style.parse(focus_data.get("style", _DEFAULT_STYLE))

    match focus_type:
        case "literal":
            return Focus.literal(
                text=focus_data["text"],
                style=style,
                word_boundary=focus_data.get("word_boundary", False),
                match_index=focus_data.get("match_index"),
            )
        case "regex":
            # Ensure the pattern is compiled for Focus.regex
            return Focus.regex(pattern=re.compile(focus_data["pattern"]), style=style)
        case "line":
            return Focus.line(line_number=focus_data["line_number"], style=style)
        case "range":
            return Focus.range(focus_data["start"], focus_data["end"], style=style)
        case "startswith":
            return Focus.startswith(
                text=focus_data["text"],
                style=style,
                from_start_of_line=focus_data.get("from_start_of_line", False),
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
        case _:  # pragma: no cover
            msg = "Should never reach this point because of validation."
            raise RuntimeError(msg)


def _validate_step_data(step_data: dict) -> None:
    if "description" not in step_data:
        msg = (
            f"Invalid step definition: Each step must have a 'description' key. Found: {step_data}"
        )
        raise InvalidYamlError(msg)
    if "image" in step_data and "focus" in step_data:
        msg = (
            f"Invalid step definition: A step cannot have both 'image' and 'focus' keys. "
            f"Found: {step_data}"
        )
        raise InvalidYamlError(msg)
    if "image" in step_data:
        allowed_keys = set(inspect.signature(ImageStep).parameters)
        for key in step_data:
            if key not in allowed_keys:
                allowed = ", ".join(allowed_keys)
                msg = (
                    f"Invalid key '{key}' for ImageStep in step with description '{step_data['description']}'. "
                    f"Allowed keys are: {allowed}"
                )
                raise InvalidYamlError(msg)
    else:
        allowed_keys = {"description", "focus"}
        for key in step_data:
            if key not in allowed_keys:
                allowed = ", ".join(allowed_keys)
                msg = (
                    f"Invalid key '{key}' for Step in step with description '{step_data['description']}'. "
                    f"Allowed keys are: {allowed}"
                )
                raise InvalidYamlError(msg)


def _parse_step(step_data: dict) -> Step | ImageStep:
    """Parses a single step from the YAML data."""
    _validate_step_data(step_data)
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


def _validate_chapter_data(chapter_data: dict) -> None:
    if "title" not in chapter_data:
        msg = f"Invalid chapter definition: Each chapter must have a 'title' key. Found: {chapter_data}"
        raise InvalidYamlError(msg)
    title = chapter_data["title"]
    if "type" in chapter_data:
        if chapter_data["type"] == "bullet_points":
            _validate_bullet_points_data(chapter_data)
            return
        msg = f"Unknown chapter type: {chapter_data['type']}'. Must be 'bullet_points' or omitted."
        raise InvalidYamlError(msg)
    if "code_file" in chapter_data and "code" in chapter_data:
        msg = (
            f"Invalid chapter definition: A chapter cannot have both 'code_file' and 'code' keys. "
            f"Found: {chapter_data}"
        )
        raise InvalidYamlError(msg)
    allowed_keys = {"title", "code_file", "code", "steps"}
    for key in chapter_data:
        if key not in allowed_keys:
            allowed = ", ".join(allowed_keys)
            msg = (
                f"Invalid key '{key}' for chapter '{title}'. "
                f"Allowed keys are: {allowed} (unless 'type: bullet_points' is specified)"
            )
            raise InvalidYamlError(msg)


def _validate_bullet_points_data(chapter_data: dict) -> None:
    title = chapter_data["title"]  # guaranteed to exist by _validate_chapter_data
    if "bullet_points" not in chapter_data:
        msg = (
            f"Invalid bullet points chapter definition: "
            f"Missing 'bullet_points' key in chapter '{title}'."
        )
        raise InvalidYamlError(msg)
    if not isinstance(chapter_data["bullet_points"], list):
        msg = (
            f"Invalid 'bullet_points' format in chapter '{title}'. "
            f"'bullet_points' must be a list."
        )
        raise InvalidYamlError(msg)
    allowed_keys = {"type", "title", "bullet_points", "marker", "style"}
    for key in chapter_data:
        if key not in allowed_keys:
            allowed = ", ".join(allowed_keys)
            msg = (
                f"Invalid key '{key}' for bullet points chapter '{title}'. "
                f"Allowed keys are: {allowed}"
            )
            raise InvalidYamlError(msg)


def _validate_title_slide_data(title_slide_data: dict) -> None:
    sig = inspect.signature(TitleSlide)
    for key in title_slide_data:
        if key not in sig.parameters:
            allowed = ", ".join(sig.parameters)
            msg = f"Invalid key '{key}' for title slide. Allowed keys are: {allowed}"
            raise InvalidYamlError(msg)


def _parse_bullet_points(title: str, chapter_data: dict) -> Chapter:
    bullet_points = []
    extras = []
    for bullet_point in chapter_data["bullet_points"]:
        if isinstance(bullet_point, str):
            text = bullet_point
            extra = ""
        elif isinstance(bullet_point, dict):
            text = bullet_point.get("text", "")
            extra = bullet_point.get("extra", "")
        else:  # pragma: no cover
            msg = (
                f"Invalid bullet point format in chapter '{title}'. "
                f"Each bullet point must be a string or a dictionary with keys 'text' and 'extra'."
            )
            raise InvalidYamlError(msg)
        bullet_points.append(text)
        extras.append(extra)
    return create_bullet_point_chapter(
        title,
        bullet_points=bullet_points,
        extras=extras,
        marker=chapter_data.get("marker", "-"),
        style=Style.parse(chapter_data.get("style", "cyan bold")),
    )


def _parse_chapter(chapter_data: dict) -> Chapter:
    """Parses a single chapter from the YAML data."""
    _validate_chapter_data(chapter_data)
    title = chapter_data["title"]
    if chapter_data.get("type") == "bullet_points":
        return _parse_bullet_points(title, chapter_data)

    code = ""
    steps = []

    if "code_file" in chapter_data:
        code_file_path = chapter_data["code_file"]
        try:
            with open(code_file_path) as code_file:  # noqa: PTH123
                code = code_file.read()
        except FileNotFoundError as e:
            msg = f"Code file not found: {code_file_path}"
            raise InvalidYamlError(msg) from e
    elif "code" in chapter_data:
        code = chapter_data["code"]

    # Only parse steps if not a bullet_points type
    if "steps" in chapter_data:
        steps = [_parse_step(step_data) for step_data in chapter_data["steps"]]

    return Chapter(title, code, steps)


def parse_yaml_config(yaml_file: str | Path) -> tuple[list[Chapter], TitleSlide | None]:
    """Parses a YAML configuration file and returns a list of Chapter objects."""
    install()
    try:
        with open(yaml_file) as f:  # noqa: PTH123
            config = yaml.safe_load(f)
    except FileNotFoundError as e:
        msg = f"YAML file not found: {yaml_file}"
        raise InvalidYamlError(msg) from e
    except yaml.YAMLError as e:
        msg = f"Error parsing YAML file {yaml_file}: {e}"
        raise InvalidYamlError(msg) from e

    if "chapters" not in config:
        msg = "Invalid YAML config: Missing 'chapters' key."
        raise InvalidYamlError(msg)

    chapters = [_parse_chapter(chapter_data) for chapter_data in config["chapters"]]
    title_slide_data = config.get("title_slide", {})
    _validate_title_slide_data(title_slide_data)
    title_slide = TitleSlide(**title_slide_data) if title_slide_data else None
    return chapters, title_slide


def run_from_yaml(
    yaml_file: str | Path,
    chapter_index: int | None = None,
    step_index: int = 0,
    theme: str | None = None,
) -> None:  # pragma: no cover
    """Parses a YAML config and runs the tutorial."""
    chapters, title_slide = parse_yaml_config(yaml_file)
    app = TuitorialApp(chapters, title_slide, chapter_index, step_index)
    if theme is not None:
        app.theme = theme
    app.run()


async def _display_error(app: TuitorialApp, error_message: str) -> None:
    """Display an error message in the current chapter tab."""
    label = TextArea(
        error_message,
        show_line_numbers=True,
        language="python",
        theme="monokai",
        read_only=True,
    )
    pane = app.current_tab_pane()
    await pane.remove_children()
    await pane.mount(label, before=0)


async def reload_app(app: TuitorialApp, yaml_file: str | Path) -> None:
    """Reloads the YAML configuration and updates the TuitorialApp instance."""
    # Store current state
    current_chapter_index = app.current_chapter_index
    current_step_index = app.current_chapter.current_index if current_chapter_index >= 0 else 0
    try:
        app.chapters, app.title_slide = parse_yaml_config(yaml_file)
    except Exception as e:  # noqa: BLE001
        error_message = f"Error reloading YAML: {e!s}\n\n"
        error_message += "".join(traceback.format_exception(*sys.exc_info()))
        await _display_error(app, error_message)
    else:
        # `active_app` is a workaround https://github.com/Textualize/textual/issues/5421#issuecomment-2569836231
        active_app.set(app)
        await app.recompose()
        # Restore previous state
        await app.set_chapter(current_chapter_index, nearest=True)
        await app.set_step(current_step_index)


async def watch_for_changes(app: App, yaml_file: str | Path) -> None:  # pragma: no cover
    """Watches for changes in the YAML file and reloads the app."""
    from watchfiles import awatch

    async for _ in awatch(yaml_file):
        await reload_app(app, yaml_file)  # Call reload_app directly


def run_dev_mode(
    yaml_file: str | Path,
    chapter_index: int | None = None,
    step_index: int = 0,
    theme: str | None = None,
) -> None:  # pragma: no cover
    """Parses a YAML config, runs the tutorial, and watches for changes."""
    chapters, title_slide = parse_yaml_config(yaml_file)
    app = TuitorialApp(chapters, title_slide, chapter_index, step_index)
    if theme is not None:
        app.theme = theme

    async def run_app_and_watch() -> None:
        """Run the app and the file watcher concurrently."""
        watch_task = asyncio.create_task(watch_for_changes(app, yaml_file))
        try:
            # Wait for app to finish
            await app.run_async()
        finally:
            # Cancel watch task when app finishes
            watch_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await watch_task

    asyncio.run(run_app_and_watch())


def cli() -> None:  # pragma: no cover
    """Run the tutorial from a YAML file."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run a tuitorial from a YAML file or URL."
        "See the documentation at https://tuitorial.readthedocs.io/ for more information.",
    )
    parser.add_argument("yaml_source", help="Path to the YAML configuration file or URL.", type=str)
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Watch the YAML file for changes and automatically reload the app.",
    )
    parser.add_argument(
        "--chapter",
        type=int,
        default=None,
        help="Initial chapter index (0-based) for development mode.",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=0,
        help="Initial step index (0-based) for development mode.",
    )
    parser.add_argument(
        "--theme",
        type=str,
        default=None,
        help="Initial theme to use for the app.",
        choices=tuple(textual.theme.BUILTIN_THEMES.keys()),
    )
    args = parser.parse_args()

    if args.yaml_source.startswith(("http://", "https://")):
        if args.watch:
            rich.print("[red bold]Error[/]: `--watch` is not supported for URLs.")
            return

        # Download YAML from URL to a temporary file
        try:
            with (
                urllib.request.urlopen(args.yaml_source) as response,  # noqa: S310
                tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp_file,
            ):
                tmp_file.write(response.read())
                yaml_file = tmp_file.name
        except urllib.error.URLError as e:
            print(f"Error fetching URL: {e}")
            return

        run_from_yaml(yaml_file, chapter_index=args.chapter, step_index=args.step)
        os.remove(yaml_file)  # Clean up the temporary file  # noqa: PTH107
        return
    # Use the provided local YAML file
    path = Path(args.yaml_source)
    os.chdir(path.parent)
    run = run_dev_mode if args.watch else run_from_yaml
    run(path.name, chapter_index=args.chapter, step_index=args.step, theme=args.theme)
