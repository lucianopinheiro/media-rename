"""Tests for the Media base class and the Image/Video chain assembly."""

import datetime

from media_rename.domain.image import Image
from media_rename.domain.media_interface import Media
from media_rename.domain.video import Video


def test_new_name_formats_standard_pattern():
    media = Media("/some/dir/whatever.jpg")
    media.found = True
    media.date = datetime.datetime(2022, 10, 10, 10, 37, 18)
    media.extension = "jpg"

    assert media.new_name() == "2022-10-10 10.37.18.jpg"


def test_new_name_returns_none_when_no_date_found():
    media = Media("/some/dir/whatever.jpg")
    # find_datetime on the base class resolves nothing.
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
