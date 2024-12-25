# Tuitorial 📚

> Create beautiful terminal-based code tutorials with syntax highlighting and interactive navigation.

[![PyPI version](https://badge.fury.io/py/tuitorial.svg)](https://badge.fury.io/py/tuitorial)
[![Python](https://img.shields.io/pypi/pyversions/tuitorial.svg)](https://pypi.org/project/tuitorial/)
[![Tests](https://github.com/basnijholt/tuitorial/actions/workflows/test.yml/badge.svg)](https://github.com/basnijholt/tuitorial/actions/workflows/pytest.yml)
[![Coverage](https://codecov.io/gh/basnijholt/tuitorial/branch/main/graph/badge.svg)](https://codecov.io/gh/basnijholt/tuitorial)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## 📚 Table of Contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [🎯 Features](#-features)
- [🚀 Installation](#-installation)
- [🎮 Quick Start](#-quick-start)
- [🎯 Focus Types](#-focus-types)
  - [Literal Match](#literal-match)
  - [Regular Expression](#regular-expression)
  - [Line Number](#line-number)
  - [Range](#range)
  - [Starts With](#starts-with)
  - [Between](#between)
- [🎨 Styling](#-styling)
- [⌨️ Controls](#-controls)
- [📖 Advanced Usage](#-advanced-usage)
  - [Custom Highlighting Patterns](#custom-highlighting-patterns)
  - [Multiple Highlights per Step](#multiple-highlights-per-step)
- [🧪 Development](#-development)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [📚 Similar Projects](#-similar-projects)
- [🐛 Troubleshooting](#-troubleshooting)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## 🎯 Features

- 🎨 Rich syntax highlighting with customizable styles
- 🔍 Multiple focus types: literal, regex, line, and range
- ⌨️ Interactive keyboard navigation
- 📝 Step-by-step tutorial presentations
- 🖼️ Beautiful TUI using [Textual](https://textual.textualize.io/)

## 🚀 Installation

```bash
pip install tuitorial
```

## 🎮 Quick Start

```python
from tuitorial import TutorialApp, Focus

# Your code to present
code = '''
def hello(name: str) -> str:
    return f"Hello, {name}!"

def main():
    print(hello("World"))
'''

# Define tutorial steps
tutorial_steps = [
    (
        "Function Definition",
        [Focus.regex(r"def hello.*:$", style="bold yellow")]
    ),
    (
        "Return Statement",
        [Focus.literal('return f"Hello, {name}!"', style="bold green")]
    ),
    (
        "Main Function",
        [Focus.range(code.find("def main"), len(code), style="bold blue")]
    ),
]

# Run the tutorial
app = TutorialApp(code, tutorial_steps)
app.run()
```

## 🎯 Focus Types

### Literal Match

```python
Focus.literal("def", style="bold yellow")
```

### Regular Expression

```python
Focus.regex(r"def \w+\(.*\):", style="bold green")
```

### Line Number

```python
Focus.line(1, style="bold blue")  # Highlight first line
```

### Range

```python
Focus.range(0, 10, style="bold magenta")  # Highlight first 10 characters
```

### Starts With

Highlights lines starting with the specified text. Can be configured to match from the start of any line or only at the start of the line.

```python
Focus.startswith("import", style="bold blue", from_start_of_line=True)
Focus.startswith("from", style="bold blue", from_start_of_line=False)
```

### Between

Highlights text between two specified patterns. Supports inclusive or exclusive bounds, multiline matching, and greedy or non-greedy matching.

```python
Focus.between("start_function", "end_function", style="bold blue", inclusive=True, multiline=True)
```

## 🎨 Styling

Styles can be customized using Rich's style syntax:

```python
from rich.style import Style

# Using string syntax
Focus.literal("def", style="bold yellow")

# Using Style object
Focus.literal("def", style=Style(bold=True, color="yellow"))
```

## ⌨️ Controls

- `→` Next step
- `←` Previous step
- `r` Reset to first step
- `q` Quit tutorial

## 📖 Advanced Usage

### Custom Highlighting Patterns

```python
from tuitorial import TutorialApp, Focus
from rich.style import Style

# Define custom styles
FUNCTION_STYLE = Style(color="bright_yellow", bold=True)
ARGUMENT_STYLE = Style(color="bright_green", italic=True)

# Create focused patterns
patterns = [
    Focus.regex(r"def \w+", style=FUNCTION_STYLE),
    Focus.regex(r"\([^)]*\)", style=ARGUMENT_STYLE),
]

# Create tutorial step
tutorial_steps = [
    ("Function Definition", patterns),
    # ... more steps
]

app = TutorialApp(code, tutorial_steps)
app.run()
```

### Multiple Highlights per Step

```python
tutorial_steps = [
    (
        "Input/Output",
        [
            Focus.literal("input", style="bold cyan"),
            Focus.literal("output", style="bold green"),
            Focus.regex(r"->.*$", style="bold yellow"),
        ]
    ),
]
```

## 🧪 Development

1. Clone the repository:

```bash
git clone https://github.com/basnijholt/tuitorial.git
cd tuitorial
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

3. Install development dependencies:

```bash
pip install -e ".[test]"
```

4. Run tests:

```bash
pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Textual](https://textual.textualize.io/) for the amazing TUI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal formatting

## 📚 Similar Projects

- [Rich-CLI](https://github.com/Textualize/rich-cli)
- [asciinema](https://github.com/asciinema/asciinema)

## 🐛 Troubleshooting

**Q: The colors don't show up correctly in my terminal.**
A: Make sure your terminal supports true color and has a compatible color scheme.

**Q: The tutorial doesn't respond to keyboard input.**
A: Verify that your terminal emulator is properly forwarding keyboard events.
