# Tuitorial 📚

> Create beautiful terminal-based code tutorials with syntax highlighting and interactive navigation.

[![Documentation](https://readthedocs.org/projects/tuitorial/badge/?version=latest)](https://tuitorial.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/tuitorial.svg)](https://badge.fury.io/py/tuitorial)
[![Python](https://img.shields.io/pypi/pyversions/tuitorial.svg)](https://pypi.org/project/tuitorial/)
[![Tests](https://github.com/basnijholt/tuitorial/actions/workflows/pytest.yml/badge.svg)](https://github.com/basnijholt/tuitorial/actions/workflows/pytest.yml)
[![Coverage](https://codecov.io/gh/basnijholt/tuitorial/branch/main/graph/badge.svg)](https://codecov.io/gh/basnijholt/tuitorial)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub Repo stars](https://img.shields.io/github/stars/basnijholt/tuitorial)](https://github.com/basnijholt/tuitorial)

> [!NOTE]
> **tuitorial**? Typo? No, a combination of "TUI" (Terminal User Interface) and "tutorial".

<!-- toc-start -->
<details><summary><b><u>[ToC]</u></b> 📚</summary>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [🎯 Features](#-features)
- [🤨 Why?](#-why)
- [📸 Recording](#-recording)
- [🚀 Installation](#-installation)
- [🎮 Quick Start](#-quick-start)
- [📖 Usage](#-usage)
  - [📚 Multiple Chapters](#-multiple-chapters)
  - [🚶 Steps](#-steps)
  - [🎯 Focus Types](#-focus-types)
    - [Literal Match](#literal-match)
    - [Regular Expression](#regular-expression)
    - [Line Number](#line-number)
    - [Range](#range)
    - [Starts With](#starts-with)
    - [Between](#between)
    - [Line Containing](#line-containing)
    - [Markdown](#markdown)
    - [Syntax Highlighting](#syntax-highlighting)
  - [🎨 Styling](#-styling)
  - [🔄 Live Reloading (Development Mode)](#-live-reloading-development-mode)
  - [🎨 Custom Highlighting Patterns](#-custom-highlighting-patterns)
  - [✨ Multiple Highlights per Step](#-multiple-highlights-per-step)
  - [🖼️ Displaying Images](#-displaying-images)
    - [ImageStep](#imagestep)
    - [Image Positioning and Sizing](#image-positioning-and-sizing)
    - [Alignment](#alignment)
  - [🎬 Title Slide](#-title-slide)
  - [📖 Helper Functions](#-helper-functions)
    - [`create_bullet_point_chapter`](#create_bullet_point_chapter)
- [⌨️ Controls](#-controls)
- [🧪 Development](#-development)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [📚 Similar Projects](#-similar-projects)
- [🐛 Troubleshooting](#-troubleshooting)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

</details>
<!-- toc-end -->

## 🎯 Features

- 🎨 **Rich Syntax Highlighting:** Customizable styles, wide language support.
- 🔍 **Multiple Focus Types:** Literal, regex, line, range, startswith, between, line containing, and syntax highlighting.
- 📝 **Step-by-Step Tutorials:** Interactive, sequential steps with clear descriptions.
- 🖼️ **Multimedia:** Markdown rendering and image embedding.
- ⌨️ **Interactive Navigation:** Intuitive keyboard and scroll controls.
- 🖥️ **Beautiful Terminal UI:** Powered by [Textual](https://textual.textualize.io/).
- 🚀 **Customizable:** Python or YAML configuration, custom highlighting.
- 🎓 **Beginner Friendly:** Simple API, no Textual knowledge required.
- ⚡ **Title Slide:** Eye-catching ASCII art title slides.
- 🔄 **Live Reloading:** Automatically refreshes app on YAML update.

## 🤨 Why?

99.9% shouldn't use `tuitorial`. But those 0.1% that should, will love it.

- **Escape the Tyranny of Slide Decks:** Ditch PowerPoint, Google Slides, and Beamer. Embrace the terminal.
- **Code is King:** Keep the focus on your code, where it belongs.
- **Interactive and Engaging:** Step-by-step walkthroughs with interactive navigation.
- **Reproducible and Versionable:** Define tutorials in code (Python or YAML) for easy tracking and updates.
- **Lightweight and Fast:** No more bloated presentation software.
- **Perfect for Nerds:** Ideal for explaining code, technical workshops, interactive documentation, and anyone who loves the terminal.
- **Parametrize:** Create dynamic tutorials driven by code snippets and focus points.

## 📸 Recording

https://github.com/user-attachments/assets/53a0cdff-ed1b-479f-b94c-6a7b113bd8b3

## 🚀 Installation

```bash
pip install tuitorial
```

## 🎮 Quick Start

> [!TIP]
> Have `uv` installed? Run the following command to see a quick example:
> `uvx tuitorial https://raw.githubusercontent.com/basnijholt/tuitorial/refs/heads/main/examples/tuitorial.yaml`

<details>
<summary><b>Python</b></summary>

```python
from tuitorial import Chapter, Step, TuitorialApp, Focus
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
app = TuitorialApp([chapter])
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
            text: 'return f"Hello, {name}!"'
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
2. Either:
   - Use the provided `tuitorial.run_from_yaml(...)` function:
   - Run `tuitorial --watch tutorial.yaml` from the command line.

```bash
# From the command line
tuitorial --watch tutorial.yaml
```

or

```python
# In a separate Python file (e.g., run_yaml.py)
from tuitorial.parse_yaml import run_from_yaml

run_from_yaml("tutorial.yaml")
```

</details>

## 📖 Usage

### 📚 Multiple Chapters

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
app = TuitorialApp([chapter1, chapter2])
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
            text: 'return f"Hello, {name}!"'

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
            text: 'return f"Goodbye, {name}!"'
```

</details>

### 🚶 Steps

Each step in a tutorial consists of a description and a list of focuses.

**Python:**

```python
Step(
    "Step Description",  # Shown in the UI
    [
        Focus.literal("some text"),  # One or more Focus objects
        Focus.regex(r"pattern.*"),   # Can combine different focus types
    ]
)
```

**YAML:**

```yaml
steps:
  - description: "Step Description"
    focus:
      - type: literal
        text: "some text"
      - type: regex
        pattern: "pattern.*"
```

### 🎯 Focus Types

#### Literal Match

**Python:**

```python
Focus.literal("def", style="bold yellow")
Focus.literal("def", style="bold yellow", match_index=[0, 2]) # Highlight the first and third "def"
```

**YAML:**

```yaml
focus:
  - type: literal
    text: "def"
    style: "bold yellow"
  - type: literal
    text: "def"
    style: "bold yellow"
    match_index: [0, 2] # Highlight the first and third "def"
```

**`match_index` note:**

- If provided as an integer, only highlight the nth match (0-based).
- If provided as a list of integers, highlight the matches corresponding to those indices.
- If None, highlight all matches.

#### Regular Expression

**Python:**

```python
Focus.regex(r"def \w+\(.*\):", style="bold green")
```

**YAML:**

```yaml
focus:
  - type: regex
    pattern: "def \\w+\\(.*\\):"
    style: "bold green"
```

#### Line Number

**Python:**

```python
Focus.line(1, style="bold blue")  # Highlight first line
```

**YAML:**

```yaml
focus:
  - type: line
    line_number: 1
    style: "bold blue"
```

#### Range

Highlights a specific range of characters within the code based on their indices (0-based).

**Python:**

```python
Focus.range(0, 10, style="bold magenta")  # Highlight first 10 characters
```

**YAML:**

```yaml
focus:
  - type: range
    start: 0
    end: 10
    style: "bold magenta"
```

#### Starts With

Highlights lines starting with the specified text. Can be configured to match from the start of any line or only at the start of the line.

**Python:**

```python
Focus.startswith("import", style="bold blue", from_start_of_line=True)
Focus.startswith("from", style="bold blue", from_start_of_line=False)
```

**YAML:**

```yaml
focus:
  - type: startswith
    text: "import"
    style: "bold blue"
    from_start_of_line: true
  - type: startswith
    text: "from"
    style: "bold blue"
    from_start_of_line: false
```

#### Between

Highlights text between two specified patterns. Supports inclusive or exclusive bounds, multiline matching, and greedy or non-greedy matching.

**Python:**

```python
Focus.between("start_function", "end_function", style="bold blue", inclusive=True, multiline=True)
```

**YAML:**

```yaml
focus:
  - type: between
    start_pattern: "start_function"
    end_pattern: "end_function"
    style: "bold blue"
    inclusive: true
    multiline: true
    match_index: 0 # Only highlight the first match (0-based)
    greedy: true # Use greedy matching (longest possible match)
```

#### Line Containing

Highlights entire lines that contain a specified pattern, with optional inclusion of surrounding lines.
Can match either literal text or regular expressions, and can select specific matches.

**Python:**

```python
# Highlight all lines containing "def"
Focus.line_containing("def", style="bold yellow")

# Include surrounding lines
Focus.line_containing(
    "def",
    style="bold yellow",
    lines_before=1,
    lines_after=1,
)

# Use regex and only highlight second match
Focus.line_containing(
    r"def \w+",
    style="bold blue",
    regex=True,
    match_index=1,
)
```

**YAML:**

```yaml
focus:
  - type: line_containing
    pattern: "def"
    style: "bold yellow"
    lines_before: 1 # optional: include line before match
    lines_after: 1 # optional: include line after match
    regex: false # optional: treat pattern as regex
    match_index: 0 # optional: only highlight first match (0-based)
```

The `line_containing` focus type is particularly useful for:

- Highlighting function definitions and their body
- Showing imports and their surrounding context
- Focusing on specific sections of code while maintaining readability
- Matching patterns across multiple lines with surrounding context

#### Markdown

Displays the content as Markdown instead of code, using Textual's built-in `Markdown` widget. Only one `markdown` focus is allowed per step, and it will take precedence over any other focus types.

**Python:**

```python
Focus.markdown()
```

**YAML:**

```yaml
focus:
  - type: markdown
```

#### Syntax Highlighting

Uses Rich's built-in syntax highlighting for the entire code or specific lines. Only one `syntax` focus is allowed per step, and it will take precedence over any other focus types besides `markdown`.

**Python:**

```python
# Highlight all code
Focus.syntax(theme="monokai", line_numbers=True)

# Highlight specific lines
Focus.syntax(
    theme="monokai",
    start_line=0,
    end_line=3,
)
```

**YAML:**

```yaml
focus:
  - type: syntax
    lexer: "python" # optional: language to highlight (default: python)
    theme: "monokai" # optional: color theme
    line_numbers: true # optional: show line numbers
    start_line: 0 # optional: first line to highlight
    end_line: 3 # optional: last line to highlight
```

### 🎨 Styling

Styles can be customized using Rich's style syntax:

**Python:**

```python
from rich.style import Style

# Using string syntax
Focus.literal("def", style="bold yellow")

# Using Style object
Focus.literal("def", style=Style(bold=True, color="yellow"))
```

**YAML:**

```yaml
focus:
  - type: literal
    text: "def"
    style: "bold yellow" # Using string syntax

  - type: literal
    text: "def"
    style: "bold color(yellow)" # Using Style object
```

</details>

### 🔄 Live Reloading (Development Mode)

`tuitorial` offers a convenient development mode that automatically reloads your tutorial whenever you make changes to the YAML configuration file. This allows you to iterate quickly on your tutorial's content and see your changes reflected in real-time without manually restarting the application.

**Usage:**

To enable live reloading, use the `--watch` (or `-w`) flag when running `tuitorial` from the command line:

```bash
tuitorial tutorial.yaml --watch
```

or

```bash
tuitorial tutorial.yaml -w
```

**How it Works:**

When you run `tuitorial` with the `--watch` flag, it will monitor the specified YAML file for any modifications. If a change is detected, `tuitorial` will automatically:

1. Parse the updated YAML configuration.
2. Reload the tutorial content within the running application.
3. Preserve the current chapter and step, so you can continue where you left off.

### 🎨 Custom Highlighting Patterns

**Python:**

<details>
<summary><b>Python</b></summary>

```python
from tuitorial import TuitorialApp, Focus
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
app = TuitorialApp([chapter])
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

### ✨ Multiple Highlights per Step

**Python:**

<details>
<summary><b>Python</b></summary>

```python
from tuitorial import Chapter, Step, TuitorialApp, Focus
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
    Step(
        "Complex Example",
        [
            Focus.literal("def", style="bold yellow"),
            Focus.regex(r"\(.*\)", style="italic green"),  # Highlight function arguments
            Focus.line(2, style="underline blue"),  # Highlight the second line
        ],
    ),
]

# Create a chapter
chapter = Chapter("Multiple Highlights", code, tutorial_steps)

# Run the tutorial
app = TuitorialApp([chapter])
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
            text: "name"
            style: "bold cyan"
          - type: regex
            pattern: "->.*$"
            style: "bold yellow"
```

</details>

### 🖼️ Displaying Images

`tuitorial` supports displaying images within your tutorials using the `ImageStep` class.
This allows you to incorporate visual aids, diagrams, or any other images to enhance your presentations.

#### ImageStep

The `ImageStep` class takes the path to an image file (or a PIL Image object) and a description as input.

**Python:**

```python
from pathlib import Path
from tuitorial import Chapter, ImageStep, TuitorialApp

# Path to your image
image_path = Path("path/to/your/image.png")

# Define an ImageStep
image_step = ImageStep("Displaying an example image", image_path)

# Create a chapter with the image step
chapter = Chapter("Image Example", "", [image_step])

# Run the tutorial
app = TuitorialApp([chapter])
app.run()
```

**YAML:**

```yaml
chapters:
  - title: "Image Example"
    steps:
      - description: "Displaying an example image"
        image: "path/to/your/image.png"
```

#### Image Positioning and Sizing

You can control the size of the image using the `width` and `height` properties when creating the `Image` widget within the `ImageStep`. These properties accept either integer values (for pixel dimensions) or strings representing percentages (relative to the container's size).

**Python:**

```python
from pathlib import Path
from textual_image.widget import Image
from tuitorial import Chapter, ImageStep, TuitorialApp

image_path = Path("path/to/your/image.png")

# Set fixed width in cells and auto height
image_step_fixed = ImageStep("Fixed Size Image", image_path, width=300, height="auto")

# Set width as a percentage of the container and height in cells
image_step_percentage = ImageStep("Percentage Width Image", image_path, width="50%", height=200)

chapter = Chapter("Image Examples", "", [image_step_fixed, image_step_percentage])
app = TuitorialApp([chapter])
app.run()
```

**YAML:**

```yaml
chapters:
  - title: "Image Examples"
    steps:
      - description: "Fixed Size Image"
        image: "path/to/your/image.png"
        width: 300 # Fixed width in cells
        height: "auto" # Auto height
      - description: "Percentage Width Image"
        image: "path/to/your/image.png"
        width: "50%" # Width as a percentage
        height: 200 # Fixed height in cells
```

#### Alignment

By default, images are aligned to the center.
You can align images to the left or right by setting `halign` to `"left"` or `"right"` respectively when creating the `Image` widget.

```python
image_widget = Image(image_path, halign="left")
```

```yaml
chapters:
  - title: "Image Alignment"
    steps:
      - description: "Left Aligned Image"
        image: "path/to/your/image.png"
        halign: "left"
      - description: "Right Aligned Image"
        image: "path/to/your/image.png"
        halign: "right"
```

### 🎬 Title Slide

`tuitorial` allows you to create a visually appealing title slide for your tutorial using ASCII art generated by [PyFiglet](https://github.com/pwaller/pyfiglet).

**Python:**

```python
from tuitorial import TuitorialApp, TitleSlide

title_slide = TitleSlide(
    "My Tutorial",     # Title text (required)
    subtitle="An Awesome Tutorial",  # Optional subtitle
    font="slant",   # Optional: PyFiglet font (see available fonts below)
    gradient="lava",  # Optional: Gradient color (see available gradients below)
)

app = TuitorialApp([], title_slide=title_slide)
app.run()
```

**YAML:**

```yaml
title_slide:
  title: "My Tutorial"
  subtitle: "An Awesome Tutorial"
  font: "slant"
  gradient: "lava"

chapters:
  # ... your chapters ...
```

**Available Fonts:**

You can choose from a variety of fonts provided by PyFiglet. Some popular options include:

- `slant`
- `3-d`
- `3x5`
- `5lineoblique`
- `acrobatic`
- `avatar`
- `banner`
- `big`
- `block`
- `bubble`
- `digital`
- `doom`
- `isometric1`
- `letters`
- `rectangles`
- `standard`

You can find a full list of available fonts in the [PyFiglet documentation](https://github.com/pwaller/pyfiglet/tree/master/pyfiglet/fonts) or by running:

```python
import pyfiglet
print(pyfiglet.FigletFont.getFonts())
```

**Available Gradients:**

You can choose from a variety of gradients Tuitorial provides. These are:

<!-- CODE:START -->
<!-- import tuitorial.widgets -->
<!-- for name in tuitorial.widgets.GRADIENTS: -->
<!--     print(f"- `{name}`") -->
<!-- CODE:END -->
<!-- OUTPUT:START -->
<!-- ⚠️ This content is auto-generated by `markdown-code-runner`. -->
- `lava`
- `blue`
- `green`
- `rainbow`
- `pink`
- `ocean`

<!-- OUTPUT:END -->

### 📖 Helper Functions

#### `create_bullet_point_chapter`

This helper function simplifies the creation of chapters that present information in a bullet-point format.
It automatically generates the code content from the list of bullet points, and each step in the generated chapter will highlight a different bullet point.

<details>
<summary><b>Python</b></summary>

```python
from rich.style import Style
from tuitorial import TuitorialApp
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

app = TuitorialApp([bullet_point_chapter, bullet_point_chapter_with_extras])
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
      - text: "This is the first point."
        extra: "Extra info for point 1."
      - text: "Here is the second point."
        extra: "More details about point 2."
      - text: "And finally, the third point."
        extra: "More details about point 2."
      - Fourth point without extra
    style: "green bold"
```

</details>

## ⌨️ Controls

- `↑` Previous step in current chapter
- `↓` Next step in current chapter
- `→` Next chapter
- `←` Previous chapter
- `r` Reset to first step of current chapter
- `d` Toggle dim/bright background
- `q` Quit `tuitorial`

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

4. Enable pre-commit hooks:

   ```bash
   pre-commit install
   ```

5. Run tests:

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

- [Spiel](https://github.com/JoshKarpel/spiel) Display richly-styled presentations using your terminal (also Textual-based, more for general presentations, no focus modes like `tuitorial`).
- [present](https://github.com/vinayak-mehta/present) A terminal-based presentation tool with markdown support (more focused on general presentations, less on code tutorials) also the last commit was in 2020.

## 🐛 Troubleshooting

**Q: The colors don't show up correctly in my terminal.**
A: Make sure your terminal supports true color and has a compatible color scheme.

**Q: The tutorial doesn't respond to keyboard input.**
A: Verify that your terminal emulator is properly forwarding keyboard events.
