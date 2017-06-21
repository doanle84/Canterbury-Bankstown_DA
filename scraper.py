from bs4 import BeautifulSoup
import logging
import scraperwiki
import sqlite3
import time
import urllib2
import re

logging.basicConfig(level=logging.DEBUG)

# Constants to be replaced
hostUrl = 'http://eplanning.bankstown.nsw.gov.au'
searchPath = '/ApplicationSearch/ApplicationSearchThroughLodgedDate?day=yesterday'
prefixAppLink = '/ApplicationSearch/ApplicationDetails?applicationId='
prefixLodgementDate = 'Lodged:'
prefixApplicant = 'Applicant:' 

commentUrl = 'mailto:test@gmail.com'


dateScraped = time.strftime('%Y-%m-%d')

# Structure of the html for one DA:
#testCon = '<div><h4><a href="/ApplicationSearch/ApplicationDetails?applicationId=17780599">CD-266/2017</a></h4>Private Certified Complying Development            - Fitout of tenancy K118 as &#39;The Mobile Phone Company&#39; <br />Address: <b> 1 North Terrace BANKSTOWN  NSW  2200                                                                 </b> <br /><label id="1" onmouseover="ShowMoreData(1);">[More]</label><div id="Data1" style="display: none;margin-left: 15px">Lodged: 19/06/2017 12:00:00 AM ( :  by )<br />Applicant: Studio Mkz                                                                                                               <br /></div></div>'

html = urllib2.urlopen(hostUrl + searchPath)

#soup = BeautifulSoup(testCon,"lxml")
htmlContents = BeautifulSoup(html.read(),"html.parser")


for listing in htmlContents.find_all('div'):
  if listing.h4 != None:
  	if listing.h4.a != None:
  	
  		#split the string to extract data
  		appIdString = str(listing.h4.a['href'])
  		appId = appIdString.split(prefixAppLink)
  		
  		#tmpContents -> temp container
  		tmpContents = listing.div.contents[0].strip().split(prefixLodgementDate)
  		tmpContents2 = str(tmpContents[1]).strip().split()
  		lodgedDate = tmpContents2[0]
  		
  		tmpContents = listing.div.contents[2].strip().split(prefixApplicant)
  		
  		applicantName = str(tmpContents[1]).strip()
  		
  		record = {
    		'da_number': str(listing.h4.a.string),
    		'application_id': appId[1],
    		'date_scraped': dateScraped,
    		'application_name': str(listing.string),
    		'property_address': str(listing.b.string).strip(),
    		'applicant_name': applicantName,
    		'application_lodgement_date': lodgedDate
  		}
  		print record

#  for row in listing.next_sibling.find_all('p', 'rowDataOnly'):
#    key = row.find_all('span', 'key')[0].string
#    value = str(row.find_all('span', 'inputField')[0].string)
#
#    if key == 'Application No.':
#      record['council_reference'] = value
#      record['comment_url'] = comment_url + urllib2.quote('Development Application Enquiry: ' + value, '')
#    elif key == 'Type of Work':
#      record['description'] = value
#    elif key == 'Date Lodged':
#      record['date_received'] = time.strftime('%Y-%m-%d', time.strptime(value, '%d/%m/%Y'))
#
#  # Skip if there is no valid council reference number found.
#  if ('council_reference' not in record or
#      not record['council_reference']):
#    continue
#
#  # Skip if the record already exists in database.
#  try:
#    if scraperwiki.sqlite.select('* FROM data WHERE council_reference="%s"' % record['council_reference']):
#      logging.info('Skipping existing record in sqlite: ' + record['council_reference'])
#      continue
#  except sqlite3.OperationalError, e:
#    if 'no such table:' in e.message:
#      logging.info('Sqlite data does not exist yet. Will be created.')
#      pass
#    else:
#      raise
#
#  logging.info('Writing new record to sqlite: ' + record['council_reference'])
#  scraperwiki.sqlite.save(unique_keys=['council_reference'], data=record)
