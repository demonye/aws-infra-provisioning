
# Welcome to AWS Infrastructure Provisioning!

## What to be provisioned
* VPC and network setup
* ECS cluster with Fargate service and Load Balancer
* S3 buckets
* CloudFront
* ECR repository
* Deployment pipeline

## How to run

* Run a docker container in the background

```
docker run --privileged --rm --name aip-demo -d demonye/aws-infra-provisioning
```

**NOTE** it's running a docker in docker, so `--privileged` needed

* Make a alias for convenience, replace the placeholders with your acutal AWS key and region

```
alias aip_run="docker exec -e AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=YOUR_AWS_DEFAULT_REGION -it aip-demo"
```

* Run some unit tests first

```
aip_run python3 -m unittest

# If you want coverage report, run

aip_run coverage run --source=aip -m unittest && \
aip_run coverage report -m --skip-empty
```

* Deploy the stack

```
aip_run ./deploy.sh
```

* When the deploy done, run the integration tests

```
aip_run behave
```

* Stop the container
```
docker stop aip-demo
```
