import os
import shutil
import subprocess

from aws_cdk import core
from aws_cdk.aws_lambda import LayerVersion, Code, Runtime, Function

from lib.utils import clean_pycache

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LAMBDAS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "lambdas")
LAYERS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "layers")
BUILD_FOLDER = os.path.join(CURRENT_DIR, "..", "..", "build")


class Lambdas(core.Stack):

    def __init__(self, app: core.App, id: str, config: dict, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self.config = config
        self.layers = {}
        self._create_lambdas_config()
        self._create_layers()
        self._create_lambdas()

    def _create_lambdas_config(self):
        self.lambdas_config = {
            "api-get_anime": {
                "layers": ["utils", "databases"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.config["ANIME_DATABASE_NAME"],
                },
                "concurrent_executions": 100
            },
            "api-get_episodes": {
                "layers": ["utils", "databases"],
                "variables": {
                    "ANIME_EPISODES_DATABASE_NAME": self.config["ANIME_EPISODES_DATABASE_NAME"],
                },
                "concurrent_executions": 100
            },
            "api-post_anime": {
                "layers": ["utils", "databases"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.config["ANIME_DATABASE_NAME"],
                    "POST_ANIME_SQS_QUEUE_URL": self.config["POST_ANIME_SQS_QUEUE_URL"],
                },
                "concurrent_executions": 100
            },
            "api-search_anime": {
                "layers": ["utils", "databases", "api"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.config["ANIME_DATABASE_NAME"],
                },
                "concurrent_executions": 100
            },
            "crons-titles_updater": {
                "layers": ["utils", "databases"],
                "variables": {},
                "concurrent_executions": 1
            },
            "sqs_handlers-post_anime": {
                "layers": ["utils", "databases", "api"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.config["ANIME_DATABASE_NAME"],
                    "ANIME_EPISODES_DATABASE_NAME": self.config["ANIME_EPISODES_DATABASE_NAME"],
                    "ANIME_PARAMS_DATABASE_NAME": self.config["ANIME_PARAMS_DATABASE_NAME"],
                },
                "concurrent_executions": 1
            },
        }

    def _create_layers(self):
        if os.path.isdir(BUILD_FOLDER):
            shutil.rmtree(BUILD_FOLDER)
        os.mkdir(BUILD_FOLDER)

        for layer in os.listdir(LAYERS_DIR):
            layer_folder = os.path.join(LAYERS_DIR, layer)
            build_folder = os.path.join(BUILD_FOLDER, layer)
            shutil.copytree(layer_folder, build_folder)

            requirements_path = os.path.join(build_folder, "requirements.txt")

            if os.path.isfile(requirements_path):
                packages_folder = os.path.join(build_folder, "python", "lib", "python3.8", "site-packages")
                print(f"Installing layer requirements to target: {os.path.abspath(packages_folder)}")
                subprocess.check_output(["pip", "install", "-r", requirements_path, "-t", packages_folder])
                clean_pycache()

            self.layers[layer] = LayerVersion(
                self,
                layer,
                code=Code.from_asset(path=build_folder),
                compatible_runtimes=[Runtime.PYTHON_3_8],
            )

    def _create_lambdas(self):
        clean_pycache()

        for root, dirs, files in os.walk(LAMBDAS_DIR):
            for _ in files:
                parent_folder = os.path.basename(os.path.dirname(root))
                lambda_folder = os.path.basename(root)
                name = f"{parent_folder}-{lambda_folder}"

                layers = []
                for layer_name in self.lambdas_config[name]["layers"]:
                    layers.append(self.layers[layer_name])

                Function(
                    self,
                    name,
                    code=Code.from_asset(root),
                    handler="__init__",
                    runtime=Runtime.PYTHON_3_8,
                    layers=layers,
                    function_name=name,
                    environment=self.lambdas_config[name]["variables"],
                    reserved_concurrent_executions=self.lambdas_config[name]["concurrent_executions"]
                )
