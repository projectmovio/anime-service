#!/usr/bin/env python3
from aws_cdk import core

from lib.anime import Anime
from lib.utils import clean_pycache

clean_pycache()

app = core.App()

env = {"region": "eu-west-1"}

Anime(app, "anime", env=env)

app.synth()
