from aws_cdk import (
    core,
    aws_s3 as s3
)


class AipStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        bucket = s3.Bucket(self,
            "MyFirstBucket",
            versioned=True,
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
