Feature: Check Vpc and subnets states

    Scenario Outline: Checking Vpc cidr
        Given I am in the Vpc <vpc_name>
         When I see the Vpc cidr is <cidr>
         Then I expect the subnets count is <subnet_count>
          And I expect the availability zones count is <az_count>

        Examples: vpc
            | vpc_name | cidr | subnet_count | az_count |
            | Infra/Vpc | 10.20.0.0/16 | 4 | 2 |

    Scenario Outline: Checking subnets
        Given I am in the Vpc <vpc_name>
         When I check the <subnet_type> subnet
         Then I expect the subnet cidr is <cidr1> and <cidr2>
          And I expect their availability zones are different

        Examples: subnet
            | vpc_name | subnet_type | cidr1 | cidr2 |
            | Infra/Vpc | public | 10.20.0.0/24 | 10.20.1.0/24 |
            | Infra/Vpc | private | 10.20.2.0/24 | 10.20.3.0/24 |
