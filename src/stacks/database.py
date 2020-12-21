from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_rds as rds,
)

from . import ConfigStoreMixin


class DatabaseStack(ConfigStoreMixin, core.Stack):
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
            vpc=ec2.Vpc.from_lookup(self, 'Vpc', vpc_name='ECS/SimpleTodoVpc'),
            vpc_subnets={
                'subnet_type': ec2.SubnetType.PRIVATE
            }
        )
