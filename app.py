#!/usr/bin/env python3

from aws_cdk import core
from aip.aip_stack import AipStack

app = core.App()
AipStack(app, "aip")
app.synth()
