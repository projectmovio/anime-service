import api.search_anime


def test_handle_search(mocked_mal):
    exp_res = {
        "id": "123"
    }
    mocked_mal.MalApi.return_value.search.return_value = exp_res
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


def test_handle_search_http_error(mocked_mal):
    mocked_mal.MalApi.return_value.search.side_effect = mocked_mal.HTTPError
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


def test_handle_search_mal_id_in_db(mocked_anime_db):
    exp_res = {
        "id": "123"
    }
    mocked_anime_db.table.query.return_value = {
        "Items": [
            exp_res
        ]
    }
    event = {
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = api.search_anime.handle(event, None)

    exp = {
        "statusCode": 200,
        "body": exp_res
    }
    assert res == exp


def test_handle_search_mal_id_not_found_in_db(mocked_anime_db, mocked_mal):
    exp_res = {
        "id": "123"
    }
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_mal.MalApi.return_value.get_anime.return_value = exp_res
    event = {
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = api.search_anime.handle(event, None)

    exp = {
        "statusCode": 200,
        "body": exp_res
    }
    assert res == exp


def test_handle_search_mal_id_not_found(mocked_anime_db, mocked_mal):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_mal.MalApi.return_value.get_anime.side_effect = mocked_mal.NotFoundError
    event = {
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = api.search_anime.handle(event, None)

    exp = {
        "statusCode": 404,
    }
    assert res == exp


def test_handle_search_mal_id_http_error(mocked_anime_db, mocked_mal):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    mocked_mal.MalApi.return_value.get_anime.side_effect = mocked_mal.HTTPError
    event = {
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = api.search_anime.handle(event, None)

    exp = {
        "statusCode": 500,
    }
    assert res == exp


def test_handle_no_query_params():
    event = {
        "queryStringParameters": {
        }
    }

    res = api.search_anime.handle(event, None)

    exp = {
        "statusCode": 400,
        "body": {"error": "Please specify either 'search' or 'mal_id' query parameter"}
    }
    assert res == exp
