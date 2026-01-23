"""Tests for _build_out_filename function."""
import pytest
from pathlib import Path

from mkdocs_build_plantuml_plugin.plantuml import PuElement


class TestBuildOutFilename:
    """Tests for BuildPlantumlPlugin._build_out_filename method."""

    def test_puml_to_png(self, plugin, tmp_path):
        """test.puml should become test.png with default format."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")

        plugin._build_out_filename(diagram)

        assert diagram.out_file == str(tmp_path / "out" / "test.png")

    def test_puml_to_svg(self, plugin_svg_format, tmp_path):
        """test.puml should become test.svg with svg format."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")

        plugin_svg_format._build_out_filename(diagram)

        assert diagram.out_file == str(tmp_path / "out" / "test.svg")

    def test_dark_filename_generated(self, plugin_with_theme, tmp_path):
        """Theme enabled should generate _dark suffix file."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")

        plugin_with_theme._build_out_filename(diagram)

        assert diagram.out_file == str(tmp_path / "out" / "test.png")
        assert diagram.out_file_dark == str(tmp_path / "out" / "test_dark.png")

    def test_dark_filename_svg(self, plugin, tmp_path):
        """Theme enabled with SVG should generate _dark.svg."""
        plugin.config["theme_enabled"] = True
        plugin.config["output_format"] = "svg"
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")

        plugin._build_out_filename(diagram)

        assert diagram.out_file == str(tmp_path / "out" / "test.svg")
        assert diagram.out_file_dark == str(tmp_path / "out" / "test_dark.svg")

    def test_plantuml_extension(self, plugin, tmp_path):
        """diagram.plantuml should become diagram.png."""
        diagram = PuElement("diagram.plantuml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")

        plugin._build_out_filename(diagram)

        assert diagram.out_file == str(tmp_path / "out" / "diagram.png")

    def test_no_extension_file(self, plugin, tmp_path):
        """File without extension should not crash."""
        diagram = PuElement("noextension", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")

        # This tests the edge case where rfind returns -1
        plugin._build_out_filename(diagram)

        # When no '.' is found, out_file stays as default (empty or unchanged)
        # The code only sets out_file if out_index > -1
        assert diagram.out_file == str(tmp_path / "out" / "")

    def test_multiple_dots_in_filename(self, plugin, tmp_path):
        """File with multiple dots should use last extension."""
        diagram = PuElement("my.complex.diagram.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")

        plugin._build_out_filename(diagram)

        assert diagram.out_file == str(tmp_path / "out" / "my.complex.diagram.png")

    def test_returns_diagram(self, plugin, tmp_path):
        """Method should return the diagram object."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")

        result = plugin._build_out_filename(diagram)

        assert result is diagram
