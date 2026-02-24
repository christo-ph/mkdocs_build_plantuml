"""Tests for exclude_dirs functionality."""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def _collect_walked_dirs(plugin, src_dir):
    """Run on_pre_build and return all (subdir, dirs) pairs seen by os.walk."""
    plugin.config["diagram_root"] = str(src_dir)
    plugin.config["allow_multiple_roots"] = False

    walked = []
    original_walk = os.walk

    def recording_walk(path, *args, **kwargs):
        for subdir, dirs, files in original_walk(path, *args, **kwargs):
            walked.append((subdir, list(dirs)))
            yield subdir, dirs, files

    with patch("mkdocs_build_plantuml_plugin.plantuml.os.walk", side_effect=recording_walk):
        with patch.object(plugin, "_convert"):
            with patch.object(plugin, "_readFile"):
                with patch.object(plugin, "_build_mtimes"):
                    with patch.object(plugin, "_search_start_tag", return_value=False):
                        with patch.object(plugin, "_build_out_filename"):
                            plugin.on_pre_build(MagicMock())

    return walked


def test_git_dir_excluded_by_default(plugin, tmp_path):
    """Directories named .git should not be descended into during walk."""
    # _make_diagram_root appends input_folder ("src") to diagram_root,
    # so actual walk happens on diagram_root/src/
    diagram_root = tmp_path / "diagrams"
    walk_root = diagram_root / "src"
    (walk_root / ".git" / "refs").mkdir(parents=True)
    (walk_root / ".git" / "refs" / "fake.puml").write_text("@startuml\nactor A\n@enduml\n")

    walked = _collect_walked_dirs(plugin, diagram_root)

    descended = [subdir for subdir, _ in walked]
    assert not any(".git" in Path(d).parts for d in descended), \
        ".git directory should never be descended into"


def test_custom_exclude_dir(plugin, tmp_path):
    """A custom excluded directory should not be descended into."""
    diagram_root = tmp_path / "diagrams"
    walk_root = diagram_root / "src"
    (walk_root / "node_modules").mkdir(parents=True)
    (walk_root / "node_modules" / "fake.puml").write_text("@startuml\nactor A\n@enduml\n")

    plugin.config["exclude_dirs"] = ["node_modules"]

    walked = _collect_walked_dirs(plugin, diagram_root)

    descended = [subdir for subdir, _ in walked]
    assert not any("node_modules" in Path(d).parts for d in descended), \
        "node_modules should never be descended into"


def test_non_excluded_dir_is_walked(plugin, tmp_path):
    """Directories not in exclude_dirs should still be descended into."""
    diagram_root = tmp_path / "diagrams"
    walk_root = diagram_root / "src"
    (walk_root / "mydiagrams").mkdir(parents=True)
    (walk_root / "mydiagrams" / "test.puml").write_text("@startuml\nactor A\n@enduml\n")

    walked = _collect_walked_dirs(plugin, diagram_root)

    descended = [subdir for subdir, _ in walked]
    assert any("mydiagrams" in Path(d).parts for d in descended), \
        "Non-excluded dirs should be walked"
