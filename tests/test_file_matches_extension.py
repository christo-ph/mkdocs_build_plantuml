"""Tests for _file_matches_extension function."""
import pytest


class TestFileMatchesExtension:
    """Tests for BuildPlantumlPlugin._file_matches_extension method."""

    def test_empty_extensions_matches_all(self, plugin):
        """Empty input_extensions config should match any file."""
        plugin.config["input_extensions"] = ""

        assert plugin._file_matches_extension("test.puml") is True
        assert plugin._file_matches_extension("test.txt") is True
        assert plugin._file_matches_extension("diagram.plantuml") is True
        assert plugin._file_matches_extension("any.file") is True

    def test_single_extension_matches(self, plugin):
        """Single extension should match files with that extension."""
        plugin.config["input_extensions"] = "puml"

        assert plugin._file_matches_extension("test.puml") is True
        assert plugin._file_matches_extension("diagram.puml") is True

    def test_single_extension_no_match(self, plugin):
        """Single extension should not match files with different extensions."""
        plugin.config["input_extensions"] = "puml"

        assert plugin._file_matches_extension("test.txt") is False
        assert plugin._file_matches_extension("diagram.plantuml") is False
        assert plugin._file_matches_extension("file.png") is False

    def test_multiple_extensions_matches(self, plugin):
        """Multiple comma-separated extensions should match any of them."""
        plugin.config["input_extensions"] = "puml,plantuml"

        assert plugin._file_matches_extension("test.puml") is True
        assert plugin._file_matches_extension("diagram.plantuml") is True

    def test_multiple_extensions_no_match(self, plugin):
        """Multiple extensions should not match other extensions."""
        plugin.config["input_extensions"] = "puml,plantuml"

        assert plugin._file_matches_extension("test.txt") is False
        assert plugin._file_matches_extension("diagram.uml") is False
        assert plugin._file_matches_extension("file.png") is False

    def test_extension_is_suffix_match(self, plugin):
        """Extension matching should use endswith (suffix matching)."""
        plugin.config["input_extensions"] = "puml"

        # These should match because they end with 'puml'
        assert plugin._file_matches_extension("test.puml") is True
        # This filename ends with puml (the literal chars)
        assert plugin._file_matches_extension("testpuml") is True

    def test_three_extensions(self, plugin):
        """Three comma-separated extensions should all match."""
        plugin.config["input_extensions"] = "puml,plantuml,iuml"

        assert plugin._file_matches_extension("test.puml") is True
        assert plugin._file_matches_extension("test.plantuml") is True
        assert plugin._file_matches_extension("test.iuml") is True
        assert plugin._file_matches_extension("test.txt") is False
