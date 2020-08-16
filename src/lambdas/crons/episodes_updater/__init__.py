import json
import os
import boto3
import logger
import anime_db

from datetime import datetime

log = logger.get_logger("episode_updater")

SQS_QUEUE_URL = os.getenv("POST_ANIME_SQS_QUEUE_URL")

sqs_queue = None


def _get_sqs_queue():
    global sqs_queue
    if sqs_queue is None:
        sqs_queue = boto3.resource("sqs").Queue(SQS_QUEUE_URL)
    return sqs_queue


def handle(event, context):
    day_of_week = datetime.today().strftime('%A').lower()
    log.info(f"Updating anime with broadcast_day: {day_of_week}")

    for anime in anime_db.anime_by_broadcast_generator(day_of_week):
        log.debug(f"Sending SQS message for anime with id: ${anime['id']}")
        _get_sqs_queue().send_message(
            MessageBody=json.dumps({
                "mal_id": anime["mal_id"],
                "force_update": True
            })
        )
