"""A Panel web app to create a tutorial from a YAML file.

Run with:
`uv run --group webapp panel serve app.py --autoreload`.
"""

from pathlib import Path

import panel as pn
import param
from panel.layout import Row
from panel.pane import Image, Markdown
from panel.widgets import Button, CodeEditor, FileInput

from tuitorial import TuitorialApp
from tuitorial.parse_yaml import parse_yaml_config

pn.extension("terminal")
pn.extension("codeeditor")
pn.extension(design="material", theme="dark")


# --- Logo ---
LOGO_URL = "https://raw.githubusercontent.com/basnijholt/tuitorial/refs/heads/main/docs/source/_static/logo-tuitorial.png"
logo = Image(LOGO_URL, width=200, align="center")

# --- Description ---
description = Markdown(
    """
## 📚 Tuitorial: Create beautiful terminal-based code tutorials with syntax highlighting and interactive navigation.

[![GitHub Repo stars](https://img.shields.io/github/stars/basnijholt/tuitorial)](https://github.com/basnijholt/tuitorial)

**🎯 Features:**

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
""",
)

# --- Components ---
# Create a Textual pane
textual_pane = pn.pane.Textual(width=1000, height=800)

# Create a FileInput widget
file_input = FileInput(accept=".yaml")

yaml_input = CodeEditor(
    name="YAML Content",
    language="yaml",
    height=300,
    width=400,
    sizing_mode="stretch_width",
    min_height=100,
    theme="dracula",
)


def read_yaml_file(filepath: Path) -> str | None:
    """Reads the content of a YAML file."""
    if not filepath.exists():
        print(f"Error: File '{filepath}' not found.")
        return None

    with filepath.open() as f:
        return f.read()


root = Path(__file__).parent.parent
yaml_content = read_yaml_file(root / "examples" / "tuitorial.yaml")

if yaml_content:
    yaml_input.value = yaml_content


# Create a Button widget to trigger the update
update_button = Button(name="Update Tutorial", button_type="primary")

# Create an area for the error message (initially hidden)
error_message = CodeEditor(
    name="Exceptions",
    language="python",
    sizing_mode="stretch_width",
    visible=False,
    height=300,
    width=400,
    min_height=100,
    theme="dracula",
    readonly=True,
)


# --- Functions ---
def update_tutorial(_event: param.parameterized.Event | None = None) -> None:
    """Updates the Textual pane with a new TuitorialApp based on the YAML content."""
    error_message.visible = False  # Hide error message initially
    error_message.value = ""

    if file_input.value:
        # If a file is uploaded, use its content
        try:
            yaml_content = file_input.value.decode("utf-8")
            yaml_input.value = yaml_content
            error_message.visible = False

        except Exception as e:  # noqa: BLE001
            error_message.value = (
                "Error: Invalid file encoding. Please upload a UTF-8 encoded YAML file. Error: "
                + str(e)
            )
            error_message.visible = True
            return
    else:
        # Otherwise, use the content of the text input
        yaml_content = yaml_input.value

    if not yaml_content.strip():
        error_message.value = "Error: No YAML content provided."
        error_message.visible = True
        return

    try:
        with open("temp.yaml", "w") as f:  # noqa: PTH123
            f.write(yaml_content)
        chapters, title_slide = parse_yaml_config("temp.yaml")
        app = TuitorialApp(chapters, title_slide)
        textual_pane.object = app
        status_message.object = "Tutorial updated successfully."
        error_message.visible = False
    except Exception as e:  # noqa: BLE001
        error_message.value = f"Error: {e}"
        error_message.visible = True


# Function to handle file upload
def handle_file_upload(_event: param.parameterized.Event | None = None) -> None:
    """Handles file upload and updates the text input with the file content."""
    if file_input.value:
        try:
            yaml_content = file_input.value.decode("utf-8")
            yaml_input.value = yaml_content
        except UnicodeDecodeError:
            error_message.value = (
                "Error: Invalid file encoding. Please upload a UTF-8 encoded YAML file."
            )
            error_message.visible = True


# --- Bindings ---
# Bind the handle_file_upload function to the value_throttled event of file_input
file_input.param.watch(handle_file_upload, "value")

# Bind the update_tutorial function to the button click event
update_button.on_click(update_tutorial)

# --- Layout ---
# Create a status message area (for success messages)
status_message = Markdown("")

# Layout the widgets
layout = pn.Column(
    logo,
    description,
    file_input,
    Row(yaml_input, error_message),  # Place YAML input and error message side-by-side
    update_button,
    status_message,
    textual_pane,
)

# --- Serve ---
# Serve the app
layout.servable()
