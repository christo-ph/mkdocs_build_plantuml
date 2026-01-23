"""Tests for _readFile function."""
import pytest
from pathlib import Path
import string

from mkdocs_build_plantuml_plugin.plantuml import PuElement, plantuml_alphabet


class TestReadFile:
    """Tests for BuildPlantumlPlugin._readFile method."""

    def test_simple_diagram_encoded(self, plugin, tmp_path):
        """Simple diagram should have b64encoded set."""
        puml_content = "@startuml\nactor User\n@enduml\n"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.src_file = puml_content.splitlines(keepends=True)
        diagram.inc_time = 0

        plugin._readFile(diagram, False)

        assert diagram.b64encoded != ""
        assert len(diagram.b64encoded) > 0

    def test_concat_file_contains_content(self, plugin, tmp_path):
        """concat_file should contain the merged content."""
        puml_content = "@startuml\nactor User\n@enduml\n"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.src_file = puml_content.splitlines(keepends=True)
        diagram.inc_time = 0

        plugin._readFile(diagram, False)

        assert "@startuml" in diagram.concat_file
        assert "actor User" in diagram.concat_file
        assert "@enduml" in diagram.concat_file

    def test_encoding_is_plantuml_alphabet(self, plugin, tmp_path):
        """Encoded content should only use PlantUML alphabet characters."""
        puml_content = "@startuml\nactor User\nUser -> System : Request\n@enduml\n"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.src_file = puml_content.splitlines(keepends=True)
        diagram.inc_time = 0

        plugin._readFile(diagram, False)

        # PlantUML alphabet: 0-9A-Za-z-_
        valid_chars = set(string.digits + string.ascii_letters + "-_")
        encoded_chars = set(diagram.b64encoded)

        assert encoded_chars.issubset(valid_chars), \
            f"Invalid chars found: {encoded_chars - valid_chars}"

    def test_with_example_sequence(self, plugin, example_src_dir):
        """Test with actual example sequence.puml file."""
        sequence_file = example_src_dir / "sequence.puml"
        if not sequence_file.exists():
            pytest.skip("Example sequence.puml not found")

        content = sequence_file.read_text()

        diagram = PuElement("sequence.puml", str(example_src_dir))
        diagram.root_dir = str(example_src_dir.parent)
        diagram.src_file = content.splitlines(keepends=True)
        diagram.inc_time = 0

        plugin._readFile(diagram, False)

        assert diagram.b64encoded != ""
        assert diagram.concat_file != ""
        # The sequence diagram has these elements
        assert "actor" in diagram.concat_file.lower() or "foo" in diagram.concat_file.lower()

    def test_with_include_resolved(self, plugin, tmp_path):
        """Includes should be resolved in the concat_file."""
        # Create include file
        include_dir = tmp_path / "include"
        include_dir.mkdir()
        include_file = include_dir / "theme.puml"
        include_file.write_text("skinparam backgroundColor white\n")

        puml_content = "@startuml\n!include include/theme.puml\nactor User\n@enduml\n"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.src_file = puml_content.splitlines(keepends=True)
        diagram.inc_time = 0

        plugin._readFile(diagram, False)

        # Include content should be in concat_file
        assert "backgroundColor white" in diagram.concat_file

    def test_dark_mode_theme_swap(self, plugin, tmp_path):
        """Dark mode should swap light theme for dark theme."""
        # Create theme files
        themes_dir = tmp_path / "themes"
        themes_dir.mkdir()
        (themes_dir / "light.puml").write_text("' Light theme\n")
        (themes_dir / "dark.puml").write_text("' Dark theme content\n")

        plugin.config["theme_light"] = "light.puml"
        plugin.config["theme_dark"] = "dark.puml"

        puml_content = "@startuml\n!include themes/light.puml\nactor User\n@enduml\n"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.src_file = puml_content.splitlines(keepends=True)
        diagram.inc_time = 0

        plugin._readFile(diagram, True)  # dark_mode=True

        assert "Dark theme content" in diagram.concat_file

    def test_empty_file_handles_gracefully(self, plugin, tmp_path):
        """Empty file should not crash."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.src_file = []
        diagram.inc_time = 0

        plugin._readFile(diagram, False)

        # Should handle empty gracefully
        assert diagram.concat_file == ""

    def test_encoding_deterministic(self, plugin, tmp_path):
        """Same content should produce same encoding."""
        puml_content = "@startuml\nactor User\n@enduml\n"

        diagram1 = PuElement("test1.puml", str(tmp_path))
        diagram1.root_dir = str(tmp_path)
        diagram1.src_file = puml_content.splitlines(keepends=True)
        diagram1.inc_time = 0

        diagram2 = PuElement("test2.puml", str(tmp_path))
        diagram2.root_dir = str(tmp_path)
        diagram2.src_file = puml_content.splitlines(keepends=True)
        diagram2.inc_time = 0

        plugin._readFile(diagram1, False)
        plugin._readFile(diagram2, False)

        assert diagram1.b64encoded == diagram2.b64encoded
