import os
from unittest import mock
from unittest.mock import patch

import pytest
import requests

from mal import HTTPError, MalApi, NotFoundError

ENV = {"MAL_CLIENT_ID": "TEST_MAL_CLIENT_ID"}


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_search(req_mock):
    exp = {
        "anime": [{
            "id": 20,
            "title": "Naruto",
            "main_picture": {
                "medium": "17405.jpg",
                "large": "17405l.jpg"
            },
        }]
    }

    req_mock.return_value.status_code = 200
    req_mock.return_value.json.return_value = {"data": [{"node": exp["anime"][0]}]}

    mal_api = MalApi()
    ret = mal_api.search("Naruto")
    assert ret == exp


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_search_error(req_mock):
    req_mock.return_value.status_code = 500

    mal_api = MalApi()

    with pytest.raises(HTTPError) as e:
        mal_api.search("Naruto")

    assert "Unexpected status code: 500" == str(e.value)


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_get_anime(req_mock):
    exp = {
        "anime": {
            "id": 21,
            "title": "One Piece",
            "main_picture": {
                "medium": "73245.jpg",
                "large": "73245l.jpg"
            }
        }
    }

    req_mock.return_value.status_code = 200
    req_mock.return_value.json.return_value = exp["anime"]

    mal_api = MalApi()
    ret = mal_api.get_anime(21)
    assert ret == exp


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
