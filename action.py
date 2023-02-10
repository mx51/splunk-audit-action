#!/usr/bin/env python3

import github
import json
import os
import re
import requests
import signal
import sys


###
# MAIN METHOD
###

def main():
    # Get event details
    event_json = read_event()

    # Send to splunk
    splunk_hook_url = get_env_var('SPLUNK_WEBHOOK_URL')
    splunk_hec_token = get_env_var('SPLUNK_HEC_TOKEN')
    post_to_webhook(splunk_hook_url, splunk_hec_token, event_json)

    # Finished
    log(' * Payload posted successfully to Splunk')


def post_to_webhook(splunk_hook_url, splunk_hec_token, event_json):
    # Prepare post header
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Splunk {splunk_hec_token}'
    }

    # Send post
    response = requests.post(
        splunk_hook_url, data=json.dumps(event_json), headers=headers
    )

    # Check response
    if response.status_code != 200:
        log('error: splunk request failed: %s' % response.text)
        sys.exit(1)


# Read github event data
def read_event():
    # Find path
    event_path = get_env_var('GITHUB_EVENT_PATH')

    # Read json contents
    with open(event_path, 'r') as f:
        json_data = json.load(f)

    return {'event': json_data}


# Look up env var
def get_env_var(env_var_name, strict=True):
    # Check env var
    value = os.getenv(env_var_name)

    # Handle missing value
    if not value:
        if strict:
            print(f'error: env var not found: {env_var_name}')
            sys.exit(1)
        else:
            print(f'warning: env var not found: {env_var_name}')

    return value


# Print wrapper
def log(msg):
    print(msg, flush=True)


# Handle interrupt
def signal_handler(_, __):
    print(' ')
    sys.exit(0)


####
# MAIN
####

# Set up Ctrl-C handler
signal.signal(signal.SIGINT, signal_handler)

# Invoke main method
if __name__ == '__main__':
    main()

