import json

from mal import MalApi, NotFoundError


class HttpError(object):
    pass


def handle(event, context):
    print(f"Received event: {event}")

    search = event["queryStringParameters"].get("search")
    mal_id = event["queryStringParameters"].get("mal_id")

    if search is None and mal_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify either 'search' or 'mal_id' query parameter"})
        }

    mal_api = MalApi()
    if mal_id:
        try:
            res = mal_api.get_anime(mal_id)
        except NotFoundError:
            return {"statusCode": 404}
        except HttpError:
            return {"statusCode": 500}
        return {"statusCode": 200, "body": json.dumps(res)}
    elif search:
        try:
            res = mal_api.search(search)
        except HttpError:
            return {"statusCode": 500}
        return {"statusCode": 200, "body": json.dumps(res)}
