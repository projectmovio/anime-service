import json

import episodes_db
import logger

log = logger.get_logger("get_anime")


class HttpError(object):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    anime_id = event["pathParameters"].get("anime_id")

    try:
        res = episodes_db.get_episodes(anime_id)
    except episodes_db.NotFoundError:
        log.debug(f"Anime with id: {anime_id} not found in episodes DB")
        return {"statusCode": 404}
    else:
        return {"statusCode": 200, "body": json.dumps(res)}
