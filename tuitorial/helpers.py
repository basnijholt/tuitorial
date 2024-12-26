"""Helper functions for the tuitorial package."""

from rich.style import Style

from tuitorial import Chapter, Focus, Step


def create_bullet_point_chapter(
    title: str,
    bullet_points: list[str],
    extras: list[str] | None = None,
    marker: str = "-",
    style: Style = Style(color="cyan", bold=True),  # noqa: B008
) -> Chapter:
    """Generates a Chapter with bullet points.

    Each step highlights a different bullet point.

    Parameters
    ----------
    title
        The title of the chapter.
    bullet_points
        A list of strings, each representing a bullet point.
    extras
        A list of strings, each representing extra content for the corresponding
        bullet point. If None, no extra content is added.
    marker
        The string used to mark each bullet point. If "1.", the list will be numbered.
    style
        The style to apply to the highlighted bullet points.

    Returns
    -------
    Chapter
        A Chapter object with steps highlighting each bullet point.

    """
    if extras is None:
        extras = [""] * len(bullet_points)
    if len(extras) != len(bullet_points):
        msg = "The number of extras must match the number of bullet points."
        raise ValueError(msg)
    # Create the code content with bullet points
    code = ""
    for i, point in enumerate(bullet_points):
        if marker == "1.":
            code += f"{i + 1}. {point}\n"
        else:
            code += f"{marker} {point}\n"
    code = code.rstrip("\n")

    # Create steps, each highlighting one bullet point
    steps = [Step(extra, [Focus.line(i, style=style)]) for i, extra in enumerate(extras)]

    return Chapter(
        title,
        code,
        steps,  # type: ignore[arg-type]
    )
