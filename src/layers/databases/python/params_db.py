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


def set_last_post_anime_update(timestamp, anime_id):
    _get_table().update_item(
        Key={"name": "post_anime_update"},
        UpdateExpression="SET time= :timestamp, anime_id = :anime_id",
        ExpressionAttributeValues={":time": timestamp, ":anime_id": anime_id}
    )


def get_last_post_anime_update():
    res = _get_table().get_item(
        Key={"name": "post_anime_update"}
    )

    if "Item" in res:
        return res["Item"]["time"]

    return 0
