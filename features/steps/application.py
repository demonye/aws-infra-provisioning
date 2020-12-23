import time
from behave import *
import boto3
import requests

session = requests.session()


@given('I am ready to go')
def step_impl(ctx):
    sts = boto3.client('sts')
    cf = boto3.client('cloudfront')
    region_name = sts.meta.region_name

    bucket_name = 'eric-devops-demo-web'
    resp = cf.list_distributions()
    ctx.default_domain_name = f"{bucket_name}.s3-website-{region_name}.amazonaws.com"
    founds = list(filter(lambda v: v['Origins']['Items'][0]['DomainName'] == ctx.default_domain_name, resp['DistributionList']['Items']))
    distribution = founds and founds[0]
    ctx.domain_name = distribution['DomainName']


@when('I get the task list')
def step_impl(ctx):
    url = f'http://{ctx.domain_name}/api/v1/task/'
    ctx.resp = session.get(url)


@then('I expect the http code 200 and get a list')
def step_impl(ctx):
    assert ctx.resp.status_code == 200
    assert isinstance(ctx.resp.json(), list)


@when('I post a task')
def step_impl(ctx):
    url = f'http://{ctx.domain_name}/api/v1/task/'
    ctx.resp = session.post(url, json={'title': f'Test task from integration {time.time()}'})


@then('I expect the http code 201 and get the new task returned')
def step_impl(ctx):
    assert ctx.resp.status_code == 201
    task = ctx.resp.json()
    for k in ('id', 'title', 'is_done', 'created_at'):
        assert k in task
    ctx.new_task_id = task['id']


@when('I update a task')
def step_impl(ctx):
    url = f'http://{ctx.domain_name}/api/v1/task/{ctx.new_task_id}'
    ctx.resp = session.patch(url, json={'is_done': True})


@then('I expect the http code 200 and get the update task back')
def step_impl(ctx):
    assert ctx.resp.status_code == 200
    task = ctx.resp.json()
    for k in ('id', 'title', 'is_done', 'created_at'):
        assert k in task
    assert task['is_done'] is True


@when('I send a put request')
def step_impl(ctx):
    url = f'http://{ctx.domain_name}/api/v1/task/{ctx.new_task_id}'
    ctx.resp = session.put(url, json={'title': 'Change', 'is_done': True})


@then('I expect the http code 405 and empty body returned')
def step_impl(ctx):
    assert ctx.resp.status_code == 405
    assert ctx.resp.json() == {"detail": "Method Not Allowed"}


@when('I delete a task')
def step_impl(ctx):
    url = f'http://{ctx.domain_name}/api/v1/task/{ctx.new_task_id}/'
    ctx.resp = session.delete(url)


@then('I expect the http code 204 and empty body returned')
def step_impl(ctx):
    assert ctx.resp.status_code == 204
    assert not ctx.resp.content
