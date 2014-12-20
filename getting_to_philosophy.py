#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import urllib2
import re
import sys

# Improperly formated names will occasionally redirect
def wiki_redirect(page_contents):
  redirect_link = re.search(r"\[\[([\w\s\(\)\|]+)\]\]", page_contents)
  redirect_link = redirect_link.group(1).split("|")[0]
  redirect_link = re.sub(r'\s', '_', redirect_link.strip())
  wiki_page_json = json.load(urllib2.urlopen("http://en.wikipedia.org/w/api.php?format=json&action=query&continue=&titles={0}&prop=revisions&rvprop=content&section=0".format(redirect_link)))

  # If no page found there is no query
  if 'query' not in wiki_page_json:
    raise Exception("Wiki page could not be found")

  # Since it gives the actual revision number as a key
  current_rev = wiki_page_json['query']['pages'].keys()[0]

  # Finally grab contents
  page_contents = wiki_page_json['query']['pages'][current_rev]['revisions'][0]['*']

  return page_contents

def remove_wiki_meta_data(page_contents):
  balance = False
  open_brace = 0
  close_brace = 0
  while not balance:
    current_line = re.search(r'.*', page_contents).group(0)
    open_brace += current_line.count("{{")
    close_brace += current_line.count("}}")
    if open_brace == close_brace:
      balance = True
    page_contents = page_contents.split("\n", 1)[1]

  return page_contents.strip()


# Leverages Wikipedia api to grab contents of current page revision
# Returns first matched linnk
def grab_first_wiki_link(page_name):
  print page_to_search
  # Wiki api call for getting the latest revision of a page
  wiki_page_json = json.load(urllib2.urlopen("http://en.wikipedia.org/w/api.php?format=json&action=query&continue=&titles={0}&prop=revisions&rvprop=content&section=0".format(page_name)))

  # If no page found there is no query
  if 'query' not in wiki_page_json:
    raise Exception("Wiki page could not be found")

  # Since it gives the actual revision number as a key
  current_rev = wiki_page_json['query']['pages'].keys()[0]

  # Finally grab contents
  page_contents = wiki_page_json['query']['pages'][current_rev]['revisions'][0]['*']

  # Handle wiki redirect
  if page_contents.startswith("#REDIRECT"):
    page_contents = wiki_redirect(page_contents)

  # Contents needs some formatting at front
  # Remove images that confuses links
  page_contents = re.sub(r'\[\[File:.*\]\]', '', page_contents)

  # Reomve references
  page_contents = re.sub(r'<ref.*?</ref>', '', page_contents)
  
  # Remove meta and listbox
  while page_contents.startswith("{{"):
    page_contents = remove_wiki_meta_data(page_contents)

  # Ignore things between parens except links
  page_contents = re.sub(r'\([^)]*\)(?!\|)', '', page_contents, count=1)
  

  # Links are enclosed with [[  ]] so grab the first one
  link_match = re.search(r"\[\[([#\w\s\(\)\|\-]+)\]\]", page_contents)
  
  # Edge case where no link found
  if not link_match:
    return None

  # Drop the pipe
  link_match = link_match.group(1).split("|")[0]
  return link_match



# Require correct number of args
if len(sys.argv) < 2:
  print "Please provide link to wikipedia page"
  sys.exit()
if len(sys.argv) > 2:
  print "Too many arguements given"
  sys.exit()

# Try and get page name
try:
  page_to_search = sys.argv[1].rsplit("/", 1)[1]
except:
  print "Improper url given"
  sys.exit()

hop_count = 0
MAX_HOPS = 100

# Main loop
print "http://en.wikipedia.org/wiki/{0}".format(page_to_search)
while page_to_search.lower() != "philosophy":

  #Catch any errors and exit gracefully
  # try:
  page_to_search = grab_first_wiki_link(page_to_search)
  # Drop hash tags
  page_to_search = page_to_search.split('#', 1)[0]
  # except Exception as e:
  #   print e
  #   sys.exit()

  # Edge case where no link found on page
  if not page_to_search:
    print "No link found"
    break
  
  # Format for new link
  page_to_search = re.sub(r'\s', '_', page_to_search.strip())

  # Print next check and increment
  print "http://en.wikipedia.org/wiki/{0}".format(page_to_search)
  hop_count +=1
  # break

  # Break out on max hops
  if hop_count == MAX_HOPS:
    print "Max hop of {} reached".format(MAX_HOPS)
    break
else:
  print "{} hops".format(hop_count)