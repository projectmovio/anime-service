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
    if query_params:
        limit = query_params.get("limit")
        start = query_params.get("start")

    try:
        res = episodes_db.get_episodes(anime_id, limit=limit, start=start)
    except episodes_db.NotFoundError:
        log.debug(f"No episodes found for anime with id: {anime_id}")
        return {"statusCode": 404}
    else:
        return {"statusCode": 200, "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
