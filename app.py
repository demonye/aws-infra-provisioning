#!/usr/bin/env python3

from aws_cdk import core
from src.stacks import S3Stack, EcrStack, PipelineStack

app = core.App()


def main():
    S3Stack(app, 'todo-list-s3')
    EcrStack(app, 'todo-list-ecr')
    PipelineStack(app, 'todo-list-pipeline', 'todo-list-web')
    # app.synth()


if __name__ == '__main__':
    main()
