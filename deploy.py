#!/usr/bin/env python
"""
Deploys new Let's Encrypt certificate.

Copyright (c) 2016 Erin Morelli

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

from __future__ import print_function
import filecmp
import os
import sys
import shutil
import subprocess
import yaml


# Define letsencrypt.sh defaults
LETSENCRYPT_ROOT = '/etc/dehydrated/certs/{domain}/{pem}.pem'

# Set user config file path
CONFIG_FILE = os.path.join(
    os.path.expanduser('~'), '.config', 'dehydrated', 'deploy.conf')

# Set generic error message template
ERROR = ' + ERROR: Could not locate {name} files:\n\t{files}'


def parse_config():
    """Parse the user config file."""
    print(
        '# INFO: Using deployment config file {0}'.format(CONFIG_FILE),
        file=sys.stdout
    )

    # Make sure file exists
    if not os.path.exists(CONFIG_FILE):
        sys.exit(ERROR.format(name='deployment config', files=CONFIG_FILE))

    # Parse YAML config file
    return yaml.load(open(CONFIG_FILE, 'r'))


def deploy_file(file_type, old_file, new_file):
    """Deploy new file and store old file."""
    # If the two files are the same, bail
    if filecmp.cmp(old_file, new_file):
        print(
            ' + WARNING: {0} matches new {1}, skipping deployment'.format(
                old_file,
                file_type
            ),
            file=sys.stdout
        )
        return False

    # Get old file information
    stat = os.stat(old_file)

    # Rename existing file
    os.rename(old_file, '{0}.bak'.format(old_file))

    # # Copy new file
    shutil.copy(new_file, old_file)

    # Update file ownership
    os.chown(old_file, stat.st_uid, stat.st_gid)

    # Update file permissions
    os.chmod(old_file, stat.st_mode)

    print(
        ' + Succesfully deployed new {0} to {1}'.format(file_type, old_file),
        file=sys.stdout
    )
    return True


def deploy_domain(domain, config):
    """Deploy new certs for a given domain."""
    print('Deploying new files for: {0}'.format(domain), file=sys.stdout)
    deployed = False

    # Deploy new certs for each location
    for location in config:

        # Loop through file types
        for file_type in location.keys():

            # Get the new version of this file
            new_file = LETSENCRYPT_ROOT.format(domain=domain, pem=file_type)

            # Make sure it exists
            if not os.path.exists(new_file):
                sys.exit(
                    ERROR.format(
                        name='new {0}'.format(file_type),
                        files=new_file
                    )
                )

            # Get the old version
            old_file = location[file_type]

            # Make sure it exists
            if not os.path.exists(old_file):
                sys.exit(
                    ERROR.format(
                        name='old {0}'.format(file_type),
                        files=old_file
                    )
                )

            # Deploy new file
            deploy_success = deploy_file(file_type, old_file, new_file)

            # Set deploy status
            if deploy_success:
                deployed = True

    return deployed


def run_deployment():
    """Main wrapper function."""
    print('Starting new file deployment', file=sys.stdout)

    # Get user deploy config
    config = parse_config()

    # Monitor for new deloyments
    saw_new_deployments = False

    # Iterate over domains
    for domain in config['domains'].keys():

        # Deploy new files for the domain
        deployed = deploy_domain(domain, config['domains'][domain])

        if deployed:
            saw_new_deployments = True

    # Only run post-deployment actions if we saw new deploys
    if saw_new_deployments:

        # Run post deployment actions
        print('Starting post-deployment actions', file=sys.stdout)

        for action in config['post_actions']:
            print(' + Attempting action: {0}'.format(action), file=sys.stdout)

            try:
                # Attempt action
                status = subprocess.call(action, shell=True)

                # Return result
                print(
                    ' + Action exited with status {0}'.format(status),
                    file=sys.stdout
                )
            except OSError as error:
                # Catch errors
                print(' + ERROR: {0}'.format(error), file=sys.stderr)

    print('New file deployment done.', file=sys.stdout)


if __name__ == '__main__':
    run_deployment()
