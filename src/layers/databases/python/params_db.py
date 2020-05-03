import os

import boto3

DATABASE_NAME = os.getenv("ANIME_PARAMS_DATABASE_NAME")

table = None


class Error(Exception):
    pass


class NotFoundError(Error):
    pass


def _get_table():
    global table
    if table is None:
        table = boto3.resource("dynamodb").Table(DATABASE_NAME)
    return table


def set_last_post_anime_update(timestamp, mal_id, anidb_id):
    _get_table().update_item(
        Key={"name": "post_anime_update"},
        UpdateExpression="SET timestamp= :timestamp, mal_id = :mal_id, anidb_id = :anidb_id",
        ExpressionAttributeValues={":timestamp": timestamp, ":mal_id": mal_id, ":anidb_id": anidb_id}
    )


def get_last_post_anime_update():
    res = _get_table().get_item(
        Key={"name": "post_anime_update"}
    )

    if "Item" in res:
        return res["Item"]["timestamp"]

    return 0
