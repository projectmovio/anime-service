import pytest


def test_get_annime_by_mal_id_not_found(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": []
    }

    with pytest.raises(mocked_anime_db.NotFoundError):
        mocked_anime_db.get_anime_by_mal_id("123")

def test_get_annime_not_found(mocked_anime_db):
    mocked_anime_db.table.query.return_value = {
        "Items": []
    }

    with pytest.raises(mocked_anime_db.NotFoundError):
        mocked_anime_db.get_anime("123")

