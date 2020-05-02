import json

from get_anime import HttpError
from mal import MalApi, NotFoundError


def handle(event, context):
    print(f"Received event: {event}")

    mal_id = event["queryStringParameters"].get("mal_id")

    if mal_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify the 'mal_id' query parameter"})
        }

    mal_api = MalApi()

    try:
        mal_api.get_anime(mal_id)
    except NotFoundError:
        pass
        
    mal_data = {}
    if mal_id:
        try:
            mal_data = mal_api.get_anime(mal_id)
        except NotFoundError:
            return {"statusCode": 404}
        except HttpError:
            return {"statusCode": 500}

    if not mal_data:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"Mal data empty for mal_id: {mal_id}"})
        }



