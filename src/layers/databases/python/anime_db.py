import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key

DATABASE_NAME = os.getenv("ANIME_DATABASE_NAME")

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


def new_anime(mal_id):
    anime_id = uuid.uuid5(uuid.NAMESPACE_OID, mal_id)

    _get_table().update_item(
        Key={"id": anime_id},
        UpdateExpression="SET #attr1 = :val1",
        ExpressionAttributeNames={"#attr1": "mal_id"},
        ExpressionAttributeValues={":val1": mal_id}
    )

    return anime_id


def get_anime(mal_id):
    res = _get_table().query(
        IndexName='mal_id',
        KeyConditionExpression=Key('mal_id').eq(mal_id)
    )

    if not res["Items"]:
        return NotFoundError(f"Anime with mal_id: {mal_id} not found")

    return res["Items"][0]
