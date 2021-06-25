import json
import os
from json import JSONDecodeError

import boto3

import anime_db
import decimal_encoder
import logger
import schema

SQS_QUEUE_URL = os.getenv("POST_ANIME_SQS_QUEUE_URL")
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
POST_SCHEMA_PATH = os.path.join(CURRENT_DIR, "post.json")

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

    method = event["requestContext"]["http"]["method"]

    if method == "POST":
        body = event.get("body")
        return _post_anime(body)
    elif method == "GET":
        query_params = event.get("queryStringParameters")
        return _get_anime_by_api_id(query_params)
    else:
        raise UnsupportedMethod()


def _post_anime(body):
    try:
        body = json.loads(body)
    except (TypeError, JSONDecodeError):
        log.debug(f"Invalid body: {body}")
        return {
            "statusCode": 400,
            "body": "Invalid post body"
        }

    try:
        schema.validate_schema(POST_SCHEMA_PATH, body)
    except schema.ValidationException as e:
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid post schema", "error": str(e)})}

    if body["api_name"] == "mal":
        return _post_mal(body["api_id"])


def _post_mal(mal_id):
    try:
        anime_db.get_anime_by_api_id("mal", int(mal_id))
    except anime_db.NotFoundError:
        pass
    else:
        return {
            "statusCode": 202,
            "body": json.dumps({"id": anime_db.create_anime_uuid(mal_id)})
        }

    _get_sqs_queue().send_message(
        MessageBody=json.dumps({"mal_id": mal_id})
    )

    return {
        "statusCode": 202,
        "body": json.dumps({"id": anime_db.create_anime_uuid(mal_id)})
    }


def _get_anime_by_api_id(query_params):
    if not query_params:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify query parameters"})
        }

    if "api_id" not in query_params:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing api_id query parameter"})
        }

    if "api_name" not in query_params:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing api_name query parameter"})
        }

    api_id = int(query_params["api_id"])
    api_name = query_params["api_name"]

    if api_name in ["mal"]:
        try:
            res = anime_db.get_anime_by_api_id(api_name, api_id)
            return {
                "statusCode": 200,
                "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)
            }
        except anime_db.NotFoundError:
            return {"statusCode": 404}
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Unsupported api_name"})
        }
