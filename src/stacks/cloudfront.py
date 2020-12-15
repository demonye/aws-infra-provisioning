from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_cloudfront as cf,
)

from . import ConfigStoreMixin


class CloudFrontStack(ConfigStoreMixin, core.Stack):
    """AWS Infrastructure Provisioning: CloudFront Stack"""

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """CloudFrontStack.__init__.
        Setup S3 bucket and CloudFront

        Parameters
        ----------
        scope :
            core.Construct
        construct_id :
            str

        Returns
        -------
        None

        """
        super().__init__(scope, construct_id, **kwargs)

        source_bucket = s3.Bucket(
            self, 'FrontendBucket',
            bucket_name=self.config.frontend_bucket_name,
            versioned=True,
            public_read_access=kwargs.get('public_read_access', True),
            removal_policy=core.RemovalPolicy.DESTROY,
        )

        source_config = cf.SourceConfiguration(
            s3_origin_source=cf.S3OriginConfig(s3_bucket_source=source_bucket),
            behaviors=[cf.Behavior(is_default_behavior=True)]
        )
        cf.CloudFrontWebDistribution(
            self, 'CloudFront',
            origin_configs=[source_config]
        )
