"""Example script to demonstrate the usage of the tuitorial package."""

from rich.style import Style

from tuitorial import Focus, TutorialApp


def main() -> None:
    """Run the example tutorial app."""
    example_code = """
@pipefunc(output_name="y", mapspec="x[i] -> y[i]")
def double_it(x: int) -> int:
    return 2 * x

@pipefunc(output_name="z", mapspec="x[j], y[i] -> z[i, j]")
def combine(x: int, y: int) -> int:
    return x + y
"""

    # Define tutorial steps with different highlight colors
    tutorial_steps = [
        (
            "Mapspec Overview\nShows all mapspec patterns in the code",
            [Focus.regex(r'mapspec="[^"]*"', Style(color="bright_blue", bold=True))],
        ),
        (
            "Input Indices\nHighlighting the input indices \\[i] and \\[j]",
            [
                Focus.literal("i", Style(color="bright_yellow", bold=True), word_boundary=True),
                Focus.literal("[i]", Style(color="bright_yellow", bold=True)),
                Focus.literal("j", Style(color="bright_green", bold=True), word_boundary=True),
                Focus.literal("[j]", Style(color="bright_green", bold=True)),
            ],
        ),
        (
            "Function Definitions\nShows all function definitions in the code",
            [Focus.regex(r"def.*:$", Style(color="bright_magenta", bold=True))],
        ),
        (
            "First Function\nComplete implementation of double_it",
            [Focus.range(1, example_code.find("\n\n"), Style(color="bright_cyan", bold=True))],
        ),
        (
            "Second Function\nComplete implementation of combine",
            [
                Focus.range(
                    example_code.find("\n\n") + 2,
                    len(example_code),
                    Style(color="bright_red", bold=True),
                ),
            ],
        ),
    ]

    # Run the app
    app = TutorialApp(example_code, tutorial_steps)
    app.run()


if __name__ == "__main__":
    main()
