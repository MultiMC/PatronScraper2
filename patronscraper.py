#!/usr/bin/env python2
from lxml import html
import requests
from operator import methodcaller
import sys
import boto
from boto.s3.key import Key
import ssl

# See: https://github.com/boto/boto/issues/2836
if hasattr(ssl, '_create_unverified_context'):
   ssl._create_default_https_context = ssl._create_unverified_context

page = requests.get('https://www.patreon.com/user?u=130816&ty=p')
if page.status_code == requests.codes.ok:
    tree = html.fromstring(page.text)
    patrons = tree.xpath("//div[contains(concat(' ', normalize-space(@class), ' '), ' shareWindow ')]/h1/a/text()")
    patron_text = "\n".join(filter(None, map(methodcaller("strip"), patrons))) + "\n"
    conn = boto.connect_s3(validate_certs=False)
    bucket = conn.get_bucket('files.multimc.org')
    k = Key(bucket)
    k.key = 'patrons.txt'
    print k.get_contents_as_string().decode('utf-8')
    print "New:"
    print patron_text
    k.set_metadata('Content-Type', 'application/json')
    k.set_contents_from_string(patron_text)
    sys.exit(0)
sys.exit(1)
