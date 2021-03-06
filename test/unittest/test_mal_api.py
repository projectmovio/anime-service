import os
from unittest import mock
from unittest.mock import patch

import pytest
import requests

from mal import HTTPError, MalApi, NotFoundError, get_all_titles

ENV = {"MAL_CLIENT_ID": "TEST_MAL_CLIENT_ID"}

BASE_NARUTO_ANIME = {
    "id": 20,
    "title": "Naruto",
    "main_picture": {
        "medium": "https://api-cdn.myanimelist.net/images/anime/13/17405.jpg",
        "large": "https://api-cdn.myanimelist.net/images/anime/13/17405l.jpg"
    },
    "media_type": "tv",
    "num_episodes": 220,
    "average_episode_duration": 1404,
    "synopsis": "Moments prior to Naruto Uzumaki's birth, a huge demon known as the Kyuubi, the Nine-Tailed Fox, attacked Konohagakure, the Hidden Leaf Village, and wreaked havoc. In order to put an end to the Kyuubi's rampage, the leader of the village, the Fourth Hokage, sacrificed his life and sealed the monstrous beast inside the newborn Naruto.\n\nNow, Naruto is a hyperactive and knuckle-headed ninja still living in Konohagakure. Shunned because of the Kyuubi inside him, Naruto struggles to find his place in the village, while his burning desire to become the Hokage of Konohagakure leads him not only to some great new friends, but also some deadly foes.\n\n[Written by MAL Rewrite]",
    "broadcast": {
        "day_of_the_week": "sunday"
    }
}


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_get_anime(req_mock):
    req_mock.return_value.status_code = 200
    req_mock.return_value.json.return_value = BASE_NARUTO_ANIME

    mal_api = MalApi()
    ret = mal_api.get_anime(21)
    assert ret == BASE_NARUTO_ANIME


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_get_anime_not_found(req_mock):
    req_mock.return_value.status_code = 404

    mal_api = MalApi()
    with pytest.raises(NotFoundError):
        mal_api.get_anime(21)


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_get_anime_error(req_mock):
    req_mock.return_value.status_code = 500

    mal_api = MalApi()
    with pytest.raises(HTTPError) as e:
        mal_api.get_anime(21)

    assert "Unexpected status code: 500" == str(e.value)


def test_get_all_titles():
    anime = {**BASE_NARUTO_ANIME, **{
        "alternative_titles": {
            "synonyms": [
                "NARUTO"
            ],
            "en": "Naruto2",
            "ja": "ナルト"
        },
    }}

    exp = [BASE_NARUTO_ANIME["title"], "NARUTO", "Naruto2", "ナルト"]
    assert get_all_titles(anime) == exp
