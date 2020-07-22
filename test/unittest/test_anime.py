import json
from unittest import mock

import pytest

import mal

from api.anime import handle


def test_post_anime(mocked_anime_db, mocked_anime):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_anime.sqs_queue.send_message.return_value = True
    event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "body": json.dumps({"anime_id": "3bce8de0-ab5d-5f8d-9b53-f3adce131b94"}),
        "statusCode": 202
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
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "body": json.dumps({"anime_id": "3bce8de0-ab5d-5f8d-9b53-f3adce131b94"}),
        "statusCode": 202
    }
    assert res == exp


def test_post_anime_no_query_params(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": [
            {
                "mal_id": "123"
            }
        ]
    }
    event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "queryStringParameters": {

        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({
            "error": "Please specify query parameters"
        })
    }
    assert res == exp


def test_post_anime_invalid_query_params(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": [
            {
                "mal_id": 123
            }
        ]
    }
    event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "queryStringParameters": {
            "aa": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({
            "error": "Please specify the 'mal_id' query parameter"
        })
    }
    assert res == exp


@mock.patch("mal.MalApi")
def test_search(mocked_mal):
    exp_res = {
        "id": "123"
    }
    mocked_mal.return_value.search.return_value = exp_res
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "search": "naruto"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps(exp_res)
    }
    assert res == exp


@mock.patch("mal.MalApi")
def test_search_http_error(mocked_mal_api):
    mocked_mal_api.return_value.search.side_effect = mal.HTTPError("TEST MESSAGE")
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "search": "naruto"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 503,
        "body": "TEST MESSAGE"
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
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps(exp_res)
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
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps(exp_res)
    }
    assert res == exp


@mock.patch("mal.MalApi")
def test_search_mal_id_not_found(mocked_mal_api, mocked_anime_db):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_mal_api.return_value.get_anime.side_effect = mal.NotFoundError
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
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
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 503,
    }
    assert res == exp


def test_search_no_query_params():
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({"error": "Please specify query parameters"})
    }
    assert res == exp


def test_search_invalid_query_params():
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "abc": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({"error": "Please specify either 'search' or 'mal_id' query parameter"})
    }
    assert res == exp


def test_unsupported_method(mocked_anime_db, mocked_anime):
    event = {
        "requestContext": {
            "http": {
                "method": "AA"
            }
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    with pytest.raises(mocked_anime.UnsupportedMethod):
        handle(event, None)
