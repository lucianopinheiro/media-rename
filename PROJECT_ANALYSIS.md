# Project Analysis

## Summary

This repository contains a Python CLI tool named `media-rename`. Its purpose is to rename image and video files into a standardized, date-based filename so files are easier to sort and identify.

The target format is:

```text
YYYY-MM-DD HH.MM.SS.ext
```

Examples:

- `2022-10-10 10.37.18.jpg`
- `2022-10-10 10.37.18.mp4`

## High-level behavior

The app scans a directory, detects which files are media, resolves a capture timestamp, and renames eligible files in place.

It tries several strategies in sequence until one succeeds:

1. Standard-name detection (already renamed files)
2. EXIF metadata for images
3. Timestamp embedded in the filename
4. Prefixed filename (`IMG_...`, `VID_...`)
5. Unix timestamp in the filename
6. Optional file modification time (`--enable-modified`)

If no date can be resolved, the file is left untouched.

## Architecture

### CLI entry point

- [src/media_rename/app.py](src/media_rename/app.py)
  - Parses command-line arguments
  - Creates the app and directory provider
  - Invokes renaming logic

### Directory discovery

- [src/media_rename/domain/directory_handler.py](src/media_rename/domain/directory_handler.py)
  - Lists files in a directory
  - Detects which ones are images or videos
  - Returns media objects for processing

### Media abstractions

- [src/media_rename/domain/media_interface.py](src/media_rename/domain/media_interface.py)
  - Base `Media` class
  - Holds filename/path metadata
  - Builds the final standardized filename from a resolved date

- [src/media_rename/domain/image.py](src/media_rename/domain/image.py)
  - `Image` subclass
  - Configures the image-specific date strategy chain

- [src/media_rename/domain/video.py](src/media_rename/domain/video.py)
  - `Video` subclass
  - Configures the video-specific date strategy chain

### Strategy chain

The date resolution is implemented through a Chain of Responsibility pattern.

- [src/media_rename/domain/strategies/date_strategy.py](src/media_rename/domain/strategies/date_strategy.py)
  - Base strategy class
  - `handle()` passes requests from one strategy to the next until a result is found

Concrete strategies include:

- [src/media_rename/domain/strategies/standard_name_strategy.py](src/media_rename/domain/strategies/standard_name_strategy.py)
- [src/media_rename/domain/strategies/exif_date_strategy.py](src/media_rename/domain/strategies/exif_date_strategy.py)
- [src/media_rename/domain/strategies/filename_timestamp_strategy.py](src/media_rename/domain/strategies/filename_timestamp_strategy.py)
- [src/media_rename/domain/strategies/prefixed_filename_strategy.py](src/media_rename/domain/strategies/prefixed_filename_strategy.py)
- [src/media_rename/domain/strategies/unix_timestamp_strategy.py](src/media_rename/domain/strategies/unix_timestamp_strategy.py)
- [src/media_rename/domain/strategies/file_mtime_strategy.py](src/media_rename/domain/strategies/file_mtime_strategy.py)

## Media detection

- [src/media_rename/domain/media_handler.py](src/media_rename/domain/media_handler.py)
  - Uses Pillow to detect images
  - Uses `pymediainfo` when available for richer video detection
  - Falls back to extensions if the native library is unavailable

## Conflict handling

The app avoids overwriting files by resolving collisions before renaming:

- if the destination name is already occupied, it tries a suffixed name
- examples: `name_1.ext`, `name_2.ext`, etc.

This is implemented in `App._resolve_collision()` inside [src/media_rename/app.py](src/media_rename/app.py).

## Idempotency

The app avoids repeatedly renaming already-standardized files. A file is considered unchanged when:

- it already matches the target format, or
- it has a valid collision suffix like `_1`, `_2`, etc.

This is implemented in `App._is_already_named()`.

## Validation

The project includes automated tests in [tests/](tests):

- app orchestration
- collision handling
- idempotency checks
- renaming logic
- strategy behavior

As of the latest execution, the suite passes successfully.

## Usage

```bash
python -m media_rename
python -m media_rename --dry-run
python -m media_rename --enable-modified
python -m media_rename ~/Pictures/camera-roll
```

The package also exposes a console script after installation:

```bash
media-rename [src] [options]
```

## Key project files

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [src/media_rename/app.py](src/media_rename/app.py)
- [src/media_rename/domain](src/media_rename/domain)
- [tests](tests)

## Notes

This is a compact, domain-driven CLI project. The design is intentionally simple and readable: the application layer orchestrates the operation, the media classes define how to resolve dates, and the strategy chain isolates the different ways dates may be extracted from files.
