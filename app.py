#!/usr/bin/env python3

from aws_cdk import core
from aip.aip_stack import AipStack

app = core.App()

if __name__ == '__main__':
    AipStack(app, "aip")
    app.synth()
