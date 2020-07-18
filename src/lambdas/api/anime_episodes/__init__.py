import json

import decimal_encoder
import episodes_db
import logger

log = logger.get_logger("anime_by_id")


class HttpError(object):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    anime_id = event["pathParameters"].get("id")
    limit = 100
    start = 1

    query_params = event.get("queryStringParameters")
    if query_params and "limit" in query_params:
        limit = query_params.get("limit")
    if query_params and "start" in query_params:
        start = query_params.get("start")

    try:
        limit = int(limit)
    except ValueError:
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid limit type"})}
    try:
        start = int(start)
    except ValueError:
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid start type"})}

    try:
        res = episodes_db.get_episodes(anime_id, limit=limit, start=start)
    except episodes_db.NotFoundError:
        log.debug(f"No episodes found for anime with id: {anime_id}")
        return {"statusCode": 404}
    except episodes_db.InvalidStartOffset:
        log.debug(f"Invalid start offset: {start}")
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid offset"})}
    else:
        return {"statusCode": 200, "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
