# tests/test_widgets.py
import pytest
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
        (Focus.regex, r"\w+\(\)", "def test()", {(4, 9)}),
        (Focus.line, 1, "line1\nline2", {(0, 5)}),
        (Focus.range, (0, 4), "test text", {(0, 4)}),
    ],
)
def test_highlight_patterns(focus_type, pattern, text, expected_highlighted):
    """Test different highlight patterns."""
    display = CodeDisplay(text)
    display.update_focuses([focus_type(pattern)])
    result = display.highlight_code()

    # Collect all highlighted ranges
    highlighted_ranges = set()
    for start, end, style in result.spans:
        if style and style.bold:  # Assuming highlighted text is bold
            highlighted_ranges.add((start, end))

    assert highlighted_ranges == expected_highlighted
