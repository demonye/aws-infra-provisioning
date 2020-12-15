#!/usr/bin/env python3

import boto3
from aws_cdk import core
from src import stacks

app = core.App()


def main():
    stacks.CloudFrontStack(app, 'CloudFront')
    stacks.FrontendPipelineStack(app, 'FrontendPipeline')
    stacks.BackendPipelineStack(app, 'BackendPipeline')

    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    stacks.DatabaseStack(app, 'Database', env=core.Environment(
        account=account_id, region=sts.meta.region_name
    ))
    stacks.EcsStack(app, 'ECS')

    # app.synth()


if __name__ == '__main__':
    main()
