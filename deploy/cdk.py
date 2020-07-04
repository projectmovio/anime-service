#!/usr/bin/env python3
from aws_cdk import core

from lib.dynamodb import DynamoDb
from lib.lambdas import Lambdas
from lib.sqs import SqS
from lib.utils import clean_pycache

clean_pycache()

app = core.App()

env = {"region": "eu-west-1"}

dynamodb = DynamoDb(app, "anime-dynmodbs", env=env)
sqs = SqS(app, "anime-sqs", env=env)

lambdas_config = {
    "ANIME_DATABASE_NAME": dynamodb.anime_table.table_name,
    "ANIME_EPISODES_DATABASE_NAME": dynamodb.anime_episodes.table_name,
    "ANIME_PARAMS_DATABASE_NAME": dynamodb.anime_params.table_name,
}
Lambdas(app, "anime-lambdas", lambdas_config, env=env)


app.synth()
