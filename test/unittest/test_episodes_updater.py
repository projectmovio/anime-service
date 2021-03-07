from datetime import datetime, timedelta

from crons.episodes_updater import _anime_airing


def test_airing_anime_without_end_date():
    anime = {}
    assert _anime_airing(anime)


def test_airing_anime_with_empty_end_date():
    anime = {"end_date": ""}
    assert _anime_airing(anime)


def test_airing_anime_with_none_end_date():
    anime = {"end_date": None}
    assert _anime_airing(anime)


def test_airing_anime_with_null_string_end_date():
    anime = {"end_date": "Null"}
    assert _anime_airing(anime)


def test_airing_anime_with_end_date_after_today():
    date_today = datetime.today() + timedelta(days=1)
    date_str = date_today.strftime("%Y-%m-%d")
    anime = {"end_date": date_str}
    assert _anime_airing(anime)
