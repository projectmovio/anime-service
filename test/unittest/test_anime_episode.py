import json
from unittest.mock import MagicMock

from api.anime_episode import handle


def test_handler(mocked_episodes_db):
    exp_ep = {
        "Items": [
            {
                "id": "0cb444d6-1509-452d-acdd-b344cc7254a0",
                "title": "ep1",
                "episode_number": 2,
            }
        ],
        "Count": 1
    }
    mocked_episodes_db.table.query.return_value = exp_ep
    event = {
        "pathParameters": {
            "id": "0cb444d6-1509-452d-acdd-b344cc7254a0",
            "episode_id": "345"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps(exp_ep["Items"][0])
    }
    assert res == exp


def test_handler_not_found(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {"Items": []}

    event = {
        "pathParameters": {
            "id": "123",
            "episode_id": "345"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 404,
    }
    assert res == exp


def test_handler_invalid_amount(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {"Items": [{"ep_1": "1"}], "Count": 10}

    event = {
        "pathParameters": {
            "id": "123",
            "episode_id": "345"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 500,
    }
    assert res == exp
