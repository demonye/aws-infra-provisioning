import os
import json
import boto3
from aws_cdk import core
from ..helpers import DotDict


class BaseStack(core.Stack):
    """Stack configurations like bucket or repo names"""

    def __init__(self, *args, **kwargs):
        """Set all configurations that the stack class needs
        """

        sts = boto3.client('sts')
        app = 'EricDemo'
        app_config = self._load_configs()

        self.config = DotDict(
            vpc_cidr='10.20.0.0/16',
            cluster_name=f'{app}Cluster',

            # API config
            api=DotDict(
                source_repo=app_config.api.source_repo,
                build_output=f'{app}ApiBuildOutput',
                pipeline=f'{app}ApiPipeline',
                ecr_repo=app_config.api.ecr_repo,
                table_name=app_config.api.table_name,
            ),

            # WEB config
            web=DotDict(
                source_repo=app_config.web.source_repo,
                build_output=f'{app}WebBuildOutput',
                pipeline=f'{app}WebPipeline',
                bucket_name=app_config.web.bucket_name,
            ),

            # Account info
            account_id=sts.get_caller_identity()['Account'],
            region_name=sts.meta.region_name,
        )
        kwargs['env'] = core.Environment(
            account=self.config.account_id, region=self.config.region_name)
        super().__init__(*args, **kwargs)

    def _load_configs(self):
        with open('demoapp/api/config.json') as fp:
            api_config = DotDict(json.load(fp))
        with open('demoapp/web/config.json') as fp:
            web_config = DotDict(json.load(fp))
        return DotDict(
            api=api_config,
            web=web_config,
        )


for filename in os.listdir(os.path.dirname(__file__)):
    name, ext = os.path.splitext(filename)
    if name != '__init__' and ext == '.py':
        exec(f'from .{name} import *')
