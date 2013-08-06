"""example using eventfabric api client library to send fake service status
updates as events"""
from __future__ import print_function

import os
import sys
import time
import random
import argparse
import threading

SAMPLE_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.join(SAMPLE_DIR, '..', 'src')
sys.path.append(BASE_DIR)

import eventfabric as ef
import requests

def now():
    "return current timestamp in ms"
    return int(time.time() * 1000)

START = "start"
STARTED = "started"
ERROR = "error"
ABORTED = "aborted"
FINISHED = "finished"

STATES = {
    START: [STARTED],
    STARTED: [ERROR, ABORTED, FINISHED],
    ERROR: [START],
    ABORTED: [START],
    FINISHED: [START]
}

ERROR_REASONS = [
    "request cannot be fulfilled due to bad syntax",
    "authentication is possible but has failed",
    "payment required, reserved for future use",
    "server refuses to respond to request",
    "requested resource could not be found",
    "request method not supported by that resource",
    "content not acceptable according to the Accept headers",
    "client must first authenticate itself with the proxy",
    "server timed out waiting for the request",
    "request could not be processed because of conflict",
    "resource is no longer available and will not be available again",
    "request did not specify the length of its content",
    "server does not meet request preconditions",
    "request is larger than the server is willing or able to process",
    "URI provided was too long for the server to process",
    "server does not support media type",
    "client has asked for unprovidable portion of the file",
    "server cannot meet requirements of Expect request-header field",
    "request unable to be followed due to semantic errors",
    "resource that is being accessed is locked",
    "request failed due to failure of a previous request",
    "client should switch to a different protocol",
    "origin server requires the request to be conditional",
    "user has sent too many requests in a given amount of time",
    "server is unwilling to process the request",
    "server returns no information and closes the connection",
    "request should be retried after performing action",
    "Windows Parental Controls blocking access to webpage",
    "The server cannot reach the client's mailbox.",
    "connection closed by client while HTTP server is processing",
    "server does not recognise method or lacks ability to fulfill",
    "server received an invalid response from upstream server",
    "server is currently unavailable",
    "gateway did not receive response from upstream server",
    "server does not support the HTTP protocol version",
    "content negotiation for the request results in a circular reference",
    "server is unable to store the representation",
    "server detected an infinite loop while processing the request",
    "bandwidth limit exceeded",
    "further extensions to the request are required",
    "client needs to authenticate to gain network access",
    "network read timeout behind the proxy",
    "network connect timeout behind the proxy"]


class ServiceRunner(threading.Thread):
    """a thread that simulates the state changes of a service and sends them
    to Event Fabric"""

    def __init__(self, name, channel, client, max_sleep):
        threading.Thread.__init__(self)
        self.name = name
        self.state = START
        self.started = None
        self.setDaemon(True)
        self.channel = channel
        self.client = client
        self.max_sleep = max_sleep

    def run(self):
        while True:
            next_state = random.choice(STATES[self.state])
            sleep_time = random.randint(1, self.max_sleep)
            print("sleeping", sleep_time, "seconds")
            time.sleep(sleep_time)

            value = {
                "name": self.name,
                "state": self.state,
                "started": self.started
            }

            if self.state == ERROR:
                value["reason"] = random.choice(ERROR_REASONS)
            elif self.state == START:
                self.started = now()

            if self.state in (ERROR, ABORTED, FINISHED):
                value["ended"] = now()

            event = ef.Event(value, self.channel)

            if self.state != START:
                print(self.client.send_event(event))

            self.state = next_state

def parse_args():
    """parse and return command line arguments"""
    parser = argparse.ArgumentParser(
            description='Send service status updates to Event Fabric')

    parser.add_argument('--username', '-u', metavar='USERNAME',
            required=True,
            help='Username to authenticate to Event Fabric')
    parser.add_argument('--password', '-p', metavar='PASSWORD',
            required=True,
            help='Password to authenticate to Event Fabric')
    parser.add_argument('--channel', '-c', metavar='CHANNEL',
            required=True,
            help='Channel used in the generated event')
    parser.add_argument('--names', '-n', nargs='+',
            required=True,
            help='Names of services to generate events')
    parser.add_argument('--sleep', '-s', type=int, default=10,
            required=True,
            help='Maximum interval between status for a service')
    parser.add_argument('--url', '-U', metavar='URL',
            help='URL for Event Fabric API',
            default="https://event-fabric.com/ef/api/")

    return parser.parse_args()

def main():
    "program entry point"
    args = parse_args()
    print("Config:", args.username, args.channel, args.names, args.sleep)
    client = ef.Client(args.username, args.password, args.url)

    try:
        login_ok, login_response = client.login()
        print("Login:", login_ok)

        if not login_ok:
            print("Error authenticating", login_response)
            return
    except requests.exceptions.ConnectionError as conn_error:
        print("Error connection to server", args.url, str(conn_error))
        return

    for name in args.names:
        service_runner = ServiceRunner(name, args.channel, client, args.sleep)
        service_runner.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Keyboard interrupt, closing")
            break

if __name__ == "__main__":
    main()
