Feature: Check ecs, fargate service and cloudftont

    Scenario Outline: Checking cluster status
        Given I get the cluster by searching <cluster_name>
         Then I expect the cluster status is <status>

        Examples: cluster
            | cluster_name | status |
            | Infra-Cluster | ACTIVE |

    Scenario Outline: Checking service
        Given I get the cluster by searching <cluster_name>
          And I get the service by searching <service_name>
         Then I expect the continaer name in LB is <container_name>

        Examples: service
            | cluster_name | service_name  | container_name |
            | Infra-Cluster | Infra-FargateService | eric-devops-demo-api |


    Scenario Outline: Checking task definition
        Given I get the cluster by searching <cluster_name>
          And I get the service by searching <service_name>
         When I get the task definition from service
         Then I expect the continaer name is <container_name>
          And I expect the continaer port is <container_port>
          And I expect the continaer cpu is <cpu>
          And I expect the continaer memory is <memory>

        Examples: task_def
            | cluster_name | service_name  | container_name | container_port | cpu | memory |
            | Infra-Clust | Infra-FargateService | eric-devops-demo-api | 80 | 256 | 512 |


    Scenario Outline: Checking task role policies
        Given I get the cluster by searching <cluster_name>
          And I get the service by searching <service_name>
         When I get the task definition from service
         Then I expect to see the task role arn and the policy <sid>
          And I expect the policy has dynamodb access permissions

        Examples: task_role
            | cluster_name | service_name  | sid |
            | Infra-Clust | Infra-FargateService | AllowFargateAccessDynamoDB |
