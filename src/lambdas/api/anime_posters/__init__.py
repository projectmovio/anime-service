import json

import anime_db
import decimal_encoder
import logger

log = logger.get_logger("anime_posters")


class HttpError(object):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    anime_ids = event["pathParameters"].get("ids")
    log.debug(f"IDs: {anime_ids}")

    res = anime_db.get_anime_posters(anime_ids.split(","))
    return {"statusCode": 200, "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
