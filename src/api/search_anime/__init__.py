import json

import mal
import anime_db
import logger

log = logger.get_logger("search_anime")


def handle(event, context):
    log.debug(f"Received event: {event}")

    search = event["queryStringParameters"].get("search")
    mal_id = event["queryStringParameters"].get("mal_id")

    if search is None and mal_id is None:
        return {
            "statusCode": 400,
            "body": {"error": "Please specify either 'search' or 'mal_id' query parameter"}
        }

    if mal_id:
        try:
            res = anime_db.get_anime_by_mal_id(mal_id)
        except anime_db.NotFoundError:
            log.debug(f"Anime with mal_id: {mal_id} not found in DB, use API")
        else:
            return {"statusCode": 200, "body": res}

        try:
            res = mal.MalApi().get_anime(mal_id)
        except mal.NotFoundError:
            return {"statusCode": 404}
        except mal.HTTPError:
            return {"statusCode": 500}
        else:
            return {"statusCode": 200, "body": res}
    elif search:
        try:
            res = mal.MalApi().search(search)
        except mal.HTTPError:
            return {"statusCode": 500}
        return {"statusCode": 200, "body": res}
