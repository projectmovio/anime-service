#!/usr/bin/env python3
from aws_cdk import core

from lib.lambdas import Lambdas
from lib.utils import clean_pycache

clean_pycache()

app = core.App()

env = {"region": "eu-west-1"}

Lambdas(app, "anime-lambdas", env=env)

app.synth()
