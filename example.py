"""Example script to demonstrate the usage of the tuitorial package."""

from rich.style import Style

from tuitorial import Chapter, Focus, Step, TuitorialApp


def main() -> None:
    """Run the example tutorial app."""
    example_code_chapter_1 = """
@pipefunc(output_name="y", mapspec="x[i] -> y[i]")
def double_it(x: int) -> int:
    return 2 * x
"""

    example_code_chapter_2 = """
@pipefunc(output_name="z", mapspec="x[j], y[i] -> z[i, j]")
def combine(x: int, y: int) -> int:
    return x + y
"""

    # Define tutorial steps for chapter 1
    tutorial_steps_chapter_1 = [
        Step(
            "@pipefunc decorator\nShows all pipefunc decorators in the code",
            [
                Focus.startswith(
                    "@pipefunc",
                    Style(color="bright_yellow", bold=True),
                    from_start_of_line=True,
                ),
            ],
        ),
        Step(
            "Mapspec Overview\nShows all mapspec patterns in the code",
            [Focus.regex(r'mapspec="[^"]*"', Style(color="bright_blue", bold=True))],
        ),
        Step(
            "Input Indices\nHighlighting the input indices \\[i]",
            [
                Focus.literal("i", Style(color="bright_yellow", bold=True), word_boundary=True),
                Focus.literal("[i]", Style(color="bright_yellow", bold=True)),
            ],
        ),
        Step(
            "Function Definitions\nShows all function definitions in the code",
            [Focus.regex(r"def.*:(?:\n|$)", Style(color="bright_magenta", bold=True))],
        ),
        Step(
            "First Function\nComplete implementation of double_it",
            [Focus.range(1, len(example_code_chapter_1), Style(color="bright_cyan", bold=True))],
        ),
    ]

    # Define tutorial steps for chapter 2
    tutorial_steps_chapter_2 = [
        Step(
            "Second Function\nComplete implementation of combine",
            [
                Focus.range(
                    1,
                    len(example_code_chapter_2),
                    Style(color="bright_red", bold=True),
                ),
            ],
        ),
        Step(
            "Input Indices\nHighlighting the input indices \\[j] and \\[i]",
            [
                Focus.literal("j", Style(color="bright_green", bold=True), word_boundary=True),
                Focus.literal("[j]", Style(color="bright_green", bold=True)),
                Focus.literal("i", Style(color="bright_yellow", bold=True), word_boundary=True),
                Focus.literal("[i]", Style(color="bright_yellow", bold=True)),
            ],
        ),
    ]

    # Create chapters
    chapter_1 = Chapter("Chapter 1", example_code_chapter_1, tutorial_steps_chapter_1)  # type: ignore[arg-type]
    chapter_2 = Chapter("Chapter 2", example_code_chapter_2, tutorial_steps_chapter_2)  # type: ignore[arg-type]

    # Run the app with multiple chapters
    app = TuitorialApp([chapter_1, chapter_2])
    app.run()


if __name__ == "__main__":
    main()
