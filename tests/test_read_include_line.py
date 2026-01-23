"""Tests for _readIncludeLine function."""
import pytest
from pathlib import Path

from mkdocs_build_plantuml_plugin.plantuml import PuElement


class TestReadIncludeLine:
    """Tests for BuildPlantumlPlugin._readIncludeLine method."""

    def test_includeurl_passthrough(self, plugin, tmp_path):
        """!includeurl with URL should be passed through unchanged."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        line = "!includeurl http://example.com/theme.puml"
        temp_file = ""

        result = plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        assert line in result

    def test_include_relative_path(self, plugin, tmp_path):
        """!include with relative path should read and include file content."""
        # Create the include file
        include_dir = tmp_path / "themes"
        include_dir.mkdir()
        include_file = include_dir / "light.puml"
        include_file.write_text("' Theme content\nskinparam backgroundColor white\n")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        line = "!include themes/light.puml"
        temp_file = ""

        result = plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        assert "skinparam backgroundColor white" in result

    def test_include_http_passthrough(self, plugin, tmp_path):
        """!include with http URL should be passed through unchanged."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        line = "!include http://example.com/theme.puml"
        temp_file = ""

        result = plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        assert "!include http://example.com/theme.puml" in result

    def test_include_stdlib_passthrough(self, plugin, tmp_path):
        """!include <stdlib> should be passed through unchanged."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        line = "!include <C4/C4_Container>"
        temp_file = ""

        result = plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        assert "!include <C4/C4_Container>" in result

    def test_include_file_not_found(self, plugin, tmp_path):
        """!include with nonexistent file should raise exception."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        line = "!include nonexistent.puml"
        temp_file = ""

        with pytest.raises(Exception) as exc_info:
            plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        assert "Include could not be resolved" in str(exc_info.value)

    def test_includesub_valid(self, plugin, tmp_path):
        """!includesub with valid syntax should extract sub content."""
        # Create file with sub definition
        include_file = tmp_path / "subs.puml"
        include_file.write_text("""
!startsub MYSUBNAME
skinparam class {
  BackgroundColor Yellow
}
!endsub
""")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        line = "!includesub subs.puml!MYSUBNAME"
        temp_file = ""

        result = plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        assert "BackgroundColor Yellow" in result

    def test_includesub_invalid_syntax(self, plugin, tmp_path):
        """!includesub without ! separator should raise exception."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        # Missing the ! separator between file and sub name
        line = "!includesub subs.puml"
        temp_file = ""

        with pytest.raises(Exception) as exc_info:
            plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        assert "Invalid !includesub syntax" in str(exc_info.value)

    def test_dark_mode_theme_replacement(self, plugin, tmp_path):
        """In dark mode, light.puml should be replaced with dark.puml."""
        # Create both theme files
        themes_dir = tmp_path / "themes"
        themes_dir.mkdir()
        (themes_dir / "light.puml").write_text("' Light theme\n")
        (themes_dir / "dark.puml").write_text("' Dark theme\nskinparam dark true\n")

        plugin.config["theme_light"] = "light.puml"
        plugin.config["theme_dark"] = "dark.puml"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        line = "!include themes/light.puml"
        temp_file = ""

        result = plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), True)

        # Should have dark theme content, not light
        assert "skinparam dark true" in result

    def test_unknown_include_type_raises(self, plugin, tmp_path):
        """Unknown include format should raise exception."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        # Invalid include line (no matching pattern)
        line = "!include"
        temp_file = ""

        with pytest.raises(Exception) as exc_info:
            plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        assert "Unknown include type" in str(exc_info.value)

    def test_include_updates_inc_time(self, plugin, tmp_path):
        """Including a file should update diagram.inc_time."""
        # Create include file
        include_file = tmp_path / "include.puml"
        include_file.write_text("' Include content\n")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0

        line = "!include include.puml"
        temp_file = ""

        plugin._readIncludeLine(diagram, line, temp_file, str(tmp_path), False)

        # inc_time should be updated via _read_incl_line_file
        assert diagram.inc_time > 0
