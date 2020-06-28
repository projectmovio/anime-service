import os

from aws_cdk import core
from aws_cdk.aws_lambda import LayerVersion, Code, Runtime

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LAYERS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "layers")


class Layers(core.Stack):

    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self._create_layers()

    def _create_layers(self):
        LayerVersion(
            self,
            "api",
            code=Code.from_asset(path=os.path.join(LAYERS_DIR, "api")),
            compatible_runtimes=[Runtime.PYTHON_3_8],
        )
