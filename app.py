#!/usr/bin/env python3

from aws_cdk import core
from aip.stacks import InfraStack

app = core.App()


if __name__ == '__main__':
    InfraStack(app, 'Infra')
    # app.synth()
