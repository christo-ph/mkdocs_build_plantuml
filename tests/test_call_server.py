"""Tests for _call_server function."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from mkdocs_build_plantuml_plugin.plantuml import PuElement


class TestCallServer:
    """Tests for BuildPlantumlPlugin._call_server method."""

    def test_url_construction(self, plugin, tmp_path):
        """URL should be constructed as server/format/b64encoded."""
        plugin.config["server"] = "https://www.plantuml.com/plantuml"
        plugin.config["output_format"] = "png"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.b64encoded = "SomeEncodedContent"

        with patch('httplib2.Http') as mock_http_class:
            mock_http = MagicMock()
            mock_http_class.return_value = mock_http
            mock_http.request.return_value = (
                MagicMock(status=200),
                b"PNG content"
            )

            plugin._call_server(diagram, str(tmp_path / "out" / "test.png"))

            # Check the URL that was called
            call_args = mock_http.request.call_args[0][0]
            assert "https://www.plantuml.com/plantuml" in call_args
            assert "/png/" in call_args
            assert "SomeEncodedContent" in call_args

    def test_success_writes_file(self, plugin, tmp_path):
        """Successful response should write content to file."""
        plugin.config["server"] = "https://www.plantuml.com/plantuml"
        plugin.config["output_format"] = "png"

        out_dir = tmp_path / "out"
        out_file = out_dir / "test.png"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(out_dir)
        diagram.b64encoded = "SomeEncodedContent"

        with patch('httplib2.Http') as mock_http_class:
            mock_http = MagicMock()
            mock_http_class.return_value = mock_http
            mock_http.request.return_value = (
                MagicMock(status=200),
                b"PNG file content here"
            )

            plugin._call_server(diagram, str(out_file))

            # Verify file was written
            assert out_file.exists()
            assert out_file.read_bytes() == b"PNG file content here"

    def test_error_status_logged(self, plugin, tmp_path, caplog):
        """Non-200 response should log error."""
        plugin.config["server"] = "https://www.plantuml.com/plantuml"
        plugin.config["output_format"] = "png"

        out_dir = tmp_path / "out"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(out_dir)
        diagram.b64encoded = "SomeEncodedContent"

        with patch('httplib2.Http') as mock_http_class:
            mock_http = MagicMock()
            mock_http_class.return_value = mock_http
            mock_http.request.return_value = (
                MagicMock(status=500),
                b"Server error"
            )

            import logging
            with caplog.at_level(logging.ERROR):
                plugin._call_server(diagram, str(out_dir / "test.png"))

            # Should log the error status
            assert "500" in caplog.text or "Wrong response status" in caplog.text

    def test_ssl_validation_disabled(self, plugin, tmp_path):
        """disable_ssl_certificate_validation should be passed to http."""
        plugin.config["server"] = "https://www.plantuml.com/plantuml"
        plugin.config["output_format"] = "png"
        plugin.config["disable_ssl_certificate_validation"] = True

        out_dir = tmp_path / "out"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(out_dir)
        diagram.b64encoded = "SomeEncodedContent"

        with patch('httplib2.Http') as mock_http_class:
            mock_http = MagicMock()
            mock_http_class.return_value = mock_http
            mock_http.request.return_value = (
                MagicMock(status=200),
                b"content"
            )

            plugin._call_server(diagram, str(out_dir / "test.png"))

            # Verify SSL validation was disabled
            assert mock_http.disable_ssl_certificate_validation is True

    def test_creates_output_directory(self, plugin, tmp_path):
        """Should create output directory with parents if needed."""
        plugin.config["server"] = "https://www.plantuml.com/plantuml"
        plugin.config["output_format"] = "png"

        # Deeply nested output directory that doesn't exist
        out_dir = tmp_path / "deep" / "nested" / "out"
        out_file = out_dir / "test.png"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(out_dir)
        diagram.b64encoded = "SomeEncodedContent"

        with patch('httplib2.Http') as mock_http_class:
            mock_http = MagicMock()
            mock_http_class.return_value = mock_http
            mock_http.request.return_value = (
                MagicMock(status=200),
                b"PNG content"
            )

            plugin._call_server(diagram, str(out_file))

            # Directory should be created
            assert out_dir.exists()
            assert out_file.exists()

    def test_svg_format_in_url(self, plugin, tmp_path):
        """SVG format should be in URL."""
        plugin.config["server"] = "https://www.plantuml.com/plantuml"
        plugin.config["output_format"] = "svg"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.b64encoded = "SomeEncodedContent"

        with patch('httplib2.Http') as mock_http_class:
            mock_http = MagicMock()
            mock_http_class.return_value = mock_http
            mock_http.request.return_value = (
                MagicMock(status=200),
                b"SVG content"
            )

            plugin._call_server(diagram, str(tmp_path / "out" / "test.svg"))

            call_args = mock_http.request.call_args[0][0]
            assert "/svg/" in call_args

    def test_network_error_raises(self, plugin, tmp_path):
        """Network error should raise exception."""
        plugin.config["server"] = "https://www.plantuml.com/plantuml"
        plugin.config["output_format"] = "png"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.b64encoded = "SomeEncodedContent"

        with patch('httplib2.Http') as mock_http_class:
            mock_http = MagicMock()
            mock_http_class.return_value = mock_http
            mock_http.request.side_effect = Exception("Network error")

            with pytest.raises(Exception) as exc_info:
                plugin._call_server(diagram, str(tmp_path / "out" / "test.png"))

            assert "Network error" in str(exc_info.value)

    def test_custom_server_url(self, plugin, tmp_path):
        """Custom server URL should be used."""
        plugin.config["server"] = "https://custom.plantuml.server/api"
        plugin.config["output_format"] = "png"

        diagram = PuElement("test.puml", str(tmp_path))
        diagram.out_dir = str(tmp_path / "out")
        diagram.b64encoded = "EncodedContent"

        with patch('httplib2.Http') as mock_http_class:
            mock_http = MagicMock()
            mock_http_class.return_value = mock_http
            mock_http.request.return_value = (
                MagicMock(status=200),
                b"content"
            )

            plugin._call_server(diagram, str(tmp_path / "out" / "test.png"))

            call_args = mock_http.request.call_args[0][0]
            assert "https://custom.plantuml.server/api" in call_args
