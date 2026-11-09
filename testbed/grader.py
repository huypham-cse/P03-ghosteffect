"""Injector/grader-only backend observations; never import into a GUI agent.

Count at a finite observation horizon. Zero is OBSERVED_ZERO, never permanent
absence. Pending requests and preapply-reject scope require proxy receipts too.
Credentials are read from named environment variables, not CLI values/logs.
"""
import argparse
import base64
import email
import imaplib
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def fetch(url, method='GET', headers=None, body=None):
    request = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    with urllib.request.urlopen(request, timeout=35) as response:
        return response.read()


def matrix_count(origin, room, tag, token, max_pages=100):
    endpoint = origin.rstrip('/') + '/_matrix/client/v3/rooms/' + urllib.parse.quote(room, safe='') + '/messages'
    headers, events, seen = {'Authorization': 'Bearer ' + token}, set(), set()
    cursor = None
    for _ in range(max_pages):
        query = {'dir': 'b', 'limit': '100'}
        if cursor:
            query['from'] = cursor
        page = json.loads(fetch(endpoint + '?' + urllib.parse.urlencode(query), headers=headers))
        chunk = page['chunk']
        for event in chunk:
            if event.get('type') == 'm.room.message' and tag in event.get('content', {}).get('body', ''):
                events.add(event['event_id'])
        end = page.get('end')
        if not chunk or not end or end == cursor:
            return dict(copies=len(events), event_ids=sorted(events), scan_complete=True)
        if end in seen:
            raise RuntimeError('Matrix pagination loop; incomplete grade')
        seen.add(end)
        cursor = end
    raise RuntimeError('Matrix history scan limit; incomplete grade')


def imap_count(host, port, mailbox, tag, username, password):
    # Local isolated backend only. Receiver Inbox, not client-written Sent.
    if not tag.isascii() or any(c in tag for c in '\r\n"\\'):
        raise ValueError('use a unique ASCII test tag without IMAP control characters')
    client = imaplib.IMAP4(host, port)
    try:
        client.login(username, password)
        status, _ = client.select(mailbox, readonly=True)
        if status != 'OK':
            raise RuntimeError('receiver mailbox not selectable')
        status, data = client.uid('search', None, 'TEXT', '"' + tag + '"')
        if status != 'OK':
            raise RuntimeError('receiver search failed')
        uids = data[0].decode('ascii').split()
        return dict(copies=len(uids), receiver_uids=uids, scan_complete=True,
                    scope='receiver mailbox at this horizon; not client Sent state')
    finally:
        try:
            client.logout()
        except imaplib.IMAP4.error:
            pass


def caldav_count(collection, tag, username, password):
    credentials = base64.b64encode((username + ':' + password).encode()).decode()
    headers = {'Authorization': 'Basic ' + credentials, 'Depth': '1', 'Content-Type': 'application/xml'}
    body = b'<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>'
    tree = ET.fromstring(fetch(collection, 'PROPFIND', headers, body))
    found = set()
    origin = urllib.parse.urlsplit(collection)
    for response in tree.findall('{DAV:}response'):
        href = response.findtext('{DAV:}href')
        if not href or response.find('.//{DAV:}collection') is not None:
            continue
        url = urllib.parse.urljoin(collection, href)
        parsed = urllib.parse.urlsplit(url)
        if (parsed.scheme, parsed.netloc) != (origin.scheme, origin.netloc):
            raise RuntimeError('backend returned an out-of-origin href')
        if tag.encode() in fetch(url, headers={'Authorization': headers['Authorization']}):
            found.add(href)
    return dict(copies=len(found), hrefs=sorted(found), scan_complete=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', choices=['matrix', 'imap', 'caldav'], required=True)
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--room', help='Matrix room ID')
    parser.add_argument('--mailbox', default='INBOX')
    parser.add_argument('--tag', required=True, help='unique test fixture content tag')
    parser.add_argument('--token-env', default='GX_GRADER_MATRIX_TOKEN')
    parser.add_argument('--username-env', default='GX_GRADER_USER')
    parser.add_argument('--password-env', default='GX_GRADER_PASSWORD')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('fresh evidence output required')
    started = time.monotonic_ns()
    if args.protocol == 'matrix':
        if not args.room:
            parser.error('--room required for Matrix')
        result = matrix_count(args.endpoint, args.room, args.tag, os.environ[args.token_env])
    elif args.protocol == 'imap':
        parsed = urllib.parse.urlsplit(args.endpoint)
        if parsed.scheme != 'imap' or not parsed.hostname or not parsed.port:
            parser.error('local test endpoint must be imap://host:port')
        result = imap_count(parsed.hostname, parsed.port, args.mailbox, args.tag,
                            os.environ[args.username_env], os.environ[args.password_env])
    else:
        result = caldav_count(args.endpoint, args.tag, os.environ[args.username_env], os.environ[args.password_env])
    result.update(kind='backend-only observation', protocol=args.protocol,
                  mono_start_ns=started, mono_end_ns=time.monotonic_ns(), utc_ns=time.time_ns(),
                  outcome_at_horizon='OBSERVED_COMMIT' if result['copies'] else 'OBSERVED_ZERO',
                  permanent_absence_proved=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(args.output), 'copies': result['copies']}))


if __name__ == '__main__':
    main()
