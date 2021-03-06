#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import urllib2
import re
import sys
from HTMLParser import HTMLParser

# HTML tag stripper
class MLStripper(HTMLParser):
  def __init__(self):
    self.reset()
    self.fed = []
  def handle_data(self, d):
    self.fed.append(d)
  def get_data(self):
    return ''.join(self.fed)

def strip_tags(html):
  s = MLStripper()
  s.feed(html)
  return s.get_data()

# Improperly formated names will occasionally redirect
def wiki_redirect(page_contents):
  redirect_link = re.search(r"\[\[(.+?)\]\]", page_contents)
  redirect_link = redirect_link.group(1).split("|")[0]
  redirect_link = redirect_link.split('#', 1)[0]
  redirect_link = re.sub(r'\s', '_', redirect_link.strip())
  wiki_page_json = json.load(urllib2.urlopen("http://en.wikipedia.org/w/api.php?format=json&action=query&continue=&titles={0}&prop=revisions&rvprop=content&section=0".format(redirect_link.encode('utf-8'))))

  # If no page found there is no query
  if 'query' not in wiki_page_json:
    raise Exception("Wiki page could not be found")

  # Since it gives the actual revision number as a key
  current_rev = wiki_page_json['query']['pages'].keys()[0]

  # Finally grab contents
  page_contents = wiki_page_json['query']['pages'][current_rev]['revisions'][0]['*']

  return page_contents

def remove_wiki_meta_data(page_contents):
  open_brace = 0
  close_brace = 0
  for current_line in page_contents:
    open_brace += current_line.count("{")
    close_brace += current_line.count("}")
    if open_brace == close_brace:
      break
  return page_contents.split("}", close_brace)[-1].strip()

def remove_wiki_file(page_contents):
  balance = False
  open_brace = 0
  close_brace = 0
  while not balance:
    current_line = re.search(r'.*', page_contents).group(0)
    open_brace += current_line.count("[[")
    close_brace += current_line.count("]]")
    if open_brace == close_brace:
      balance = True
    page_contents = page_contents.split("\n", 1)[1]

  return page_contents.strip()


# Leverages Wikipedia api to grab contents of current page revision
# Returns first matched linnk
def grab_first_wiki_link(page_name):
  # Wiki api call for getting the latest revision of a page
  wiki_page_json = json.load(urllib2.urlopen("http://en.wikipedia.org/w/api.php?format=json&action=query&continue=&titles={0}&prop=revisions&rvprop=content&section=0".format(page_name.encode('utf-8'))))

  # If no page found there is no query
  if 'query' not in wiki_page_json:
    raise Exception("Wiki page could not be found")

  # Since it gives the actual revision number as a key
  current_rev = wiki_page_json['query']['pages'].keys()[0]

  # Finally grab contents
  page_contents = wiki_page_json['query']['pages'][current_rev]['revisions'][0]['*']

  # Handle wiki redirect
  if page_contents.startswith("#"):
    page_contents = wiki_redirect(page_contents)

  # Contents needs some formatting at front

  # Remove comments
  page_contents = re.sub(r'<!--.*?-->', '', page_contents)

  # Remove div tags and their contents
  page_contents = re.sub(re.compile(r'<div.*?>.*?\n', re.S), '', page_contents)

    # Remove nutshell sections
  page_contents = re.sub(re.compile(r'<section begin=nutshell />.*?<section end=nutshell />', re.S), '', page_contents)

  page_contents = page_contents.strip()

  # Remove meta and listbox
  # Remove images that confuses links
  while page_contents.startswith("{") or page_contents.startswith("[[File:") or page_contents.startswith("[[Image:"):
    if page_contents.startswith("{"):
      page_contents = remove_wiki_meta_data(page_contents)
    else:
      page_contents = remove_wiki_file(page_contents)

  # Remove references
  page_contents = re.sub(r'<ref.*?</ref>', '', page_contents)

  # Ignore things between parens except links
  page_contents = re.sub(r'\([^)]*\)(?!\|)', '', page_contents)

  # Ignore italizied but not bold
  page_contents = re.sub(r'(?<!\')\'{2}[^\']+?\'{2}(?!\')', '', page_contents)

  # Remove html tags
  page_contents = strip_tags(page_contents)

  # Links are enclosed with [[  ]] so grab the first one
  link_match = re.search(r"\[\[(.+?)\]\]", page_contents)
  
  # Edge case where no link found
  if not link_match:
    return None

  # Drop the pipe
  link_match = link_match.group(1).split("|")[0]
  return link_match


def get_to_philosophy(page_to_search):

  hop_count = 0
  MAX_HOPS = 100

  # Main loop
  print "http://en.wikipedia.org/wiki/{0}".format(page_to_search.encode('utf-8'))
  while page_to_search.lower() != "philosophy":

    #Catch any errors and exit gracefully
    # try:
    page_to_search = grab_first_wiki_link(page_to_search)
    # except Exception as e:
    #   print e
    #   sys.exit()
    # Drop hash tags
    if page_to_search.startswith("#"):
      print "Page links to self"
      return hop_count

    # Drop wiktionary entries
    if page_to_search.startswith("wiktionary:"):
      print "Wiktionary entry found"
      return hop_count

    page_to_search = page_to_search.split('#', 1)[0]

    # Edge case where no link found on page
    if not page_to_search:
      print "No link found"
      return hop_count
    
    # Format for new link
    page_to_search = re.sub(r'\s', '_', page_to_search.strip())

    # Print next check and increment
    print "http://en.wikipedia.org/wiki/{0}".format(page_to_search.encode('utf-8'))
    hop_count +=1
    # break

    # Break out on max hops
    if hop_count == MAX_HOPS:
      print "Max hop of {} reached".format(MAX_HOPS)
      return -1
  else:
    return hop_count
    

if __name__ == "__main__":
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

  hop_count = get_to_philosophy(page_to_search)
  if hop_count >= 0:
    print "{} hops".format(hop_count)

