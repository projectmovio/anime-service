import json
from unittest.mock import MagicMock

import pytest

from api.anime_episodes import handle, UnsupportedMethod

POST_EVENT = {
    "pathParameters": {
        "id": "123"
    },
    "requestContext": {
        "http": {
            "method": "POST"
        }
    },
    "body": '{ "api_name": "anidb", "api_id": "456"}'
}


def test_post_episode(mocked_episodes_db, mocked_anime):
    mocked_episodes_db.table.query.return_value = {
        "Items": [
            {
                "anidb_id": "456"
            }
        ],
        "Count": 1
    }
    mocked_anime.sqs_queue.send_message.return_value = True

    res = handle(POST_EVENT, None)

    exp = {
        "body": json.dumps({"anidb_id": "456"}),
        "statusCode": 200
    }
    assert res == exp


def test_post_episode_not_found(mocked_episodes_db, mocked_anime):
    mocked_episodes_db.table.query.side_effect = mocked_episodes_db.NotFoundError
    mocked_anime.sqs_queue.send_message.return_value = True

    res = handle(POST_EVENT, None)

    exp = {
        "statusCode": 404
    }
    assert res == exp


def test_post_episode_no_body(mocked_anime_db):
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
        "pathParameters": {
            "id": "123"
        },
        "body": {}
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": "Invalid post body"
    }
    assert res == exp


def test_post_episode_invalid_api_name(mocked_anime_db):
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
        "pathParameters": {
            "id": "123"
        },
        "body": '{ "api_name": "bad_name", "api_id": "123"}'
    }
    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({
            "message": "Invalid post schema",
            "error": "\'bad_name\' is not one of [\'anidb\']",
        })
    }
    assert res == exp


def test_unsupported_method(mocked_anime_db):
    event = {
        "requestContext": {
            "http": {
                "method": "AA"
            }
        },
        "pathParameters": {
            "id": "123"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    with pytest.raises(UnsupportedMethod):
        handle(event, None)


def test_handler(mocked_episodes_db):
    exp_eps = [
        {
            "id": "1",
            "title": "ep1",
        },
        {
            "id": "2",
            "title": "ep2",
        }
    ]
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": exp_eps}
    ]

    event = {
        "pathParameters": {
            "id": "123"
        },
        "queryStringParameters": {},
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps({"items": exp_eps, "total_pages": 1})
    }
    assert res == exp


def test_handler_not_found(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": []}
    ]

    event = {
        "pathParameters": {
            "id": "123"
        },
        "queryStringParameters": {},
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 404,
    }
    assert res == exp


def test_handler_with_limit(mocked_episodes_db):
    exp_eps = [
        {
            "id": "1",
            "title": "ep1",
        },
        {
            "id": "2",
            "title": "ep2",
        }
    ]
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [exp_eps[0]]},
        {"Items": [exp_eps[1]]}
    ]

    event = {
        "pathParameters": {
            "anime_id": "123"
        },
        "queryStringParameters": {
            "limit": 1
        },
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps({"items": [exp_eps[0]], "total_pages": 2})
    }
    assert res == exp


def test_handler_with_start(mocked_episodes_db):
    exp_eps = [
        {
            "id": "1",
            "title": "ep1",
        },
        {
            "id": "2",
            "title": "ep2",
        }
    ]
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [exp_eps[0]]},
        {"Items": [exp_eps[1]]}
    ]

    event = {
        "pathParameters": {
            "anime_id": "123"
        },
        "queryStringParameters": {
            "start": 2
        },
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps({"items": [exp_eps[1]], "total_pages": 2})
    }
    assert res == exp


def test_handler_with_limit_and_start(mocked_episodes_db):
    exp_eps = [
        {
            "id": "1",
            "title": "ep1",
        },
        {
            "id": "2",
            "title": "ep2",
        }
    ]
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [exp_eps[0]]},
        {"Items": [exp_eps[1]]}
    ]

    event = {
        "pathParameters": {
            "anime_id": "123"
        },
        "queryStringParameters": {
            "limit": 1,
            "start": 2
        },
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps({"items": [exp_eps[1]], "total_pages": 2})
    }
    assert res == exp


def test_handler_with_invalid_limit_type(mocked_episodes_db):
    exp_eps = [
        {
            "id": "1",
            "title": "ep1",
        },
        {
            "id": "2",
            "title": "ep2",
        }
    ]
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [exp_eps[0]]},
        {"Items": [exp_eps[1]]}
    ]

    event = {
        "pathParameters": {
            "anime_id": "123"
        },
        "queryStringParameters": {
            "limit": "abc",
            "start": 2
        },
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({"message": "Invalid limit type"})
    }
    assert res == exp


def test_handler_with_invalid_start_type(mocked_episodes_db):
    exp_eps = [
        {
            "id": "1",
            "title": "ep1",
        },
        {
            "id": "2",
            "title": "ep2",
        }
    ]
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [exp_eps[0]]},
        {"Items": [exp_eps[1]]}
    ]

    event = {
        "pathParameters": {
            "anime_id": "123"
        },
        "queryStringParameters": {
            "limit": 1,
            "start": "abc"
        },
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({"message": "Invalid start type"})
    }
    assert res == exp


def test_handler_invalid_offset(mocked_episodes_db):
    exp_eps = [
        {
            "id": "1",
            "title": "ep1",
        },
        {
            "id": "2",
            "title": "ep2",
        }
    ]
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [exp_eps[0]]},
        {"Items": [exp_eps[1]]}
    ]

    event = {
        "pathParameters": {
            "anime_id": "123"
        },
        "queryStringParameters": {
            "limit": 1,
            "start": 0
        },
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({"message": "Invalid offset"})
    }
    assert res == exp
