from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_ecr as ecr,
    aws_codecommit as cc,
    aws_codebuild as cb,
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
)

from . import ConfigStoreMixin


class FrontendPipelineStack(ConfigStoreMixin, core.Stack):
    """AWS Infrastructure Provisioning: Pipeline Stack"""
    prefix = 'Frontend'

    def __init__(self,
                 scope: core.Construct,
                 construct_id: str,
                 **kwargs) -> None:
        """FrontendPipelineStack.__init__.

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

        self.setup_pipeline(self.setup_build_project())

    def setup_build_project(self):
        """Setup the build project.
        Using codebuild to create a PipelineProject
        including three phases:
            * install:   npm install
            * pre_build: run unit tests
            * build:     npm run build and setup artifacts

        Parameters
        ----------
        None

        Returns
        -------
        PipelineProject object to be used in Pipeline

        """
        return cb.PipelineProject(
            self, 'FrontendBuild',
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

    def setup_pipeline(self, build_project):
        """Setup the build pipeline.
        Using codepipeline to create a Pipeline
        including two stages:
            * Source: CodeCommitSourceAction
            * Build : CodeBuildActioin
            * Deploy: S3DeployAction

        Parameters
        ----------
        build_object :
            PipelineProject the object returned from self.setup_build_project

        Returns
        -------
        None
        """
        source_repo = cc.Repository.from_repository_name(
            self, 'FrontendSourceRepo',
            repository_name=self.config.frontend_repo
        )
        source_output = cp.Artifact()
        build_output = cp.Artifact(self.config.frontend_build_output)
        web_s3_bucket = s3.Bucket.from_bucket_name(
            self, 'FrontendBucket',
            bucket_name=self.config.frontend_bucket_name
        )
        cp.Pipeline(
            self, 'FrontendPipeline',
            pipeline_name=self.config.frontend_pipeline,
            stages=[
                cp.StageProps(
                    stage_name='Source',
                    actions=[
                        cp_actions.CodeCommitSourceAction(
                            action_name='GetFrontendSource',
                            repository=source_repo,
                            branch='main',
                            output=source_output,
                        )
                    ]
                ),
                cp.StageProps(
                    stage_name='Build',
                    actions=[
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


class BackendPipelineStack(ConfigStoreMixin, core.Stack):
    """AWS Infrastructure Provisioning: Pipeline Stack"""
    prefix = 'Backend'

    def __init__(self,
                 scope: core.Construct,
                 construct_id: str,
                 **kwargs) -> None:
        """BackendPipelineStack.__init__.

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

        # get ECR repository object
        self.ecr_repo = ecr.Repository.from_repository_name(
            self, 'GetEcrRepo', repository_name=self.config.ecr_repo_name
        )
        if not self.ecr_repo:
            # create ECR repository object if no existing one
            self.ecr_repo = ecr.Repository(
                self, 'BackendEcrRepo',
                repository_name=self.config.ecr_repo_name,
                image_scan_on_push=True,
            )

        self.setup_pipeline(self.setup_build_project())

    def setup_build_project(self):
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
        return cb.PipelineProject(
            self, 'BackendBuild',
            build_spec=cb.BuildSpec.from_object(dict(
                version=0.2,
                phases={
                    'install': {'commands': [
                        'pip install -r src/test.txt'
                    ]},
                    'pre_build': {'commands': [
                        'cd src',
                        'coverage run --source=. manage.py test',
                        'coverage report -m',
                        'cd ..',
                        'aws --version',
                        '$(aws ecr get-login --no-include-email)',
                        'VERSION=$(cat VERSION)'
                    ]},
                    'build': {'commands': [
                        f'docker build . -t {self.config.ecr_repo_name}',
                        f'docker tag {self.config.ecr_repo_name} {self.ecr_repo.repository_uri}:$VERSION',
                    ]},
                    'post_build': {'commands': [
                        f'docker push {self.ecr_repo.repository_uri}:$VERSION',
                        f'docker push {self.ecr_repo.repository_uri}:latest',
                        # TODO imagedefinitions for deploy
                        # f'printf \'[{{"name": "{self.config.ecr_repo_name}", "imageUrl": "{self.ecr_repo_name.repository_uri}:latest"}}]\' > imagedefinitions.json',
                        # 'cat imagedefinitions.json',
                    ]},
                },
                artifacts={
                    'type': 'NO_ARTIFACTS',
                    # 'files': ['imagedefinitions.json']
                }
            ))
        )

    def setup_pipeline(self, build_project):
        """Setup the build pipeline.
        Using codepipeline to create a Pipeline
        including two stages:
            * Source: CodeCommitSourceAction
            * Build:  CodeBuildActioin
            * Deploy: -TODO-

        Parameters
        ----------
        build_object :
            PipelineProject the object returned from self.setup_build_project

        Returns
        -------
        None
        """
        source_repo = cc.Repository.from_repository_name(
            self, 'BackendSourceRepo',
            repository_name=self.config.backend_repo
        )
        source_output = cp.Artifact()
        build_output = cp.Artifact(self.config.backend_build_output)
        cp.Pipeline(
            self, 'BackendPipeline',
            pipeline_name=self.config.backend_pipeline,
            stages=[
                cp.StageProps(
                    stage_name='Source',
                    actions=[
                        cp_actions.CodeCommitSourceAction(
                            action_name='GetBackendSource',
                            repository=source_repo,
                            branch='main',
                            output=source_output,
                        )
                    ]
                ),
                cp.StageProps(
                    stage_name='Build',
                    actions=[
                        cp_actions.CodeBuildAction(
                            action_name='BuildBackend',
                            project=build_project,
                            input=source_output,
                            outputs=[build_output]
                        )
                    ]
                ),
                # FIXME deploy to ECS service
                # cp.StageProps(
                #     stage_name='Deploy',
                #     actions=[
                #         cp_actions.EcsDeployAction(
                #             action_name='DeployBackend',
                #             service=service,
                #             input=build_output,
                #         )
                #     ]
                # )
            ]
        )
