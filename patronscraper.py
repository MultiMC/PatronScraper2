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
    # determine new patrons
    tree = html.fromstring(page.text)
    patrons_extracted = tree.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' favesHover ')]/@title")
    new_patrons = filter(None, map(methodcaller("strip"), patrons_extracted))
    try:
        new_patrons.remove(u'');
    except ValueError:
        pass  # do nothing!

    # determine old patrons
    conn = boto.connect_s3(validate_certs=False)
    bucket = conn.get_bucket('files.multimc.org')
    k = Key(bucket)
    k.key = 'patrons.txt'
    old_patrons = k.get_contents_as_string().decode('utf-8').split('\n')
    old_patrons.sort(key=lambda y: y.lower())
    try:
        old_patrons.remove(u'');
    except ValueError:
        pass  # do nothing!

    # merge lists
    patrons = new_patrons + list(set(old_patrons) - set(new_patrons))
    patrons.sort(key=lambda y: y.lower())

    # print
    old_patron_text = "\n".join(old_patrons) + "\n"
    patron_text = "\n".join(patrons) + "\n"
    print old_patron_text
    print "New:"
    print patron_text

    # upload to s3
    k.set_metadata('Content-Type', 'application/json')
    k.set_contents_from_string(patron_text)
    sys.exit(0)
sys.exit(1)
