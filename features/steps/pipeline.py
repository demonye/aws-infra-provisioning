from behave import *
from __init__ import session


@given('I get the pipeline by name {pipeline_name}')
def step_impl(ctx, pipeline_name):
    pipeline = session.client('codepipeline')
    resp = pipeline.get_pipeline(name=pipeline_name)
    ctx.pipeline = resp['pipeline']
    assert ctx.pipeline['name'] == pipeline_name


@then('I expect the pipeline has {stage_count} stages')
def step_impl(ctx, stage_count):
    assert len(ctx.pipeline['stages']) == int(stage_count)


@when('I get the build project of the pipeline')
def step_impl(ctx):
    founds = list(filter(lambda v: v['name'] == 'Build', ctx.pipeline['stages']))
    ctx.build_project = founds and founds[0]


@when('I get the deploy stage of the pipeline')
def step_impl(ctx):
    founds = list(filter(lambda v: v['name'] == 'Deploy', ctx.pipeline['stages']))
    ctx.deploy_stage = founds and founds[0]


@then('I expect it has ECR permissions to push image')
def step_impl(ctx):
    iam = session.client('iam')
    resp = iam.list_roles()
    founds = list(filter(lambda v: v['RoleName'].startswith('Infra-ApiBuild'), resp['Roles']))
    role_name = founds and founds[0]['RoleName']

    resp = iam.list_role_policies(RoleName=role_name)
    policy_name = resp['PolicyNames'][0]

    ctx.policy = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
    action = None
    for stat in ctx.policy['PolicyDocument']['Statement']:
        _action = stat['Action']
        if _action[0].startswith('ecr:'):
            action = _action
            break
    assert action == [
        "ecr:GetAuthorizationToken",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage"
    ]


@then('I expect the deploy action is {action_type}')
def step_impl(ctx, action_type):
    ctx.provider = ctx.deploy_stage['actions'][0]['actionTypeId']['provider']
    assert ctx.provider == action_type


@then('I expect the provider name is {provider_name}')
def step_impl(ctx, provider_name):
    if ctx.provider == 'S3':
        name = ctx.deploy_stage['actions'][0]['configuration']['BucketName']
        assert name == provider_name
    if ctx.provider == 'ECS':
        name = ctx.deploy_stage['actions'][0]['configuration']['ClusterName']
        assert name.startswith(provider_name)
