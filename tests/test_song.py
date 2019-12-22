import pytest
import tablib

from impresario.song import Song, Songbook


@pytest.fixture(scope="function")
def songbook():
    data = tablib.Dataset(headers=["name", "key", "hymn_ref", "sheet_type"])
    songs = [("歌曲 A", "Bb", 3, "PDF"), ("歌曲 B", "C", 10, "PNG")]
    for song in songs:
        data.append(song)

    yield Songbook(data, sort_by="name")


@pytest.fixture(scope="function")
def another_songbook():
    data = tablib.Dataset(headers=["name", "key", "hymn_ref", "sheet_type"])
    songs = [("歌曲 C", "A", "--", "GIF"), ("歌曲 D", "G", 400, "JPG")]
    for song in songs:
        data.append(song)

    yield Songbook(data, sort_by="key")


def test_song_pinyin():
    song = Song(name="歌曲")
    assert song.pinyin == ["Ge", "Qu"]


def test_song_mixed_title():
    song = Song(name="歌曲 some songs")
    assert song.pinyin == ["Ge", "Qu", "Some", "Songs"]


def test_song_normalized_key():
    song = Song(name="歌曲", key="A#")
    assert song.key == "Bb"


def test_songbook_sanity():
    data = tablib.Dataset(headers=["name", "key", "sheet_type"])
    data.append(("歌曲", "C", "PDF"))
    Songbook(data)


def test_songbook_get_songs(songbook):
    assert songbook.songs == [
        Song("歌曲 A", "Bb", 3, "PDF"),
        Song("歌曲 B", "C", 10, "PNG"),
    ]


def test_songbook_sort_by_name(songbook):
    songbook.sort(by="name")
    assert songbook.songs == [
        Song("歌曲 A", "Bb", 3, "PDF"),
        Song("歌曲 B", "C", 10, "PNG"),
    ]


def test_songbook_sort_by_key(songbook):
    songbook.sort(by="key")
    assert songbook.songs == [
        Song("歌曲 B", "C", 10, "PNG"),
        Song("歌曲 A", "Bb", 3, "PDF"),
    ]


@pytest.mark.xfail
def test_songbook_merge(songbook, another_songbook):
    songbook.merge(another_songbook)
    assert songbook.songs == [
        Song("歌曲 A", "Bb", 3, "PDF"),
        Song("歌曲 B", "C", 10, "PNG"),
        Song("歌曲 C", "A", "--", "GIF"),
        Song("歌曲 D", "G", 400, "JPG"),
    ]
