import base64
import os
import subprocess
from getpass import getpass

from verified_https import VerifiedHTTPSConnection


def get_jira_credentials():
    """
    Gets the jira server, username, and password.
    Returns these values as a 3-tuple in that order
    """
    jira_username = raw_input('Please enter your JIRA username: ').strip()
    jira_password = getpass("Please enter your JIRA password: ")
    return (jira_username, jira_password)


def get_auth_header():
    """
    Generates the Basic Auth header content for the headers on an
    HTTPS connection to the JIRA server.
    """
    (jira_username, jira_password) = get_jira_credentials()
    # credentials are base64 encoded for basic auth
    creds = base64.b64encode(jira_username+':'+jira_password)
    return 'Basic ' + creds


def get_jira_server():
    """
    Gets the JIRA server DNS name.
    """
    return 'globus.atlassian.net'


def connect():
    """
    Opens a Verified HTTPS Connection with the JIRA server.
    """
    certs_file = os.path.join(os.path.dirname(__file__), 'all-certs.pem')
    conn = VerifiedHTTPSConnection(get_jira_server(), ca_certs=certs_file)

    return conn
