import os

from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_codecommit as cc,
    aws_codebuild as cb,
    aws_codedeploy as cd,
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
)


class PipelineStack(core.Stack):
    """AWS Infrastructure Provisioning: Pipeline Stack"""

    def __init__(self,
                 scope: core.Construct,
                 construct_id: str,
                 repo_name: str,
                 **kwargs) -> None:
        """PipelineStack.__init__.

        Parameters
        ----------
        scope : core.Construct
        construct_id : str
        repo_name : str
            repository name in CodeCommit

        Returns
        -------
        None

        """
        super().__init__(scope, construct_id, **kwargs)

        self.name = construct_id
        self.repo_name = repo_name
        build_project = self.setup_build_project()
        self.setup_pipeline(build_project)

    def setup_build_project(self):
        # commit_sha = os.getenv('CODEBUILD_RESOLVED_SOURCE_VERSION')
        return cb.PipelineProject(
            self, f'{self.name}-build',
            build_spec=cb.BuildSpec.from_object(dict(
                version=0.2,
                phases={
                    'install': {'commands': ['npm install']},
                    'build': {'commands': [
                        # 'npm run test:unit && npm run build'
                        'npm run build'
                    ]}
                },
                artifacts={
                    'files': ['**/*'],
                    'base-directory': 'dist',
                    'name': "dist-$CODEBUILD_RESOLVED_SOURCE_VERSION"
                }
            ))
        )

    def setup_pipeline(self, build_project):
        repo_id = f'{self.name}-source-repo'
        source_repo = cc.Repository.from_repository_name(
            self, repo_id, repository_name=self.repo_name
        )
        source_output = cp.Artifact()
        build_output = cp.Artifact(f'{self.name}-build')
        web_s3_bucket = s3.Bucket.from_bucket_name(
            self, 'todo-list-s3', bucket_name='todo-list-s3-bucket'
        )
        cp.Pipeline(
            self, 'cicd-pipeline',
            pipeline_name=self.name,
            stages=[
                cp.StageProps(
                    stage_name='Source',
                    actions=[
                        cp_actions.CodeCommitSourceAction(
                            action_name='GetFrontendSource',
                            repository=source_repo,
                            output=source_output,
                        )
                    ]
                ),
                cp.StageProps(
                    stage_name='Build',
                    actions=[
                        cp_actions.CodeBuildAction(
                            action_name='TestFrontend',
                            project=build_project,
                            input=source_output,
                            outputs=[build_output]
                        ),
                        cp_actions.CodeBuildAction(
                            action_name='BuildFrontend',
                            project=build_project,
                            input=source_output,
                            outputs=[build_output]
                        )
                    ]
                ),
                cp.StageProps(
                    stage_name='Deploy',
                    actions=[
                        cp_actions.S3DeployAction(
                            action_name='DeployFrontend',
                            bucket=web_s3_bucket,
                            input=build_output,
                            access_control=s3.BucketAccessControl.PUBLIC_READ
                        )
                    ]
                )
            ]
        )
