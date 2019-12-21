import tablib
from impresario.song import Song, Songbook


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
