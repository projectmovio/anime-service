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


def new_anime(mal_info):
    anime_id = uuid.uuid5(uuid.NAMESPACE_OID, mal_info["mal_id"])
    update_anime(anime_id, mal_info)

    return anime_id


def update_anime(anime_id, data):
    items = " ".join(f"#{k} = :{k}" for k, in data)
    update_expression = f"SET {items}"
    expression_attribute_names = {f'#{k}': k for k in data}
    expression_attribute_values = {f':{k}': v for k, v in data.iteritems()}

    _get_table().update_item(
        Key={"id": anime_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )


def get_anime_by_mal_id(mal_id):
    res = _get_table().query(
        IndexName='mal_id',
        KeyConditionExpression=Key('mal_id').eq(mal_id)
    )

    if not res["Items"]:
        return NotFoundError(f"Anime with mal_id: {mal_id} not found")

    return res["Items"][0]
