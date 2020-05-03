import os

import boto3

SQS_QUEUE_URL = os.getenv("POST_ANIME_SQS_QUEUE_URL")

sqs_queue = None


def _get_sqs_queue():
    global sqs_queue
    if sqs_queue is None:
        sqs_queue = boto3.resource("sqs").Queue(SQS_QUEUE_URL)
    return sqs_queue


def publish_message(mal_id):
    _get_sqs_queue().send_message(
        MessageBody=str(mal_id)
    )
