from unittest.mock import MagicMock

import pytest

from api.get_episodes import handle


@pytest.fixture
def mocked_episodes_db():
    import episodes_db

    episodes_db.table = MagicMock()

    return episodes_db


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
    mocked_episodes_db.table.query.return_value = {
        "Items": exp_eps
    }
    event = {
        "pathParameters": {
            "anime_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": exp_eps
    }
    assert res == exp


def test_handler_not_found(mocked_episodes_db):
    mocked_episodes_db.table.query.side_effect = mocked_episodes_db.NotFoundError
    event = {
        "pathParameters": {
            "anime_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 404,
    }
    assert res == exp
