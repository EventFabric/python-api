"""example using eventfabric api client library to send an arbitrary json
file as an event"""
from __future__ import print_function

import os
import sys
import json
import argparse

SAMPLE_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.join(SAMPLE_DIR, '..', 'src')
sys.path.append(BASE_DIR)

import eventfabric as ef
import requests

def parse_args():
    """parse and return command line arguments"""
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--username', '-u', metavar='USERNAME',
            required=True,
            help='Username to authenticate to Event Fabric')
    parser.add_argument('--password', '-p', metavar='PASSWORD',
            required=True,
            help='Password to authenticate to Event Fabric')
    parser.add_argument('--channel', '-c', metavar='CHANNEL',
            required=True,
            help='Channel used in the generated event')
    parser.add_argument('--path', '-P', metavar='PATH',
            required=True,
            help='Path to the JSON file you want to send')
    parser.add_argument('--url', '-U', metavar='URL',
            help='URL for Event Fabric API',
            default="https://event-fabric.com/ef/api/")

    return parser.parse_args()

def main():
    """main program entry point"""
    args = parse_args()

    print("Config:", args.username, args.channel, args.path, args.url)

    client = ef.Client(args.username, args.password, args.url)

    try:
        login_ok, login_response = client.login()
        print("Login:", login_ok)

        if not login_ok:
            print("Error authenticating", login_response)
            return

        value = None
        try:
            value = json.load(open(args.path))
        except IOError as error:
            print("Error opening file", args.path, str(error))
            return

        event = ef.Event(value, args.channel)
        send_ok, send_response = client.send_event(event)
        print("Send Event:", send_ok)

        if not send_ok:
            print("Error sending event", send_response)
            return

    except requests.exceptions.ConnectionError as conn_error:
        print("Error connection to server", args.url, str(conn_error))
        return

if __name__ == "__main__":
    main()
