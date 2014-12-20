#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import urllib2
import re
import sys


# Leverages Wikipedia api to grab contents of current page revision
# Returns first matched linnk
def grab_first_wiki_link(page_name):
  # Wiki api call for getting the latest revision of a page
  wiki_page_json = json.load(urllib2.urlopen("http://en.wikipedia.org/w/api.php?format=json&action=query&continue=&titles={0}&prop=revisions&rvprop=content".format(page_name)))

  # If no page found there is no query
  if 'query' not in wiki_page_json:
    raise Exception("Wiki page could not be found")

  # Since it gives the actual revision number as a key
  current_rev = wiki_page_json['query']['pages'].keys()[0]

  # Links are enclosed with [[  ]] so grab that
  page_contents = wiki_page_json['query']['pages'][current_rev]['revisions'][0]['*']
  link_match = re.search(r"\[\[([\w\s\(\)]+)\]\]", page_contents)

  # Edge case where no link found
  if not link_match:
    return None

  return link_match.group(1)


# page_to_search = "Philosophy"
# page_to_search = "Property_(philosophy)".capitalize()

if len(sys.argv) < 2:
  print "Please provide link to wikipedia page"
  sys.exit()
if len(sys.argv) > 2:
  print "Too many arguements given"
  sys.exit()

try:
  page_to_search = sys.argv[1].rsplit("/", 1)[1]
except:
  print "Improper url given"
  sys.exit()

hop_count = 0
MAX_HOPS = 100


print "http://en.wikipedia.org/wiki/{0}".format(page_to_search)

while page_to_search.lower() != "philosophy":

  #Catch any errors and exit gracefully
  try:
    page_to_search = grab_first_wiki_link(page_to_search)
  except Exception as e:
    print e
    sys.exit()

  # Edge case where no link found on page
  if not page_to_search:
    print "No link found"
    break
  page_to_search = re.sub(r'\s', '_', page_to_search.strip()).capitalize()
  print "http://en.wikipedia.org/wiki/{0}".format(page_to_search)
  hop_count +=1
  if hop_count == MAX_HOPS:
    print "Max hop of {} reached".format(MAX_HOPS)
    break
else:
  print "{} hops".format(hop_count)