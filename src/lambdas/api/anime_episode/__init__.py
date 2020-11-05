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
    episode_id = event["pathParameters"].get("episode_id")

    try:
        res = episodes_db.get_episode(anime_id, episode_id)
    except episodes_db.NotFoundError:
        log.debug(f"No episodes found for anime with id: {anime_id}")
        return {"statusCode": 404}
    except episodes_db.InvalidAmountOfEpisodes:
        return {"statusCode": 500}
    else:
        return {"statusCode": 200, "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
