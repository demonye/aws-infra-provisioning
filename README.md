
# Welcome to AWS Infrastructure Provisioning!

## What to be provisioned
* VPC/subnets
* ECS cluster with Fargate service
* S3 buckets
* CloudFront
* Database on RDS
* ECR repository
* Frontend pipeline
* Backend pipeline

## CloudFormation Stacks

* CloudFront Stack
  * Cloud Front
  * S3
* Pipeline Stack
  * CodeBuild (frontend)
  * CodeDeploy (frontend)
  * CodePipeline (frontend)
  * CodeBuild (backend)
  * CodeDeploy (to do)
  * CodePipeline (backend)
* Database Stack
  * RDS
* Ecs Stack
  * VPC/subnets
  * ECS cluster with Fargate service
  * ELB (To be fixed)

## How to run

```
mkdir aip
git clone https://github.com/demonye/aws-infra-provisioning.git aip
cd aip
python3 -m venv .venv/aip
source .venv/aip/bin/activate
pip install -r requirements/base.txt
```

Assume you have installed cdk client.
If not, refers to [AWS CDK Guide](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_install).

Check your aws profile and build up stacks

```
# Check your ~/.aws/credentials get the YOUR_PROFILE
export AWS_PROFILE=YOUR_PROFILE
cdk deploy ECS
cdk deploy Database
cdk deploy CloudFront
cdk deploy FrontendPipeline
cdk deploy BackendPipeline
```
