import json
from unittest.mock import MagicMock

from api.anime_episodes import handle


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
            "anime_id": "123"
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
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({"message": "Invalid offset"})
    }
    assert res == exp
