import unittest
import boto3
from moto import mock_dynamodb2
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TaskAPITest(unittest.TestCase):
    @mock_dynamodb2
    def test_create_and_list(self):
        import main

        db = main.SimpleTodoDB()
        t1, t2 = db.add('title 1'), db.add('title 2')
        self.assertEqual(db.list(), [
            {'id': t1['id'], 'title': 'title 1', 'is_done': False, 'created_at': t1['created_at']},
            {'id': t2['id'], 'title': 'title 2', 'is_done': False, 'created_at': t2['created_at']},
        ])

    @mock_dynamodb2
    def test_update_and_delete(self):
        import main

        db = main.SimpleTodoDB()
        t1, t2 = db.add('title 1'), db.add('title 2')

        db.update(t1['id'], 'Done')
        db.update(t2['id'], 'Archived')
        self.assertEqual(db.list(), [
            {'id': t1['id'], 'title': 'title 1', 'is_done': True, 'created_at': t1['created_at']},
        ])

    @mock_dynamodb2
    def test_request_status(self):
        import main

        db = main.SimpleTodoDB()
        client = TestClient(main.app)
        resp = client.get('/api/v1/task/')
        self.assertEqual(resp.status_code, 200)

        resp = client.post('/api/v1/task/', json={'title': 'title 1'})
        self.assertEqual(resp.status_code, 201)
        id_ = resp.json()['id']

        resp = client.patch(f'/api/v1/task/{id_}', json={'is_done': True})
        self.assertEqual(resp.status_code, 307)

        resp = client.patch(f'/api/v1/task/{id_}/', json={'is_done': True})
        self.assertEqual(resp.status_code, 200)

        resp = client.delete(f'/api/v1/task/{id_}/')
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(db.list(), [])
