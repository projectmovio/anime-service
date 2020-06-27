import json
import os

import boto3

import anime_db
import logger

SQS_QUEUE_URL = os.getenv("POST_ANIME_SQS_QUEUE_URL")

sqs_queue = None

log = logger.get_logger("post_anime")


def _get_sqs_queue():
    global sqs_queue
    if sqs_queue is None:
        sqs_queue = boto3.resource("sqs").Queue(SQS_QUEUE_URL)
    return sqs_queue


def handle(event, context):
    log.debug(f"Received event: {event}")

    mal_id = event["queryStringParameters"].get("mal_id")

    if mal_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify the 'mal_id' query parameter"})
        }

    try:
        anime_db.get_anime_by_mal_id(mal_id)
    except anime_db.NotFoundError:
        pass
    else:
        return {
            "statusCode": 202,
        }

    _get_sqs_queue().send_message(
        MessageBody=str(mal_id)
    )


