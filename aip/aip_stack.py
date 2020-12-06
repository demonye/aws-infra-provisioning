from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_codecommit as cc,
    aws_codebuild as cb,
)


class AipStack(core.Stack):
    """AWS Infrastructure Provisioning Stack"""

    _steps = (
        's3',
        'codebuild',
    )

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """AIP __init__"""
        super().__init__(scope, construct_id, **kwargs)
        for step in self._steps:
            getattr(self, f'setup_{step}')()

    def setup_s3(self) -> None:
        """Setup S3 buckets"""
        s3.Bucket(
            self, 'MyFirstBucket',
            versioned=True,
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

    def setup_codebuild(self) -> None:
        """Setup CodeBuild"""
        # filters = [
        #     cb.FilterGroup.in_event_of(cb.EventAction.PUSH).and_branch_is('main')
        # ]
        # source = cb.Source.git_hub(
        #     owner='demonye',
        #     repo='aws-infra-provisioning',
        #     webhookfilters=filters
        # )
        source = cb.Source.code_commit(
            repository=cc.Repository(
                self, 'MyRepo',
                repository_name='SA-DevOps-Assignment',
            ),
            branch_or_ref='main',
        )
        cb.Project(self, 'MyProject', source=source)
