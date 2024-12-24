# tests/test_highlighting.py
import re
from re import Pattern

import pytest
from rich.style import Style

from tuitorial.highlighting import Focus, FocusType
from tuitorial.widgets import CodeDisplay


def test_focus_type_enum():
    """Test that FocusType enum has all expected values."""
    assert len(FocusType) == 4
    assert all(hasattr(FocusType, t) for t in ["LITERAL", "REGEX", "LINE", "RANGE"])


@pytest.mark.parametrize(
    ("method", "args", "expected_type"),
    [
        ("literal", ("test",), FocusType.LITERAL),
        ("regex", (r"\w+",), FocusType.REGEX),
        ("line", (1,), FocusType.LINE),
        ("range", (0, 10), FocusType.RANGE),
    ],
)
def test_focus_factory_methods(method, args, expected_type):
    """Test Focus class factory methods."""
    focus = getattr(Focus, method)(*args)
    assert isinstance(focus, Focus)
    assert focus.type == expected_type


def test_focus_default_style():
    """Test that Focus uses default style correctly."""
    focus = Focus("test")
    assert isinstance(focus.style, Style)
    assert focus.style.color.name == "yellow"


def test_focus_custom_style():
    """Test that Focus accepts custom style."""
    custom_style = Style(color="red", italic=True)
    focus = Focus("test", style=custom_style)
    assert focus.style == custom_style


def test_regex_pattern_conversion():
    """Test that string patterns are converted to regex patterns."""
    focus = Focus.regex(r"\w+")
    assert isinstance(focus.pattern, Pattern)


def test_regex_pattern_passthrough():
    """Test that compiled patterns are passed through."""
    pattern = re.compile(r"\w+")
    focus = Focus.regex(pattern)
    assert focus.pattern is pattern


def test_literal_word_boundary():
    """Test literal focus with word boundary."""
    text = "i init in string"  # "i" as word, "i" in "init", "in", and "string"

    display = CodeDisplay(text)

    # Without word boundary
    focus = Focus.literal("i")
    display.update_focuses([focus])
    result = display.highlight_code()
    highlighted = {(start, end) for start, end, style in result.spans if style and style.bold}
    assert highlighted == {(0, 1), (13, 14), (2, 3), (4, 5), (7, 8)}  # matches all "i"s

    # With word boundary
    focus = Focus.literal("i", word_boundary=True)
    display.update_focuses([focus])
    result = display.highlight_code()
    highlighted = {(start, end) for start, end, style in result.spans if style and style.bold}
    assert highlighted == {(0, 1)}  # only matches the standalone "i"


def test_bracket_highlighting():
    """Test that brackets are highlighted correctly."""
    code = "text [i] more [j] text"
    focuses = [
        Focus.literal("[i]", Style(color="bright_yellow", bold=True)),
        Focus.literal("[j]", Style(color="bright_green", bold=True)),
    ]

    display = CodeDisplay(code)
    display.update_focuses(focuses)
    result = display.highlight_code()

    # Collect all highlighted ranges and their styles
    highlights = {
        (start, end): style for start, end, style in result.spans if style and not style.dim
    }

    # Check the exact ranges for [i] and [j]
    assert (5, 8) in highlights  # "[i]" should be highlighted as one unit
    assert (14, 17) in highlights  # "[j]" should be highlighted as one unit

    # Print the actual ranges and their content for debugging
    for (start, end), style in highlights.items():
        print(f"Range {start}:{end} = '{code[start:end]}' with style {style}")

    # Check that no partial brackets are highlighted
    partial_highlights = [
        code[start:end] for (start, end) in highlights if code[start:end] in ["[", "]", "i", "j"]
    ]
    assert not partial_highlights, f"Found partial highlights: {partial_highlights}"


def test_bracket_highlighting_detailed():
    """Test bracket highlighting with character-by-character analysis."""
    code = "[i]"
    focus = Focus.literal("[i]", Style(color="bright_yellow", bold=True))

    display = CodeDisplay(code)
    display.update_focuses([focus])
    result = display.highlight_code()

    # Collect character-by-character styling
    char_styles = []
    for i in range(len(code)):
        styles = [style for start, end, style in result.spans if start <= i < end]
        char_styles.append((code[i], styles))

    # Check each character's styling
    for char, styles in char_styles:
        style = next((s for s in styles if not s.dim), None)
        assert style is not None, f"Character '{char}' is not highlighted"
        assert style.color.name == "bright_yellow", f"Character '{char}' has wrong color"
        assert style.bold, f"Character '{char}' is not bold"


def test_bracket_highlighting_in_context():
    """Test bracket highlighting in the context of a larger code example."""
    code = """
@pipefunc(output_name="y", mapspec="x[i] -> y[i]")
def double_it(x: int) -> int:
    return 2 * x
"""
    focus = Focus.literal("[i]", Style(color="bright_yellow", bold=True))

    display = CodeDisplay(code)
    display.update_focuses([focus])
    result = display.highlight_code()

    # Find all occurrences of [i] in the code
    import re

    expected_positions = [(m.start(), m.end()) for m in re.finditer(r"\[i\]", code)]

    # Check that each [i] is highlighted as a complete unit
    highlights = {(start, end) for start, end, style in result.spans if style and not style.dim}

    for start, end in expected_positions:
        assert (
            start,
            end,
        ) in highlights, f"[i] at position {start}:{end} not highlighted correctly"
        # Check that no partial highlights exist within this range
        partial_highlights = {
            (s, e) for (s, e) in highlights if (start < s < end) or (start < e < end)
        }
        assert not partial_highlights, f"Found partial highlights within [i]: {partial_highlights}"


def test_compound_and_single_char_highlighting():
    """Test highlighting of both compound ([i]) and single character (i) tokens."""
    code = "test [i] and i in z[i, j]"
    focuses = [
        Focus.literal("[i]", Style(color="bright_yellow", bold=True)),
        Focus.literal("i", Style(color="bright_yellow", bold=True), word_boundary=True),
        Focus.literal("[j]", Style(color="bright_green", bold=True)),
        Focus.literal("j", Style(color="bright_green", bold=True), word_boundary=True),
    ]

    display = CodeDisplay(code)
    display.update_focuses(focuses)
    result = display.highlight_code()

    from rich.console import Console

    console = Console()
    segments = list(result.render(console))

    # Helper function to get style at position
    def get_style_at(pos: int) -> Style | None:
        current_pos = 0
        for segment in segments:
            if current_pos <= pos < current_pos + len(segment.text):
                return segment.style
            current_pos += len(segment.text)
        return None

    # Check specific positions
    assert get_style_at(code.find("[i]")).bold  # start of [i]
    assert get_style_at(code.find("[i]") + 1).bold  # middle of [i]
    assert get_style_at(code.find("[i]") + 2).bold  # end of [i]

    # Check standalone i
    standalone_i_pos = code.find(" i ")
    assert get_style_at(standalone_i_pos + 1).bold  # standalone i

    # Check i in z[i, j]
    array_i_pos = code.find("z[") + 2
    assert get_style_at(array_i_pos).bold  # i in array

    # Print debug information
    print("\nSegment analysis:")
    current_pos = 0
    for segment in segments:
        print(f"Text: {segment.text!r}, Style: {segment.style}")
        current_pos += len(segment.text)


def test_overlapping_bracket_highlights():
    """Test that bracket highlights don't mix with word boundary highlights."""
    code = '"x[i] -> y[i]"\n"x[j], y[i] -> z[i, j]"'
    focuses = [
        Focus.literal("[i]", Style(color="bright_yellow", bold=True)),
        Focus.literal("i", Style(color="bright_yellow", bold=True), word_boundary=True),
    ]

    display = CodeDisplay(code)
    display.update_focuses(focuses)
    result = display.highlight_code()

    from rich.console import Console

    console = Console()
    segments = list(result.render(console))

    # Check that no segment has both dim and bold styles
    for segment in segments:
        if segment.style:
            assert not (
                segment.style.dim and segment.style.bold
            ), f"Segment '{segment.text}' has both dim and bold styles: {segment.style}"

    # Specifically check the closing brackets
    for segment in segments:
        if segment.text == "]":
            assert not segment.style.dim, "Closing bracket should not be dimmed"
            assert segment.style.bold, "Closing bracket should be bold"
