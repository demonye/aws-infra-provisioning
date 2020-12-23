import unittest

from aws_cdk import core
from aip.stacks import InfraStack


class TestInstallRequires(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = core.App()
        cls.stack = InfraStack(cls.app, 'AipTestStack')

    def test_vpc_setup(self):
        self.assertEqual(str(type(self.stack.vpc)), "<class 'aws_cdk.aws_ec2.Vpc'>")
        self.assertEqual(self.stack.vpc.to_string(), 'AipTestStack/Vpc')
        self.assertEqual(len(self.stack.vpc.availability_zones), 2)

        self.assertEqual(len(self.stack.vpc.public_subnets), 2)
        self.assertEqual(self.stack.vpc.public_subnets[0].ipv4_cidr_block, '10.20.0.0/24')
        self.assertEqual(self.stack.vpc.public_subnets[1].ipv4_cidr_block, '10.20.1.0/24')

        self.assertEqual(len(self.stack.vpc.private_subnets), 2)
        self.assertEqual(self.stack.vpc.private_subnets[0].ipv4_cidr_block, '10.20.2.0/24')
        self.assertEqual(self.stack.vpc.private_subnets[1].ipv4_cidr_block, '10.20.3.0/24')

        self.assertEqual(len(self.stack.vpc.isolated_subnets), 0)

    def test_cluster_setup(self):
        self.assertEqual(str(type(self.stack.cluster)), "<class 'aws_cdk.aws_ecs.Cluster'>")
        self.assertEqual(self.stack.cluster.to_string(), 'AipTestStack/Cluster')
        self.assertEqual(self.stack.cluster.vpc, self.stack.vpc)

    def test_ecr_repo_setup(self):
        self.assertEqual(str(type(self.stack.ecr_repo)), "<class 'aws_cdk.aws_ecr._RepositoryBaseProxy'>")
        self.assertEqual(self.stack.ecr_repo.to_string(), 'AipTestStack/Repository')
        self.assertEqual(self.stack.ecr_repo.repository_name, self.stack.config.api.ecr_repo)
        repo_uri = '{}.dkr.ecr.{}.${{Token[AWS.URLSuffix.1]}}/{}'.format(
            self.stack.config.account_id,
            self.stack.config.region_name,
            self.stack.config.api.ecr_repo
        )
        self.assertEqual(self.stack.ecr_repo.repository_uri, repo_uri)

    def test_service_setup(self):
        self.assertEqual(
            str(type(self.stack.service)),
            "<class 'aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService'>"
        )
        self.assertEqual(
            self.stack.service.to_string(), 'AipTestStack/FargateService'
        )
        self.assertEqual(
            str(type(self.stack.service.service)),
            "<class 'aws_cdk.aws_ecs.FargateService'>"
        )
        self.assertEqual(
            str(type(self.stack.service.load_balancer)),
            "<class 'aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer'>"
        )
        self.assertEqual(
            str(type(self.stack.service.task_definition)),
            "<class 'aws_cdk.aws_ecs.FargateTaskDefinition'>"
        )
        self.assertEqual(
            str(type(self.stack.service.listener)),
            "<class 'aws_cdk.aws_elasticloadbalancingv2.ApplicationListener'>"
        )
        self.assertEqual(
            str(type(self.stack.service.target_group)),
            "<class 'aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup'>"
        )

        self.assertEqual(self.stack.service.desired_count, 2)
        self.assertFalse(self.stack.service.assign_public_ip)

    def test_task_definition_setup(self):
        self.assertEqual(
            self.stack.service.task_definition.to_string(),
            'AipTestStack/FargateService/TaskDef'
        )
        self.assertEqual(
            self.stack.service.task_definition.default_container.container_name,
            self.stack.config.api.ecr_repo
        )
        self.assertEqual(
            self.stack.service.task_definition.default_container.container_port, 80
        )
        self.assertTrue(self.stack.service.task_definition.is_fargate_compatible)

        task_def = self.stack.service.task_definition
        self.assertEqual(task_def.node.default_child.cpu, '256')
        self.assertEqual(task_def.node.default_child.memory, '512')
        resource_arn = 'arn:${{Token[AWS.Partition.3]}}:dynamodb:{}:{}:table/{}'.format(
            self.stack.config.region_name,
            self.stack.config.account_id,
            self.stack.config.api.table_name
        )
        self.assertEqual(
            task_def.task_role.node.children[1].document.to_json(),
            {
                'Statement': [{
                    'Action': [
                        'dynamodb:Scan',
                        'dynamodb:Query',
                        'dynamodb:GetItem',
                        'dynamodb:PutItem',
                        'dynamodb:UpdateItem',
                        'dynamodb:DeleteItem',
                        'dynamodb:BatchGetItem',
                        'dynamodb:BatchWriteItem'
                    ],
                    'Effect': 'Allow',
                    'Resource': resource_arn,
                    'Sid': 'AllowFargateAccessDynamoDB'
                }],
                'Version': '2012-10-17'
            }
        )

    def test_cloudfront_setup(self):
        self.assertEqual(str(type(self.stack.distribution)), "<class 'aws_cdk.aws_cloudfront.Distribution'>")

    def test_api_pipeline_setup(self):
        self.assertEqual(str(type(self.stack.api_pipeline)), "<class 'aws_cdk.aws_codepipeline.Pipeline'>")

    def test_web_pipeline_setup(self):
        self.assertEqual(str(type(self.stack.web_pipeline)), "<class 'aws_cdk.aws_codepipeline.Pipeline'>")
