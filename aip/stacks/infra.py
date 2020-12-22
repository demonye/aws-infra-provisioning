"""AWS Infrastructure Provisioning

What to provision?
    VPC and network setup
    ECS cluster with Fargate service and Load Balancer
    S3 buckets
    CloudFront
    ECR repository
    Deployment pipeline

"""

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
    aws_ecs_patterns as patterns,
    aws_cloudfront as cf,
    aws_cloudfront_origins as origins,

    aws_codecommit as cc,
    aws_codebuild as cb,
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
)

from . import BaseStack


class InfraStack(BaseStack):
    """AWS Infrastructure Provisioning Stack"""

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """InfraStack.__init__.

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
        # asg = self.setup_asg()

        # ECS Service
        self.cluster = self.setup_cluster()
        self.ecr_repo = self.setup_ecr()
        self.service = self.setup_service()

        # API pipeline
        self.api_source = self.setup_api_source()
        self.api_build_project = self.setup_api_build_project()
        self.setup_api_pipeline()

        # Web pipeline
        self.web_bucket = self.setup_web_bucket()
        self.web_source = self.setup_web_source()
        self.web_build_project = self.setup_web_build_project()
        self.setup_web_pipeline()

        # Others
        self.table = self.setup_db()
        self.distribution = self.setup_cloudfront()

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

        table = db.Table.from_table_name(self, 'Table', table_name=self.config.api.table_name)
        if not table:
            table = db.Table(
                self, 'Table', table_name=self.config.api.table_name,
                partition_key=db.Attribute(name='id', type=db.AttributeType.STRING)
            )
        self.service.task_definition.add_to_task_role_policy(iam.PolicyStatement(
            resources=[table.table_arn],
            actions=[
                "dynamodb:Scan",
                "dynamodb:Query",
                'dynamodb:GetItem',
                "dynamodb:PutItem",
                'dynamodb:UpdateItem',
                "dynamodb:DeleteItem",
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
            ],
            sid='AllowFargateAccessDynamoDB'
        ))
        return table

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

        return ecs.Cluster(
            self, 'Cluster', vpc=self.vpc,
            cluster_name=self.config.custer_name,
        )

    def setup_service(self):
        """Setup task definition"""

        service = patterns.ApplicationLoadBalancedFargateService(
            self, 'FargateService',
            cluster=self.cluster,            # Required
            cpu=256,                    # Default is 256
            memory_limit_mib=512,
            desired_count=2,            # Default is 1
            task_image_options=patterns.ApplicationLoadBalancedTaskImageOptions(
                container_name=self.config.api.ecr_repo,
                container_port=80,
                image=ecs.ContainerImage.from_ecr_repository(self.ecr_repo)),
            public_load_balancer=True
        )
        return service

    def setup_cloudfront(self):
        """Setup CloudFront
        / is pointing to S3
        /api is pointing to Load Balancer

        """

        return cf.Distribution(
            self, 'CloudFront',
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3Origin(self.web_bucket)),
            additional_behaviors={
                '/api/*': cf.BehaviorOptions(
                    origin=origins.LoadBalancerV2Origin(
                        self.service.load_balancer,
                        protocol_policy=cf.OriginProtocolPolicy.HTTP_ONLY,
                    ),
                    cache_policy=cf.CachePolicy.CACHING_DISABLED,
                    allowed_methods=cf.AllowedMethods.ALLOW_ALL,
                )
            }
        )

    def setup_ecr(self):
        """Get or create a ECR repository"""

        ecr_repo = ecr.Repository.from_repository_name(
            self, 'Repository', repository_name=self.config.api.ecr_repo
        )
        if not ecr_repo:
            # create ECR repository object if no existing one
            ecr_repo = ecr.Repository(
                self, 'Repository',
                repository_name=self.config.api.ecr_repo,
                image_scan_on_push=True,
            )
        return ecr_repo

    def setup_api_build_project(self):
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
            self, 'ApiBuild',
            environment={
                'build_image': cb.LinuxBuildImage.STANDARD_4_0,
                'privileged': True,
            },
            build_spec=cb.BuildSpec.from_object(dict(
                version=0.2,
                phases={
                    'install': {'commands': [
                        'pip install -r requirements_test.txt',
                        'pip install -U awscli',
                    ]},
                    'pre_build': {'commands': [
                        'coverage run --source=. -m unittest',
                        'coverage report -m',
                    ]},
                    'build': {'commands': [
                        f'docker build . -t {self.ecr_repo.repository_uri}:latest',
                    ]},
                    'post_build': {'commands': [
                        '$(aws ecr get-login --no-include-email)',
                        f'docker push {self.ecr_repo.repository_uri}:latest',
                        ''.join([
                            'printf \'[{',
                            f'"name": "{self.config.api.ecr_repo}",',
                            f'"imageUri": "{self.ecr_repo.repository_uri}:latest"',
                            '}]\' > imagedefinitions.json',
                        ]),
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

    def setup_api_source(self):
        """Get or create a CodeCommit repository

        Returns
        -------
        codecommit.Repository

        """

        source_repo = cc.Repository.from_repository_name(
            self, 'ApiCodeRepository',
            repository_name=self.config.api.source_repo
        )
        if not source_repo:
            # create ECR repository object if no existing one
            source_repo = cc.Repository(
                self, 'ApiCodeRepository',
                repository_name=self.config.api.ecr_repo,
            )
        return source_repo

    def setup_api_pipeline(self):
        """Setup the build pipeline.
        Using codepipeline to create a Pipeline
        including two stages:
            * Source: CodeCommitSourceAction
            * Build:  CodeBuildActioin
            * Deploy: Deploy to Fargate service

        Returns
        -------
        None
        """
        source_output = cp.Artifact()
        build_output = cp.Artifact(self.config.build_output)
        cp.Pipeline(
            self, 'ApiPipeline',
            pipeline_name=self.config.api.pipeline,
            stages=[
                cp.StageProps(
                    stage_name='Source',
                    actions=[
                        cp_actions.CodeCommitSourceAction(
                            action_name='Source',
                            repository=self.api_source,
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
                            project=self.api_build_project,
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
                            service=self.service.service,
                            input=build_output,
                            # image_file=build_output.at_path('imagedefinitions.json')
                        )
                    ]
                )
            ]
        )

    def setup_web_bucket(self):
        """Setup S3 bucket to host website"""

        return s3.Bucket(
            self, 'WebBucket',
            bucket_name=self.config.web.bucket_name,
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY,
            website_index_document='index.html',
        )

    def setup_web_source(self):
        """Setup source repo for WEB frontend

        Returns
        -------
        codecommit.Repository

        """

        name = 'WebSourceRepo'
        source_repo = cc.Repository.from_repository_name(
            self, name,
            repository_name=self.config.web.source_repo
        )
        if not source_repo:
            source_repo = cc.Repository(
                self, name,
                repository_name=self.config.web.source_repo
            )
        return source_repo

    def setup_web_build_project(self):
        """Setup build project for WEB frontend
        Using codebuild to create a PipelineProject
        including three phases:
            * install:   npm install
            * pre_build: run unit tests
            * build:     npm run build and setup artifacts

        Returns
        -------
        codepipeline.PipelineProject

        """

        return cb.PipelineProject(
            self, 'WebBuild',
            build_spec=cb.BuildSpec.from_object(dict(
                version=0.2,
                phases={
                    'install': {'commands': ['npm install']},
                    'pre_build': {'commands': ['npm run test:unit']},
                    'build': {'commands': [
                        'npm run build',
                        'COMMIT_HAHS=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION |cut -c 1-7)'
                        'echo ${COMMIT_HASH} > dist/version.txt',
                    ]}
                },
                artifacts={
                    'files': ['**/*'],
                    'base-directory': 'dist',
                    'name': "dist-${COMMIT_HASH}"
                }
            ))
        )

    def setup_web_pipeline(self):
        """Setup the build pipeline.
        Using codepipeline to create a Pipeline
        including two stages:
            * Source: CodeCommitSourceAction
            * Build : CodeBuildActioin
            * Deploy: S3DeployAction

        Returns
        -------
        codepipeline.Pipeline

        """

        source_output = cp.Artifact()
        build_output = cp.Artifact(self.config.web.build_output)
        cp.Pipeline(
            self, 'WebPipeline',
            pipeline_name=self.config.web.pipeline,
            stages=[
                cp.StageProps(
                    stage_name='Source',
                    actions=[
                        cp_actions.CodeCommitSourceAction(
                            action_name='Source',
                            repository=self.web_source,
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
                            project=self.web_build_project,
                            input=source_output,
                            outputs=[build_output]
                        )
                    ]
                ),
                cp.StageProps(
                    stage_name='Deploy',
                    actions=[
                        cp_actions.S3DeployAction(
                            action_name='Deploy',
                            bucket=self.web_bucket,
                            input=build_output,
                            access_control=s3.BucketAccessControl.PUBLIC_READ
                        )
                    ]
                )
            ]
        )
