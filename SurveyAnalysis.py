
import os

class UserResponse:

	def __init__(self, response):

		if response[1] == '"Yes"':
			self.knows_BIC = True
			self.known_services = response[2].strip('"').split(';')
		else:
			self.knows_BIC = False
			self.known_services = None

		if response[3] == '"Yes"':
			self.uses_microscopes = True
			self.reason_no_microscopes = None
		else:
			self.uses_microscopes = False
			if response[4] == '""':
				self.reason_no_microscopes = None
			else:
				self.reason_no_microscopes = response[4].strip('"').split(';')

		self.microscope_evaluation = dict()
		if response[5] is not '""':
			self.microscope_evaluation['general'] = int(response[5].strip('"'))
		if response[6] is not '""':
			self.microscope_evaluation['LSM880'] = int(response[6].strip('"'))
		if response[7] is not '""':
			self.microscope_evaluation['LSM700'] = int(response[7].strip('"'))
		if response[8] is not '""':
			self.microscope_evaluation['SD'] = int(response[8].strip('"'))
		if response[9] is not '""':
			self.microscope_evaluation['OMX'] = int(response[9].strip('"'))
		if response[10] is not '""':
			self.microscope_evaluation['TIRF'] = int(response[10].strip('"'))
		if response[11] is not '""':
			self.microscope_evaluation['AxioZoom'] = int(response[11].strip('"'))

		self.training_evaluation = dict()
		if response[12] is not '""':
			self.training_evaluation['training'] = int(response[12].strip('"'))
		if response[13] is not '""':
			self.training_evaluation['advice'] = int(response[13].strip('"'))
		if response[14] is not '""':
			self.training_evaluation['challenges'] = int(response[14].strip('"'))

		if response[15] == '"Yes"' or response[16] == '"Yes"':
			self.uses_imageanalysis = True
		else:
			self.uses_imageanalysis = False

		if response[17] is not '""':
			self.imageanalysis_evaluation = int(response[17].strip('"'))
		elif response[21] is not '""':
			self.imageanalysis_evaluation = int(response[21].strip('"'))
		else:
			self.imageanalysis_evaluation = None

		if response[18] == '"Yes"' or response[22] == '"Yes"':
			self.uses_workstation = True
		else:
			self.uses_workstation = False

		if response[19] == '"Yes"' or response[23] == '"Yes"':
			self.uses_imaris = True
		else:
			self.uses_imaris = False

		if response[20] is not '""':
			self.needed_softwaresupport = response[20].strip('"')
		elif response[24] is not '""':
			self.needed_softwaresupport = response[24].strip('"')
		else:
			self.needed_softwaresupport = None

		self.impact_evaluation = dict()
		if response[12] is not '""':
			self.training_evaluation['training'] = int(response[12].strip('"'))
		if response[13] is not '""':
			self.training_evaluation['advice'] = int(response[13].strip('"'))





survey_path ='Z:\\BIC Outreach\\Bio-Chem-Phys_survey_2018\\'
survey_filename = 'Bioimaging Center - Survey 2018.csv'

with open(os.path.join(survey_path, survey_filename)) as sf:
	survey_responses = sf.readlines()

single_response = survey_responses[11].split(',')
numbered_response = [x for x in zip(range(len(single_response)), single_response)]
for item in numbered_response:
	print item

