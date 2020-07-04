import os
import boto3

import anime_db
import logger
import mal

SQS_QUEUE_URL = os.getenv("POST_ANIME_SQS_QUEUE_URL")

sqs_queue = None

log = logger.get_logger("anime")


class Error(Exception):
    pass


class UnsupportedMethod(Error):
    pass


def _get_sqs_queue():
    global sqs_queue
    if sqs_queue is None:
        sqs_queue = boto3.resource("sqs").Queue(SQS_QUEUE_URL)
    return sqs_queue


def handle(event, context):
    log.debug(f"Received event: {event}")

    method = event["http"]["method"]

    mal_id = event["queryStringParameters"].get("mal_id")
    search = event["queryStringParameters"].get("search")

    if method == "POST":
        return _post_anime(mal_id)
    elif method == "GET":
        return _search_anime(mal_id, search)
    else:
        raise UnsupportedMethod()


def _post_anime(mal_id):
    if mal_id is None:
        return {
            "statusCode": 400,
            "body": {"error": "Please specify the 'mal_id' query parameter"}
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

    return {
        "statusCode": 202,
    }


def _search_anime(mal_id, search):
    if search is None and mal_id is None:
        return {
            "statusCode": 400,
            "body": {"error": "Please specify either 'search' or 'mal_id' query parameter"}
        }

    if mal_id:
        try:
            res = anime_db.get_anime_by_mal_id(mal_id)
        except anime_db.NotFoundError:
            log.debug(f"Anime with mal_id: {mal_id} not found in DB, use API")
        else:
            return {"statusCode": 200, "body": res}

        try:
            res = mal.MalApi().get_anime(mal_id)
        except mal.NotFoundError:
            return {"statusCode": 404}
        except mal.HTTPError:
            return {"statusCode": 500}
        else:
            return {"statusCode": 200, "body": res}
    elif search:
        try:
            res = mal.MalApi().search(search)
        except mal.HTTPError:
            return {"statusCode": 500}
        return {"statusCode": 200, "body": res}
