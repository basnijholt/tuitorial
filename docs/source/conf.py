#
# Configuration file for the Sphinx documentation builder.
#

import os
import sys
from pathlib import Path

package_path = Path("../..").resolve()
sys.path.insert(0, str(package_path))
os.environ["PYTHONPATH"] = ":".join(
    (str(package_path), os.environ.get("PYTHONPATH", "")),
)
docs_path = Path("..").resolve()
sys.path.insert(1, str(docs_path))

import tuitorial  # noqa: E402, isort:skip

# -- Project information -----------------------------------------------------

project = "tuitorial"
author = "tuitorial Developers"
copyright = f"2024, {author}"

version = ".".join(tuitorial.__version__.split(".")[:3])
release = version


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_nb",
    "sphinx_togglebutton",
    "sphinx_copybutton",
    "notfound.extension",
]

templates_path = ["_templates"]
source_suffix = [".rst", ".md"]
master_doc = "index"
language = "en"
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

html_logo = "https://github.com/basnijholt/nijho.lt/raw/92b0aa820318f466388d828adf01120760255acf/content/project/tuitorial/featured.png"
html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

# -- Options for HTMLHelp output ---------------------------------------------

htmlhelp_basename = "tuitorialdoc"

# -- Extension configuration -------------------------------------------------

default_role = "autolink"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_member_order = "bysource"

# myst-nb configuration
nb_execution_mode = "cache"
nb_execution_timeout = 180
nb_execution_raise_on_error = True
myst_heading_anchors = 4
myst_enable_extensions = [
    "html_admonition",
    "colon_fence",
]
html_theme_options = {
    "show_toc_level": 2,
    "repository_url": "https://github.com/tuitorial/tuitorial",
    "repository_branch": "main",
    "home_page_in_toc": False,
    "path_to_docs": "docs",
    "show_navbar_depth": 1,
    "use_edit_page_button": True,
    "use_repository_button": True,
    "use_download_button": True,
    "navigation_with_keys": False,
}


def replace_named_emojis(input_file: Path, output_file: Path) -> None:
    """Replace named emojis in a file with unicode emojis."""
    import emoji

    with input_file.open("r") as infile:
        content = infile.read()
        content_with_emojis = emoji.emojize(content, language="alias")

        with output_file.open("w") as outfile:
            outfile.write(content_with_emojis)




def _change_alerts_to_admonitions(input_text: str) -> str:
    # Splitting the text into lines
    lines = input_text.split("\n")

    # Placeholder for the edited text
    edited_text = []

    # Mapping of markdown markers to their new format
    mapping = {
        "IMPORTANT": "important",
        "NOTE": "note",
        "TIP": "tip",
        "WARNING": "caution",
    }

    # Variable to keep track of the current block type
    current_block_type = None

    for line in lines:
        # Check if the line starts with any of the markers
        if any(line.strip().startswith(f"> [!{marker}]") for marker in mapping):
            # Find the marker and set the current block type
            current_block_type = next(marker for marker in mapping if f"> [!{marker}]" in line)
            # Start of a new block
            edited_text.append("```{" + mapping[current_block_type] + "}")
        elif current_block_type and line.strip() == ">":
            # Empty line within the block, skip it
            continue
        elif current_block_type and not line.strip().startswith(">"):
            # End of the current block
            edited_text.append("```")
            edited_text.append(line)  # Add the current line as it is
            current_block_type = None  # Reset the block type
        elif current_block_type:
            # Inside the block, so remove '>' and add the line
            edited_text.append(line.lstrip("> ").rstrip())
        else:
            # Outside any block, add the line as it is
            edited_text.append(line)

    # Join the edited lines back into a single string
    return "\n".join(edited_text)


def change_alerts_to_admonitions(input_file: Path, output_file: Path) -> None:
    """Change markdown alerts to admonitions.

    For example, changes
    > [!NOTE]
    > This is a note.
    to
    ```{note}
    This is a note.
    ```
    """
    with input_file.open("r") as infile:
        content = infile.read()
    new_content = _change_alerts_to_admonitions(content)

    with output_file.open("w") as outfile:
        outfile.write(new_content)


def process_readme_for_sphinx_docs(readme_path: Path, docs_path: Path) -> None:
    """Process the README.md file for Sphinx documentation generation.

    Parameters
    ----------
    readme_path
        Path to the original README.md file.
    docs_path
        Path to the Sphinx documentation source directory.

    """
    # Step 1: Copy README.md to the Sphinx source directory and apply transformations
    output_file = docs_path / "source" / "README.md"
    replace_named_emojis(readme_path, output_file)
    change_alerts_to_admonitions(output_file, output_file)


# Process the README.md file for Sphinx documentation
readme_path = package_path / "README.md"
process_readme_for_sphinx_docs(readme_path, docs_path)


# Group into single streams to prevent multiple output boxes
nb_merge_streams = True


def setup(app) -> None:
    pass
