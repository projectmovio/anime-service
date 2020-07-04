import os
import shutil
import subprocess

from aws_cdk import core
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement
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
        self.lambdas = {}
        self._create_lambdas_config()
        self._create_layers()
        self._create_lambdas()

    def _create_lambdas_config(self):
        self.lambdas_config = {
            "api-anime_by_id": {
                "layers": ["utils", "databases"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.config["anime_database_name"],
                },
                "concurrent_executions": 100,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[self.config["anime_database_arn"]]
                    )
                ]
            },
            "api-anime_episodes": {
                "layers": ["utils", "databases"],
                "variables": {
                    "ANIME_EPISODES_DATABASE_NAME": self.config["anime_episodes_database_name"],
                },
                "concurrent_executions": 100,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[self.config["anime_episodes_database_arn"]]
                    )
                ]
            },
            "api-anime": {
                "layers": ["utils", "databases"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.config["anime_database_name"],
                    "POST_ANIME_SQS_QUEUE_URL": self.config["post_anime_sqs_queue_url"],
                },
                "concurrent_executions": 100,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[self.config["anime_database_arn"]]
                    ),
                    PolicyStatement(
                        actions=["sqs:SendMessage"],
                        resources=[self.config["post_anime_sqs_queue_arn"]]
                    ),
                ]
            },
            "api-search_anime": {
                "layers": ["utils", "databases", "api"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.config["anime_database_name"],
                },
                "concurrent_executions": 100,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[self.config["anime_database_arn"]]
                    )
                ]
            },
            "crons-titles_updater": {
                "layers": ["utils", "databases"],
                "variables": {},
                "concurrent_executions": 1,
                "policies": [
                    PolicyStatement(
                        actions=["s3:GetItem", "s3:PutItem"],
                        resources=[self.config["anidb_titles_bucket_objects_arn"]]
                    )
                ]
            },
            "sqs_handlers-anime": {
                "layers": ["utils", "databases", "api"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.config["anime_database_name"],
                    "ANIME_EPISODES_DATABASE_NAME": self.config["anime_episodes_database_name"],
                    "ANIME_PARAMS_DATABASE_NAME": self.config["anime_params_database_name"],
                },
                "concurrent_executions": 1,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[self.config["anime_database_arn"]]
                    ),
                    PolicyStatement(
                        actions=["dynamodb:UpdateItem"],
                        resources=[self.config["anime_episodes_database_arn"]]
                    ),
                    PolicyStatement(
                        actions=["dynamodb:UpdateItem"],
                        resources=[self.config["anime_params_database_arn"]]
                    )
                ]
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
                lambda_config = self.lambdas_config[name]

                layers = []
                for layer_name in lambda_config["layers"]:
                    layers.append(self.layers[layer_name])

                lambda_role = Role(
                    self,
                    f"{name}_role",
                    assumed_by=ServicePrincipal(service="lambda.amazonaws.com")
                )
                for policy in lambda_config["policies"]:
                    lambda_role.add_to_policy(policy)

                self.lambdas[name] = Function(
                    self,
                    name,
                    code=Code.from_asset(root),
                    handler="__init__",
                    runtime=Runtime.PYTHON_3_8,
                    layers=layers,
                    function_name=name,
                    environment=lambda_config["variables"],
                    reserved_concurrent_executions=lambda_config["concurrent_executions"],
                    role=lambda_role,
                )
