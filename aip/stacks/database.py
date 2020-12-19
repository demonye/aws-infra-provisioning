from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_rds as rds,
)

from . import BaseStack


class DatabaseStack(BaseStack):
    """AWS Infrastructure Provisioning: RDS Stack"""

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """DatabaseStack.__init__.
        Create a database instance on RDS

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

        rds.DatabaseInstance(
            self, 'Database',
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0_21),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            vpc=ec2.Vpc.from_lookup(self, 'Vpc', vpc_name='SimpleTodoVpc'),
            vpc_subnets={
                'subnet_type': ec2.SubnetType.PRIVATE
            }
        )

        # source_bucket = s3.Bucket(
        #     self, 'FrontendBucket',
        #     bucket_name=self.config.frontend_bucket_name,
        #     versioned=True,
        #     public_read_access=kwargs.get('public_read_access', True),
        #     removal_policy=core.RemovalPolicy.DESTROY,
        # )
