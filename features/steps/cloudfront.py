from behave import *
from __init__ import session


@given('I get the distribution by bucket {bucket_name}')
def step_impl(ctx, bucket_name):
    sts = session.client('sts')
    cf = session.client('cloudfront')
    # account = sts.get_caller_identity()['Account']
    region_name = sts.meta.region_name

    resp = cf.list_distributions()
    ctx.default_domain_name = f"{bucket_name}.s3-website-{region_name}.amazonaws.com"
    founds = list(filter(lambda v: v['Origins']['Items'][0]['DomainName'] == ctx.default_domain_name, resp['DistributionList']['Items']))
    ctx.distribution = founds and founds[0]
    ctx.origins = {
        item['Id']: item
        for item in ctx.distribution['Origins']['Items']
    }


@then('I expect the status is {status}')
def step_impl(ctx, status):
    assert ctx.distribution['Status'] == status
    assert ctx.distribution['Origins']['Quantity'] == 2

@then('I expect the default behaviour is redirecting to bucket')
def step_impl(ctx):
    default_origin_id = ctx.distribution['DefaultCacheBehavior']['TargetOriginId']
    assert ctx.origins[default_origin_id]['DomainName'] == ctx.default_domain_name


@then('I expect the api call redirecting to {target}')
def step_impl(ctx, target):
    api_behavior = ctx.distribution['CacheBehaviors']['Items'][0]
    assert api_behavior['PathPattern'] == "/api/*"
    api_origin_id = api_behavior['TargetOriginId']
    assert ctx.origins[api_origin_id]['DomainName'].endswith(target)
    assert len({'GET', 'POST', 'PATCH', 'DELETE'}.intersection(api_behavior['AllowedMethods']['Items'])) == 4
