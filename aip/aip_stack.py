from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_codecommit as cc,
    aws_codebuild as cb,
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_ecr as ecr,
)


class AipStack(core.Stack):
    """AWS Infrastructure Provisioning Stack"""

    name = 'aws-infra-provisioning'
    _steps = (
        'codepipeline',
        'ecr',
        's3',
    )

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """AIP __init__"""
        super().__init__(scope, construct_id, **kwargs)
        self.code_repo = None
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
        return cb.Source.git_hub(owner=owner, repo=repo, webhook_filters=filters)

    def setup_codepipeline(self) -> None:
        """Setup CodePipeline"""
        code_repo = cc.Repository(
            self, 'AIP-codecommit-repo-1',
            repository_name=self.name,
        )
        source = cb.Source.code_commit(repository=code_repo)
        # source = self._get_github_source(owner='demonye', repo=self.name)
        build_project = cb.Project(self, 'AIP-codebuild-project-1', source=source)

        code_repo = cc.Repository.from_repository_name(
            self, 'ImportedRepo',
            repository_name=self.name,
        )
        source_output = cp.Artifact()
        source_action = cp_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=code_repo,
            output=source_output
        )
        build_action = cp_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=build_project,
            input=source_output,
            outputs=[cp.Artifact()]
        )
        self.pipeline = cp.Pipeline(
            self, 'AIP-codepipeline-pipeline-1',
            pipeline_name=self.name,
            stages=[
                cp.StageProps(
                    stage_name='Source',
                    actions=[source_action],
                ),
                cp.StageProps(
                    stage_name='Build',
                    actions=[build_action],
                ),
            ]
        )

    def setup_ecr(self) -> None:
        """Setup ECR"""
        self.ecr_repo = ecr.Repository(
            self, 'AIP-ecr-repo-1',
            repository_name=self.name,
            image_scan_on_push=True,
        )
