import os

import boto3
from boto3.dynamodb.conditions import Key

import logger

DATABASE_NAME = os.getenv("ANIME_EPISODES_DATABASE_NAME")

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
        client = boto3.resource("dynamodb")
    return client


def put_episodes(anime_id, episodes):
    with _get_table().batch_writer() as batch:
        for ep in episodes:
            ep["anime_id"] = anime_id
            batch.put_item(Item=ep)


def get_episodes(anime_id, limit=100, start=1):
    start_page = 1
    res = []
    for p in _episodes_generator(anime_id, limit):
        if start_page < start:
            continue
        res = p
        break

    log.debug(f"get_episodes response: {res}")

    if not res:
        raise NotFoundError(f"Anime with id: {anime_id} not found")

    return res


def _episodes_generator(anime_id, limit):
    paginator = _get_client().get_paginator('query')

    page_iterator = paginator.paginate(
        TableName=DATABASE_NAME,
        KeyConditionExpression="anime_id = :anime_id",
        ExpressionAttributeValues={":anime_id": {"S": str(anime_id)}},
        Limit=limit
    )

    for p in page_iterator:
        yield p["Items"]

    yield None


