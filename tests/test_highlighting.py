# tests/test_highlighting.py
import re
from re import Pattern

import pytest
from rich.style import Style

from tuitorial.highlighting import Focus, FocusType


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
    assert focus.style.color == "yellow"
    assert focus.style.bold


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
