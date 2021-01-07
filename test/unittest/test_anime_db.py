import pytest


def test_get_anime_by_api_id_not_found(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": []
    }

    with pytest.raises(mocked_anime_db.NotFoundError):
        mocked_anime_db.get_anime_by_api_id("mal", "123")


def test_get_anime_by_id_not_found(mocked_anime_db):
    mocked_anime_db.table.get_item.return_value = {
        "Items": []
    }

    with pytest.raises(mocked_anime_db.NotFoundError):
        mocked_anime_db.get_anime_by_id("123")
