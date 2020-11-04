import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util

import logger

DATABASE_NAME = os.getenv("ANIME_EPISODES_DATABASE_NAME")
EPISODE_ID_INDEX_NAME = "episode_id"

table = None
client = None

log = logger.get_logger(__name__)


class Error(Exception):
    pass


class NotFoundError(Error):
    pass


class InvalidStartOffset(Error):
    pass


class InvalidAmountOfEpisodes(Error):
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


def put_episodes(anime_id, episodes):
    with _get_table().batch_writer() as batch:
        for ep in episodes:
            ep["id"] = _create_episode_uuid(anime_id, ep["episode_number"])
            ep["anime_id"] = anime_id
            batch.put_item(Item=ep)


def _create_episode_uuid(anime_id, episode_id):
    return str(uuid.uuid5(uuid.UUID(anime_id), str(episode_id)))


def get_episode(anime_id, episode_id):
    res = table.query(
        IndexName=EPISODE_ID_INDEX_NAME,
        KeyConditionExpression=Key("anime_id").eq(anime_id) & Key("id").eq(episode_id)
    )

    if "Items" not in res or not res["Items"]:
        raise NotFoundError(f"Episode with ID: {episode_id} and anime_id: {anime_id} not found")

    if res["Count"] != 1:
        raise InvalidAmountOfEpisodes(f"Episode with ID: {episode_id} and anime_id: {anime_id} has {res['Count']} results")

    return res["Items"][0]


def get_episodes(anime_id, limit=100, start=1):
    start_page = 0
    total_pages = 0
    res = []

    if start <= 0:
        raise InvalidStartOffset

    for p in _episodes_generator(anime_id, limit):
        total_pages += 1
        start_page += 1
        if start_page == start:
            res = p

    if start_page == 0:
        raise NotFoundError(f"Episodes for anime with id: {anime_id} not found")

    if start > start_page:
        raise InvalidStartOffset

    log.debug(f"get_episodes response: {res}")

    return {
        "items": res,
        "total_pages": total_pages
    }


def _episodes_generator(anime_id, limit):
    paginator = _get_client().get_paginator('query')

    page_iterator = paginator.paginate(
        TableName=DATABASE_NAME,
        KeyConditionExpression="anime_id = :anime_id",
        ExpressionAttributeValues={":anime_id": {"S": str(anime_id)}},
        Limit=limit,
        ScanIndexForward=False
    )

    for p in page_iterator:
        items = []
        for i in p["Items"]:
            items.append(json_util.loads(i))
        if items:
            yield items
