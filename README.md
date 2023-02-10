# Splunk Audit Github Action


## Overview

This Github Action posts the Github trigger event payload to a target Splunk HEC endpoint.


## Requirements


### Environment

The following environment variables are required to run this Github Action:

```
SPLUNK_WEBHOOK_URL  # Splunk HEC endpoint URL
SPLUNK_HEC_TOKEN    # Auth token associated with Splunk HEC endpoint
```


### Github Action Workflow

This action can be configured to work on any trigger. Here is an example trigger configuration:


```
on:
  pull_request_review:
    types: [ submitted ]

  pull_request:
    types: [ opened, synchronize, reopened, edited ]
    branches:
      - master
...

```


### Example Action

```
    - name: Splunk Audit
      uses: mx51/splunk-audit-action@master
      env:
        SPLUNK_WEBHOOK_URL: ${{ secrets.SPLUNK_WEBHOOK_URL }}
        SPLUNK_HEC_TOKEN: ${{ secrets.SPLUNK_HEC_TOKEN }}
```


## References

- https://docs.github.com/en/actions/creating-actions/creating-a-composite-action
- https://medium.com/intelligentmachines/github-actions-building-and-publishing-own-actions-using-python-d94e2724b08c


