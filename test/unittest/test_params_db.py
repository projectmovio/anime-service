def test_get_last_post_anime_update_not_found(mocked_params_db):
    mocked_params_db.table.query.return_value = {
        "Items": []
    }

    ret = mocked_params_db.get_last_post_anime_update()
    assert ret == 0


