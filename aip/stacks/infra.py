from aws_cdk import (
    core,

    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_ecr as ecr,
    aws_iam as iam,

    aws_ecs as ecs,
    aws_dynamodb as db,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    aws_ecs_patterns as patterns,
    aws_cloudfront as cf,

    aws_codecommit as cc,
    aws_codebuild as cb,
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
)

from . import BaseStack


class InfraStack(BaseStack):
    """AWS Infrastructure Provisioning: VPC, network, Database, Cluster and Load Balancer"""

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """RdsStack.__init__.

        Parameters
        ----------
        scope : core.Construct
        construct_id : str

        Returns
        -------
        None

        """
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = self.setup_vpc()
        self.setup_db()
        # asg = self.setup_asg()

        cluster = self.setup_cluster()
        ecr_repo = self.setup_ecr()
        service = self.setup_service(cluster, ecr_repo)
        # self.setup_lb(service)

        source_repo = self.setup_source_repo()
        build_project = self.setup_build_project(ecr_repo)
        self.setup_pipeline(source_repo, build_project, service)

        # elbv2.ApplicationLoadBalancer.from_lookup(self, 'LB')

    def setup_vpc(self):
        """Setup VPC and network"""

        return ec2.Vpc(
            self, 'Vpc', cidr=self.config.vpc_cidr,
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name='Public',
                    cidr_mask=24,
                ), ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE,
                    name='Application',
                    cidr_mask=24,
                )
            ]
        )

    def setup_db(self):
        """Setup DynamoDB database"""

        table = db.Table.from_table_name(self, 'Table', table_name='cdkdemo')
        if not table:
            table = db.Table(
                self, 'Table', table_name='cdkdemo',
                partition_key=db.Attribute(name='id', type=db.AttributeType.STRING)
            )
        return table
        # return rds.DatabaseInstance(
        #     self, 'Database',
        #     engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0_21),
        #     instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
        #     vpc=self.vpc,
        #     vpc_subnets={
        #         'subnet_type': ec2.SubnetType.PRIVATE
        #     }
        # )

    def setup_asg(self):
        """Setup the auto scaling group"""

        return autoscaling.AutoScalingGroup(
            self, 'ASG', vpc=self.vpc,
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            # task_drain_time=core.Duration.seconds(300)
            desired_capacity=2
        )

    def setup_cluster(self):
        """Setup ECS cluster"""

        cluster = ecs.Cluster(
            self, 'Cluster', vpc=self.vpc,
            cluster_name=self.config.custer_name,
        )
        # cluster.add_auto_scaling_group(asg)
        # Add capacity to it
        # cluster.add_capacity(
        #     'DefaultAutoScalingGroup',
        #     instance_type=ec2.InstanceType("t2.micro"),
        #     desired_capacity=2,
        #     task_drain_time=core.Duration.seconds(300)
        # )
        return cluster

    def setup_lb(self, service):
        """Setup load balancer"""

        load_balancer = elbv2.ApplicationLoadBalancer(
            self, 'LB',
            vpc=self.vpc, internet_facing=True
        )
        listener = load_balancer.add_listener('Listener', port=80)
        listener.add_targets(
            'ApplicationFleet', port=8000,
            targets=[service]
            # targets=[targets.IpTarget('10.20.2.0/24')]
            # targets=[asg]
        )
        return load_balancer

    def setup_service(self, cluster, ecr_repo):
        """Setup task definition"""

        return patterns.ApplicationLoadBalancedFargateService(
            self, 'FargateService',
            cluster=cluster,            # Required
            cpu=256,                    # Default is 256
            memory_limit_mib=512,
            desired_count=2,            # Default is 1
            task_image_options=patterns.ApplicationLoadBalancedTaskImageOptions(
                container_name=self.config.ecr_repo_name,
                container_port=8000,
                image=ecs.ContainerImage.from_ecr_repository(ecr_repo)),
            public_load_balancer=True
        )

    def setup_ecr(self):
        """Get or create a ECR repository"""

        ecr_repo = ecr.Repository.from_repository_name(
            self, 'Repository', repository_name=self.config.ecr_repo_name
        )
        if not ecr_repo:
            # create ECR repository object if no existing one
            ecr_repo = ecr.Repository(
                self, 'Repository',
                repository_name=self.config.ecr_repo_name,
                image_scan_on_push=True,
            )
        return ecr_repo

    def setup_build_project(self, ecr_repo):
        """Setup the build project.
        Using codebuild to create a PipelineProject
        including four phases:
            * install:    Instaall requirements for unit test
            * pre_build:  kRun tests and login into aws ecr
            * build:      Build and tag docker image
            * post_build: push image to ECR

        Parameters
        ----------
        None

        Returns
        -------
        PipelineProject object to be used in Pipeline

        """
        project = cb.PipelineProject(
            self, 'Build',
            environment={
                'build_image': cb.LinuxBuildImage.STANDARD_4_0,
                'privileged': True,
            },
            build_spec=cb.BuildSpec.from_object(dict(
                version=0.2,
                phases={
                    'install': {'commands': [
                        'pip install -r requirements_test.txt'
                    ]},
                    'pre_build': {'commands': [
                        'coverage run --source=. -m unittest',
                        'coverage report -m',
                    ]},
                    'build': {'commands': [
                        f'docker build . -t {ecr_repo.repository_uri}:latest',
                    ]},
                    'post_build': {'commands': [
                        '$(aws ecr get-login --no-include-email)',
                        f'docker push {ecr_repo.repository_uri}:latest',
                        f'printf \'[{{"name": "{self.config.ecr_repo_name}", "imageUri": "{ecr_repo.repository_uri}:latest"}}]\' > imagedefinitions.json',
                        'cat imagedefinitions.json',
                    ]},
                },
                artifacts={
                    'files': 'imagedefinitions.json'
                }
            ))
        )
        project.role.add_to_policy(iam.PolicyStatement(
            resources=['*'],
            actions=[
                'ecr:GetAuthorizationToken',
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:BatchCheckLayerAvailability",
                'ecr:PutImage',
            ],
            sid='AllowECRLoginAndPush'
        ))
        return project

    def setup_source_repo(self):
        """Get or create a CodeCommit repository"""
        source_repo = cc.Repository.from_repository_name(
            self, 'CodeRepository',
            repository_name=self.config.source_repo
        )
        if not source_repo:
            # create ECR repository object if no existing one
            source_repo = cc.Repository(
                self, 'CodeRepository',
                repository_name=self.config.ecr_repo_name,
            )
        return source_repo

    def setup_pipeline(self, source_repo, build_project, service):
        """Setup the build pipeline.
        Using codepipeline to create a Pipeline
        including two stages:
            * Source: CodeCommitSourceAction
            * Build:  CodeBuildActioin
            * Deploy: Deploy to Fargate service

        Parameters
        ----------
        build_object : PipelineProject
            The object returned from self.setup_build_project

        Returns
        -------
        None
        """
        source_output = cp.Artifact()
        build_output = cp.Artifact(self.config.build_output)
        cp.Pipeline(
            self, 'Pipeline',
            pipeline_name=self.config.pipeline,
            stages=[
                cp.StageProps(
                    stage_name='Source',
                    actions=[
                        cp_actions.CodeCommitSourceAction(
                            action_name='Source',
                            repository=source_repo,
                            branch='master',
                            output=source_output,
                        )
                    ]
                ),
                cp.StageProps(
                    stage_name='Build',
                    actions=[
                        cp_actions.CodeBuildAction(
                            action_name='Build',
                            project=build_project,
                            input=source_output,
                            outputs=[build_output]
                        )
                    ]
                ),
                cp.StageProps(
                    stage_name='Deploy',
                    actions=[
                        cp_actions.EcsDeployAction(
                            action_name='Deploy',
                            service=service.service,
                            input=build_output,
                            # image_file=build_output.at_path('imagedefinitions.json')
                        )
                    ]
                )
            ]
        )
