"""Tests for the date-resolution strategies (Chain of Responsibility handlers)."""

import datetime

import pytest

from media_rename.domain.strategies.date_strategy import DateResult, DateStrategy
from media_rename.domain.strategies.file_mtime_strategy import FileMtimeStrategy
from media_rename.domain.strategies.filename_timestamp_strategy import (
    FilenameTimestampStrategy,
)
from media_rename.domain.strategies.prefixed_filename_strategy import (
    PrefixedFilenameStrategy,
)
from media_rename.domain.strategies.standard_name_strategy import StandardNameStrategy
from media_rename.domain.strategies.unix_timestamp_strategy import UnixTimestampStrategy

from .conftest import FakeMedia

IMAGE_EXT = r"jp[e]?g|png|gif"
VIDEO_EXT = r"mp[e]?g|mp4|3gp"


# --------------------------------------------------------------------------- #
# DateStrategy — chain mechanics
# --------------------------------------------------------------------------- #


class _ConstStrategy(DateStrategy):
    """Handler that always resolves to a fixed result (for chain tests)."""

    def __init__(self, result, enabled=True):
        super().__init__(enabled=enabled)
        self._result = result

    def resolve(self, media):
        return self._result


class _NullStrategy(DateStrategy):
    """Handler that never resolves, always forwarding to the next link."""

    def resolve(self, media):
        return None


def test_set_next_returns_the_linked_handler():
    a = _NullStrategy()
    b = _NullStrategy()
    assert a.set_next(b) is b


def test_handle_forwards_until_a_handler_resolves():
    expected = DateResult(datetime.datetime(2020, 1, 1), "jpg")
    first = _NullStrategy()
    first.set_next(_ConstStrategy(expected))

    assert first.handle(FakeMedia("whatever.jpg")) is expected


def test_disabled_handler_is_skipped():
    should_not_win = DateResult(datetime.datetime(1999, 1, 1), "jpg")
    should_win = DateResult(datetime.datetime(2020, 1, 1), "jpg")

    disabled = _ConstStrategy(should_not_win, enabled=False)
    disabled.set_next(_ConstStrategy(should_win))

    assert disabled.handle(FakeMedia("x.jpg")) is should_win


def test_handle_returns_none_when_no_handler_resolves():
    chain = _NullStrategy()
    chain.set_next(_NullStrategy())
    assert chain.handle(FakeMedia("x.jpg")) is None


def test_normalized_extension_lowercases_and_strips_dot():
    assert DateStrategy.normalized_extension("PHOTO.JPG") == "jpg"


# --------------------------------------------------------------------------- #
# FilenameTimestampStrategy — yyyymmdd_hhMMss
# --------------------------------------------------------------------------- #


def test_filename_timestamp_basic():
    result = FilenameTimestampStrategy(IMAGE_EXT).resolve(
        FakeMedia("20221010_103718.jpg")
    )
    assert result.date == datetime.datetime(2022, 10, 10, 10, 37, 18)
    assert result.extension == "jpg"


def test_filename_timestamp_ignores_trailing_milliseconds():
    result = FilenameTimestampStrategy(IMAGE_EXT).resolve(
        FakeMedia("20190120_072900398.png")
    )
    assert result.date == datetime.datetime(2019, 1, 20, 7, 29, 0)


def test_filename_timestamp_lowercases_extension():
    result = FilenameTimestampStrategy(IMAGE_EXT).resolve(
        FakeMedia("20221010_103718.JPG")
    )
    assert result.extension == "jpg"


def test_filename_timestamp_no_match_returns_none():
    assert (
        FilenameTimestampStrategy(IMAGE_EXT).resolve(FakeMedia("holiday.jpg")) is None
    )


def test_filename_timestamp_rejects_unlisted_extension():
    # A video extension should not match the image strategy.
    assert (
        FilenameTimestampStrategy(IMAGE_EXT).resolve(FakeMedia("20221010_103718.mp4"))
        is None
    )


# --------------------------------------------------------------------------- #
# PrefixedFilenameStrategy — PREFIX_yyyymmdd_hhMMss
# --------------------------------------------------------------------------- #


def test_prefixed_image():
    result = PrefixedFilenameStrategy(IMAGE_EXT).resolve(
        FakeMedia("IMG_20201210_182442.jpg")
    )
    assert result.date == datetime.datetime(2020, 12, 10, 18, 24, 42)
    assert result.extension == "jpg"


def test_prefixed_video():
    result = PrefixedFilenameStrategy(VIDEO_EXT).resolve(
        FakeMedia("VID_20201219_092426.3gp")
    )
    assert result.date == datetime.datetime(2020, 12, 19, 9, 24, 26)
    assert result.extension == "3gp"


def test_prefixed_ignores_trailing_counter():
    result = PrefixedFilenameStrategy(IMAGE_EXT).resolve(
        FakeMedia("IMG_20201210_182442_001.jpg")
    )
    assert result.date == datetime.datetime(2020, 12, 10, 18, 24, 42)


def test_prefixed_no_match_returns_none():
    assert (
        PrefixedFilenameStrategy(IMAGE_EXT).resolve(
            FakeMedia("20201210_182442.jpg")  # no PREFIX_
        )
        is None
    )


# --------------------------------------------------------------------------- #
# UnixTimestampStrategy — seconds and milliseconds
# --------------------------------------------------------------------------- #


def test_unix_seconds():
    result = UnixTimestampStrategy(IMAGE_EXT).resolve(FakeMedia("1665394638.jpg"))
    # 1665394638 == 2022-10-10 09:37:18 UTC
    assert result.date == datetime.datetime(2022, 10, 10, 9, 37, 18)
    assert result.extension == "jpg"


def test_unix_milliseconds():
    result = UnixTimestampStrategy(IMAGE_EXT).resolve(FakeMedia("1665394638123.jpg"))
    # The millisecond remainder is dropped: the date is second-resolution.
    assert result.date == datetime.datetime(2022, 10, 10, 9, 37, 18)
    assert result.date.microsecond == 0


def test_unix_result_is_naive_datetime():
    result = UnixTimestampStrategy(IMAGE_EXT).resolve(FakeMedia("1665394638.jpg"))
    assert result.date.tzinfo is None


def test_unix_rejects_out_of_range_year():
    # 12 digits is neither 10 (s) nor 13 (ms), so it never matches the pattern;
    # use a valid-length value that lands outside the sanity window instead.
    # 99999999999 is 11 digits -> no match. A very large 13-digit ms value
    # overflows the plausible year window.
    assert (
        UnixTimestampStrategy(IMAGE_EXT).resolve(
            FakeMedia("9999999999999.jpg")  # year well beyond 2100
        )
        is None
    )


def test_unix_does_not_match_underscore_names():
    # yyyymmdd_hhMMss contains an underscore, so it must not be read as a
    # Unix timestamp.
    assert (
        UnixTimestampStrategy(IMAGE_EXT).resolve(FakeMedia("20221010_103718.jpg"))
        is None
    )


# --------------------------------------------------------------------------- #
# StandardNameStrategy — already-formatted names
# --------------------------------------------------------------------------- #


def test_standard_name_recognized():
    result = StandardNameStrategy(IMAGE_EXT).resolve(
        FakeMedia("2022-08-11 23.12.02.jpg")
    )
    assert result.date == datetime.datetime(2022, 8, 11, 23, 12, 2)
    assert result.extension == "jpg"


def test_standard_name_with_collision_suffix():
    result = StandardNameStrategy(IMAGE_EXT).resolve(
        FakeMedia("2022-08-11 23.12.02_1.jpg")
    )
    assert result.date == datetime.datetime(2022, 8, 11, 23, 12, 2)


def test_standard_name_rejects_impossible_date():
    assert (
        StandardNameStrategy(IMAGE_EXT).resolve(FakeMedia("2022-13-40 25.61.61.jpg"))
        is None
    )


def test_standard_name_no_match():
    assert StandardNameStrategy(IMAGE_EXT).resolve(FakeMedia("random.jpg")) is None


# --------------------------------------------------------------------------- #
# FileMtimeStrategy — filesystem modified time
# --------------------------------------------------------------------------- #


def test_mtime_disabled_by_default():
    strategy = FileMtimeStrategy()
    assert strategy.enabled is False


def test_mtime_resolves_from_file(tmp_path):
    f = tmp_path / "no_date_here.jpg"
    f.write_text("")
    known = datetime.datetime(2021, 6, 15, 12, 0, 0)
    ts = known.timestamp()
    import os

    os.utime(f, (ts, ts))

    strategy = FileMtimeStrategy(enabled=True)
    result = strategy.resolve(FakeMedia("no_date_here.jpg", path=str(tmp_path)))
    assert result.date == known
    assert result.extension == "jpg"


def test_mtime_missing_file_returns_none(tmp_path):
    strategy = FileMtimeStrategy(enabled=True)
    result = strategy.resolve(FakeMedia("ghost.jpg", path=str(tmp_path)))
    assert result is None


# --------------------------------------------------------------------------- #
# ExifDateStrategy — reads EXIF metadata from a real image
# --------------------------------------------------------------------------- #


def test_exif_reads_datetime_original(tmp_path):
    PILImage = pytest.importorskip("PIL.Image")
    from PIL.ExifTags import Base

    from media_rename.domain.strategies.exif_date_strategy import ExifDateStrategy

    img = PILImage.new("RGB", (2, 2), "white")
    exif = img.getexif()
    # 0x9003 == DateTimeOriginal, stored in the Exif sub-IFD.
    exif_ifd = exif.get_ifd(0x8769)
    exif_ifd[Base.DateTimeOriginal.value] = "2020:05:01 08:09:10"

    target = tmp_path / "photo.jpg"
    img.save(target, exif=exif)

    result = ExifDateStrategy().resolve(FakeMedia("photo.jpg", path=str(tmp_path)))
    assert result is not None
    assert result.date == datetime.datetime(2020, 5, 1, 8, 9, 10)
    assert result.extension == "jpg"


def test_exif_no_metadata_returns_none(tmp_path):
    PILImage = pytest.importorskip("PIL.Image")

    from media_rename.domain.strategies.exif_date_strategy import ExifDateStrategy

    img = PILImage.new("RGB", (2, 2), "white")
    target = tmp_path / "plain.jpg"
    img.save(target)

    result = ExifDateStrategy().resolve(FakeMedia("plain.jpg", path=str(tmp_path)))
    assert result is None
