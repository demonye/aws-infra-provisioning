from aws_cdk import (
    core,
    aws_s3 as s3,
)


class S3Stack(core.Stack):
    """AWS Infrastructure Provisioning: S3 Stack"""

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """S3Stack.__init__.

        Parameters
        ----------
        scope : core.Construct
        construct_id : str

        Returns
        -------
        None

        """
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(
            self, construct_id,
            bucket_name=f'{construct_id}-bucket',
            versioned=True,
            public_read_access=kwargs.get('public_read_access', False),
            removal_policy=core.RemovalPolicy.DESTROY,
        )
