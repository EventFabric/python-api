"tests for event fabric API"
import os
import sys
import json
import unittest

TEST_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.join(TEST_DIR, '..', 'src')
sys.path.append(BASE_DIR)
USERNAME = "admin"
PASSWORD = "secret"

import eventfabric as ef

class FakeResponse(object):
    "fake response object"
    def __init__(self, status_code=200):
        self.status_code = status_code
    def json(self):
        return {"token": "mytoken"}

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
        client = ef.Client(USERNAME, PASSWORD, "http://localhost:8080/")
        self.assertEqual(client.username, USERNAME)
        self.assertEqual(client.password, PASSWORD)
        self.assertEqual(client.root_url, "http://localhost:8080/")
        self.assertEqual(client.credentials["username"], USERNAME)
        self.assertEqual(client.credentials["password"], PASSWORD)

    def test_endpoint(self):
        "tests that endpoints are created correctly"
        client = ef.Client(USERNAME, PASSWORD, "http://localhost:8080/")
        self.assertEqual(client.endpoint("sessions"),
                "http://localhost:8080/sessions")

    def test_login(self):
        client = ef.Client(USERNAME, PASSWORD, "http://localhost:8080/")
        storage = []
        requester = fake_post(storage, FakeResponse(200))
        status, response = client.login(requester)
        args, kwargs = storage.pop()
        endpoint = args[0]
        data_arg = kwargs["data"]
        headers = kwargs["headers"]

        self.assertTrue(status)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data_arg, json.dumps(client.credentials))
        self.assertEqual(headers["content-type"], "application/json")
        self.assertEqual(endpoint, "http://localhost:8080/sessions")

    def test_send_event(self):
        client = ef.Client(USERNAME, PASSWORD, "http://localhost:8080/")
        storage = []
        requester = fake_post(storage, FakeResponse(201))
        data = {"text": "bob", "percentage": 10}
        channel = "my.channel"
        event = ef.Event(data, channel)
        status, response = client.send_event(event, requester)
        args, kwargs = storage.pop()
        endpoint = args[0]
        data_arg = kwargs["data"]
        headers = kwargs["headers"]

        self.assertTrue(status)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data_arg, json.dumps(event.json["value"]))
        self.assertEqual(headers["content-type"], "application/json")
        self.assertEqual(endpoint, "http://localhost:8080/streams/" + USERNAME + "/" + channel + "/")

if __name__ == '__main__':
    unittest.main()
