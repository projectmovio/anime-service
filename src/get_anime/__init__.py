import json

from mal import MalApi


def handle(event, context):
    print(f"Received event: {event}")

    if "queryStringParameters" not in event:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify either 'search' or 'mid' query parameter"})
        }

    mal_api = MalApi()
    search = event["queryStringParameters"].get("search")
    mid = event["queryStringParameters"].get("mid")

    if mid:
        res = mal_api.get_anime(mid)
        return {
            "statusCode": 200,
            "body": json.dumps(res)
        }
    elif search:
        res = mal_api.search(search)
        return {
            "statusCode": 200,
            "body": json.dumps(res)
        }
