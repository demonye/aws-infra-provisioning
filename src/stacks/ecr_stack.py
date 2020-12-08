from aws_cdk import (
    core,
    aws_ecr as ecr,
)


class EcrStack(core.Stack):
    """AWS Infrastructure Provisioning: CodePipeline Stack"""

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        """CodePipelineStack.__init__.

        Parameters
        ----------
        scope : core.Construct
        construct_id : str
        name: str
            repository name

        Returns
        -------
        None

        """
        super().__init__(scope, construct_id, **kwargs)

        ecr.Repository(
            self, construct_id,
            repository_name=f'{construct_id}-images',
            image_scan_on_push=True,
        )
