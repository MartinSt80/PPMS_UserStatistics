#!/usr/bin/env python
# -*- coding: utf-8

from lib import Options, PPMSAPICalls


class Instrument:

		def __init__(self, id, name, type):
			self.id = id
			self.name = name
			self.type = type

class Equipment:

	instrument_groups = {'3':'LSM', '7':'LSM', '18':'LSM', '5':'WF', '6':'WF', '16':'WF', '17':'WF', '14':'SR'}

	def __init__(self):
		get_systems = PPMSAPICalls.NewCall(calling_mode)
		self.systems = get_systems.getSystems()
		self.microscope_list = []
		self.microscope_ids = []

	def addMicroscopes(self):
		for system in self.systems:
			system_info = system.split(',')
			if '"Microscope"' == system_info[2] and 'True' == system_info[5] and not system_info[3].startswith('"CAP'):
				self.microscope_list.append(Instrument(system_info[1], system_info[3][1:-1], self.instrument_groups[system_info[1]]))
		for microscope in self.microscope_list:
			self.microscope_ids.append(microscope.id)

class BICUser:

	def __init__(self, login):
		self.login = login
		self.BIC_user = False

	def checkBICUserRights(self):
		get_user_rights = PPMSAPICalls.NewCall(calling_mode)
		user_rights = get_user_rights.getUserRights(self.login)
		for user_right in user_rights:
			user_right = user_right.split(',')
			if 'D' != user_right[0] and user_right[1] in microscopes.microscope_ids:
				self.BIC_user = True
				break

SYSTEM_OPTIONS = Options.OptionReader('SystemOptions.txt')

#facility_id = SYSTEM_OPTIONS.getValue('PPMS_facilityid')
#system_id = SYSTEM_OPTIONS.getValue('PPMS_systemid')
calling_mode = SYSTEM_OPTIONS.getValue('calling_mode')

microscopes = Equipment()
microscopes.addMicroscopes()

get_active_users = PPMSAPICalls.NewCall(calling_mode)
active_users = get_active_users.getAllUsers(True)

active_user_count = 0

for user_login in active_users:
	user = BICUser(user_login)
	try:
		user.checkBICUserRights()
		if user.BIC_user:
			active_user_count += 1
	except RuntimeError:
		pass

print active_user_count