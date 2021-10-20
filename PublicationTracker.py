#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
import unidecode

from lib import Options, PPMSAPICalls, Reporting

reload(sys)
sys.setdefaultencoding('utf-8')


class Publication:

	def __init__(self, PI, FirstAu, PMID, doi):
		self.PI = PI
		self.FirstAuthor = FirstAu
		self.PMID = PMID
		self.doi = doi


class EncodeToRIS:

	Pubmed_to_RIS = {'PubDate': 'PY',
					 'Source': 'T2',
					 'Author': 'AU',
					 'Title': 'TI',
					 'Volume': 'VL',
					 'Issue': 'IS',
					 'Pages': 'SP',
					 'Lang': 'LA',
					 'doi': 'DO',
	}

	def __init__(self, response_string):
		self.authorlist = []
		self.root = ET.fromstring(response_string)

	def getItems(self, item_name):
		self.itemlist = []
		for self.child in self.root.iter('Item'):
			if self.child.get('Name') == item_name:
				self.itemlist.append(self.child.text)
		return self.itemlist

	def writeRISFile(self, file_name):
		with open(file_name, 'w') as self.f:
			for self.child in self.root.iter('Item'):
				if self.child.get('Name') in EncodeToRIS.Pubmed_to_RIS:
					try:
						self.f.write(EncodeToRIS.Pubmed_to_RIS[self.child.get('Name')] + ' - ' + self.child.text + '\n')
					except TypeError: # self.child.text returns None if field is empty
						pass



OPTIONS = Options.OptionReader('PublicationTrackerOptions.txt')

parser = argparse.ArgumentParser("Publication Tracker")
parser.add_argument("year",  nargs='?', help="Specify the year of publication, if omitted current year (last year, if Jan-Mar) will be used", type=int)
args = parser.parse_args()

# at the beginning of the year we want to search for papers submitted the year before
if args.year is None:
	date = datetime.now()
	if date.month < 4:
		year = str(date.year - 1)
	else:
		year = str(date.year)
else:
	year = str(args.year)

save_dir = os.path.join(OPTIONS.getValue('save_dir'), year)
if not os.path.isdir(save_dir):
	os.mkdir(save_dir)

# read list of already downloaded references, to be skipped
with open(OPTIONS.getValue('PMID_knownlist'), 'r') as knownlist:
	PMID_known = knownlist.readlines()
PMID_known = [PMID.strip('\n') for PMID in PMID_known]

# from the PPMS database retrieve group PIs and users belonging to that group, query Pubmed for publications authored by PI and each user
new_publications = []

get_groups = PPMSAPICalls.NewCall('PPMS API')
group_list = get_groups.getGroupList()

for group in group_list:
	get_groupPI = PPMSAPICalls.NewCall('PPMS API')
	group_head = unidecode.unidecode(get_groupPI.getGroupPI(group))
	get_user_API = PPMSAPICalls.NewCall('PPMS API')
	users = get_user_API.getGroupUsers(group)

	for user in users:
		try:
			user_call_API = PPMSAPICalls.NewCall('PPMS API')
			user_name = user_call_API.getUserFullName(user)
			author_name = unidecode.unidecode(user_name['lname']) + ', ' + unidecode.unidecode(user_name['fname'])
			payload = {'db': 'pubmed', 'term': group_head + '[FAU]+AND+' + author_name + '[FAU]+AND+' + year + '[pdat]'}
			payload_string = "&".join("%s=%s" % (k,v) for k,v in payload.items())
			response = requests.get(OPTIONS.getValue('getPMIDs'), params=payload_string)
			root = ET.fromstring(response.text)
			PMID_list = []
			for PMID in root.iter('Id'):
				PMID_list.append(PMID.text)

			for PMID in PMID_list:
				if PMID not in PMID_known:
					payload = {'db': 'pubmed', 'id': PMID}
					response = requests.get(OPTIONS.getValue('getSummary'), params=payload)
					RIS_bibliography = EncodeToRIS(response.text)
					authorlist = RIS_bibliography.getItems('Author')

					file_name = authorlist[-1].split()[0] + '_' + authorlist[0].split()[0] + '_' + PMID
					with open(os.path.join(save_dir, file_name + '.txt'), 'w') as f:
						f.write(response.text)
					RIS_bibliography.writeRISFile(os.path.join(save_dir, file_name + '.ris'))

					with open(OPTIONS.getValue('PMID_knownlist'), 'a') as knownlist:
						knownlist.write(PMID + '\n')
					PMID_known.append(PMID)
					new_publications.append(Publication(authorlist[-1], authorlist[0], PMID, RIS_bibliography.getItems('doi')[0]))
		except:
			pass

if new_publications:
	Reporting.reportPublications(new_publications)