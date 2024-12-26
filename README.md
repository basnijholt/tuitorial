# Tuitorial 📚

> Create beautiful terminal-based code tutorials with syntax highlighting and interactive navigation.

[![PyPI version](https://badge.fury.io/py/tuitorial.svg)](https://badge.fury.io/py/tuitorial)
[![Python](https://img.shields.io/pypi/pyversions/tuitorial.svg)](https://pypi.org/project/tuitorial/)
[![Tests](https://github.com/basnijholt/tuitorial/actions/workflows/pytest.yml/badge.svg)](https://github.com/basnijholt/tuitorial/actions/workflows/pytest.yml)
[![Coverage](https://codecov.io/gh/basnijholt/tuitorial/branch/main/graph/badge.svg)](https://codecov.io/gh/basnijholt/tuitorial)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<details><summary><b><u>[ToC]</u></b> 📚</summary>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [🎯 Features](#-features)
- [🚀 Installation](#-installation)
- [🎮 Quick Start](#-quick-start)
- [📖 Advanced Usage](#-advanced-usage)
  - [Multiple Chapters](#multiple-chapters)
    - [Python](#python)
  - [Steps](#steps)
    - [Python](#python-1)
- [🎯 Focus Types](#-focus-types)
  - [Literal Match](#literal-match)
    - [Python](#python-2)
    - [YAML](#yaml)
  - [Regular Expression](#regular-expression)
    - [Python](#python-3)
    - [YAML](#yaml-1)
  - [Line Number](#line-number)
    - [Python](#python-4)
    - [YAML](#yaml-2)
  - [Range](#range)
    - [Python](#python-5)
    - [YAML](#yaml-3)
  - [Starts With](#starts-with)
    - [Python](#python-6)
    - [YAML](#yaml-4)
  - [Between](#between)
    - [Python](#python-7)
    - [YAML](#yaml-5)
- [🎨 Styling](#-styling)
    - [Python](#python-8)
    - [YAML](#yaml-6)
- [⌨️ Controls](#-controls)
- [📖 Advanced Usage](#-advanced-usage-1)
  - [Custom Highlighting Patterns](#custom-highlighting-patterns)
    - [Python](#python-9)
  - [Multiple Highlights per Step](#multiple-highlights-per-step)
    - [Python](#python-10)
- [📖 Helper Functions](#-helper-functions)
  - [`create_bullet_point_chapter`](#create_bullet_point_chapter)
    - [Python](#python-11)
- [🧪 Development](#-development)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [📚 Similar Projects](#-similar-projects)
- [🐛 Troubleshooting](#-troubleshooting)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

</details>

## 🎯 Features

- 🎨 Rich syntax highlighting with customizable styles
- 🔍 Multiple focus types: literal, regex, line, range, startswith, and between.
- ⌨️ Interactive keyboard navigation
- 📝 Step-by-step tutorial presentations
- 🖼️ Beautiful TUI using [Textual](https://textual.textualize.io/)

## 🚀 Installation

```bash
pip install tuitorial
```

## 🎮 Quick Start

<details>
<summary><b>Python</b></summary>

```python
from tuitorial import Chapter, Step, TutorialApp, Focus
from rich.style import Style

# Your code to present
code = '''
def hello(name: str) -> str:
    return f"Hello, {name}!"

def main():
    print(hello("World"))
'''

# Define tutorial steps
steps = [
    Step(
        "Function Definition",
        [Focus.regex(r"def hello.*:$", style="bold yellow")]
    ),
    Step(
        "Return Statement",
        [Focus.literal('return f"Hello, {name}!"', style="bold green")]
    ),
    Step(
        "Main Function",
        [Focus.range(code.find("def main"), len(code), style="bold blue")]
    ),
]

# Create a chapter
chapter = Chapter("Basic Example", code, steps)

# Run the tutorial
app = TutorialApp([chapter])
app.run()
```

</details>

<details>
<summary><b>YAML</b></summary>

```yaml
chapters:
  - title: "Basic Example"
    code: |
      def hello(name: str) -> str:
          return f"Hello, {name}!"

      def main():
          print(hello("World"))
    steps:
      - description: "Function Definition"
        focus:
          - type: regex
            pattern: "def hello.*:$"
            style: "bold yellow"
      - description: "Return Statement"
        focus:
          - type: literal
            pattern: 'return f"Hello, {name}!"'
            style: "bold green"
      - description: "Main Function"
        focus:
          - type: range
            start: 26 #  Calculated index for "def main"
            end: 53 #  Calculated length of the code
            style: "bold blue"
```

To run the YAML example:

1. Save the YAML content as a `.yaml` file (e.g., `tutorial.yaml`).
2. Use the provided `run_tutorial_from_yaml` function:

```python
# In a separate Python file (e.g., run_yaml.py)
from parse_yaml import run_tutorial_from_yaml  # Assuming parse_yaml.py is where you have the YAML parsing code

run_tutorial_from_yaml("tutorial.yaml")
```

</details>

## 📖 Advanced Usage

### Multiple Chapters

#### Python

<details>
<summary><b>Python</b></summary>

```python
# First chapter
chapter1_code = '''
def greet(name: str) -> str:
    return f"Hello, {name}!"
'''
chapter1_steps = [
    Step("Greeting Function", [Focus.regex(r"def greet.*:$")]),
    Step("Return Statement", [Focus.literal('return f"Hello, {name}!"')]),
]
chapter1 = Chapter("Greetings", chapter1_code, chapter1_steps)

# Second chapter
chapter2_code = '''
def farewell(name: str) -> str:
    return f"Goodbye, {name}!"
'''
chapter2_steps = [
    Step("Farewell Function", [Focus.regex(r"def farewell.*:$")]),
    Step("Return Statement", [Focus.literal('return f"Goodbye, {name}!"')]),
]
chapter2 = Chapter("Farewells", chapter2_code, chapter2_steps)

# Run tutorial with multiple chapters
app = TutorialApp([chapter1, chapter2])
app.run()
```

</details>

<details>
<summary><b>YAML</b></summary>

```yaml
chapters:
  - title: "Greetings"
    code: |
      def greet(name: str) -> str:
          return f"Hello, {name}!"
    steps:
      - description: "Greeting Function"
        focus:
          - type: regex
            pattern: "def greet.*:$"
      - description: "Return Statement"
        focus:
          - type: literal
            pattern: 'return f"Hello, {name}!"'

  - title: "Farewells"
    code: |
      def farewell(name: str) -> str:
          return f"Goodbye, {name}!"
    steps:
      - description: "Farewell Function"
        focus:
          - type: regex
            pattern: "def farewell.*:$"
      - description: "Return Statement"
        focus:
          - type: literal
            pattern: 'return f"Goodbye, {name}!"'
```

</details>

### Steps

Each step in a tutorial consists of a description and a list of focuses.

#### Python

```python
Step(
    "Step Description",  # Shown in the UI
    [
        Focus.literal("some text"),  # One or more Focus objects
        Focus.regex(r"pattern.*"),   # Can combine different focus types
    ]
)
```

#### YAML

```yaml
steps:
  - description: "Step Description"
    focus:
      - type: literal
        pattern: "some text"
      - type: regex
        pattern: "pattern.*"
```

## 🎯 Focus Types

### Literal Match

#### Python

```python
Focus.literal("def", style="bold yellow")
```

#### YAML

```yaml
focus:
  - type: literal
    pattern: "def"
    style: "bold yellow"
```

### Regular Expression

#### Python

```python
Focus.regex(r"def \w+\(.*\):", style="bold green")
```

#### YAML

```yaml
focus:
  - type: regex
    pattern: "def \\w+\\(.*\\):"
    style: "bold green"
```

### Line Number

#### Python

```python
Focus.line(1, style="bold blue")  # Highlight first line
```

#### YAML

```yaml
focus:
  - type: line
    pattern: 1
    style: "bold blue"
```

### Range

#### Python

```python
Focus.range(0, 10, style="bold magenta")  # Highlight first 10 characters
```

#### YAML

```yaml
focus:
  - type: range
    start: 0
    end: 10
    style: "bold magenta"
```

### Starts With

Highlights lines starting with the specified text. Can be configured to match from the start of any line or only at the start of the line.

#### Python

```python
Focus.startswith("import", style="bold blue", from_start_of_line=True)
Focus.startswith("from", style="bold blue", from_start_of_line=False)
```

#### YAML

```yaml
focus:
  - type: startswith
    pattern: "import"
    style: "bold blue"
    from_start_of_line: true
  - type: startswith
    pattern: "from"
    style: "bold blue"
    from_start_of_line: false
```

### Between

Highlights text between two specified patterns. Supports inclusive or exclusive bounds, multiline matching, and greedy or non-greedy matching.

#### Python

```python
Focus.between("start_function", "end_function", style="bold blue", inclusive=True, multiline=True)
```

#### YAML

```yaml
focus:
  - type: between
    start_pattern: "start_function"
    end_pattern: "end_function"
    style: "bold blue"
    inclusive: true
    multiline: true
```

## 🎨 Styling

Styles can be customized using Rich's style syntax:

#### Python

```python
from rich.style import Style

# Using string syntax
Focus.literal("def", style="bold yellow")

# Using Style object
Focus.literal("def", style=Style(bold=True, color="yellow"))
```

#### YAML

```yaml
focus:
  - type: literal
    pattern: "def"
    style: "bold yellow" # Using string syntax

  - type: literal
    pattern: "def"
    style: "bold color(yellow)" # Using Style object
```

</details>

## ⌨️ Controls

- `→` Next step in current chapter
- `←` Previous step in current chapter
- `tab` Next chapter
- `shift+tab` Previous chapter
- `r` Reset to first step of current chapter
- `d` Toggle dim/bright background
- `q` Quit tutorial

## 📖 Advanced Usage

### Custom Highlighting Patterns

#### Python

<details>
<summary><b>Python</b></summary>

```python
from tuitorial import TutorialApp, Focus
from rich.style import Style

# Define custom styles
FUNCTION_STYLE = Style(color="bright_yellow", bold=True)
ARGUMENT_STYLE = Style(color="bright_green", italic=True)

# Your code to present
code = '''
def hello(name: str) -> str:
    return f"Hello, {name}!"
'''

# Create focused patterns
patterns = [
    Focus.regex(r"def \w+", style=FUNCTION_STYLE),
    Focus.regex(r"\([^)]*\)", style=ARGUMENT_STYLE),
]

# Create tutorial step
tutorial_steps = [
    Step("Function Definition", patterns),
]

# Create a chapter
chapter = Chapter("Custom Patterns", code, tutorial_steps)

# Run the tutorial
app = TutorialApp([chapter])
app.run()
```

</details>

<details>
<summary><b>YAML</b></summary>

```yaml
chapters:
  - title: "Custom Patterns"
    code: |
      def hello(name: str) -> str:
          return f"Hello, {name}!"
    steps:
      - description: "Function Definition"
        focus:
          - type: regex
            pattern: "def \\w+"
            style: "bright_yellow bold"
          - type: regex
            pattern: "\\([^)]*\\)"
            style: "bright_green italic"
```

</details>

### Multiple Highlights per Step

#### Python

<details>
<summary><b>Python</b></summary>

```python
from tuitorial import Chapter, Step, TutorialApp, Focus
from rich.style import Style

# Your code to present
code = '''
def hello(name: str) -> str:
    return f"Hello, {name}!"
'''

tutorial_steps = [
    Step(
        "Input/Output",
        [
            Focus.literal("name", style="bold cyan"),
            Focus.regex(r"->.*$", style="bold yellow"),
        ]
    ),
]

# Create a chapter
chapter = Chapter("Multiple Highlights", code, tutorial_steps)

# Run the tutorial
app = TutorialApp([chapter])
app.run()
```

</details>

<details>
<summary><b>YAML</b></summary>

```yaml
chapters:
  - title: "Multiple Highlights"
    code: |
      def hello(name: str) -> str:
          return f"Hello, {name}!"
    steps:
      - description: "Input/Output"
        focus:
          - type: literal
            pattern: "name"
            style: "bold cyan"
          - type: regex
            pattern: "->.*$"
            style: "bold yellow"
```

</details>

## 📖 Helper Functions

### `create_bullet_point_chapter`

This helper function simplifies the creation of chapters that present information in a bullet-point format. Each step in the generated chapter will highlight a different bullet point.

#### Python

<details>
<summary><b>Python</b></summary>

```python
from rich.style import Style
from tuitorial import TutorialApp
from tuitorial.helpers import create_bullet_point_chapter

bullet_points = [
    "This is the first point.",
    "Here is the second point.",
    "And finally, the third point.",
]

# Create a chapter with bullet points
bullet_point_chapter = create_bullet_point_chapter(
    "My Bullet Points",
    bullet_points,
    style=Style(color="magenta", bold=True),
)

# You can also add extra descriptive text per step:
bullet_point_chapter_with_extras = create_bullet_point_chapter(
    "My Bullet Points with Extras",
    bullet_points,
    extras=[
        "Extra info for point 1.",
        "More details about point 2.",
        "Final thoughts on point 3.",
    ],
    style=Style(color="green", bold=True),
)

app = TutorialApp([bullet_point_chapter, bullet_point_chapter_with_extras])
app.run()
```

</details>

<details>
<summary><b>YAML</b></summary>

```yaml
chapters:
  - title: "My Bullet Points"
    type: bullet_points
    bullet_points:
      - "This is the first point."
      - "Here is the second point."
      - "And finally, the third point."
    style: "magenta bold"

  - title: "My Bullet Points with Extras"
    type: bullet_points
    bullet_points:
      - "This is the first point."
      - "Here is the second point."
      - "And finally, the third point."
    extras:
      - "Extra info for point 1."
      - "More details about point 2."
      - "Final thoughts on point 3."
    style: "green bold"
```

</details>

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
