#!/usr/bin/env python3


from jsonpath_ng import jsonpath, parse
from munch import Munch

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
    github_event = read_event()

    # Process event
    event_json = process_event(github_event)

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

    return json_data


# Process github event payload
def process_event(github_event):
    # Create new payload
    payload = Munch()

    # Include subset of fields
    payload.action = process_path('$.action', github_event)
    payload.number = process_path('$.number', github_event)
    payload.repository = process_path('$.repository.full_name', github_event)

    # Pull request details
    pull_request = Munch()
    pull_request.state = process_path('$.pull_request.state', github_event)
    pull_request.url = process_path('$.pull_request.html_url', github_event)
    pull_request.branch_name = process_path('$.pull_request.head.ref', github_event)
    pull_request.user_login = process_path('$.pull_request.user.login', github_event)
    pull_request.head_sha = process_path('$.pull_request.head.sha', github_event)
    pull_request.base_sha = process_path('$.pull_request.base.sha', github_event)
    pull_request.merge_commit_sha = process_path('$.pull_request.merge_commit_sha', github_event)
    payload.pull_request = pull_request

    # Review details
    payload.reviewed_by = process_path('$.review', github_event)

    # Merge details
    payload.merged = process_path('$.pull_request.merged', github_event)
    payload.merged_by = process_path('$.pull_request.merged_by', github_event)

    # Return payload
    return {'event': payload}


# Process jsonpath
def process_path(path, json_data):
    # Create expression
    expr = parse(path)

    # Match results
    match = expr.find(json_data)

    if match:
        if len(match) == 1:
            return match[0].value
        else:
            return match

    return None


# Get field if exists
def extract_field(field_name, json_data):
    if field_name in json_data:
        return json_data[field_name]

    return None


# Look up env var
def get_env_var(env_var_name, strict=True):
    # Check env var
    value = os.getenv(env_var_name)

    # Handle missing value
    if not value:
        if strict:
            if env_var_name == 'GITHUB_TOKEN':
                print(f'error: env var not found: {env_var_name}')
                print('''please ensure your workflow step includes
                env:
                    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}''')
                sys.exit(1)

            else:
                print(f'error: env var not found: {env_var_name}')
                sys.exit(1)

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

