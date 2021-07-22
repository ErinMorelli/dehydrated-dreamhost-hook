#!/usr/bin/env python
"""
Copyright (c) 2016-2021 Erin Morelli

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
"""

import os
import sys
import time

import requests
import dns.resolver
import dns.exception

import deploy

# DNS globals
DNS_PREFIX = '_acme-challenge'
DNS_COUNTER = 0

# Attempt to find Dreamhost API key in environment
try:
    HOST_API_KEY = os.environ['DREAMHOST_API_KEY']
except KeyError:
    print(' + Unable to locate Dreamhost API key in environment!')
    sys.exit(1)

# Dreamhost API Globals
HOST_API_ROOT = 'https://api.dreamhost.com'
HOST_API_PARAMS = {
    'key': HOST_API_KEY,
    'format': 'json',
}


def remove_record(record, value):
    """Remove a TXT DNS record via Dreamhost API."""
    remove_params = HOST_API_PARAMS
    remove_params['cmd'] = 'dns-remove_record'
    remove_params['record'] = record
    remove_params['type'] = 'TXT'
    remove_params['value'] = value

    # Set up GET request
    res = requests.get(HOST_API_ROOT, params=remove_params)

    # Return response object
    return res.json()


def add_record(record, value):
    """Add a TXT DNS record via Dreamhost API."""
    add_params = HOST_API_PARAMS
    add_params['cmd'] = 'dns-add_record'
    add_params['record'] = record
    add_params['type'] = 'TXT'
    add_params['value'] = value

    # Set up GET request
    res = requests.get(HOST_API_ROOT, params=add_params)

    # Return response object
    return res.json()


def record_exists(record):
    """Check if TXT DNS record exists via Dreamhost API."""
    exist_params = HOST_API_PARAMS
    exist_params['cmd'] = 'dns-list_records'

    # Set up GET request
    res = requests.get(HOST_API_ROOT, params=exist_params)

    # Get results
    dns_list = res.json()

    # Check results for
    for dns_item in dns_list['data']:
        # If we found it, return True with the value
        if dns_item['record'] == record:
            return True, dns_item['value']

    # Otherwise, return false
    return False, None


def has_dns_propagated(record, value):
    """Check TXT DNS records for update via MX Toolbox API."""
    global DNS_COUNTER

    # Set up storage for TXT records
    txt_records = []

    try:
        # Query TXT DNS records
        answer = dns.resolver.query(record, 'TXT')

        # Store TXT values from response
        for rdata in answer:
            txt_records.append(rdata.to_text()[1:-1])

    except dns.exception.DNSException:
        # Bail if the query failed
        return False

    # Look for expected value in results
    if value in txt_records:
        # Increase seen counter
        DNS_COUNTER += 1
        print(f' + New record seen {DNS_COUNTER} times')

        # Return true if we've seen this enough times
        if DNS_COUNTER == 3:
            return True

    # Return not propagated
    return False


def deploy_challenge(args):
    """Add required TXT DNS record and wait for it to propagate."""
    domain = args[0]
    token = args[2]

    # Set up record
    record = '{0}.{1}'.format(DNS_PREFIX, domain)

    # Check if record exists
    print(f' + Checking if TXT record for {record} exists...')
    (exists, value) = record_exists(record)

    if exists:
        # If it exists but does not have the token we need, remove it
        print(' + Old TXT record found, removing...')
        removed = remove_record(record, value)
        print(f" + {removed['data']}: {removed['result']}")

        print(' + Settling down for 10s...')
        time.sleep(10)

    # Add new record
    print(f' + Adding new TXT record {token}...')
    added = add_record(record, token)
    print(f" + {added['data']}: {added['result']}")

    # Sleep to give record time to update
    print(' + Settling down for 10s...')
    time.sleep(10)

    # Wait for the DNS change to propagate
    while has_dns_propagated(record, token) is False:
        print(' + DNS not propagated, waiting 30s...')
        time.sleep(30)


def clean_challenge(args):
    """Clean up by removing any leftover TXT DNS records."""
    domain = args[0]

    # Set up record
    record = f'{DNS_PREFIX}.{domain}'

    # Check if record exists
    print(f' + Checking if TXT record for {record} exists...')
    (exists, value) = record_exists(record)

    if exists:
        # Sleep before removing to allow request to complete
        print(' + Old TXT record found, waiting 30s before removing...')
        time.sleep(30)

        # If it exists but does not have the token we need, remove it
        print(' + Removing old TXT record...')
        removed = remove_record(record, value)
        print(f" + {removed['data']}: {removed['result']}")


def deploy_cert(args):
    """Print out information about our new certs."""
    privkey_file = args[1]
    cert_file = args[2]
    fullchain_file = args[3]

    # Print results
    print(f' + Private Key: {privkey_file}')
    print(f' + Certificate: {cert_file}')
    print(f' + Full Chain: {fullchain_file}')

    # Run deployment script
    deploy.run_deployment()


def unchanged_cert(args):
    """Print out unchanged certificate notice."""
    domain = args[0]

    # Print message
    print(f' + Existing cert for \'{domain}\' is unchanged. Skipping hook!')


def invalid_challenge(args):
    domain, result = args
    print(f" + Invalid challenge for '{domain}'")
    print(f" + Full error: '{result}'")


def startup_hook(_):
    return


def exit_hook(_):
    return


def run_hook(args):
    """Determine action to take based on CLI args."""
    operations = {
        'deploy_challenge': deploy_challenge,
        'clean_challenge': clean_challenge,
        'deploy_cert': deploy_cert,
        'unchanged_cert': unchanged_cert,
        'invalid_challenge': invalid_challenge,
        'startup_hook': startup_hook,
        'exit_hook': exit_hook
    }

    # Deploy hook operation
    print(f' + Dreamhost hook executing: {args[0]}')
    operations[args[0]](args[1:])


# Run this thing
if __name__ == '__main__':
    run_hook(sys.argv[1:])
