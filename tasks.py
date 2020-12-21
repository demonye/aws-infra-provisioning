import os
from functools import partial
from invoke import task
from rich.prompt import Prompt


@task
def deploy(c):
    run = partial(c.run, shell=os.getenv('SHELL') or '/bin/ash')

    access_key_id = os.getenv('AWS_ACCESS_KEY_ID') or \
        Prompt.ask('AWS [bold yellow]access key id[/]? ')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY') or \
        Prompt.ask('AWS [bold yellow]secret access key[/]? ')
    region_name = os.getenv('AWS_DEFAULT_REGION') or \
        Prompt.ask('Region name? ')

    set_envs = (
        f'AWS_ACCESS_KEY_ID={access_key_id} '
        f'AWS_SECRET_ACCESS_KEY={secret_access_key} '
        f'AWS_DEFAULT_REGION={region_name} '
    )

    # run('dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 1>/tmp/dockerd.log 2>&1 &')
    # run('sleep 3')

    run(f'{set_envs} && cd demoapp && ash ./set_code.sh')
    run(f'{set_envs} && cd demoapp && ash ./build.sh')
    run(f'{set_envs} cdk deploy')
