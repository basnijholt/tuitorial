# tests/test_widgets.py
import pytest
from rich.style import Style
from rich.text import Text

from tuitorial.highlighting import Focus
from tuitorial.widgets import CodeDisplay


@pytest.fixture
def example_code():
    return "def test():\n    pass\n"


@pytest.fixture
def code_display(example_code):
    return CodeDisplay(example_code)


def test_code_display_init(code_display, example_code):
    """Test CodeDisplay initialization."""
    assert code_display.code == example_code
    assert code_display.focuses == []


def test_code_display_update_focuses(code_display):
    """Test updating focuses."""
    focuses = [Focus.literal("def")]
    code_display.update_focuses(focuses)
    assert code_display.focuses == focuses


def test_code_display_highlight_code(code_display):
    """Test highlight_code method."""
    focuses = [Focus.literal("def")]
    code_display.update_focuses(focuses)
    result = code_display.highlight_code()
    assert isinstance(result, Text)


@pytest.mark.parametrize(
    ("focus_type", "pattern", "text", "expected_highlighted"),
    [
        (Focus.literal, "def", "def test()", {(0, 3)}),
        (Focus.regex, r"test\(\)", "def test()", {(4, 10)}),  # Fixed regex pattern
        (Focus.line, 0, "line1\nline2", {(0, 5)}),  # Changed to 0-based index
        (Focus.range, (0, 4), "test text", {(0, 4)}),
    ],
)
def test_highlight_patterns(focus_type, pattern, text, expected_highlighted):
    """Test different highlight patterns."""
    display = CodeDisplay(text)
    if focus_type == Focus.range:
        start, end = pattern
        focus = focus_type(start, end)  # Special handling for range
    else:
        focus = focus_type(pattern)
    display.update_focuses([focus])
    result = display.highlight_code()

    # Collect all highlighted ranges
    highlighted_ranges = set()
    for start, end, style in result.spans:
        if style and style.bold:  # Assuming highlighted text is bold
            highlighted_ranges.add((start, end))

    assert highlighted_ranges == expected_highlighted


@pytest.mark.parametrize("dim_background", [True, False])
@pytest.mark.parametrize(
    ("code", "focus", "expected_bright", "expected_dim"),
    [
        # Single character highlight
        (
            "abc",
            Focus.literal("b"),
            {(1, 2)},  # "b" is bright
            {(0, 1), (2, 3)},  # "a" and "c" are dim
        ),
        # First character highlight
        (
            "abc",
            Focus.literal("a"),
            {(0, 1)},  # "a" is bright
            {(1, 3)},  # "bc" is dim
        ),
        # Last character highlight
        (
            "abc",
            Focus.literal("c"),
            {(2, 3)},  # "c" is bright
            {(0, 2)},  # "ab" is dim
        ),
        # Multiple character highlight
        (
            "abcdef",
            Focus.literal("bcd"),
            {(1, 4)},  # "bcd" is bright
            {(0, 1), (4, 6)},  # "a" and "ef" are dim
        ),
        # Entire string highlight
        (
            "abc",
            Focus.literal("abc"),
            {(0, 3)},  # "abc" is bright
            set(),  # nothing is dim
        ),
        # Multiple occurrences
        (
            "aba",
            Focus.literal("a"),
            {(0, 1), (2, 3)},  # both "a"s are bright
            {(1, 2)},  # "b" is dim
        ),
        # Empty string
        (
            "",
            Focus.literal("a"),
            set(),  # nothing is bright
            set(),  # nothing is dim
        ),
        # Newlines
        (
            "a\nb\nc",
            Focus.literal("b"),
            {(2, 3)},  # "b" is bright
            {(0, 2), (3, 5)},  # "a\n" and "\nc" are dim
        ),
        # Multiple newlines
        (
            "\n\n\n",
            Focus.literal("\n"),
            {(0, 1), (1, 2), (2, 3)},  # all newlines are bright
            set(),  # nothing is dim
        ),
    ],
)
def test_highlighting_ranges(code, focus, expected_bright, expected_dim, dim_background):
    """Test that highlighting ranges are correct with no off-by-one errors."""
    display = CodeDisplay(code, dim_background=dim_background)
    display.update_focuses([focus])
    result = display.highlight_code()

    # Collect bright and dim ranges
    bright_ranges = set()
    dim_ranges = set()

    for start, end, style in result.spans:
        if style:
            if style.dim:
                dim_ranges.add((start, end))
            else:
                bright_ranges.add((start, end))

    assert bright_ranges == expected_bright
    assert dim_ranges == (expected_dim if dim_background else set())


def test_multiple_focuses():
    """Test that multiple focuses work correctly."""
    code = "abc def ghi"
    focuses = [
        Focus.literal("abc"),
        Focus.literal("ghi"),
    ]

    display = CodeDisplay(code)
    display.update_focuses(focuses)
    result = display.highlight_code()

    bright_ranges = {(start, end) for start, end, style in result.spans if style and not style.dim}
    dim_ranges = {(start, end) for start, end, style in result.spans if style and style.dim}

    assert bright_ranges == {(0, 3), (8, 11)}  # "abc" and "ghi"
    assert dim_ranges == {(3, 8)}  # " def "


def test_overlapping_focuses():
    """Test that overlapping focuses are handled correctly."""
    code = "abcdef"
    focuses = [
        Focus.literal("abc"),
        Focus.literal("cde"),
    ]

    display = CodeDisplay(code)
    display.update_focuses(focuses)
    result = display.highlight_code()

    bright_ranges = {(start, end) for start, end, style in result.spans if style and not style.dim}
    dim_ranges = {(start, end) for start, end, style in result.spans if style and style.dim}

    assert bright_ranges == {(0, 3), (2, 5)}  # "abc" and "cde"
    assert dim_ranges == {(5, 6)}  # "f"


def test_focus_at_boundaries():
    """Test highlighting at string boundaries."""
    code = "abc\ndef\nghi"

    # Test start boundary
    display = CodeDisplay(code)
    display.update_focuses([Focus.literal("abc")])
    result = display.highlight_code()
    bright_ranges = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert (0, 3) in bright_ranges

    # Test end boundary
    display.update_focuses([Focus.literal("ghi")])
    result = display.highlight_code()
    bright_ranges = {(start, end) for start, end, style in result.spans if style and not style.dim}
    assert (8, 11) in bright_ranges


@pytest.mark.parametrize("dim_background", [True, False])
def test_dim_background(dim_background):
    """Test that dim_background parameter works correctly."""
    code = "abc def ghi"
    focus = Focus.literal("def")

    display = CodeDisplay(code, [focus], dim_background=dim_background)
    result = display.highlight_code()

    dim_ranges = {(start, end) for start, end, style in result.spans if style and style.dim}

    if dim_background:
        assert dim_ranges == {(0, 4), (7, 11)}  # "abc " and " ghi"
    else:
        assert not dim_ranges  # no dim ranges when dim_background is False


@pytest.mark.parametrize("dim_background", [True, False])
def test_no_focuses(dim_background):
    """Test text dimming behavior when there are no focuses."""
    code = "abc def"
    display = CodeDisplay(code, dim_background=dim_background)
    result = display.highlight_code()

    dim_ranges = {(start, end) for start, end, style in result.spans if style and style.dim}

    if dim_background:
        assert dim_ranges == {(0, 7)}  # entire text is dim
    else:
        assert not dim_ranges  # no dim ranges


def test_style_preservation():
    """Test that styles are preserved correctly."""
    code = "abc"
    custom_style = Style(color="red", bold=True)
    focus = Focus.literal("b", style=custom_style)

    display = CodeDisplay(code)
    display.update_focuses([focus])
    result = display.highlight_code()

    for start, end, style in result.spans:
        if (start, end) == (1, 2):  # the "b"
            assert style.color.name == "red"
            assert style.bold is True
