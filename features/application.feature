Feature: Check API running status

    @app
    Scenario: Checking API status
        Given I am ready to go
         When I get the task list
         Then I expect the http code 200 and get a list
         When I post a task
         Then I expect the http code 201 and get the new task returned
         When I update a task
         Then I expect the http code 200 and get the update task back
         When I send a put request
         Then I expect the http code 405 and empty body returned
         When I delete a task
         Then I expect the http code 204 and empty body returned
