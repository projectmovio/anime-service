from aws_cdk import core
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode


class DynamoDb(core.Stack):

    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self._create_tables()

    def _create_tables(self):
        self.anime_table = Table(
            self,
            "anime",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )
        self.anime_table.add_global_secondary_index(
            partition_key=Attribute(name="mal_id", type=AttributeType.STRING),
            index_name="mal_id"
        )

        self.anime_episodes = Table(
            self,
            "anime_episodes",
            partition_key=Attribute(name="anime_id", type=AttributeType.STRING),
            sort_key=Attribute(name="id", type=AttributeType.NUMBER),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        self.anime_params = Table(
            self,
            "anime_params",
            partition_key=Attribute(name="name", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )
