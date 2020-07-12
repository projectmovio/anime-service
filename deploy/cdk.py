#!/usr/bin/env python3
import os

from aws_cdk import core

from lib.anime import Anime
from lib.utils import clean_pycache

clean_pycache()

app = core.App()

env = {"region": "eu-west-1"}

mal_client_id = os.getenv("MAL_CLIENT_ID")
if mal_client_id is None:
    raise RuntimeError("Please set the MAL_CLIENT_ID environment variable")

anidb_client = os.getenv("ANIDB_CLIENT")
if mal_client_id is None:
    raise RuntimeError("Please set the ANIDB_CLIENT environment variable")


Anime(app, "anime", mal_client_id, anidb_client, env=env)

app.synth()
