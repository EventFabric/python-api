"""Event Fabric API Client Library"""
from __future__ import print_function

import sys
import json

try:
    import requests
except ImportError:
    print("Couldn't import requests library")
    print("Install it with 'pip install requests' and try again")
    sys.exit(-1)

class Client(object):
    """API Client"""
    def __init__(self, username, password,
            root_url="https://event-fabric.com/"):
        self.root_url = root_url if root_url.endswith("/") else root_url + "/"
        self.username = username
        self.token = None
        self.session_header_name = "x-session"
        self.password = password

    def login(self, requester=requests.post):
        """login to the service with the specified credentials, return a tuple
        with a boolean specifying if the login was successful and the response
        object"""
        headers = {'content-type': 'application/json'}
        response = requester(self.endpoint("sessions"),
                verify = False,
                data=json.dumps(self.credentials), headers=headers)

        self.token = response.json().get("token")

        status_ok = response.status_code in (200, 201)
        return status_ok, response

    @property
    def credentials(self):
        """get credentials information"""
        return {
                "username": self.username,
                "password": self.password
        }

    def endpoint(self, path):
        """return the service endpoint for path"""
        return self.root_url + path

    def send_event(self, event, requester=requests.post):
        """send event to server, return a tuple with a boolean specifying if
        the login was successful and the response object"""
 
        headers = {'content-type': 'application/json'}
        if self.token:
            headers[self.session_header_name] = self.token
        url = self.endpoint("streams") + "/" + (event.username or self.username) + "/" + event.channel + "/"
        response = requester(url,
                verify = False,
                data=json.dumps(event.value),
                headers=headers)

        status_ok = response.status_code in (200, 201)
        return status_ok, response

class Event(object):
    """an object representing an event to be sent to the server,
    
    value is a free form json value that contains the information from
    the event.
    channel is a string with the name that identifies this kind of events
    username is the logged in username"""

    def __init__(self, value, channel, username=None):
        self.value = value
        self.channel = channel
        self.username = username

    @property
    def json(self):
        """return a json representation of the object"""
        res = {"value": self.value, "channel": self.channel}
        if self.username is not None:
            res["username"] = self.username
        return res

    def __str__(self):
        return json.dumps(self.json)
