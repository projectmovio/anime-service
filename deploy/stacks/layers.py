from aws_cdk import core


class Layers(core.Stack):

    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
