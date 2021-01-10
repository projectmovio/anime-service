import json
from unittest import mock

import pytest

import mal

from api.anime import handle

POST_EVENT = {
    "requestContext": {
        "http": {
            "method": "POST"
        }
    },
    "body": '{ "api_name": "mal", "api_id": "123"}'
}


def test_post_anime(mocked_anime_db, mocked_anime):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_anime.sqs_queue.send_message.return_value = True

    res = handle(POST_EVENT, None)

    exp = {
        "body": json.dumps({"id": "7e2c8ee2-66cf-598f-aedf-cdfba825613b"}),
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

    res = handle(POST_EVENT, None)

    exp = {
        "body": json.dumps({"id": "7e2c8ee2-66cf-598f-aedf-cdfba825613b"}),
        "statusCode": 202
    }
    assert res == exp


def test_post_anime_no_body(mocked_anime_db):
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
        "body": {

        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": "Invalid post body"
    }
    assert res == exp


def test_post_anime_invalid_api_name(mocked_anime_db):
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
        "body": '{ "api_name": "bad_name", "api_id": "123"}'
    }
    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({
            "message": "Invalid post schema",
            "error": "\'bad_name\' is not one of [\'mal\']",
        })
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


def test_get_mal_id_in_db(mocked_anime_db):
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


def test_get_mal_id_not_found(mocked_anime_db):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
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


def test_get_no_query_params():
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


def test_get_invalid_query_params():
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
        "body": json.dumps({"error": "Unsupported query param"})
    }
    assert res == exp
