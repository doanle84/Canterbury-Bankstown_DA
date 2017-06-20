import scraperwiki
import lxml.html
import datetime

from bs4 import BeautifulSoup
import logging
import sqlite3
import urllib2


url = "http://eplanning.bankstown.nsw.gov.au/ApplicationSearch/ApplicationSearchThroughLodgedDate?day=yesterday"
#
# # Read in a page
html = urllib2.urlopen(url)
soup = BeautifulSoup(html.read())

for listing in soup.find_all('div'):
  record = {
    'DA_number': str(listing.h4.a.string),
    'application_id': str(listing.h4.a.['href']),
    
  }


# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".
