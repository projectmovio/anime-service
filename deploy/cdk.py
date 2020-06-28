#!/usr/bin/env python3

from aws_cdk import core

from stacks.layers import Layers

app = core.App()

env = {"region": "eu-west-1"}

Layers(app, "layers", env=env)

app.synth()
