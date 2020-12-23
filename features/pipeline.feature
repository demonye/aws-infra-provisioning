Feature: Check piplines, including API and Web frontend

    Scenario Outline: Checking general data of the pipelines
        Given I get the pipeline by name <pipeline_name>
         Then I expect the pipeline has <stage_count> stages

        Examples: pipeline_general
            | pipeline_name | stage_count |
            | EricDemoApiPipeline | 3 |
            | EricDemoWebPipeline | 3 |

    Scenario Outline: Checking API build
        Given I get the pipeline by name <pipeline_name>
         When I get the build project of the pipeline
         Then I expect it has ECR permissions to push image

        Examples: api_build
            | pipeline_name |
            | EricDemoApiPipeline |

    Scenario Outline: Checking deploy stage
        Given I get the pipeline by name <pipeline_name>
         When I get the deploy stage of the pipeline
         Then I expect the deploy action is <action_type>
          And I expect the provider name is <provider_name>

        Examples: deploy_stage
            | pipeline_name | action_type | provider_name |
            | EricDemoWebPipeline | S3 | eric-devops-demo-web |
            | EricDemoApiPipeline | ECS | Infra-Cluster |
