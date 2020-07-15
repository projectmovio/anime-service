import os

import boto3
from boto3.dynamodb.conditions import Key

import logger

DATABASE_NAME = os.getenv("ANIME_EPISODES_DATABASE_NAME")

table = None

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


def put_episodes(anime_id, episodes):
    with _get_table().batch_writer() as batch:
        for ep in episodes:
            ep["anime_id"] = anime_id
            batch.put_item(Item=ep)


def get_episodes(anime_id):
    res = _get_table().query(
        KeyConditionExpression=Key('anime_id').eq(str(anime_id))
    )
    log.debug(f"get_episodes response: {res}")

    if not res["Items"]:
        raise NotFoundError(f"Anime with id: {anime_id} not found")

    return res["Items"]
