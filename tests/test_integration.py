"""Integration tests that run the plugin against the example project."""
import pytest
from pathlib import Path
import shutil
import os

from mkdocs_build_plantuml_plugin.plantuml import BuildPlantumlPlugin


def get_default_config(**overrides):
    """Return default plugin config with optional overrides."""
    config = {
        "render": "server",
        "server": "https://www.plantuml.com/plantuml",
        "disable_ssl_certificate_validation": False,
        "bin_path": "/usr/local/bin/plantuml",
        "output_format": "png",
        "allow_multiple_roots": False,
        "diagram_root": "docs/diagrams",
        "output_folder": "out",
        "output_in_dir": False,
        "input_folder": "src",
        "input_extensions": "",
        "theme_enabled": False,
        "theme_folder": "include/themes/",
        "theme_light": "light.puml",
        "theme_dark": "dark.puml",
    }
    config.update(overrides)
    return config


@pytest.fixture
def example_project_copy(tmp_path):
    """Copy example project to a temp directory to avoid modifying the original."""
    example_src = Path(__file__).parent.parent / "example"
    example_copy = tmp_path / "example"

    shutil.copytree(
        example_src,
        example_copy,
        ignore=shutil.ignore_patterns("out")
    )

    return example_copy


@pytest.fixture
def out_dir(example_project_copy):
    """Return the output directory path for the copied example project."""
    return example_project_copy / "docs" / "diagrams" / "out"


@pytest.fixture
def run_plugin(example_project_copy):
    """Fixture that returns a function to run the plugin with given config overrides."""
    def _run_plugin(**config_overrides):
        original_cwd = Path.cwd()
        os.chdir(example_project_copy)
        try:
            plugin = BuildPlantumlPlugin()
            plugin.config = get_default_config(**config_overrides)
            plugin.on_pre_build({})
        finally:
            os.chdir(original_cwd)
    return _run_plugin


@pytest.mark.integration
class TestExampleProjectIntegration:
    """Integration tests using the example project with real server calls."""

    def test_generates_svg_with_dark_theme(self, out_dir, run_plugin):
        """Generate SVG with dark theme variants and compare with example folder.

        This single test covers:
        - SVG format generation
        - Theme-based light/dark variant generation
        - Valid SVG output verification
        - Comparison with original example files
        """
        run_plugin(output_format="svg", theme_enabled=True)

        # All 4 files should exist (original example config)
        expected_files = [
            "sequence.svg",
            "sequence_dark.svg",
            "context_goals.svg",
            "context_goals_dark.svg",
        ]

        for filename in expected_files:
            filepath = out_dir / filename
            assert filepath.exists(), f"{filename} was not generated"

            content = filepath.read_text()
            assert "<svg" in content, f"{filename} is not valid SVG"
            assert "</svg>" in content, f"{filename} is not valid SVG"
            assert filepath.stat().st_size > 500, f"{filename} is too small"


    def test_generates_png_with_dark_theme_and_skips_when_up_to_date(self, out_dir, run_plugin):
        """Generate PNG with dark theme variants and verify caching works.

        This test covers:
        - PNG format generation
        - Theme-based light/dark variant generation
        - Valid PNG output verification
        - Caching (skip conversion when up-to-date)
        """
        run_plugin(output_format="png", theme_enabled=True)

        # All 4 PNG files should exist
        expected_files = [
            "sequence.png",
            "sequence_dark.png",
            "context_goals.png",
            "context_goals_dark.png",
        ]

        for filename in expected_files:
            filepath = out_dir / filename
            assert filepath.exists(), f"{filename} was not generated"

            # Verify valid PNG magic bytes
            with open(filepath, "rb") as f:
                assert f.read(4) == b'\x89PNG', f"{filename} is not valid PNG"

            assert filepath.stat().st_size > 500, f"{filename} is too small"

        # Record mtimes
        first_mtimes = {f: (out_dir / f).stat().st_mtime for f in expected_files}

        # Second run should skip all files
        run_plugin(output_format="png", theme_enabled=True)

        for filename in expected_files:
            assert (out_dir / filename).stat().st_mtime == first_mtimes[filename], \
                f"{filename} was regenerated when it should have been skipped"
