import json

from mal import MalApi, NotFoundError


class HttpError(object):
    pass


def handle(event, context):
    print(f"Received event: {event}")

    search = event["queryStringParameters"].get("search")
    mid = event["queryStringParameters"].get("mid")

    if search is None and mid is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify either 'search' or 'mid' query parameter"})
        }

    mal_api = MalApi()
    if mid:
        try:
            res = mal_api.get_anime(mid)
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
