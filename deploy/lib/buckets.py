from aws_cdk import core
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess


class Buckets(core.Stack):

    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self._create_buckets()

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
