import json

import anime_db
import decimal_encoder
import logger

log = logger.get_logger("anime_by_ids")


class HttpError(object):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    anime_ids = event["pathParameters"].get("ids")

    ids = anime_ids.split(",")
    if len(ids) > 20:
        return {"statusCode": 400, "body": json.dumps({"error": "Max allowed IDs to get is 20"})}

    res = anime_db.get_anime_by_ids(ids)
    return {"statusCode": 200, "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
