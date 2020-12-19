#!/usr/bin/env python3

from aws_cdk import core
from aip import stacks

app = core.App()


def main():
    stacks.PipelineStack(app, 'Pipeline')
    stacks.DatabaseStack(app, 'Database')
    stacks.EcsStack(app, 'ECS')

    # app.synth()


if __name__ == '__main__':
    main()
