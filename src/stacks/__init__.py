import os
import boto3
from aws_cdk import core
from src.lib.helpers import DotDict


class BaseStack(core.Stack):
    """Stack configurations like bucket or repo names"""

    def __init__(self, *args, **kwargs):
        domain = 'simple2do.xyz'
        app = 'SimpleTodo'
        self.config = DotDict(
            app_name=app,
            domain=domain,

            docker_registry=os.getenv('DOCKER_REGISTRY'),

            vpc_cidr='10.20.0.0/16',
            cluster_name=f'{app}Cluster',
            frontend_repo=domain,
            backend_repo=f'api.{domain}',
            frontend_bucket_name=domain,

            frontend_build_output=f'{app}FrontendBuildOutput',
            frontend_pipeline=f'{app}FrontendPipeline',
            backend_build_output=f'{app}BackendBuildOutput',
            backend_pipeline=f'{app}BackendPipeline',
            ecr_repo_name=domain,

            db_name=app.lower(),
        )

        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()['Account']
        kwargs['env'] = core.Environment(account=account_id, region=sts.meta.region_name)
        super().__init__(*args, **kwargs)


for filename in os.listdir(os.path.dirname(__file__)):
    name, ext = os.path.splitext(filename)
    if name != '__init__' and ext == '.py':
        exec(f'from .{name} import *')
