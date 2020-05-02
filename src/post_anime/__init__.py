import json


import anime as anime_database
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
        ret = anime_database.get_anime(mal_id)
    except NotFoundError:
        pass
    else:
        return {
            "statusCode": 202,
            "body": json.dumps({"id": ret["id"]})
        }

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
