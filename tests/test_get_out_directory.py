"""Tests for _get_out_directory function."""
import pytest
from pathlib import Path

from mkdocs_build_plantuml_plugin.plantuml import DiagramRoot


class TestGetOutDirectory:
    """Tests for BuildPlantumlPlugin._get_out_directory method."""

    def test_output_in_dir_false(self, plugin, tmp_path):
        """With output_in_dir=False, output goes to root/out/subdir."""
        plugin.config["output_in_dir"] = False
        plugin.config["output_folder"] = "out"

        root = DiagramRoot()
        root.root_dir = str(tmp_path / "diagrams")
        root.src_dir = str(tmp_path / "diagrams" / "src")

        subdir = tmp_path / "diagrams" / "src" / "subdir"

        result = plugin._get_out_directory(root, subdir)

        # Should be: root_dir / output_folder / relative_path
        expected = str(Path.cwd() / tmp_path / "diagrams" / "out" / "subdir")
        assert result == expected

    def test_output_in_dir_true(self, plugin, tmp_path):
        """With output_in_dir=True, output goes to root/subdir/out."""
        plugin.config["output_in_dir"] = True
        plugin.config["output_folder"] = "out"

        root = DiagramRoot()
        root.root_dir = str(tmp_path / "diagrams")
        root.src_dir = str(tmp_path / "diagrams" / "src")

        subdir = tmp_path / "diagrams" / "src" / "subdir"

        result = plugin._get_out_directory(root, subdir)

        # Should be: root_dir / relative_path / output_folder
        expected = str(Path.cwd() / tmp_path / "diagrams" / "subdir" / "out")
        assert result == expected

    def test_nested_subdirectory(self, plugin, tmp_path):
        """Deeply nested subdirectories should work correctly."""
        plugin.config["output_in_dir"] = False
        plugin.config["output_folder"] = "out"

        root = DiagramRoot()
        root.root_dir = str(tmp_path / "diagrams")
        root.src_dir = str(tmp_path / "diagrams" / "src")

        subdir = tmp_path / "diagrams" / "src" / "a" / "b" / "c"

        result = plugin._get_out_directory(root, subdir)

        # Should be: root_dir / output_folder / a/b/c
        expected = str(Path.cwd() / tmp_path / "diagrams" / "out" / "a" / "b" / "c")
        assert result == expected

    def test_nested_subdirectory_output_in_dir(self, plugin, tmp_path):
        """Nested subdirectories with output_in_dir=True."""
        plugin.config["output_in_dir"] = True
        plugin.config["output_folder"] = "out"

        root = DiagramRoot()
        root.root_dir = str(tmp_path / "diagrams")
        root.src_dir = str(tmp_path / "diagrams" / "src")

        subdir = tmp_path / "diagrams" / "src" / "a" / "b" / "c"

        result = plugin._get_out_directory(root, subdir)

        # Should be: root_dir / a/b/c / output_folder
        expected = str(Path.cwd() / tmp_path / "diagrams" / "a" / "b" / "c" / "out")
        assert result == expected

    def test_src_dir_itself(self, plugin, tmp_path):
        """When subdir is exactly src_dir, should get clean output path."""
        plugin.config["output_in_dir"] = False
        plugin.config["output_folder"] = "out"

        root = DiagramRoot()
        root.root_dir = str(tmp_path / "diagrams")
        root.src_dir = str(tmp_path / "diagrams" / "src")

        # Subdir is exactly the src_dir
        subdir = tmp_path / "diagrams" / "src"

        result = plugin._get_out_directory(root, subdir)

        # Relative path should be empty, so result is just root/out
        expected = str(Path.cwd() / tmp_path / "diagrams" / "out")
        assert result == expected

    def test_custom_output_folder_name(self, plugin, tmp_path):
        """Custom output folder name should be used."""
        plugin.config["output_in_dir"] = False
        plugin.config["output_folder"] = "generated"

        root = DiagramRoot()
        root.root_dir = str(tmp_path / "diagrams")
        root.src_dir = str(tmp_path / "diagrams" / "src")

        subdir = tmp_path / "diagrams" / "src"

        result = plugin._get_out_directory(root, subdir)

        assert "generated" in result
