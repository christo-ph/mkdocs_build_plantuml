"""Tests for _read_incl_sub function."""
import pytest
from pathlib import Path

from mkdocs_build_plantuml_plugin.plantuml import PuElement


class TestReadInclSub:
    """Tests for BuildPlantumlPlugin._read_incl_sub method."""

    def test_extracts_sub_content(self, plugin, tmp_path):
        """Content between !startsub and !endsub should be extracted."""
        # Create file with sub definition
        include_file = tmp_path / "subs.puml"
        include_file.write_text("""
' Header comment
!startsub MYSUB
skinparam class {
  BackgroundColor Yellow
}
!endsub
' Footer comment
""")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.inc_time = 0
        temp_file = ""

        result = plugin._read_incl_sub(
            diagram, temp_file, False, str(include_file), "MYSUB"
        )

        assert "BackgroundColor Yellow" in result
        # Header and footer should not be included
        assert "Header comment" not in result
        assert "Footer comment" not in result

    def test_enduml_terminates_sub(self, plugin, tmp_path):
        """@enduml should also end a sub section."""
        include_file = tmp_path / "subs.puml"
        include_file.write_text("""
@startuml
!startsub MYSUB
actor User
@enduml
""")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.inc_time = 0
        temp_file = ""

        result = plugin._read_incl_sub(
            diagram, temp_file, False, str(include_file), "MYSUB"
        )

        assert "actor User" in result

    def test_updates_inc_time(self, plugin, tmp_path):
        """Reading includesub should update diagram.inc_time."""
        include_file = tmp_path / "subs.puml"
        include_file.write_text("""
!startsub MYSUB
content here
!endsub
""")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.inc_time = 0
        temp_file = ""

        plugin._read_incl_sub(
            diagram, temp_file, False, str(include_file), "MYSUB"
        )

        # inc_time should be updated to file's mtime
        assert diagram.inc_time > 0
        assert diagram.inc_time == include_file.stat().st_mtime

    def test_sub_not_found_empty(self, plugin, tmp_path):
        """Missing sub should return without the sub content."""
        include_file = tmp_path / "subs.puml"
        include_file.write_text("""
!startsub OTHERSUB
other content
!endsub
""")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.inc_time = 0
        temp_file = "existing content\n"

        result = plugin._read_incl_sub(
            diagram, temp_file, False, str(include_file), "NONEXISTENT"
        )

        # Only the existing content should be there
        assert "existing content" in result
        assert "other content" not in result

    def test_multiple_subs_in_file(self, plugin, tmp_path):
        """Only the requested sub should be extracted."""
        include_file = tmp_path / "subs.puml"
        include_file.write_text("""
!startsub FIRST
first content
!endsub

!startsub SECOND
second content
!endsub

!startsub THIRD
third content
!endsub
""")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.inc_time = 0
        temp_file = ""

        result = plugin._read_incl_sub(
            diagram, temp_file, False, str(include_file), "SECOND"
        )

        assert "second content" in result
        assert "first content" not in result
        assert "third content" not in result

    def test_nested_includes_in_sub(self, plugin, tmp_path):
        """Sub content with !include should be resolved."""
        # Create nested include file
        nested_file = tmp_path / "nested.puml"
        nested_file.write_text("' Nested content\n")

        include_file = tmp_path / "subs.puml"
        include_file.write_text(f"""
!startsub MYSUB
!include {nested_file.name}
!endsub
""")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.root_dir = str(tmp_path)
        diagram.inc_time = 0
        temp_file = ""

        result = plugin._read_incl_sub(
            diagram, temp_file, False, str(include_file), "MYSUB"
        )

        assert "Nested content" in result

    def test_inc_time_not_decreased(self, plugin, tmp_path):
        """inc_time should only increase, never decrease."""
        include_file = tmp_path / "subs.puml"
        include_file.write_text("!startsub MYSUB\ncontent\n!endsub\n")

        diagram = PuElement("test.puml", str(tmp_path))
        # Set a high initial inc_time
        diagram.inc_time = 9999999999.0
        temp_file = ""

        plugin._read_incl_sub(
            diagram, temp_file, False, str(include_file), "MYSUB"
        )

        # inc_time should not be decreased
        assert diagram.inc_time == 9999999999.0
