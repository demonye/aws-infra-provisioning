from behave import *
from __init__ import session


@given('I get the cluster by searching {cluster_name}')
def step_impl(ctx, cluster_name):
    ecs = session.client('ecs')
    resp = ecs.list_clusters()
    arns = list(filter(lambda v: v.find(cluster_name) >= 0, resp['clusterArns']))
    arn = arns[0] if arns else None

    resp = ecs.describe_clusters(clusters=[arn])
    ctx.cluster = resp['clusters'][0]


@then('I expect the cluster status is {status}')
def step_impl(ctx, status):
    assert ctx.cluster['status'] == status


@given('I get the service by searching {service_name}')
def step_impl(ctx, service_name):
    ecs = session.client('ecs')
    resp = ecs.list_services(cluster=ctx.cluster['clusterArn'])
    arns = list(filter(lambda v: v.find(service_name) >= 0, resp['serviceArns']))
    service_arn = arns[0] if arns else None

    resp = ecs.describe_services(
        cluster=ctx.cluster['clusterName'],
        services=[service_arn.split('/')[-1]]
    )
    ctx.service = resp['services'][0]


@then('I expect the continaer name in LB is {container_name}')
def step_impl(ctx, container_name):
    assert ctx.service['loadBalancers'][0]['containerName'] == container_name


@when('I get the task definition from service')
def step_impl(ctx):
    ecs = session.client('ecs')
    task_def_name = ctx.service['taskDefinition']
    assert len(list(filter(lambda v: v['taskDefinition'] == task_def_name, ctx.service['deployments']))) > 0
    resp = ecs.describe_task_definition(taskDefinition=task_def_name)
    ctx.task_def = resp['taskDefinition']


@then('I expect the continaer cpu is {cpu}')
def step_impl(ctx, cpu):
    assert ctx.task_def['cpu'] == str(cpu)


@then('I expect the continaer memory is {memory}')
def step_impl(ctx, memory):
    assert ctx.task_def['memory'] == str(memory)


@then('I expect the continaer port is {container_port}')
def step_impl(ctx, container_port):
    port_mapping = ctx.task_def['containerDefinitions'][0]['portMappings'][0]
    assert port_mapping['containerPort'] == int(container_port)
    assert port_mapping['hostPort'] == int(container_port)


@then('I expect the continaer name is {container_name}')
def step_impl(ctx, container_name):
    assert ctx.task_def['containerDefinitions'][0]['name'] == container_name


@then('I expect to see the task role arn and the policy {sid}')
def step_impl(ctx, sid):
    iam = session.client('iam')
    assert 'taskRoleArn' in ctx.task_def
    role_name = ctx.task_def['taskRoleArn'].split('/')[-1]
    resp = iam.list_role_policies(RoleName=role_name)
    policy_name = resp['PolicyNames'][0]

    policy = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
    ctx.policy = policy
    assert ctx.policy['PolicyDocument']['Statement'][0]['Sid'] == sid


@then('I expect the policy has dynamodb access permissions')
def step_impl(ctx):
    assert ctx.policy['PolicyDocument']['Statement'][0]['Action'] == [
        "dynamodb:Scan",
        "dynamodb:Query",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem"
    ]
