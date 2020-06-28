#!/usr/bin/env python3
from aws_cdk import core

from lib.lambdas import Lambdas
from lib.layers import Layers
from lib.utils import clean_pycache

clean_pycache()

app = core.App()

env = {"region": "eu-west-1"}

layers_stack = Layers(app, "anime-layers", env=env)
Lambdas(app, "anime-lambdas", layers_stack.layers, env=env)

app.synth()
