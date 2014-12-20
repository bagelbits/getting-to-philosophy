#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import urllib2
import re

test_page = "Philosophy"
test_page = "study"

# Wiki api call for getting the latest revision of a page
wiki_page_json = json.load(urllib2.urlopen("http://en.wikipedia.org/w/api.php?format=json&action=query&continue=&titles={0}&prop=revisions&rvprop=content".format(test_page)))

# Since it gives the actual revision number
current_rev = wiki_page_json['query']['pages'].keys()[0]

# Links are enclosed with [[  ]]
page_contents = wiki_page_json['query']['pages'][current_rev]['revisions'][0]['*']
link_match = re.search(r"\[\[([\w\s\(\)]+)\]\]", page_contents)
link_match.group(1)


# Remember to sub spaces with underscore for links