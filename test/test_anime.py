from unittest import mock

import pytest

import mal

from api.anime import handle


def test_post_anime(mocked_anime_db, mocked_anime):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_anime.sqs_queue.send_message.return_value = True
    event = {
        "http": {
            "method": "POST"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 202,
    }
    assert res == exp


def test_post_anime_already_exist(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": [
            {
                "mal_id": "123"
            }
        ]
    }
    event = {
        "http": {
            "method": "POST"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 202,
    }
    assert res == exp


def test_post_anime_no_id_provided(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": [
            {
                "mal_id": "123"
            }
        ]
    }
    event = {
        "http": {
            "method": "POST"
        },
        "queryStringParameters": {
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": {
            "error": "Please specify the 'mal_id' query parameter"
        }
    }
    assert res == exp


@mock.patch("mal.MalApi")
def test_search(mocked_mal):
    exp_res = {
        "id": "123"
    }
    mocked_mal.return_value.search.return_value = exp_res
    event = {
        "http": {
            "method": "GET"
        },
        "queryStringParameters": {
            "search": "naruto"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": exp_res
    }
    assert res == exp


@mock.patch("mal.MalApi")
def test_search_http_error(mocked_mal_api):
    mocked_mal_api.return_value.search.side_effect = mal.HTTPError
    event = {
        "http": {
            "method": "GET"
        },
        "queryStringParameters": {
            "search": "naruto"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 500,
    }
    assert res == exp


def test_search_mal_id_in_db(mocked_anime_db):
    exp_res = {
        "id": "123"
    }
    mocked_anime_db.table.query.return_value = {
        "Items": [
            exp_res
        ]
    }
    event = {
        "http": {
            "method": "GET"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": exp_res
    }
    assert res == exp


@mock.patch("mal.MalApi")
def test_search_mal_id_not_found_in_db(mocked_mal_api, mocked_anime_db):
    exp_res = {
        "id": "123"
    }
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_mal_api.return_value.get_anime.return_value = exp_res
    event = {
        "http": {
            "method": "GET"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": exp_res
    }
    assert res == exp


@mock.patch("mal.MalApi")
def test_search_mal_id_not_found(mocked_mal_api, mocked_anime_db):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_mal_api.return_value.get_anime.side_effect = mal.NotFoundError
    event = {
        "http": {
            "method": "GET"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 404,
    }
    assert res == exp


@mock.patch("mal.MalApi")
def test_search_mal_id_http_error(mocked_mal_api, mocked_anime_db):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_mal_api.return_value.get_anime.side_effect = mal.HTTPError
    event = {
        "http": {
            "method": "GET"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 500,
    }
    assert res == exp


def test_search_no_query_params():
    event = {
        "http": {
            "method": "GET"
        },
        "queryStringParameters": {
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": {"error": "Please specify either 'search' or 'mal_id' query parameter"}
    }
    assert res == exp


def test_unsupported_method(mocked_anime_db, mocked_anime):
    event = {
        "http": {
            "method": "AA"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    with pytest.raises(mocked_anime.UnsupportedMethod):
        handle(event, None)