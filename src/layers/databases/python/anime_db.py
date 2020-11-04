import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util

import logger

DATABASE_NAME = os.getenv("ANIME_DATABASE_NAME")
ANIME_UUID_NAMESPACE = uuid.UUID("e27bf9e0-e54a-4260-bcdc-7baad9a3c36b")

table = None
client = None

log = logger.get_logger(__name__)


class Error(Exception):
    pass


class NotFoundError(Error):
    pass


def _get_table():
    global table
    if table is None:
        table = boto3.resource("dynamodb").Table(DATABASE_NAME)
    return table


def _get_client():
    global client
    if client is None:
        client = boto3.client("dynamodb")
    return client


def new_anime(anime_info):
    anime_id = create_anime_uuid(anime_info["mal_id"])
    update_anime(anime_id, anime_info)

    return anime_id


def create_anime_uuid(mal_id):
    return str(uuid.uuid5(ANIME_UUID_NAMESPACE, str(mal_id)))


def update_anime(anime_id, data):
    items = ','.join(f'#{k}=:{k}' for k in data)
    update_expression = f"SET {items}"
    expression_attribute_names = {f'#{k}': k for k in data}
    expression_attribute_values = {f':{k}': v for k, v in data.items()}

    log.debug("Running update_item")
    log.debug(f"Update expression: {update_expression}")
    log.debug(f"Expression attribute names: {expression_attribute_names}")
    log.debug(f"Expression attribute values: {expression_attribute_values}")

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
    log.debug(f"get_anime_by_mal_id res: {res}")

    if not res["Items"]:
        raise NotFoundError(f"Anime with mal_id: {mal_id} not found")

    return res["Items"][0]


def get_anime_by_id(anime_id):
    res = _get_table().get_item(Key={"id": anime_id})

    if "Item" not in res:
        raise NotFoundError(f"Anime with id: {anime_id} not found")

    return res["Item"]


def get_anime_by_ids(anime_ids):
    ret = {}

    res = _get_client().batch_get_item(
        RequestItems={
            DATABASE_NAME: {
                "Keys": [{"id": {"S": anime_id}} for anime_id in anime_ids],
                "AttributesToGet": ["id", "title", "main_picture", "start_date"]
            }
        }
    )

    for item in res["Responses"][DATABASE_NAME]:
        anime_id = item.pop("id")["S"]
        ret[anime_id] = json_util.loads(item)

    return ret


def get_ids(mal_items):
    id_map = {}
    for mal_item in mal_items:
        mal_id = mal_item["id"]
        try:
            res = get_anime_by_mal_id(mal_item["id"])
            id_map[mal_id] = res["id"]
        except NotFoundError:
            pass

    return id_map


def anime_by_broadcast_generator(day_of_week, limit=100):
    paginator = _get_client().get_paginator('query')

    page_iterator = paginator.paginate(
        TableName=DATABASE_NAME,
        IndexName="broadcast_day",
        KeyConditionExpression="broadcast_day=:day_of_week",
        ExpressionAttributeValues={":day_of_week": {"S": str(day_of_week)}},
        Limit=limit,
        ScanIndexForward=False
    )

    for p in page_iterator:
        for i in p["Items"]:
            yield json_util.loads(i)
