import os

from aws_cdk import core
from aws_cdk.aws_lambda import LayerVersion, Code, Runtime, Function

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LAMBDAS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "lambdas")

LAMBDA_CONFIG = {
    "api-get_anime": {
        "layers": ["utils", "databases"],
    },
    "api-get_episodes": {
        "layers": ["utils", "databases"],
    },
    "api-post_anime": {
        "layers": ["utils", "databases"],
    },
    "api-search_anime": {
        "layers": ["utils", "databases", "api"],
    },
    "crons-titles_updater": {
        "layers": ["utils", "databases"],
    },
    "sqs_handlers-post_anime": {
        "layers": ["utils", "databases", "api"],
    }
}


class Lambdas(core.Stack):

    def __init__(self, app: core.App, id: str, layers: dict, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self.layers = layers
        self._create_lambdas()

    def _create_lambdas(self):
        for root, dirs, files in os.walk(LAMBDAS_DIR):
            for _ in files:
                parent_folder = os.path.basename(os.path.dirname(root))
                lambda_folder = os.path.basename(root)
                name = f"{parent_folder}-{lambda_folder}"

                layers = []
                for layer_name in LAMBDA_CONFIG[name]["layers"]:
                    layers.append(self.layers[layer_name])

                Function(
                    self,
                    name,
                    code=Code.from_asset(root),
                    handler="__init__",
                    runtime=Runtime.PYTHON_3_8,
                    layers=layers,
                    function_name=name
                )
