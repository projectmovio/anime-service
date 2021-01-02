import json

import anime_db
import decimal_encoder
import logger

log = logger.get_logger("anime_by_id")


class HttpError(object):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    anime_id = event["pathParameters"].get("id")

    try:
        res = anime_db.get_anime_by_id(anime_id)
    except anime_db.NotFoundError:
        return {"statusCode": 404}

    return {"statusCode": 200, "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
