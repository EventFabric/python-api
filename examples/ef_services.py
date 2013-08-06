import ef
import sys
import time
import math
import random
import threading
import itertools

username, password, channel, sleep_s_str, name_csv = sys.argv[1:]
sleep_s = int(sleep_s_str)
names = [name.strip() for name in name_csv.split(",")]

print "starting with", username, password, channel, names
c = ef.Client("http://localhost:8080/ef/api/", username, password)

print(c.login())

def now():
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

MAX_SLEEP_BY_STATE = {
    START: int(sleep_s / 3.0) + 1,
    STARTED: sleep_s,
    ERROR: sleep_s,
    ABORTED: sleep_s,
    FINISHED: sleep_s
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
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.state = START
        self.started = None
        self.setDaemon(True)

    def run(self):
        while True:
            next_state = random.choice(STATES[self.state])
            sleep_time = random.randint(1, MAX_SLEEP_BY_STATE[self.state])
            print "sleeping", sleep_time, "seconds"
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

            event = ef.Event(value, channel, username)

            if self.state != START:
                print c.send_event(event)

            self.state = next_state

if __name__ == "__main__":
    for name in names:
        service_runner = ServiceRunner(name)
        service_runner.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "closing"
            break
