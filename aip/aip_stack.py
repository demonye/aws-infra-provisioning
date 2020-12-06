from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_codecommit as cc,
    aws_codebuild as cb,
    aws_ecr as ecr,
)


class AipStack(core.Stack):
    """AWS Infrastructure Provisioning Stack"""

    name = 'aws-infra-provisioning'
    _steps = (
        'codecommit',
        'codebuild',
        'ecr',
        's3',
    )

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """AIP __init__"""
        super().__init__(scope, construct_id, **kwargs)
        for step in self._steps:
            getattr(self, f'setup_{step}')()

    def setup_s3(self) -> None:
        """Setup S3 buckets"""
        self.s3_bucket = s3.Bucket(
            self, 'AIP-s3-bucket-1',
            bucket_name=self.name,
            versioned=True,
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY,
        )

    def setup_codecommit(self) -> None:
        """Setup CodeCommit"""
        self.code_repo = cc.Repository(
            self, 'AIP-codecommit-repo-1',
            repository_name=self.name,
        )

    def _get_github_source(self, owner: str, repo: str = None) -> cb.Source:
        """Returns the codebuild source for github repo

        :param owner: repo owner
        :param repo: repo name
        :returns: codebuild source
        """
        if repo is None:
            repo = self.name
        filters = [
            cb.FilterGroup.in_event_of(cb.EventAction.PUSH).and_branch_is('main')
        ]
        return cb.Source.git_hub(owner=owner, repo=repo, webhookfilters=filters)

    def setup_codebuild(self) -> None:
        """Setup CodeBuild"""
        # source = cb.Source.code_commit(repository=self.code_repo, branch_or_ref='main')
        source = self._get_github_source(owner='demonye', repo=self.name)
        self.build_project = cb.Project(self, 'AIP-codebuild-project-1', source=source)

    def setup_ecr(self) -> None:
        """Setup ECR"""
        self.ecr_repo = ecr.Repository(
            self, 'AIP-ecr-repo-1',
            repository_name=self.name,
            image_scan_on_push=True,
        )
