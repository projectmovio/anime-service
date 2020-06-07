import os
import uuid
from typing import List

import boto3

DATABASE_NAME = os.getenv("ANIME_EPISODES_DATABASE_NAME")

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


def put_episodes(anime_id, episodes):
    with _get_table().batch_writer() as batch:
        for ep in episodes:
            ep["anime_id"] = anime_id
            batch.put_item(Item=ep)
