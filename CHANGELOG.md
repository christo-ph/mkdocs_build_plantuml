# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-02-24

### Fixed

- Replace `Path.walk()` with `os.walk()` to restore Python < 3.12 compatibility (#45)
- Strip quotes from diagram names (e.g. `@startuml "mydiagram"`) to prevent infinite regeneration during `mkdocs serve` (#41)
- Exclude `.git` and other configurable directories when walking diagram roots to prevent errors when `diagram_root` is set to `.` (#42)

### Added

- New `exclude_dirs` config option (default: `[".git"]`) to skip directories during diagram discovery (#42)

### Changed

- Bump `python_requires` from `>=3.12` to `>=3.10` (Python 3.8/3.9 are EOL; ecosystem deps require 3.10+)
- Move "Processing diagram" and "root dir / src dir" log messages from `INFO` to `DEBUG` level to reduce log noise in large projects (#38). Use `mkdocs serve --verbose` to see them.
- Extend CI matrix to cover Python 3.10–3.13

## [2.0.0] - 2025-01-23

### Breaking Changes

This release updates the example project to MkDocs Material 9.x, which requires changes to dark mode configuration.

**If you copied the example setup, you need to update:**

1. **mkdocs.yml theme configuration** - Material 9.x uses a different palette syntax:
   ```yaml
   theme:
     name: material
     palette:
       - scheme: default
         toggle:
           icon: material/brightness-7
           name: Switch to dark mode
       - scheme: slate
         toggle:
           icon: material/brightness-4
           name: Switch to light mode
   ```

2. **CSS dark mode selector** - Change from `@media(prefers-color-scheme: dark)` to `[data-md-color-scheme="slate"]`

3. **JavaScript theme detection** - Update from `matchMedia('prefers-color-scheme')` to MutationObserver watching `data-md-color-scheme` attribute

4. **PlantUML theme files** - Add `skinparam backgroundColor transparent` for proper dark mode display

### Added

- Test suite with pytest (unit and integration tests)
- GitHub Actions workflow for automated testing
- Transparent background support in PlantUML themes

### Changed

- Updated example dependencies to current versions (Material 9.x, pymdown-extensions 10.12, etc.)
- Updated documentation for Material 9.x dark mode setup

## [1.11.0] - 2024-xx-xx

### Fixed

- Replace `print` with mkdocs logger for proper logging

## [1.10.0] - 2024-xx-xx

### Fixed

- `Path.walk` not supported in Python < 3.12 (#37)
- Print diagram file names as they are processed (#35)

## [1.9.0] - 2024-xx-xx

### Changed

- Switched from `os.path` to `pathlib`
- Migrated GitHub Actions from Node 16 to 20

## [1.8.0] - 2023-xx-xx

### Fixed

- All subs that started with the same characters were included

### Added

- Support for recursive `!includesub` statements
- Read diagrams explicitly with UTF-8 encoding (#10, #28)
- Support for multiple diagram roots (for large code repos)

## [1.7.4] - 2023-xx-xx

### Fixed

- Fixed #23
- Add newline in `_readFileRec` if not present

## [1.7.0] - 2022-xx-xx

### Added

- Parameter `disable_ssl_certificate_validation` for self-signed certs (#20)

## [1.6.0] - 2022-xx-xx

### Added

- Support for stdlib extensions (`!include <C4/C4_Container>`)

### Fixed

- Do not repeat input directory in output directory
- Convert response status code to string
- Search in diagram root

## [1.4.0] - 2021-xx-xx

### Added

- Dark mode / theme support for server rendering

[2.1.0]: https://github.com/christo-ph/mkdocs_build_plantuml/releases/tag/2.1.0
[2.0.0]: https://github.com/christo-ph/mkdocs_build_plantuml/releases/tag/2.0.0
[1.11.0]: https://github.com/christo-ph/mkdocs_build_plantuml/releases/tag/1.11.0
[1.10.0]: https://github.com/christo-ph/mkdocs_build_plantuml/releases/tag/1.10.0
