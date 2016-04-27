from __future__ import print_function
import string
import sys
import json
import unicodedata

from jira_auth import get_auth_header, get_jira_server, connect as jira_connect

project_id = 'GT'
start_index = 2
# can't trust the first failure we get from the API, since we've seen missing
# issues and other bad results -- so walk to a manually specified limit
max_issue_num = 700


def ensure_ascii(mystring):
    """
    Decode a string of unknown type (UTF-x or ASCII) to ASCII

    Args:
        @mystring
        String input, unicode or ascii
    """
    if isinstance(mystring, unicode):
        mystring = unicodedata.normalize('NFKD', mystring)
        mystring = mystring.encode('ascii', 'ignore')
    return mystring


def get_issue_json(auth_header, issue_id):
    """
    Looks up the JSON representation of an issue from a server.

    Args:
        @auth_header
        The (username,password) encoded in b64 as the Authorization
        header.

        @issue_id
        The issue's short identifier. Ex: "INF-101"
    """
    conn = jira_connect()

    ISSUE_URI = '/rest/api/2/issue/{0}'.format(issue_id)
    headers = {'Authorization': auth_header,
               'Content-Type': 'application/json'}
    conn.request('GET', ISSUE_URI, None, headers)
    response = conn.getresponse()

    if response.status != 200:
        return None

    result = json.loads(response.read())
    conn.close()
    return result


def format_issue(issue, template_str):
    template = string.Template(template_str)

    status_string = issue['fields']['status']['name']
    if status_string in ('Closed', 'Resolved'):
        status_string += ' {}'.format(issue['fields']['updated'][:10])
    status_string = ensure_ascii(status_string)

    def get_comment_author(comment):
        try:
            return ensure_ascii(comment['updateAuthor']['displayName'])
        except KeyError:
            return 'Anonymous'

    comment_string = '\n'.join(
        '{} - {}:: {}'.format(
            get_comment_author(c),
            ensure_ascii(c['created'][:10]),
            ensure_ascii(c['body']))
        for c in issue['fields']['comment']['comments'])

    return template.substitute(
        issue_id=issue['key'], summary=issue['fields']['summary'],
        type=issue['fields']['issuetype']['name'],
        status=status_string,
        description=ensure_ascii(issue['fields']['description']),
        comments=comment_string)


if __name__ == '__main__':
    def positive_integers():
        cur = start_index
        while True:
            yield cur
            cur += 1

    jira_server = get_jira_server()
    auth_header = get_auth_header()
    with open('template.adoc', 'r') as f:
        template_str = f.read()

    for i in positive_integers():
        issue_name = '{}-{}'.format(project_id, i)
        issue = get_issue_json(auth_header, issue_name)
        if issue is None:
            pass
        else:
            print(format_issue(issue, template_str))

        if i > max_issue_num:
            sys.exit(0)
