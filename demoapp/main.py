"""SimpleTodo service based on FastAPI
Use DynamoDB as backup database

Endpoints
---------
    GET    /api/v1/task/ list all tasks
    POST   /api/v1/task/ add new task
    PATCH  /api/v1/task/{id}/ set task status
    DELETE /api/v1/task/{id}/ archive task
    update(PATCH) and delete(DELETE) operations

"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key, And, Or, Not
from botocore.exceptions import ClientError

from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI()
session = boto3.session.Session()
dynamodb = session.resource('dynamodb')


class Task(BaseModel):
    """Data model: Task
    """
    title: Optional[str]
    is_done: Optional[bool] = False


class SimpleTodoDB:
    """DynamoDB wrapper
    Get or create dynamodb table
    """

    table_name = 'eric-devops-demo-tasks'
    table = None

    def __init__(self):
        """Returns a dynamodb table instance in self.table
        If no existing table, create a new table.

        """
        try:
            self.table = dynamodb.Table(self.table_name)
            _ = self.table.table_status
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'ResourceNotFoundException':
                self.table = self._create_table()

    def _create_table(self):
        """Create a new dynamodb table

        Returns
        -------
        dynamodb.Table
            The Table instance that created.

        """
        table = dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH',
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S',
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10,
            }
        )
        table.wait_until_exists(TableName=self.table_name)
        return table

    def _to_resp(self, item: dict):
        """Convert table item to task response

        Parameters
        ----------
        item: dict
            Task item

        Returns
        -------
        dict
            The task response for frontend

        """
        return {
            'id': item['id'],
            'title': item['title'],
            'is_done': item['task_status'] == 'Done',
            'created_at': item['created_at'],
        }

    def list(self):
        """List task items

        Returns
        -------
        list
            The tasks list

        """
        resp = self.table.scan(
            FilterExpression=Not(Key('task_status').eq('Archived'))
        )
        return [self._to_resp(v) for v in resp['Items']]

    def add(self, title: str):
        """Add new task item

        Parameters
        ----------
        title: str
            New task title

        Returns
        -------
        dict
            The created task

        """
        id_ = str(uuid.uuid4())
        self.table.put_item(
            Item={
                'id': id_,
                'title': title,
                'task_status': 'Todo',
                'created_at': datetime.utcnow().isoformat()
            }
        )
        return self._to_resp(db.table.get_item(Key={'id': id_})['Item'])

    def update(self, id_: int, status: str):
        """Update item status

        Parameters
        ----------
        id_: int
            Table key
        status: str
            The status has 3 values: Todo, Done, Archived

        Returns
        -------
        dict
            The updated task

        """
        item = self.table.update_item(
            Key={'id': id_},
            UpdateExpression='set task_status=:s',
            ExpressionAttributeValues={
                ':s': status
            },
            ReturnValues='UPDATED_NEW'
        )
        return self._to_resp(db.table.get_item(Key={'id': id_})['Item'])


db = SimpleTodoDB()


@app.get('/')
def version():
    """Returns version

    Read VERSION file content and return

    Returns
    -------
    dict
        {"version": <VERSION>}

    """
    try:
        with open('VERSION') as fp:
            return {'version': fp.read().strip()}
    except (IOError, FileNotFoundError):
        pass

    return {'version': '_UNKNOWN_'}


@app.get('/api/v1/task/')
def list_tasks():
    """GET method: list all tasks

    Notes
    -----
    The status has 3 values: Todo, Done, Archived

    Returns
    -------
    list
        The tasks list

    """
    return db.list()


@app.post('/api/v1/task/', status_code=201)
def add_task(task: Task):
    """POST method: add new task

    Parameters
    ----------
    task: Task
        New task values, must have title, status will always be 'Todo'

    Returns
    -------
    dict
        The created task

    """
    return db.add(task.title)


@app.patch('/api/v1/task/{id_:str}/')
def update_task(id_: str, task: Task):
    """PATCH method: update task status

    Parameters
    ----------
    id_ : int
        Key in task table
    task: Task
        Only take is_done filed
        if task.is_done is True, set status to 'Done', otherwise, 'Todo'

    Returns
    -------
    dict
        The updated task

    """
    return db.update(id_, 'Done' if task.is_done else 'Todo')


@app.delete('/api/v1/task/{id_:str}/', status_code=204)
def delete_task(id_: str):
    """DELETE method: archive the task
    Not actually delete the item, just update status to: 2 - archived

    Parameters
    ----------
    id_ : int
        Task table key

    Returns
    -------
    None

    """
    db.update(id_, 'Archived')
    return Response(status_code=204)
