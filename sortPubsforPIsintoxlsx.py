
import xlsxwriter, os, unidecode
import xml.etree.ElementTree as ET
from lib import PPMSAPICalls


class Publication:

	def __init__(self, ris_string):
		self.root = ET.fromstring(ris_string)
		self.author_list = []
		self.url = ''
		for item in self.root.iter("Item"):
			if item.attrib['Name'] == 'Author':
				author = item.text
				if isinstance(author, unicode):
					author = unidecode.unidecode(author)
				author = author.split()
				if len(author) == 2:
					self.author_list.append(author[0])
				if len(author) == 3:
					self.author_list.append(author[0] + ' ' + author[1])
			if item.attrib['Name'] == 'Title':
				self.title = item.text
			if item.attrib['Name'] == 'Source':
				self.journal = item.text
			if item.attrib['Name'] == 'EPubDate':
				self.epubdate = item.text
			if item.attrib['Name'] == 'DOI':
				self.url = 'https://doi.org/' + item.text

	def findPIs(self, PI_list):
		intersection = []
		for author in self.author_list:
			if author in PI_list:
				intersection.append(author)
		self.PIs = intersection



publication_dir = 'N:\\Facility\\temperature_logger\\Publication_Tracker\\Publications'

list_of_years = sorted(filter(os.path.isdir, [os.path.join(publication_dir, subdir) for subdir in os.listdir(publication_dir)]))
workbook = xlsxwriter.Workbook(os.path.join(publication_dir, 'publications_by_group.xlsx'))
bold = workbook.add_format({'bold': True})
labels = ('Authors', 'Title', 'Journal', 'EpubDate', 'URL')


sheets_to_PIs = {}

get_groups = PPMSAPICalls.NewCall('PPMS API')
group_list = get_groups.getGroupList()
get_groupPI = PPMSAPICalls.NewCall('PPMS API')
group_heads = [unidecode.unidecode(get_groupPI.getGroupPI(group)).split(', ')[0] for group in group_list]
# group_heads = ['May', 'Leist', 'Groettrup', 'Dietrich', 'Kroth', 'Mayer', 'Gross', 'Sturmer', 'Burkle', 'Scheffner', 'Adamska', 'Mecking', 'Begemann', 'Galizia', 'Kleineidam', 'Marx', 'Brunner', 'Thum', 'Wittmann', 'Colfen', 'Drescher', 'Farhan', 'Frickey', 'May', 'Hartig', 'Leitenstorfer', 'Zumbusch', 'Hauck', 'Groth', 'FlowKon', 'Meyer', 'Bottcher', 'Spiteller', 'Legler', 'Hutteroth', 'Wikelski', 'Deuerling', 'Gebauer', 'Wittemann', 'Laumann', 'Schink', 'Polarz', 'Isono', 'Rossy', 'Schmidt-Mende', 'Rothhaupt', 'Kratochwil', 'Funck', 'Couzin', 'Hauser', 'Becks']

PI_publications = {}
for group_head in group_heads:
	PI_publications[group_head] = []
PI_publications['other'] = []

for year_dir in list_of_years:
	file_list = filter(lambda x: x.endswith('.txt'), os.listdir(year_dir))
	for file in file_list:
		with open(os.path.join(year_dir, file)) as ris_file:
			ris_string = ris_file.read()

		publication = Publication(ris_string)
		publication.findPIs(group_heads)
		if publication.PIs:
			for PI in publication.PIs:
				temp_pub_list = PI_publications[PI]
				temp_pub_list.append(publication)
				PI_publications[PI] = temp_pub_list
		else:
			temp_pub_list = PI_publications['other']
			temp_pub_list.append(publication)
			PI_publications['other'] = temp_pub_list

for PI, publications in PI_publications.iteritems():
	if publications:
		current_sheet = workbook.add_worksheet(PI)
		publications = sorted(publications, key=lambda pub: pub.epubdate)
		current_sheet.write_row(0, 0, labels)
		current_sheet.set_row(0, None, bold)
		row_counter = 1
		for publication in publications:
			authors = ', '.join(publication.author_list)
			pub = (authors, publication.title, publication.journal, publication.epubdate, publication.url)
			current_sheet.write_row(row_counter, 0, pub)
			row_counter += 1

workbook.close()
