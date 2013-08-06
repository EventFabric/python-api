"""example using eventfabric api client library to send an arbitrary json
file as an event"""
from __future__ import print_function

import sys
import json

import eventfabric as ef

def main():
    username, password, channel, path = sys.argv[1:]

    print("Config:", username, channel, path, api_root)

    c = ef.Client(username, password, "http://localhost:8080/ef/api/")

    print("Login:", c.login())
    value = json.load(open(path))
    event = ef.Event(value, channel, username)
    print("Send Event:", c.send_event(event))

if __name__ == "__main__":
    main()
