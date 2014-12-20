#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import urllib2

test_page = "Philosophy"

wiki_page_json = json.load(urllib2.urlopen("http://en.wikipedia.org/w/api.php?format=json&action=query&continue=&titles={0}&prop=revisions&rvprop=content".format(test_page)))

current_rev = wiki_page_json['query']['pages'].keys()[0]

print wiki_page_json['query']['pages'][current_rev]['revisions'][0]['*']

#print json.dumps(wiki_page_json, sort_keys=True, indent=4)