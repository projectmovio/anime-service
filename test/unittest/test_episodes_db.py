import pytest


def test_get_episodes_not_found(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {
        "Items": []
    }

    with pytest.raises(mocked_episodes_db.NotFoundError):
        mocked_episodes_db.get_episodes("123")


