#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import urllib2
import re

def grab_first_wiki_link(page_name):
  # Wiki api call for getting the latest revision of a page
  wiki_page_json = json.load(urllib2.urlopen("http://en.wikipedia.org/w/api.php?format=json&action=query&continue=&titles={0}&prop=revisions&rvprop=content".format(page_name)))

  # Since it gives the actual revision number
  current_rev = wiki_page_json['query']['pages'].keys()[0]

  # Links are enclosed with [[  ]]
  page_contents = wiki_page_json['query']['pages'][current_rev]['revisions'][0]['*']
  link_match = re.search(r"\[\[([\w\s\(\)]+)\]\]", page_contents)

  return link_match.group(1)


page_to_search = "Philosophy"
page_to_search = "Property_(philosophy)".capitalize()
hop_count = 0

print "http://en.wikipedia.org/wiki/{0}".format(page_to_search)

while page_to_search.lower() != "philosophy":
  page_to_search = grab_first_wiki_link(page_to_search)
  page_to_search = re.sub(r'\s', '_', page_to_search.strip()).capitalize()
  print "http://en.wikipedia.org/wiki/{0}".format(page_to_search)
  hop_count +=1

print "{} hops".format(hop_count)