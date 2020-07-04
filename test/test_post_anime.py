from api.anime import handle


def test_handler(mocked_anime_db, mocked_post_anime):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_post_anime.sqs_queue.send_message.return_value = True
    event = {
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 202,
    }
    assert res == exp


def test_handler_already_exist(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": [
            {
                "mal_id": "123"
            }
        ]
    }
    event = {
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 202,
    }
    assert res == exp


def test_handler_no_id_provided(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": [
            {
                "mal_id": "123"
            }
        ]
    }
    event = {
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
