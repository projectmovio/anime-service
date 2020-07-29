import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key

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


def new_anime(mal_info):
    anime_id = create_anime_uuid(mal_info["mal_id"])
    update_anime(anime_id, mal_info)

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


def get_anime(anime_id):
    res = _get_table().get_item(Key={"id": anime_id})

    if "Item" not in res:
        raise NotFoundError(f"Anime with mal_id: {anime_id} not found")

    return res["Item"]


def get_anime_posters(anime_ids):
    ret = {}

    res = _get_client().batch_get_item(
        RequestItems={
            DATABASE_NAME: {
                "Keys": [{"id": {"S": anime_id}} for anime_id in anime_ids],
                "AttributesToGet": ["id", "main_picture"]
            }
        }
    )

    for item in res["Responses"][DATABASE_NAME]:
        anime_id = item["id"]["S"]
        poster = item["main_picture"]["M"]["medium"]["S"]
        ret[anime_id] = poster

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
