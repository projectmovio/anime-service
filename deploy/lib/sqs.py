from aws_cdk import core
from aws_cdk.aws_sqs import Queue, DeadLetterQueue


class SqS(core.Stack):

    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        self._create_queues()

    def _create_queues(self):
        post_anime_dl = Queue(self, "post_anime_dl")
        self.post_anime_queue = Queue(
            self,
            "anime",
            dead_letter_queue=DeadLetterQueue(max_receive_count=5, queue=post_anime_dl)
        )
