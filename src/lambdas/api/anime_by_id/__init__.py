import json

import anime_db
import logger

log = logger.get_logger("anime_by_id")


class HttpError(object):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    anime_id = event["pathParameters"].get("id")

    try:
        res = anime_db.get_anime(anime_id)
    except anime_db.NotFoundError:
        log.debug(f"Anime with id: {anime_id} not found in DB")
        return {"statusCode": 404}
    else:
        return {"statusCode": 200, "body": json.dumps(res)}
