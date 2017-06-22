from bs4 import BeautifulSoup
import logging
import scraperwiki
import sqlite3
import time
import requests
import re
import json

logging.basicConfig(level=logging.DEBUG)

# Constants to be replaced
hostUrl = 'http://eplanning.bankstown.nsw.gov.au'
searchPath = '/ApplicationSearch/ApplicationSearchThroughLodgedDate?day=yesterday'
prefixAppLink = '/ApplicationSearch/ApplicationDetails?applicationId='
prefixLodgementDate = 'Lodged:'
prefixApplicant = 'Applicant:' 

commentUrl = 'mailto:council@cbcity.nsw.gov.au'

dateScraped = time.strftime('%Y-%m-%d')

googleURL = 'https://maps.googleapis.com/maps/api/geocode/json?address=' 

apiKey = 'AIzaSyAZ42WZR4AL7cr5H0KiW7fKSWEYEDv0G5Y'

# Structure of the html for one DA:
#testCon = '<div><h4><a href="/ApplicationSearch/ApplicationDetails?applicationId=17780599">CD-266/2017</a></h4>Private Certified Complying Development- Fitout of tenancy K118 as &#39;The Mobile Phone Company&#39; <br />Address: <b> 1 North Terrace BANKSTOWNNSW2200 </b> <br /><label id="1" onmouseover="ShowMoreData(1);">[More]</label><div id="Data1" style="display: none;margin-left: 15px">Lodged: 19/06/2017 12:00:00 AM ( :by )<br />Applicant: Studio Mkz <br /></div></div>'

html = requests.get(hostUrl + searchPath)

#htmlContents = BeautifulSoup(testCon,"html.parser")

if html.status_code == requests.codes.ok:

	htmlContents = BeautifulSoup(html.text,"lxml")
	for listing in htmlContents.find_all('div'):
		if listing.h4 != None:
			if listing.h4.a != None:
				#split the string to extract data
				tmp1 = str(listing.h4.a['href']).split(prefixAppLink)
				applicationId = tmp1[1]
				
				#tmpContents -> temp container
				tmp2 = listing.div.contents[0].strip().split(prefixLodgementDate)
				tmp3 = str(tmp2[1]).strip().split()
				dateReceived = tmp3[0]
				
				tmp4 = listing.div.contents[2].strip().split(prefixApplicant)
				
				# TODO: check applicant Name
				applicantName = str(tmp4[1]).strip()
				propertyAddress = re.sub('[\s]+',' ',str(listing.b.string).strip())
				
				# TODO: change back to 2 with real scaping
				applicationDetails = re.sub('[\s]+',' ',str(listing.contents[2].strip()))
				
				# get the longitude and latitude using Google API based on address
				# Replace the spaces with +
				#addressQueryString = re.sub('[\s]+','+', propertyAddress)
				#result = requests.get(googleURL + addressQueryString + '&key=' + apiKey)
				
				#print json.dumps(result.json())
				
				####################################################################
				
				record = {
				'council_reference': str(listing.h4.a.string),
				'address': propertyAddress,
				'description': applicationDetails,
				'info_url': str(hostUrl + prefixAppLink + applicationId),
				'comment_url': commentUrl,
				'date_scraped': dateScraped,
				#'applicant_name': applicantName,
				#'application_id': applicationId,# internal application ID for href to council website
				'date_received': dateReceived
				}
				
				print record
				
				# Skip if the record already exists in database.
				try:
					if scraperwiki.sqlite.select('* FROM data WHERE council_reference="%s"' % record['council_reference']):
						logging.info('Skipping existing record in sqlite: ' + record['council_reference'])
						continue
				
				except sqlite3.OperationalError, e:
					if 'no such table:' in e.message:
						logging.info('Sqlite data does not exist yet. Will be created.')
						pass
					else:
						raise
				
				logging.info('Writing new record to sqlite: ' + record['council_reference'])
				scraperwiki.sqlite.save(unique_keys=['council_reference'], data=record)
