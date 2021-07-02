import json
import os
from json import JSONDecodeError

import decimal_encoder
import episodes_db
import logger
import schema

log = logger.get_logger("anime_by_id")

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
POST_SCHEMA_PATH = os.path.join(CURRENT_DIR, "post.json")


class Error(Exception):
    pass


class UnsupportedMethod(Error):
    pass


class HttpError(Error):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    method = event["requestContext"]["http"]["method"]
    anime_id = event["pathParameters"].get("id")

    if method == "POST":
        body = event.get("body")
        return _post(body)
    elif method == "GET":
        query_params = event.get("queryStringParameters")
        return _get(anime_id, query_params)
    else:
        raise UnsupportedMethod()


def _post(body):
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
        return {"statusCode": 400, "body": json.dumps(
            {"message": "Invalid post schema", "error": str(e)})}

    if body["api_name"] == "anidb":
        log.debug("Anidb episodes added during mal item post, getting ep")
        try:
            res = episodes_db.get_episode_by_api_id(body["api_name"],
                                                    int(body["api_id"]))
            return {"statusCode": 200,
                    "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
        except (episodes_db.NotFoundError, episodes_db.InvalidAmountOfEpisodes):
            return {"statusCode": 404}


def _get(anime_id, query_params):
    if "api_id" in query_params and "api_name" in query_params:
        api_id = query_params["api_id"]
        api_name = query_params["api_name"]
        return _get_episode_by_api_id(api_id, api_name)
    else:
        return _get_episodes(anime_id, query_params)


def _get_episode_by_api_id(api_id, api_name):
    if api_name in ["anidb"]:
        try:
            res = episodes_db.get_episode_by_api_id(api_name, int(api_id))
            return {"statusCode": 200,
                    "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
        except (episodes_db.NotFoundError, episodes_db.InvalidAmountOfEpisodes):
            return {"statusCode": 404}
    else:
        return {"statusCode": 400,
                "body": json.dumps({"error": "Unsupported api_name"})}


def _get_episodes(anime_id, query_params):
    limit = 100
    start = 1

    if query_params and "limit" in query_params:
        limit = query_params.get("limit")
    if query_params and "start" in query_params:
        start = query_params.get("start")

    try:
        limit = int(limit)
    except ValueError:
        return {"statusCode": 400,
                "body": json.dumps({"message": "Invalid limit type"})}
    try:
        start = int(start)
    except ValueError:
        return {"statusCode": 400,
                "body": json.dumps({"message": "Invalid start type"})}

    try:
        res = episodes_db.get_episodes(anime_id, limit=limit, start=start)
    except episodes_db.NotFoundError:
        log.debug(f"No episodes found for anime with id: {anime_id}")
        return {"statusCode": 404}
    except episodes_db.InvalidStartOffset:
        log.debug(f"Invalid start offset: {start}")
        return {"statusCode": 400,
                "body": json.dumps({"message": "Invalid offset"})}
    else:
        return {"statusCode": 200,
                "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
