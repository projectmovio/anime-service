import json

from api.anime_by_id import handle
from dynamodb_json import json_util


def test_handler(mocked_anime_db):
    exp_item = {
        "id": "123",
        "title": "naruto",
    }
    mocked_anime_db.DATABASE_NAME = "TEST_DB"
    mocked_anime_db.client.batch_get_item.return_value = {
        "Responses": {
            mocked_anime_db.DATABASE_NAME: [
                json_util.dumps(exp_item, as_dict=True)
            ]
        }
    }
    event = {
        "pathParameters": {
            "ids": "123"
        }
    }

    res = handle(event, None)

    exp = {'body': '{"123": {"title": "naruto"}}', 'statusCode': 200}
    assert res == exp


def test_handler_not_found(mocked_anime_db):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    event = {
        "pathParameters": {
            "ids": "123"
        }
    }

    res = handle(event, None)

    assert res == {'body': '{}', 'statusCode': 200}
