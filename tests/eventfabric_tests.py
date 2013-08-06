"tests for event fabric API"
import os
import sys
import json
import unittest

TEST_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.join(TEST_DIR, '..')
sys.path.append(BASE_DIR)

import eventfabric as ef

class FakeResponse(object):
    "fake response object"
    def __init__(self, status_code=200, cookies=None):
        self.status_code = status_code
        self.cookies = cookies

def fake_post(storage, return_value):
    "build a fake post function"
    def fun(*args, **kwargs):
        "receives and stores all args, returns return_value"
        storage.append((args, kwargs))
        return return_value

    return fun


class TestEventFabric(unittest.TestCase):
    "tests event fabric api"

    def test_client_creation(self):
        "test that the client is created and parameters are set correctly"
        client = ef.Client("username", "password",
                "http://localhost:8080/ef/api")
        self.assertEqual(client.username, "username")
        self.assertEqual(client.password, "password")
        self.assertEqual(client.root_url, "http://localhost:8080/ef/api/")
        self.assertEqual(client.cookies, None)
        self.assertEqual(client.credentials["username"], "username")
        self.assertEqual(client.credentials["password"], "password")

    def test_endpoint(self):
        "tests that endpoints are created correctly"
        client = ef.Client("username", "password",
                "http://localhost:8080/ef/api")
        self.assertEqual(client.endpoint("session"),
                "http://localhost:8080/ef/api/session")

    def test_login(self):
        client = ef.Client("username", "password",
                "http://localhost:8080/ef/api")
        storage = []
        requester = fake_post(storage, FakeResponse(200, "cookies!"))
        status, response = client.login(requester)
        args, kwargs = storage.pop()
        endpoint = args[0]
        data_arg = kwargs["data"]
        headers = kwargs["headers"]

        self.assertTrue(status) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies, "cookies!")
        self.assertEqual(response.cookies, client.cookies)
        self.assertEqual(data_arg, json.dumps(client.credentials))
        self.assertEqual(headers["content-type"], "application/json")
        self.assertEqual(endpoint, "http://localhost:8080/ef/api/session")

    def test_send_event(self):
        client = ef.Client("username", "password",
                "http://localhost:8080/ef/api")
        storage = []
        requester = fake_post(storage, FakeResponse(201))
        data = {"name": "bob", "count": 10}
        channel = "my.channel"
        event = ef.Event(data, channel)
        status, response = client.send_event(event, requester)
        args, kwargs = storage.pop()
        endpoint = args[0]
        data_arg = kwargs["data"]
        headers = kwargs["headers"]

        self.assertTrue(status) 
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data_arg, json.dumps(event.json))
        self.assertEqual(headers["content-type"], "application/json")
        self.assertEqual(endpoint, "http://localhost:8080/ef/api/event")

if __name__ == '__main__':
    unittest.main()
