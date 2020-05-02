import json
import os

import boto3

from anime import get_anime, NotFoundError

QUEUE_URL = os.getenv("POST_ANIME_QUEUE_URL")

sqs_queue = None


def _get_sqs_queue():
    global sqs_queue
    if sqs_queue is None:
        sqs_queue = boto3.resource("sqs").Queue(QUEUE_URL)


def handle(event, context):
    print(f"Received event: {event}")

    mal_id = event["queryStringParameters"].get("mal_id")

    if mal_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify the 'mal_id' query parameter"})
        }

    try:
        get_anime(mal_id)
    except NotFoundError:
        pass
    else:
        return {
            "statusCode": 202,
        }

    _get_sqs_queue().send_message(
        MessageBody=str(mal_id)
    )
