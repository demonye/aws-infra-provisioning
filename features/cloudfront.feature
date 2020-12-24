Feature: Check cloudfront and load balancer

    Scenario Outline: Checking cloudfront status
        Given I get the distribution by bucket <bucket_name>
         Then I expect the status is <status>
          And I expect the default behaviour is redirecting to bucket
          And I expect the api call redirecting to <target>

        Examples: cloundfront
            | bucket_name | status | target |
            | eric-devops-demo-web | Deployed | elb.amazonaws.com |
