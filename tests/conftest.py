"""Pytest fixtures for mkdocs-build-plantuml-plugin tests."""
import pytest
from pathlib import Path

from mkdocs_build_plantuml_plugin.plantuml import (
    BuildPlantumlPlugin,
    PuElement,
    DiagramRoot,
)


@pytest.fixture
def plugin():
    """Create a BuildPlantumlPlugin instance with default config."""
    p = BuildPlantumlPlugin()
    # Initialize config with defaults
    p.config = {
        "render": "server",
        "server": "https://www.plantuml.com/plantuml",
        "disable_ssl_certificate_validation": False,
        "bin_path": "/usr/local/bin/plantuml",
        "output_format": "png",
        "allow_multiple_roots": False,
        "diagram_root": "docs/diagrams",
        "output_folder": "out",
        "output_in_dir": False,
        "input_folder": "src",
        "input_extensions": "",
        "theme_enabled": False,
        "theme_folder": "include/themes/",
        "theme_light": "light.puml",
        "theme_dark": "dark.puml",
    }
    return p


@pytest.fixture
def plugin_with_theme(plugin):
    """Create a plugin with theme enabled."""
    plugin.config["theme_enabled"] = True
    return plugin


@pytest.fixture
def plugin_svg_format(plugin):
    """Create a plugin with SVG output format."""
    plugin.config["output_format"] = "svg"
    return plugin


@pytest.fixture
def example_root():
    """Return Path to example/docs/diagrams."""
    return Path(__file__).parent.parent / "example" / "docs" / "diagrams"


@pytest.fixture
def example_src_dir(example_root):
    """Return Path to example/docs/diagrams/src."""
    return example_root / "src"


@pytest.fixture
def example_include_dir(example_root):
    """Return Path to example/docs/diagrams/include."""
    return example_root / "include"


@pytest.fixture
def tmp_puml_file(tmp_path):
    """Create a temporary .puml file for testing."""
    puml_content = """@startuml
actor User
User -> System : Request
System --> User : Response
@enduml
"""
    puml_file = tmp_path / "test.puml"
    puml_file.write_text(puml_content)
    return puml_file


@pytest.fixture
def tmp_puml_with_name(tmp_path):
    """Create a .puml file with named output (@startuml mydiagram)."""
    puml_content = """@startuml mydiagram
actor User
@enduml
"""
    puml_file = tmp_path / "test_named.puml"
    puml_file.write_text(puml_content)
    return puml_file


@pytest.fixture
def diagram_element(tmp_path):
    """Create a basic PuElement for testing."""
    puml_file = tmp_path / "test.puml"
    puml_file.write_text("@startuml\nactor User\n@enduml\n")

    elem = PuElement("test.puml", str(tmp_path))
    elem.root_dir = str(tmp_path)
    elem.out_dir = str(tmp_path / "out")
    elem.src_file = puml_file.read_text().splitlines(keepends=True)
    return elem


@pytest.fixture
def diagram_root_fixture(tmp_path):
    """Create a DiagramRoot for testing."""
    root = DiagramRoot()
    root.root_dir = str(tmp_path)
    root.src_dir = str(tmp_path / "src")
    return root


@pytest.fixture
def sequence_puml_path(example_src_dir):
    """Return path to example sequence.puml file."""
    return example_src_dir / "sequence.puml"


@pytest.fixture
def context_goals_puml_path(example_src_dir):
    """Return path to example context_goals.puml file."""
    return example_src_dir / "context_goals.puml"
