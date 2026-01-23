"""Tests for _build_mtimes function."""
import pytest
from pathlib import Path
import time

from mkdocs_build_plantuml_plugin.plantuml import PuElement


class TestBuildMtimes:
    """Tests for BuildPlantumlPlugin._build_mtimes method."""

    def test_output_exists_gets_mtime(self, plugin, tmp_path):
        """When output file exists, img_time should be set from file mtime."""
        # Create source file
        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        # Create output file
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        out_file = out_dir / "test.png"
        out_file.write_bytes(b"fake png content")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_file = str(out_file)
        diagram.out_dir = str(out_dir)

        plugin._build_mtimes(diagram)

        assert diagram.img_time > 0
        assert diagram.img_time == out_file.stat().st_mtime

    def test_output_missing_zero_mtime(self, plugin, tmp_path):
        """When output file is missing, img_time should be 0."""
        # Create source file
        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_file = str(tmp_path / "out" / "nonexistent.png")

        plugin._build_mtimes(diagram)

        assert diagram.img_time == 0

    def test_dark_output_mtime(self, plugin_with_theme, tmp_path):
        """With theme_enabled, img_time_dark should be set."""
        # Create source file
        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        # Create output files
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        out_file = out_dir / "test.png"
        out_file.write_bytes(b"fake png content")
        out_file_dark = out_dir / "test_dark.png"
        out_file_dark.write_bytes(b"fake dark png content")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_file = str(out_file)
        diagram.out_file_dark = str(out_file_dark)

        plugin_with_theme._build_mtimes(diagram)

        assert diagram.img_time > 0
        assert diagram.img_time_dark > 0
        assert diagram.img_time_dark == out_file_dark.stat().st_mtime

    def test_dark_output_missing(self, plugin_with_theme, tmp_path):
        """When dark output is missing, img_time_dark should be 0."""
        # Create source file
        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        # Create only light output
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        out_file = out_dir / "test.png"
        out_file.write_bytes(b"fake png content")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_file = str(out_file)
        diagram.out_file_dark = str(out_dir / "nonexistent_dark.png")

        plugin_with_theme._build_mtimes(diagram)

        assert diagram.img_time > 0
        assert diagram.img_time_dark == 0

    def test_source_mtime_always_set(self, plugin, tmp_path):
        """Source file mtime should always be set."""
        # Create source file
        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_file = str(tmp_path / "out" / "test.png")

        plugin._build_mtimes(diagram)

        assert diagram.src_time > 0
        assert diagram.src_time == src_file.stat().st_mtime

    def test_inc_time_initialized_to_zero(self, plugin, tmp_path):
        """Include time should be initialized to 0."""
        # Create source file
        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_file = str(tmp_path / "out" / "test.png")

        plugin._build_mtimes(diagram)

        assert diagram.inc_time == 0

    def test_newer_source_than_output(self, plugin, tmp_path):
        """Source newer than output should be detectable."""
        # Create output first
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        out_file = out_dir / "test.png"
        out_file.write_bytes(b"old content")

        # Small delay to ensure different mtime
        time.sleep(0.01)

        # Create source after
        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_file = str(out_file)

        plugin._build_mtimes(diagram)

        # Source should be newer
        assert diagram.src_time > diagram.img_time
