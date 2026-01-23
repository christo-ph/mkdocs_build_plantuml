"""Tests for _convert function."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import time

from mkdocs_build_plantuml_plugin.plantuml import PuElement


class TestConvert:
    """Tests for BuildPlantumlPlugin._convert method."""

    def test_skip_when_up_to_date(self, plugin, tmp_path):
        """Should skip conversion when output is newer than source."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file = str(tmp_path / "out" / "test.png")
        # Output is newer than source
        diagram.img_time = 1000.0
        diagram.src_time = 500.0
        diagram.inc_time = 0

        with patch.object(plugin, '_call_server') as mock_server:
            plugin._convert(diagram, False)
            mock_server.assert_not_called()

    def test_convert_when_source_newer(self, plugin, tmp_path):
        """Should convert when source is newer than output."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.directory = str(tmp_path)
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file = str(tmp_path / "out" / "test.png")
        diagram.b64encoded = "SomeEncodedContent"
        # Source is newer than output
        diagram.img_time = 500.0
        diagram.src_time = 1000.0
        diagram.inc_time = 0

        with patch.object(plugin, '_call_server') as mock_server:
            plugin._convert(diagram, False)
            mock_server.assert_called_once_with(diagram, diagram.out_file)

    def test_convert_when_include_newer(self, plugin, tmp_path):
        """Should convert when include file is newer than output."""
        diagram = PuElement("test.puml", str(tmp_path))
        diagram.directory = str(tmp_path)
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file = str(tmp_path / "out" / "test.png")
        diagram.b64encoded = "SomeEncodedContent"
        # Output is newer than source, but include is newest
        diagram.img_time = 500.0
        diagram.src_time = 400.0
        diagram.inc_time = 1000.0

        with patch.object(plugin, '_call_server') as mock_server:
            plugin._convert(diagram, False)
            mock_server.assert_called_once()

    def test_dark_mode_only_server(self, plugin, tmp_path):
        """Dark mode with local render should skip."""
        plugin.config["render"] = "local"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.directory = str(tmp_path)
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file_dark = str(tmp_path / "out" / "test_dark.png")
        # Source is newer
        diagram.img_time_dark = 500.0
        diagram.src_time = 1000.0
        diagram.inc_time = 0

        with patch.object(plugin, '_call_server') as mock_server:
            plugin._convert(diagram, True)  # dark_mode=True
            # Should not call server because render=local and dark_mode
            mock_server.assert_not_called()

    def test_local_calls_subprocess(self, plugin, tmp_path):
        """Local render should call subprocess with bin_path."""
        plugin.config["render"] = "local"
        plugin.config["bin_path"] = "/usr/local/bin/plantuml"

        # Create source file
        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.directory = str(tmp_path)
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file = str(tmp_path / "out" / "test.png")
        # Source is newer
        diagram.img_time = 500.0
        diagram.src_time = 1000.0
        diagram.inc_time = 0

        with patch('mkdocs_build_plantuml_plugin.plantuml.call') as mock_call:
            plugin._convert(diagram, False)
            mock_call.assert_called_once()
            # Check it was called with the bin_path
            call_args = mock_call.call_args[0][0]
            assert "/usr/local/bin/plantuml" in call_args

    def test_server_calls_http(self, plugin, tmp_path):
        """Server render should call _call_server."""
        plugin.config["render"] = "server"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.directory = str(tmp_path)
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file = str(tmp_path / "out" / "test.png")
        diagram.b64encoded = "EncodedContent"
        # Source is newer
        diagram.img_time = 500.0
        diagram.src_time = 1000.0
        diagram.inc_time = 0

        with patch.object(plugin, '_call_server') as mock_server:
            plugin._convert(diagram, False)
            mock_server.assert_called_once_with(diagram, diagram.out_file)

    def test_dark_mode_server_render(self, plugin, tmp_path):
        """Dark mode with server render should call _call_server."""
        plugin.config["render"] = "server"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.directory = str(tmp_path)
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file_dark = str(tmp_path / "out" / "test_dark.png")
        diagram.b64encoded = "EncodedContent"
        # Source is newer
        diagram.img_time_dark = 500.0
        diagram.src_time = 1000.0
        diagram.inc_time = 0

        with patch.object(plugin, '_call_server') as mock_server:
            plugin._convert(diagram, True)  # dark_mode=True
            mock_server.assert_called_once_with(diagram, diagram.out_file_dark)

    def test_dark_mode_skip_when_up_to_date(self, plugin, tmp_path):
        """Dark mode should skip when dark output is newer."""
        plugin.config["render"] = "server"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.directory = str(tmp_path)
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file_dark = str(tmp_path / "out" / "test_dark.png")
        # Dark output is newer
        diagram.img_time_dark = 1000.0
        diagram.src_time = 500.0
        diagram.inc_time = 0

        with patch.object(plugin, '_call_server') as mock_server:
            plugin._convert(diagram, True)
            mock_server.assert_not_called()

    def test_local_output_format_passed(self, plugin, tmp_path):
        """Local render should pass output_format to plantuml."""
        plugin.config["render"] = "local"
        plugin.config["output_format"] = "svg"
        plugin.config["bin_path"] = "/usr/local/bin/plantuml"

        src_file = tmp_path / "test.puml"
        src_file.write_text("@startuml\n@enduml\n")

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.directory = str(tmp_path)
        diagram.out_dir = str(tmp_path / "out")
        diagram.out_file = str(tmp_path / "out" / "test.svg")
        diagram.img_time = 0
        diagram.src_time = 1000.0
        diagram.inc_time = 0

        with patch('mkdocs_build_plantuml_plugin.plantuml.call') as mock_call:
            plugin._convert(diagram, False)
            call_args = mock_call.call_args[0][0]
            assert "-tsvg" in call_args
