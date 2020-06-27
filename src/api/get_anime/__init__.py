import json

from mal import MalApi, NotFoundError
import anime_db
import logger

log = logger.get_logger("get_anime")


class HttpError(object):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    search = event["queryStringParameters"].get("search")
    mal_id = event["queryStringParameters"].get("mal_id")

    if search is None and mal_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify either 'search' or 'mal_id' query parameter"})
        }

    if mal_id:
        try:
            res = anime_db.get_anime(mal_id)
        except anime_db.NotFoundError:
            log.debug(f"Anime with mal_id: {mal_id} not found in DB, use API")
        else:
            return {"statusCode": 200, "body": json.dumps(res)}

        try:
            res = MalApi().get_anime(mal_id)
        except NotFoundError:
            return {"statusCode": 404}
        except HttpError:
            return {"statusCode": 500}
        else:
            return {"statusCode": 200, "body": json.dumps(res)}
    elif search:
        try:
            res = MalApi().search(search)
        except HttpError:
            return {"statusCode": 500}
        return {"statusCode": 200, "body": json.dumps(res)}
