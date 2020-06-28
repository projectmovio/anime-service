import os

from aws_cdk import core
from aws_cdk.aws_lambda import LayerVersion, Code, Runtime, Function

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LAMBDAS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "lambdas")


class Lambdas(core.Stack):

    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self._create_layers()
        self.layers = {}

    def _create_layers(self):
        for root, dirs, files in os.walk(LAMBDAS_DIR):
            for f in files:
                lambda_path = os.path.join(root, f)
                print(lambda_path)
            # for d in dirs:
            #
            #     if d == "__pycache__":
            #         continue
            #     lambda_path = os.path.join(root, d, "__init__.py")
            #     print(lambda_path)
            # Function(
            #     self,
            #
            # )
