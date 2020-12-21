import os
from ..lib.helpers import DotDict


class ConfigStoreMixin(object):

    """Stack configurations like bucket or repo names"""

    _domain = 'simple2do.xyz'
    _app = 'SimpleTodo'

    config = DotDict(
        app_name=_app,
        domain=_domain,

        docker_registry=os.getenv('DOCKER_REGISTRY'),

        vpc_cidr='10.20.0.0/16',
        cluster_name=f'{_app}Cluster',
        frontend_repo=_domain,
        backend_repo=f'api.{_domain}',
        frontend_bucket_name=_domain,

        frontend_build_output=f'{_app}FrontendBuildOutput',
        frontend_pipeline=f'{_app}FrontendPipeline',
        backend_build_output=f'{_app}BackendBuildOutput',
        backend_pipeline=f'{_app}BackendPipeline',
        ecr_repo_name=_domain,

        db_name=_app.lower(),
    )


for filename in os.listdir(os.path.dirname(__file__)):
    name, ext = os.path.splitext(filename)
    if name != '__init__' and ext == '.py':
        exec(f'from .{name} import *')
