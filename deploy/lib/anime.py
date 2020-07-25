import os
import shutil
import subprocess

from aws_cdk import core
from aws_cdk.aws_apigateway import DomainName
from aws_cdk.aws_apigatewayv2 import HttpApi, HttpMethod, CfnAuthorizer, CfnRoute, \
    HttpIntegration, HttpIntegrationType, PayloadFormatVersion, CfnStage, DefaultDomainMappingOptions, HttpApiMapping
from aws_cdk.aws_certificatemanager import Certificate, ValidationMethod
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement, ManagedPolicy
from aws_cdk.aws_lambda import LayerVersion, Code, Runtime, Function
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess
from aws_cdk.aws_sqs import Queue, DeadLetterQueue
from aws_cdk.core import Duration

from lib.utils import clean_pycache

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LAMBDAS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "lambdas")
LAYERS_DIR = os.path.join(CURRENT_DIR, "..", "..", "src", "layers")
BUILD_FOLDER = os.path.join(CURRENT_DIR, "..", "..", "build")


class Anime(core.Stack):

    def __init__(self, app: core.App, id: str, mal_client_id: str, anidb_client: str, domain_name: str,
                 **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self.mal_client_id = mal_client_id
        self.anidb_client = anidb_client
        self.domain_name = domain_name
        self.layers = {}
        self.lambdas = {}
        self._create_buckets()
        self._create_tables()
        self._create_queues()
        self._create_lambdas_config()
        self._create_layers()
        self._create_lambdas()
        self._create_gateway()

    def _create_buckets(self):
        self.anidb_titles_bucket = Bucket(
            self,
            "anidb_titles_bucket",
            block_public_access=BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
            ),
            removal_policy=core.RemovalPolicy.DESTROY,
        )

    def _create_tables(self):
        self.anime_table = Table(
            self,
            "anime_items",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )
        self.anime_table.add_global_secondary_index(
            partition_key=Attribute(name="mal_id", type=AttributeType.NUMBER),
            index_name="mal_id"
        )

        self.anime_episodes = Table(
            self,
            "anime_episodes",
            partition_key=Attribute(name="anime_id", type=AttributeType.STRING),
            sort_key=Attribute(name="episode_number", type=AttributeType.NUMBER),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        self.anime_params = Table(
            self,
            "anime_params",
            partition_key=Attribute(name="name", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

    def _create_queues(self):
        post_anime_dl = Queue(self, "post_anime_dl")
        self.post_anime_queue = Queue(
            self,
            "anime",
            dead_letter_queue=DeadLetterQueue(max_receive_count=5, queue=post_anime_dl),
            receive_message_wait_time=Duration.seconds(10)
        )

    def _create_lambdas_config(self):
        self.lambdas_config = {
            "api-anime_by_id": {
                "layers": ["utils", "databases"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.anime_table.table_name,
                    "LOG_LEVEL": "INFO",
                },
                "concurrent_executions": 100,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:GetItem"],
                        resources=[self.anime_table.table_arn]
                    )
                ],
                "timeout": 3
            },
            "api-anime_episodes": {
                "layers": ["utils", "databases"],
                "variables": {
                    "ANIME_EPISODES_DATABASE_NAME": self.anime_episodes.table_name,
                    "LOG_LEVEL": "INFO",
                },
                "concurrent_executions": 100,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[self.anime_episodes.table_arn]
                    )
                ],
                "timeout": 3
            },
            "api-anime": {
                "layers": ["utils", "databases", "api"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.anime_table.table_name,
                    "POST_ANIME_SQS_QUEUE_URL": self.post_anime_queue.queue_url,
                    "MAL_CLIENT_ID": self.mal_client_id,
                    "LOG_LEVEL": "INFO",
                },
                "concurrent_executions": 100,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[f"{self.anime_table.table_arn}/index/mal_id"]
                    ),
                    PolicyStatement(
                        actions=["sqs:SendMessage"],
                        resources=[self.post_anime_queue.queue_arn]
                    ),
                ],
                "timeout": 10
            },
            "crons-titles_updater": {
                "layers": ["utils", "databases", "api"],
                "variables": {
                    "ANIDB_TITLES_BUCKET": self.anidb_titles_bucket.bucket_name,
                    "LOG_LEVEL": "INFO",
                },
                "concurrent_executions": 1,
                "policies": [
                    PolicyStatement(
                        actions=["s3:ListBucket"],
                        resources=[self.anidb_titles_bucket.bucket_arn]
                    ),
                    PolicyStatement(
                        actions=["s3:GetObject", "s3:PutObject"],
                        resources=[self.anidb_titles_bucket.arn_for_objects("*")]
                    )
                ],
                "timeout": 120
            },
            "sqs_handlers-post_anime": {
                "layers": ["utils", "databases", "api"],
                "variables": {
                    "ANIME_DATABASE_NAME": self.anime_table.table_name,
                    "ANIME_EPISODES_DATABASE_NAME": self.anime_episodes.table_name,
                    "ANIME_PARAMS_DATABASE_NAME": self.anime_params.table_name,
                    "MAL_CLIENT_ID": self.mal_client_id,
                    "ANIDB_TITLES_BUCKET": self.anidb_titles_bucket.bucket_name,
                    "ANIDB_CLIENT": self.anidb_client,
                    "LOG_LEVEL": "INFO",
                },
                "concurrent_executions": 1,
                "policies": [
                    PolicyStatement(
                        actions=["dynamodb:Query"],
                        resources=[f"{self.anime_table.table_arn}/index/mal_id"]
                    ),
                    PolicyStatement(
                        actions=["dynamodb:UpdateItem"],
                        resources=[self.anime_table.table_arn]
                    ),
                    PolicyStatement(
                        actions=["dynamodb:BatchWriteItem"],
                        resources=[self.anime_episodes.table_arn]
                    ),
                    PolicyStatement(
                        actions=["dynamodb:UpdateItem", "dynamodb:GetItem"],
                        resources=[self.anime_params.table_arn]
                    ),
                    PolicyStatement(
                        actions=["s3:ListBucket"],
                        resources=[self.anidb_titles_bucket.bucket_arn]
                    ),
                    PolicyStatement(
                        actions=["s3:GetObject"],
                        resources=[self.anidb_titles_bucket.arn_for_objects("*")]
                    )
                ],
                "timeout": 15
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
                lambda_role.add_managed_policy(
                    ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))

                self.lambdas[name] = Function(
                    self,
                    name,
                    code=Code.from_asset(root),
                    handler="__init__.handle",
                    runtime=Runtime.PYTHON_3_8,
                    layers=layers,
                    function_name=name,
                    environment=lambda_config["variables"],
                    reserved_concurrent_executions=lambda_config["concurrent_executions"],
                    role=lambda_role,
                    timeout=Duration.seconds(lambda_config["timeout"])
                )

        self.lambdas["sqs_handlers-post_anime"].add_event_source(SqsEventSource(self.post_anime_queue))

        Rule(
            self,
            "titles_updater",
            schedule=Schedule.cron(hour="2", minute="10"),
            targets=[LambdaFunction(self.lambdas["crons-titles_updater"])]
        )

    def _create_gateway(self):
        cert = Certificate(
            self,
            "certificate",
            domain_name=self.domain_name,
            validation_method=ValidationMethod.DNS
        )
        domain_name = DomainName(
            self,
            "domain",
            domain_name=self.domain_name,
            certificate=cert
        )

        http_api = HttpApi(
            self,
            "anime",
            create_default_stage=False,
        )

        authorizer = CfnAuthorizer(
            self,
            "cognito",
            api_id=http_api.http_api_id,
            authorizer_type="JWT",
            identity_source=["$request.header.Authorization"],
            name="cognito",
            jwt_configuration=CfnAuthorizer.JWTConfigurationProperty(
                audience=["2uqacp9st5av58h7kfhcq1eoa6"],
                issuer="https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_sJ3Y4kSv6"
            )
        )

        routes = {
            "get_anime": {
                "method": "GET",
                "route": "/anime",
                "target_lambda": self.lambdas["api-anime"]
            },
            "post_anime": {
                "method": "POST",
                "route": "/anime",
                "target_lambda": self.lambdas["api-anime"]
            },
            "get_anime_by_id": {
                "method": "GET",
                "route": "/anime/{id}",
                "target_lambda": self.lambdas["api-anime_by_id"]
            },
            "get_anime_episodes": {
                "method": "GET",
                "route": "/anime/{id}/episodes",
                "target_lambda": self.lambdas["api-anime_episodes"]
            }
        }

        for r in routes:
            integration = HttpIntegration(
                self,
                f"{r}_integration",
                http_api=http_api,
                integration_type=HttpIntegrationType.LAMBDA_PROXY,
                integration_uri=routes[r]["target_lambda"].function_arn,
                method=getattr(HttpMethod, routes[r]["method"]),
                payload_format_version=PayloadFormatVersion.VERSION_2_0,
            )
            CfnRoute(
                self,
                r,
                api_id=http_api.http_api_id,
                route_key=f"{routes[r]['method']} {routes[r]['route']}",
                authorization_type="JWT",
                authorizer_id=authorizer.ref,
                target="integrations/" + integration.integration_id
            )

            routes[r]["target_lambda"].add_permission(
                f"{r}_apigateway_invoke",
                principal=ServicePrincipal("apigateway.amazonaws.com"),
                source_arn=f"arn:aws:execute-api:{self.region}:{self.account}:{http_api.http_api_id}/*"
            )

        stage = CfnStage(
            self,
            "v1",
            api_id=http_api.http_api_id,
            auto_deploy=True,
            default_route_settings=CfnStage.RouteSettingsProperty(
                throttling_burst_limit=1,
                throttling_rate_limit=1
            ),
            stage_name="live"
        )

        HttpApiMapping(
            self,
            "mapping",
            api=http_api,
            domain_name=domain_name,
            stage=stage
        )
