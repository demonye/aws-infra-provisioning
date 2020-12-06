
# Welcome to AWS Infrastructure Provisioning!

## What to be provisioned
* S3 buckets
* CodeBuild
* ECR

### To-do
* VPC/subnets
* Availability Zone
* RDS
* ECS
* Fargate
* CodeDeploy
* CodePipeline

## How to run

```
mkdir aip
git clone https://github.com/demonye/aws-infra-provisioning.git aip
cd aip
python3 -m venv .venv/aip
source .venv/aip/bin/activate
pip install -r requirements.txt
```

Assume you have installed cdk client.
If not, refers to [AWS CDK Guide](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_install).

Deploy this stack to your default AWS account/region by running:

```
cdk deploy
```

Or deply to the indicated AWS account/region `cdk deploy --profile YOUR_PROFILE`
