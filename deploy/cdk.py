#!/usr/bin/env python3
from aws_cdk import core

from lib.buckets import Buckets
from lib.dynamodb import DynamoDb
from lib.lambdas import Lambdas
from lib.sqs import SqS
from lib.utils import clean_pycache

clean_pycache()

app = core.App()

env = {"region": "eu-west-1"}

dynamodb = DynamoDb(app, "anime-dynmodbs", env=env)
sqs = SqS(app, "anime-sqs", env=env)
buckets = Buckets(app, "anime-buckets", env=env)

lambdas_config = {
    "anime_database_name": dynamodb.anime_table.table_name,
    "anime_database_arn": dynamodb.anime_table.table_arn,
    "anime_episodes_database_name": dynamodb.anime_episodes.table_name,
    "anime_episodes_database_arn": dynamodb.anime_episodes.table_arn,
    "anime_params_database_name": dynamodb.anime_params.table_name,
    "anime_params_database_arn": dynamodb.anime_params.table_arn,
    "post_anime_sqs_queue_url": sqs.post_anime_queue.queue_url,
    "post_anime_sqs_queue_arn": sqs.post_anime_queue.queue_arn,
    "anidb_titles_bucket_arn": buckets.anidb_titles_bucket.bucket_arn,
    "anidb_titles_bucket_objects_arn": buckets.anidb_titles_bucket.arn_for_objects("*"),
}
Lambdas(app, "anime-lambdas", lambdas_config, env=env)

app.synth()
