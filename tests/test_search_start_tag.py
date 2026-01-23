"""Tests for _search_start_tag function."""
import pytest
from pathlib import Path

from mkdocs_build_plantuml_plugin.plantuml import PuElement


class TestSearchStartTag:
    """Tests for BuildPlantumlPlugin._search_start_tag method."""

    def test_startuml_without_filename(self, plugin, tmp_path):
        """@startuml without filename should return False."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.src_file = ["@startuml\n", "actor User\n", "@enduml\n"]

        result = plugin._search_start_tag(diagram)

        assert result is False
        assert diagram.out_file == ""

    def test_startuml_with_filename(self, plugin, tmp_path):
        """@startuml with filename should set out_file and return True."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.src_file = ["@startuml mydiagram\n", "actor User\n", "@enduml\n"]

        result = plugin._search_start_tag(diagram)

        assert result is True
        assert diagram.out_file == str(tmp_path / "out" / "mydiagram.png")

    def test_startuml_with_filename_theme(self, plugin_with_theme, tmp_path):
        """@startuml with filename and theme_enabled should set out_file_dark."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.src_file = ["@startuml mydiagram\n", "actor User\n", "@enduml\n"]

        result = plugin_with_theme._search_start_tag(diagram)

        assert result is True
        assert diagram.out_file == str(tmp_path / "out" / "mydiagram.png")
        assert diagram.out_file_dark == str(tmp_path / "out" / "mydiagram_dark.png")

    def test_no_startuml_tag(self, plugin, tmp_path):
        """File without @startuml should return False."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.src_file = ["' This is a comment\n", "actor User\n"]

        result = plugin._search_start_tag(diagram)

        assert result is False

    def test_startuml_with_trailing_whitespace(self, plugin, tmp_path):
        """@startuml with trailing whitespace should extract filename."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.src_file = ["@startuml myname  \n", "actor User\n", "@enduml\n"]

        result = plugin._search_start_tag(diagram)

        assert result is True
        assert "myname" in diagram.out_file

    def test_startuml_with_leading_whitespace_no_filename(self, plugin, tmp_path):
        """@startuml with leading whitespace returns True but finds leading space first."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        # Leading whitespace causes line.find(" ") to return 0, so ws > 0 is False
        diagram.src_file = ["  @startuml myname\n", "actor User\n", "@enduml\n"]

        result = plugin._search_start_tag(diagram)

        # Returns False because line.find(" ") returns 0 (first leading space), not > 0
        assert result is False

    def test_startuml_with_svg_format(self, plugin_svg_format, tmp_path):
        """@startuml with SVG format should use .svg extension."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.src_file = ["@startuml mydiagram\n", "actor User\n", "@enduml\n"]

        result = plugin_svg_format._search_start_tag(diagram)

        assert result is True
        assert diagram.out_file.endswith(".svg")

    def test_startuml_not_on_first_line(self, plugin, tmp_path):
        """@startuml on a later line should still be found."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.src_file = [
            "' Header comment\n",
            "' Another comment\n",
            "@startuml mydiagram\n",
            "actor User\n",
            "@enduml\n"
        ]

        result = plugin._search_start_tag(diagram)

        assert result is True
        assert "mydiagram" in diagram.out_file
