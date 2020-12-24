from behave import *
from __init__ import session


def tag_value(item, key):
    founds = list(filter(lambda v: v['Key'] == key, item['Tags']))
    if founds:
        return founds[0]['Value']
    return None


@given('I am in the Vpc {vpc_name}')
def step_impl(ctx, vpc_name):
    ec2 = session.client('ec2')
    for vpc in ec2.describe_vpcs()['Vpcs']:
        if tag_value(vpc, 'Name') == vpc_name:
            ctx.vpc = vpc
            break
    assert ctx.vpc


@when('I see the Vpc cidr is {cidr}')
def step_impl(ctx, cidr):
    assert cidr == ctx.vpc['CidrBlock']


@then('I expect the subnets count is {subnet_count}')
def step_impl(ctx, subnet_count):
    ec2 = session.client('ec2')
    resp = ec2.describe_subnets(
        Filters=[{'Name': 'vpc-id', 'Values': [ctx.vpc['VpcId']]}]
    )
    ctx.subnets = resp['Subnets']
    assert len(resp['Subnets']) == int(subnet_count)


@then('I expect the availability zones count is {az_count}')
def step_impl(ctx, az_count):
    az_set = {v['AvailabilityZone'] for v in ctx.subnets}
    assert len(az_set) == int(az_count)


@when('I check the {subnet_type} subnet')
def step_impl(ctx, subnet_type):
    ctx.subnet_type = subnet_type.title()


@then('I expect the subnet cidr is {cidr1} and {cidr2}')
def step_impl(ctx, cidr1, cidr2):
    ec2 = session.client('ec2')
    resp = ec2.describe_subnets(
        Filters=[
            {'Name': 'vpc-id', 'Values': [ctx.vpc['VpcId']]},
        ]
    )
    subnets = list(filter(lambda v: tag_value(v, 'aws-cdk:subnet-type') == ctx.subnet_type, resp['Subnets']))
    ctx.subnets = subnets
    assert sorted([v['CidrBlock'] for v in subnets]) == [cidr1, cidr2]


@then('I expect their availability zones are different')
def step_impl(ctx):
    azs = [v['AvailabilityZone'] for v in ctx.subnets]
    assert len(azs) == 2
    assert azs[0] != azs[1]
