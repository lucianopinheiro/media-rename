"""Tests for the Media base class and the Image/Video chain assembly."""

import datetime

from media_rename.domain.image import Image
from media_rename.domain.media_interface import Media
from media_rename.domain.strategies.date_strategy import DateResult
from media_rename.domain.video import Video


class _ResolvedMedia(Media):
    """Media whose ``find_datetime`` returns a preset result."""

    def __init__(self, filename, result):
        super().__init__(filename)
        self._result = result

    def find_datetime(self):
        return self._result


def test_new_name_formats_standard_pattern():
    result = DateResult(datetime.datetime(2022, 10, 10, 10, 37, 18), "jpg")
    media = _ResolvedMedia("/some/dir/whatever.jpg", result)
    assert media.new_name() == "2022-10-10 10.37.18.jpg"


def test_new_name_returns_none_when_no_date_found():
    # The base Media has no chain, so it resolves nothing.
    media = Media("/some/dir/whatever.jpg")
    assert media.find_datetime() is None
    assert media.new_name() is None


def test_source_path_joins_dir_and_name():
    media = Media("/some/dir/whatever.jpg")
    assert media.source_path() == "/some/dir/whatever.jpg"


def test_media_splits_path_and_name():
    media = Media("/some/dir/whatever.jpg")
    assert media.path == "/some/dir"
    assert media.original_name == "whatever.jpg"


def test_image_resolves_filename_timestamp():
    img = Image("/x/20221010_103718.jpg")
    assert img.new_name() == "2022-10-10 10.37.18.jpg"


def test_image_resolves_prefixed_name():
    img = Image("/x/IMG_20201210_182442.png")
    assert img.new_name() == "2020-12-10 18.24.42.png"


def test_image_unmatched_name_returns_none():
    img = Image("/x/vacation.jpg")
    assert img.new_name() is None


def test_video_resolves_filename_timestamp():
    vid = Video("/x/20221010_103718.mp4")
    assert vid.new_name() == "2022-10-10 10.37.18.mp4"


def test_video_resolves_prefixed_name():
    vid = Video("/x/VID_20201219_092426.3gp")
    assert vid.new_name() == "2020-12-19 09.24.26.3gp"


def test_video_already_standard_name_is_recognized():
    vid = Video("/x/2022-08-11 23.12.02.mp4")
    assert vid.new_name() == "2022-08-11 23.12.02.mp4"
