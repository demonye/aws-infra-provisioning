
# Welcome to AWS Infrastructure Provisioning!

## What to be provisioned
* VPC and network setup
* ECS cluster with Fargate service and Load Balancer
* S3 buckets
* CloudFront
* ECR repository
* Deployment pipeline

## CloudFormation Stacks

* Infra Stack
  * Cloud Front
  * S3
  * CodePipeline (including build and deploy to ECS)
  * RDS (Commented out for now due to long wait)
  * VPC/subnets
  * ECS patterns service (ALB Fargate)

## How to run

```
docker run --privileged --rm --name aip-demo -d demonye/aws-infra-provisioning

docker exec \
-e AWS_ACCESS_KEY_ID=<your_aws_access_key_id> \
-e AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key> \
-e AWS_DEFAULT_REGION=<your_aws_default_region> \
-it aip-demo ash deploy.sh

docker stop aip-demo
```
