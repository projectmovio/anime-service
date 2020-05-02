import json

from get_anime import HttpError
from mal import MalApi, NotFoundError


def handle(event, context):
    print(f"Received event: {event}")

    mid = event["queryStringParameters"].get("mid")

    if mid is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify the 'mid' query parameter"})
        }

    mal_api = MalApi()

    mal_data = {}
    if mid:
        try:
            mal_data = mal_api.get_anime(mid)
        except NotFoundError:
            return {"statusCode": 404}
        except HttpError:
            return {"statusCode": 500}

    if not mal_data:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"Mal data empty for MID: {mid}"})
        }



