#!/usr/bin/env python
# -*- coding: utf-8


# TODO: User die nur assisted sessions hatten, fallen durchs Raster, da keine Nutzerrechte vorhanden sind
# TODO: Überprüfen: Nutzer ohne "last usage" Eintrag

import time
from datetime import datetime, timedelta

from lib import Options, PPMSAPICalls, Errors


class Timer(object):
	""" Adopted from answer by Eli Bendersky
	https://stackoverflow.com/questions/5849800/what-is-the-python-equivalent-of-matlabs-tic-and-toc-functions """

	def __init__(self, start_msg=None, stop_msg=None, print_divider=True):
		self.start_msg = start_msg
		self.stop_msg = stop_msg
		self.print_divider = print_divider

	def __enter__(self):
		self.tstart = time.time()
		if self.start_msg:
			print(self.start_msg)

	def __exit__(self, type, value, traceback):
		if self.stop_msg:
			print(self.stop_msg,)
		print('Elapsed time: {0:.2f}s'.format(time.time() - self.tstart))
		if self.print_divider:
			print('----------------------------')


class Equipment:

	_central_microscope_ids = [3, 5, 7, 14, 17, 18, 58]
	_decentral_microscope_ids = [6, 16, 56, 57]
	_external_tracked_microscope_ids = [29, 60]

	def __init__(self):
		self.microscope_list = []
		self._get_bic_microscopes()

	def _get_bic_microscopes(self):

		def get_system_status(system_id):
			sys_stat = None
			if system_id in self._central_microscope_ids:
				sys_stat = 'central'
			if system_id in self._decentral_microscope_ids:
				sys_stat = 'decentral'
			if system_id in self._external_tracked_microscope_ids:
				sys_stat = 'external'
			return sys_stat

		def identify_microscopes(ppms_system_string):
			ppms_system_info = ppms_system_string.split(',')

			# check if system is a microscope, and if it is active
			if 'Microscope' in ppms_system_info[2] and 'True' == ppms_system_info[5]:
				start_index = ppms_system_info[2].index('(')
				stop_index = ppms_system_info[2].index(')')

				system_type = ppms_system_info[2][start_index + 1: stop_index]
				system_status = get_system_status(int(ppms_system_info[1]))

				if system_status:
					new_microscope = Instrument(ppms_system_info[1],
											ppms_system_info[3].strip('"'),
											system_type,
											system_status,
											)
					return new_microscope

		ppms_system_call = PPMSAPICalls.NewCall(calling_mode)
		ppms_system_list = ppms_system_call.getSystems()

		for system in ppms_system_list:
			instrument = identify_microscopes(system)
			if instrument:
				self.microscope_list.append(instrument)

	def microscope_list_with_user_rights(self, login):
		user_right_list = []
		for microscope in self.microscope_list:
			if login in microscope.unfiltered_login_list:
				user_right_list.append(microscope)
		return user_right_list


class Instrument:

	def __init__(self, id, name, type, status):
		self.id = id
		self.name = name
		self.type = type
		self.status = status
		self.unfiltered_login_list = self._get_active_user_rights()
		self.user_list = []
		self.group_list = []

	def _get_active_user_rights(self):

		user_rights_call = PPMSAPICalls.NewCall(calling_mode)
		user_rights = user_rights_call.getUserRights(system_id=self.id)

		login_list =[]
		for user_right in user_rights:
			user_right = user_right.split(',')
			if ('D' != user_right[0]) and ('.' in user_right[1]):
				login_list.append(user_right[1].strip('"'))
		return login_list

	def add_user(self, user):
		self.user_list.append(user)
		if user.group not in self.group_list:
			self.group_list.append(user.group)

	def get_active_user_logins(self):
		return[u.login for u in self.user_list]

	def get_active_group_names(self):
		return [g.name for g in self.group_list]

	def number_of_users(self):
		return len(self.user_list)

	def number_of_groups(self, department=None):
		if not department:
			return len(self.group_list)
		else:
			return len(list(filter(lambda g: department in g.department.lower(), self.group_list)))


class ActiveBICUsers:

	# List of ignored user logins, to remove internal accounts
	ignored_login_list = ['martin.stoeckl',
						  'elisa.may',
						  'daniela.rothoehler',
						  'niklas.blank',
						  'carolin.bottling',
						  'christina.hipper-meier',
						  ]

	def __init__(self, equipment):
		self._microscope_list = equipment.microscope_list
		self._current_date = datetime.today()
		self.user_list = self._get_active_users()
		self.group_list = self._get_active_groups()

	def _get_user_rights(self, user_login):
		get_user_rights = PPMSAPICalls.NewCall(calling_mode)
		user_right_microscope_list = []
		try:
			user_rights = get_user_rights.getUserRights(login=user_login)
		# TODO: Somehow 'except Errors.APIError:' does not catch the exception raised in PPMSAPICalls._performCall (l49)
		except Exception:
			return user_right_microscope_list
		else:
			for user_right in user_rights:
				user_right = user_right.split(',')
				if 'D' != user_right[0]:
					for microscope in self._microscope_list:
						if microscope.id == user_right[1]:
							user_right_microscope_list.append(microscope)
							break
		return user_right_microscope_list

	def _check_user_experience(self, login, user_right_id_list):
		last_usage_call = PPMSAPICalls.NewCall(calling_mode)
		get_usage_info = last_usage_call.getLastUsage(login)
		last_usage_list = []
		last_training_list = []

		for usage_entry in get_usage_info:
			if usage_entry['id'] in user_right_id_list:
				if usage_entry['last res'] != 'n/a':
					last_usage_list.append(datetime.strptime(usage_entry['last res'], '%Y/%m/%d'))
				if usage_entry['last train'] != 'n/a':
					last_training_list.append(datetime.strptime(usage_entry['last train'], '%Y/%m/%d'))
		try:
			last_usage_date = max(last_usage_list)
			days_since_last_usage = self._current_date - max(last_usage_list)
			recent_usage = days_since_last_usage < timedelta(days=730)
			last_usage_date = datetime.strftime(last_usage_date, '%d/%m/%Y')
		except ValueError:
			recent_usage = False
			last_usage_date = 'n/a'
		try:
			days_since_last_training = self._current_date - max(last_training_list)
			recent_training = days_since_last_training < timedelta(days=730)
		except ValueError:
			recent_training = False

		active_within_2y = recent_usage or recent_training
		training_year_list = [td.year for td in last_training_list]
		return active_within_2y, training_year_list, last_usage_date

	def _get_active_users(self):

		# get all logins in PPMS, for accounts with the 'active' flag set
		active_user_call = PPMSAPICalls.NewCall(calling_mode)
		active_user_logins = active_user_call.getAllUsers(True)

		user_list = []
		for login in active_user_logins:
			# check if account is not an account to ignore
			if (login not in self.ignored_login_list):

				# get the microscopes with enabled user rights, for the given account, generate a microscope id list
				microscopes_with_user_right_list = equipment.microscope_list_with_user_rights(login)
				microscope_ids_with_user_right_list = [m.id for m in microscopes_with_user_right_list]

				# check whether the user has been working or been trained on a microscope in the last two years,
				# get the years when the user has been trained and the date of the last activity
				active_within_2years, training_year_list, last_usage = self._check_user_experience(login, microscope_ids_with_user_right_list)

				# if the user has shown activity in the last two years, create an user object,
				# add it to the microscope.user_list and the ActiveBICUsers.user_list
				if active_within_2years:
					active_user = BICUser(login, microscopes_with_user_right_list, last_usage, training_year_list)
					user_list.append(active_user)
					for microscope in microscopes_with_user_right_list:
						microscope.add_user(active_user)
		return user_list

	def _get_active_groups(self):
		group_list = []
		for user in self.user_list:
			if user.group not in group_list:
				group_list.append((user.group))
		return group_list

	def number_of_users(self, department=None):
		if not department:
			return len(self.user_list)
		else:
			return len(list(filter(lambda u: department in u.group.department.lower(), self.user_list)))

	def number_of_groups(self, department=None):
		if not department:
			return len(self.group_list)
		else:
			return len(list(filter(lambda g: department in g.department.lower(), self.group_list)))

	def number_of_trainings(self, year, department=None):
		if not department:
			user_list = self.user_list
		else:
			user_list = list(filter(lambda u: department in u.group.department.lower(), self.user_list))
		return sum([user.get_training_years(year) for user in user_list])


class BICUser:

	def __init__(self, login, user_rights_for_microscopes, last_usage_date, training_year_list):
		self.login = login
		self.user_rights_for_microscopes = user_rights_for_microscopes
		self._training_years_list = training_year_list
		self.last_usage_date = last_usage_date
		self.group = Group(self._get_user_full_info()['unitlogin'])


	def _get_user_full_info(self):
		user_info_call = PPMSAPICalls.NewCall(calling_mode)
		return user_info_call.getUserFullInfo(self.login)


	def get_training_years(self, year=None):
		if year == None:
			return self._training_years_list
		else:
			return self._training_years_list.count(year)

	def user_rights_microscope_names(self):
		return [m.name for m in self.user_rights_for_microscopes]


class Group:

	def __init__(self, id):
		self.id = id
		self.name, self.real_name, self.department = self._populate_group_info()

	def __eq__(self, other):
		if not isinstance(other, Group):
			# don't attempt to compare against unrelated types
			return NotImplemented

		return self.id == other.id

	def _populate_group_info(self):
		group_info_call = PPMSAPICalls.NewCall(calling_mode)
		full_group_info = group_info_call.getGroupFullInfo(self.id)
		return full_group_info['unitbcode'], full_group_info['unitname'], full_group_info['department']


def print_microscope_users(microscope_list):
	print('Microscope statistics:')
	for m in microscope_list:
		print(f'{m.name} (id: {m.id})')
		print(f'All logins: {m.unfiltered_login_list}')
		print(f'Active user logins: {m.get_active_user_logins()}')
		print(f'Active groups: {m.get_active_group_names()}')
		print('--------------------')

def print_user_info(user_list):
	print('User statistics:')
	for user in user_list:
		print(f"User login: {user.login} from {user.group.name} ({user.group.department}), "
			  f"used a BIC microscope last time on: {user.last_usage_date}")
		print(f'{user.login} can use the following microscopes: {user.user_rights_microscope_names()}')
		print(f'The trainings were conducted in the years: {user.get_training_years()}')
		print('--------------------')

def print_facility_statistics(bic_equipment, active_users=None):
	print('System statistics:')
	for microscope in bic_equipment.microscope_list:
		print(f'The {microscope.name} has {microscope.number_of_users()} active users.')
		print(f'The {microscope.name} has {microscope.number_of_groups()} active groups.')
		print(f'FB Bio: {microscope.number_of_groups("bio")}, '
			  f'FB Che: {microscope.number_of_groups("che")}, '
			  f'FB Phy: {microscope.number_of_groups("phy")}')
	print('--------------------')
	print('Facility statistics:')
	print(f'The facility has {active_users.number_of_groups()} active groups.')
	print(f'FB Bio: {active_users.number_of_groups("bio")}, '
		  f'FB Che: {active_users.number_of_groups("che")}, '
		  f'FB Phy: {active_users.number_of_groups("phy")}')
	print('--------------------')
	print(f'The facility has {active_users.number_of_users()} active users.')
	print(f'FB Bio: {active_users.number_of_users("bio")}, '
		  f'FB Che: {active_users.number_of_users("che")}, '
		  f'FB Phy: {active_users.number_of_users("phy")}')
	print('--------------------')
	print('Facility statistics:')
	year = 2020
	print(f'The facility has given {active_users.number_of_trainings(year)} trainings in {year}.')
	print(f'FB Bio: {active_users.number_of_trainings(year, "bio")}, '
		  f'FB Che: {active_users.number_of_trainings(year, "che")}, '
		  f'FB Phy: {active_users.number_of_trainings(year, "phy")}')
	print('--------------------')



SYSTEM_OPTIONS = Options.OptionReader('SystemOptions.txt')
calling_mode = SYSTEM_OPTIONS.getValue('calling_mode')

with Timer('Getting facility system info from PPMS...', 'Microscope list populated!'):
	equipment = Equipment()

with Timer('Getting active users from PPMS...', 'Active user list populated!'):
	active_bic_users = ActiveBICUsers(equipment)

print_microscope_users(equipment.microscope_list)
print_user_info(active_bic_users.user_list)
print_facility_statistics(equipment, active_bic_users)





# for user_login in active_users:
# 	user = BICUser(user_login)
# 	try:
# 		user.checkBICUserRights()
# 		if user.BIC_user:
# 			active_BIC_users.append(user)
# 	except RuntimeError:
# 		pass
#
# LSM_count = 0
# WF_count = 0
#
# for user in active_BIC_users:
# 	if 'LSM' in user.trained_instrument_types:
# 		LSM_count += 1
# 	if 'WF' in user.trained_instrument_types:
# 		WF_count += 1
#
# print(len(active_BIC_users), LSM_count, WF_count)

