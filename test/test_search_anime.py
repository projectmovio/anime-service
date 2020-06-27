from unittest.mock import MagicMock

import pytest
import api.search_anime


@pytest.fixture
def mock():
    import anime_db
    import mal

    anime_db.table = MagicMock()
    mal.MalApi = MagicMock()

    return anime_db, mal


def test_handle_search(mock):
    anime_db, mal_api = mock
    exp_res = {
        "id": "123"
    }
    mal_api.MalApi.return_value.search.return_value = exp_res
    event = {
        "queryStringParameters": {
            "search": "naruto"
        }
    }

    res = api.search_anime.handle(event, None)

    exp = {
        "statusCode": 200,
        "body": exp_res
    }
    assert res == exp


def test_handle_search_http_error(mock):
    anime_db, mal_api = mock
    mal_api.MalApi.return_value.search.side_effect = mal_api.HTTPError
    event = {
        "queryStringParameters": {
            "search": "naruto"
        }
    }

    res = api.search_anime.handle(event, None)

    exp = {
        "statusCode": 500,
    }
    assert res == exp
