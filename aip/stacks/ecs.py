from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elbv2,
)

from . import BaseStack


class EcsStack(BaseStack):
    """AWS Infrastructure Provisioning: ECS Stack"""

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """RdsStack.__init__.

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

        vpc = ec2.Vpc(
            self, 'Vpc', cidr=self.config.vpc_cidr,
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name='Public',
                    cidr_mask=24,
                ), ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.ISOLATED,
                    name='Isolated',
                    cidr_mask=24,
                )
            ]
        )

        # Create an ECS cluster
        cluster = ecs.Cluster(
            self, 'Cluster', vpc=vpc,
            cluster_name=self.config.custer_name,
        )

        # Add capacity to it
        cluster.add_capacity(
            'DefaultAutoScalingGroup',
            instance_type=ec2.InstanceType("t2.micro"),
            desired_capacity=2,
            task_drain_time=core.Duration.seconds(300)
        )

        task_definition = ecs.FargateTaskDefinition(self, 'TaskDef')
        ecr_repo = ecr.Repository.from_repository_name(
            self, 'GetEcrRepo', repository_name=self.config.ecr_repo_name
        )
        task_definition.add_container(
            'APIContainer',
            image=ecs.ContainerImage.from_ecr_repository(ecr_repo, 'latest'),
            cpu=256,
            memory_limit_mib=512
        )

        # Instantiate an Amazon ECS Service
        service = ecs.FargateService(
            self, "Service",
            cluster=cluster,
            task_definition=task_definition
        )

        # FIXME Setup load balancer
        lb = elbv2.ApplicationLoadBalancer(self, 'LB', vpc=vpc, internet_facing=True)
        listener = lb.add_listener('Listener', port=8000)
        service.register_load_balancer_targets(
            container_name='web',
            container_port=8000,
            new_target_group_id='ECS',
            listener=ecs.ListenerConfig.application_listener(
                listener,
                protocol=elbv2.ApplicationProtocol.HTTPS
            )
        )
