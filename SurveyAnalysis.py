
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

class ColorScheme:

	def __init__(self):
		self.bio_base = '#BBDB49'
		self.bio_light = '#D2E787'
		self.bio_dark = '#91AF23'
		self.chem_base = '#FD6E21'
		self.chem_light = '#FD9D69'
		self.chem_dark = '#CB4902'
		self.phys_base = '#5536DD'
		self.phys_light = '#8772E7'
		self.phys_dark = '#361DA9'

class UserResponse:

	def __init__(self, response):

		if response[1] == 'Yes':
			self.knows_BIC = True
			self.known_services = response[2].strip('"').split(';')
		else:
			self.knows_BIC = False
			self.known_services = None

		if response[3] == 'Yes':
			self.uses_microscopes = True
			self.reason_no_microscopes = None
		else:
			self.uses_microscopes = False
			if response[4] == '""':
				self.reason_no_microscopes = None
			else:
				self.reason_no_microscopes = response[4].strip('"').split(';')

		self.microscope_evaluation = {}
		if response[5]:
			self.microscope_evaluation['general'] = int(response[5].strip('"'))
		if response[6]:
			self.microscope_evaluation['LSM880'] = int(response[6].strip('"'))
		if response[7]:
			self.microscope_evaluation['LSM700'] = int(response[7].strip('"'))
		if response[8]:
			self.microscope_evaluation['SD'] = int(response[8].strip('"'))
		if response[9]:
			self.microscope_evaluation['OMX'] = int(response[9].strip('"'))
		if response[10]:
			self.microscope_evaluation['TIRF'] = int(response[10].strip('"'))
		if response[11]:
			self.microscope_evaluation['AxioZoom'] = int(response[11].strip('"'))

		self.training_evaluation = {}
		if response[12]:
			self.training_evaluation['training'] = int(response[12].strip('"'))
		if response[13]:
			self.training_evaluation['advice'] = int(response[13].strip('"'))
		if response[14]:
			self.training_evaluation['challenges'] = int(response[14].strip('"'))

		if response[15] == 'Yes' or response[16] == 'Yes':
			self.uses_imageanalysis = True
		else:
			self.uses_imageanalysis = False

		if response[17]:
			self.imageanalysis_evaluation = int(response[17].strip('"'))
		elif response[21]:
			self.imageanalysis_evaluation = int(response[21].strip('"'))
		else:
			self.imageanalysis_evaluation = None

		if response[18] == 'Yes' or response[22] == 'Yes':
			self.uses_workstation = True
		else:
			self.uses_workstation = False

		if response[19] == 'Yes' or response[23] == 'Yes':
			self.uses_imaris = True
		else:
			self.uses_imaris = False

		if response[20]:
			self.feedback_softwaresupport = response[20].strip('"')
		elif response[24]:
			self.feedback_softwaresupport = response[24].strip('"')
		else:
			self.feedback_softwaresupport = None

		self.impact_evaluation = {}
		if response[25]:
			self.impact_evaluation['importance'] = int(response[25].strip('"'))
		if response[26]:
			self.impact_evaluation['workload'] = int(response[26].strip('"'))

		if response[27] == 'Yes':
			self.uses_courses = True
		else:
			self.uses_courses = False

		self.course_evaluation = {}
		if response[28]:
			self.course_evaluation['microscopy_clarity'] = int(response[28].strip('"'))
		if response[29]:
			self.course_evaluation['microscopy_helpful'] = int(response[29].strip('"'))
		if response[31]:
			self.course_evaluation['imageanalysis_prepared'] = int(response[31].strip('"'))
		if response[32]:
			self.course_evaluation['imageanalysis_helpful'] = int(response[32].strip('"'))

		if response[30] == 'Yes':
			self.recommend_microscopy_course = True
		else:
			self.recommend_microscopy_course = False
		if response[33] == 'Yes':
			self.recommend_imageanalysis_course = True
		else:
			self.recommend_imageanalysis_course = False

		if response[34]:
			self.interaction_evaluation = int(response[34].strip('"'))
		else:
			self.interaction_evaluation = None

		self.feedback_BIC = {}
		if response[35]:
			self.feedback_BIC['strength'] = response[35].strip('"')
		if response[36]:
			self.feedback_BIC['improvements'] = response[36].strip('"')
		if response[37]:
			self.feedback_BIC['new_technique'] = response[37].strip('"')
		if response[38]:
			self.feedback_BIC['additional_service'] = response[38].strip('"')

		self.department = response[39].strip('"')
		self.position = response[40].strip('"')

def square_chart(fractions, defaultcolor='lightgrey'):

	if sum([f[0] for f in fractions]) > 1 or not all([f[0] >= 0 for f in fractions]):
		raise ValueError('Fractions must be positive and in sum between 0 and 1.')

	fractions, colors = zip(*fractions)
	percentages = [int(round(fraction * 100, 0)) for fraction in fractions]
	percentages = np.cumsum(percentages)
	percentages = np.append([0], percentages)
	color_counter = len(colors) - 1

	matrix = np.full((10, 10), len(fractions), dtype=int)

	while True:
		square_counter = percentages[-1] - 1
		if square_counter == -1:
			break
		percentages = percentages[:-1]
		while (square_counter >= percentages[-1]):
			matrix[9 - square_counter % 10][9 - square_counter // 10] = color_counter
			square_counter -= 1
		color_counter -= 1

	fig = plt.figure(figsize=(10,10), dpi=300,edgecolor='white', facecolor='white', tight_layout=True)
	ax = plt.gca()
	ax.set_aspect('equal', 'box')
	for spine in ax.spines.values():
		spine.set_edgecolor('white')
	ax.xaxis.set_major_locator(plt.NullLocator())
	ax.yaxis.set_major_locator(plt.NullLocator())

	for (x, y), color_index in np.ndenumerate(matrix):
		try:
			color = colors[color_index]
		except IndexError:
			color = defaultcolor
		size = 1
		padding = 0.3
		rect = FancyBboxPatch((x - size / 2, y - size / 2),
							  size - 2 * padding, size - 2 * padding,
							  boxstyle="round, pad=" + str(padding),
							  linewidth=2,
							  fc=color,
							  ec='white')
		ax.add_patch(rect)

	ax.invert_yaxis()
	ax.autoscale(enable=True)
	fig.add_axes(ax)
	return fig, ax


def fractions(numerator, denominator):
	try:
		return float(numerator) / denominator
	except ZeroDivisionError:
		return 0.


def evaluate_feedback(responses):

	like, hate, want = [], [], []

	for response in responses:
		for key, value in response.feedback_BIC.iteritems():
			if key == 'strength':
				like.append(value)
			if key == 'improvements':
				hate.append(value)
			if key == 'new_technique' or key == 'additional_service':
				want.append(value)

	return like, hate, want


survey_path ='Z:\\BIC Facility\\Bio-Chem-Phys_survey_2018'
survey_filename = 'Bioimaging Center - Survey 2018.csv'
with open(os.path.join(survey_path, survey_filename)) as sf:
	survey_responses = sf.readlines()

'''Initialize the colorscheme'''
cs = ColorScheme()

# One line for each response, create USerResponse; survey_responses[0] is headers
user_responses = [UserResponse(response.strip('"\n').split('","')) for response in survey_responses[1:]]

responses_bio = filter(lambda x: x.department == 'Biology', user_responses)
responses_chem = filter(lambda x: x.department == 'Chemistry', user_responses)
responses_phys = filter(lambda x: x.department == 'Physics', user_responses)

responses_PIs = filter(lambda x: x.position == 'Group leader', user_responses)
responses_Scientists = filter(lambda x: x.position in ('Postdoc', 'PhD student'), user_responses)
responses_Students = filter(lambda x: x.position in ('Master student', 'Bachelor student'), user_responses)

responses_PIs_bio = filter(lambda x: x.position == 'Group leader', responses_bio)
responses_Scientists_bio = filter(lambda x: x.position in ('Postdoc', 'PhD student'), responses_bio)
responses_Students_bio = filter(lambda x: x.position in ('Master student', 'Bachelor student'), responses_bio)

responses_PIs_chem = filter(lambda x: x.position == 'Group leader', responses_chem)
responses_Scientists_chem = filter(lambda x: x.position in ('Postdoc', 'PhD student'), responses_chem)
responses_Students_chem = filter(lambda x: x.position in ('Master student', 'Bachelor student'), responses_chem)

responses_PIs_phys = filter(lambda x: x.position == 'Group leader', responses_phys)
responses_Scientists_phys = filter(lambda x: x.position in ('Postdoc', 'PhD student'), responses_phys)
responses_Students_phys = filter(lambda x: x.position in ('Master student', 'Bachelor student'), responses_phys)


count_departments = (len(responses_bio), len(responses_chem), len(responses_phys))
print 'Answers from Biology: {:d}, Chemistry {:d}, and Physics: {:d}'.format(*count_departments)

department_fractions = [float(n) / len(user_responses) for n in count_departments]
fig, ax = square_chart(zip(department_fractions, (cs.bio_dark, cs.chem_dark, cs.phys_dark)))
fig.savefig('D:\\Survey\\answers_from.png')
plt.close(fig)

responses_knowsBIC_bio = filter(lambda x: x.knows_BIC, responses_bio)
responses_knowsBIC_chem = filter(lambda x: x.knows_BIC, responses_chem)
responses_knowsBIC_phys = filter(lambda x: x.knows_BIC, responses_phys)
responses_knowsBIC = responses_knowsBIC_bio + responses_knowsBIC_chem + responses_knowsBIC_phys

count_departments_knowsBIC = (len(responses_knowsBIC_bio), len(responses_knowsBIC_chem), len(responses_knowsBIC_phys))
print 'Numbers of users knowing BIC: Biology: {}, Chemistry: {}, Physics {}'.format(*count_departments_knowsBIC)
print 'Numbers of users not knowing BIC: Biology: {}, Chemistry: {}, Physics {}'.format(*[total - knows for knows, total in zip(count_departments_knowsBIC, count_departments)])
print 'Percentage of users knowing BIC: Biology: {:.1%}, Chemistry: {:.1%}, Physics {:.1%}'.format(*[fractions(*num_denom) for num_denom in zip(count_departments_knowsBIC, count_departments)])


fig, ax = square_chart([(float(count_departments_knowsBIC[0]) / count_departments[0], cs.bio_dark)], cs.bio_light)
fig.savefig('D:\\Survey\\bio_knows.png')
plt.close(fig)
fig, ax = square_chart([(float(count_departments_knowsBIC[1]) / count_departments[1], cs.chem_dark)], cs.chem_light)
fig.savefig('D:\\Survey\\chem_knows.png')
plt.close(fig)
fig, ax = square_chart([(float(count_departments_knowsBIC[2]) / count_departments[2], cs.phys_dark)], cs.phys_light)
fig.savefig('D:\\Survey\\phys_knows.png')
plt.close(fig)

count_PIs_knowsBIC_bio = len(filter(lambda x: x.knows_BIC, responses_PIs_bio))
count_Scientists_knowsBIC_bio = len(filter(lambda x: x.knows_BIC, responses_Scientists_bio))
count_Students_knowsBIC_bio = len(filter(lambda x: x.knows_BIC, responses_Students_bio))

count_PIs_knowsBIC_chem = len(filter(lambda x: x.knows_BIC, responses_PIs_chem))
count_Scientists_knowsBIC_chem = len(filter(lambda x: x.knows_BIC, responses_Scientists_chem))
count_Students_knowsBIC_chem = len(filter(lambda x: x.knows_BIC, responses_Students_chem))

count_PIs_knowsBIC_phys = len(filter(lambda x: x.knows_BIC, responses_PIs_phys))
count_Scientists_knowsBIC_phys = len(filter(lambda x: x.knows_BIC, responses_Scientists_phys))
count_Students_knowsBIC_phys = len(filter(lambda x: x.knows_BIC, responses_Students_phys))

print 'Fraction of Group leaders (Biology) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_PIs_knowsBIC_bio, len(responses_PIs_bio)), len(responses_PIs_bio))
print 'Fraction of Scientists (Biology) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_Scientists_knowsBIC_bio, len(responses_Scientists_bio)), len(responses_Scientists_bio))
print 'Fraction of Students (Biology) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_Students_knowsBIC_bio, len(responses_Students_bio)), len(responses_Students_bio))

print 'Fraction of Group leaders (Chemistry) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_PIs_knowsBIC_chem, len(responses_PIs_chem)), len(responses_PIs_chem))
print 'Fraction of Scientists (Chemistry) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_Scientists_knowsBIC_chem, len(responses_Scientists_chem)), len(responses_Scientists_chem))
print 'Fraction of Students (Chemistry) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_Students_knowsBIC_chem, len(responses_Students_chem)), len(responses_Students_chem))

print 'Fraction of Group leaders (Physics) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_PIs_knowsBIC_phys, len(responses_PIs_phys)), len(responses_PIs_phys))
print 'Fraction of Scientists (Physics) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_Scientists_knowsBIC_phys, len(responses_Scientists_phys)), len(responses_Scientists_phys))
print 'Fraction of Students (Physics) who know the BIC: {:.1%} (n={:d})'.format(fractions(count_Students_knowsBIC_phys, len(responses_Students_phys)), len(responses_Students_phys))

fig, ax = square_chart([(fractions(count_PIs_knowsBIC_bio, len(responses_PIs_bio)), cs.bio_dark)], cs.bio_light)
fig.savefig('D:\\Survey\\bio_PIs_knows.png')
plt.close(fig)
fig, ax = square_chart([(fractions(count_Scientists_knowsBIC_bio, len(responses_Scientists_bio)), cs.bio_dark)], cs.bio_light)
fig.savefig('D:\\Survey\\bio_Scientists_knows.png')
plt.close(fig)
fig, ax = square_chart([(fractions(count_Students_knowsBIC_bio, len(responses_Students_bio)), cs.bio_dark)], cs.bio_light)
fig.savefig('D:\\Survey\\bio_Students_knows.png')
plt.close(fig)

fig, ax = square_chart([(fractions(count_PIs_knowsBIC_chem, len(responses_PIs_chem)), cs.chem_dark)], cs.chem_light)
fig.savefig('D:\\Survey\\chem_PIs_knows.png')
plt.close(fig)
fig, ax = square_chart([(fractions(count_Scientists_knowsBIC_chem, len(responses_Scientists_chem)), cs.chem_dark)], cs.chem_light)
fig.savefig('D:\\Survey\\chem_Scientists_knows.png')
plt.close(fig)
fig, ax = square_chart([(fractions(count_Students_knowsBIC_chem, len(responses_Students_chem)), cs.chem_dark)], cs.chem_light)
fig.savefig('D:\\Survey\\chem_Students_knows.png')
plt.close(fig)

fig, ax = square_chart([(fractions(count_PIs_knowsBIC_phys, len(responses_PIs_phys)), cs.phys_dark)], cs.phys_light)
fig.savefig('D:\\Survey\\phys_PIs_knows.png')
plt.close(fig)
fig, ax = square_chart([(fractions(count_Scientists_knowsBIC_phys, len(responses_Scientists_phys)), cs.phys_dark)], cs.phys_light)
fig.savefig('D:\\Survey\\phys_Scientists_knows.png')
plt.close(fig)
fig, ax = square_chart([(fractions(count_Students_knowsBIC_phys, len(responses_Students_phys)), cs.phys_dark)], cs.phys_light)
fig.savefig('D:\\Survey\\phys_Students_knows.png')
plt.close(fig)

PIs_like, PIs_hate, PIs_want = evaluate_feedback(responses_PIs)
scientists_like, scientists_hate, scientists_want = evaluate_feedback(responses_Scientists)
students_like, students_hate, students_want = evaluate_feedback(responses_Students)

print '\nFeedback from Group leaders:'
print 'Like about BIC:'
print PIs_like
print 'Want to see improved:'
print PIs_hate
print 'Want to have:'
print PIs_want

print '\nFeedback from researchers:'
print 'Like about BIC:'
print scientists_like
print 'Want to see improved:'
print scientists_hate
print 'Want to have:'
print scientists_want

print '\nFeedback from undergraduate students:'
print 'Like about BIC:'
print students_like
print 'Want to see improved:'
print students_hate
print 'Want to have:'
print students_want

responses_usesMicroscopes = filter(lambda x: x.uses_microscopes, responses_knowsBIC)
responses_usesImageAnalysis = filter(lambda x: x.uses_imageanalysis, responses_knowsBIC)
responses_usesCourses = filter(lambda x: x.uses_courses, responses_knowsBIC)
responses_usesNoMicroscopes = filter(lambda x: not x.uses_microscopes, responses_knowsBIC)
responses_usesNoBIC = filter(lambda x: not x.uses_microscopes and not x.uses_imageanalysis and not x.uses_courses, responses_knowsBIC)

print '\nNumber of users who use microscopes: {}, image analysis: {}, courses: {} or nothing: {}.'.format(len(responses_usesMicroscopes), len(responses_usesImageAnalysis), len(responses_usesCourses), len(responses_usesNoBIC))
print '\nFraction of people knowing BIC who use microscopes: {:.1%} (n={:d})'.format(fractions(len(responses_usesMicroscopes), len(responses_usesMicroscopes) + len(responses_usesNoMicroscopes)), len(responses_usesMicroscopes) + len(responses_usesNoMicroscopes))
fig, ax = square_chart([(fractions(len(responses_usesMicroscopes), len(responses_usesMicroscopes) + len(responses_usesNoMicroscopes)), '#8801B2')], '#F7DBFF')
fig.savefig('D:\\Survey\\uses microscopes.png')
plt.close(fig)

reasons = {}

for resp in responses_usesNoMicroscopes:
	for r in resp.reason_no_microscopes:
		if r:
			try:
				reasons[r.strip('"')] += 1
			except KeyError:
				reasons[r.strip('"')] = 1

print '\nReasons people are not using microscopes (n={:d}): '.format(len(responses_usesNoMicroscopes))
for key, value in reasons.iteritems():
	print key, value

reason_fractions = [(25. / 56, '#004FA8'), (25. / 56,  '#347B98'), (5. / 56, '#559E54'), (1. / 56, '#98CA32')]

fig, ax = square_chart(reason_fractions, 'white')
fig.savefig('D:\\Survey\\why_no_microscopes.png')
plt.close(fig)

fig, ax = square_chart([(1., '#66AB36')], '#FF2D1A')
fig.savefig('D:\\Survey\\recommend_microscope_courses.png')
plt.close(fig)

fig, ax = square_chart([(10. / 11, '#66AB36')], '#FF2D1A')
fig.savefig('D:\\Survey\\recommend_imageanalysis_courses.png')
plt.close(fig)


