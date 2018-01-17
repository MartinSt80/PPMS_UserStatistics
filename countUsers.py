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

	def addMicroscopes(self):
		for system in self.systems:
			system_info = system.split(',')
			if '"Microscope"' == system_info[2] and 'True' == system_info[5] and not system_info[3].startswith('"CAP'):
				self.microscope_list.append(Instrument(system_info[1], system_info[3][1:-1], self.instrument_groups[system_info[1]]))


#
# class BICUser:
#
# 	def __init__(self, login):
# 		self.login = login
# 		self.active_instruments = {}
# 		for key in self.instruments:
# 			self.active_instruments[key] = False
# 		self.active_groups = {}
# 		for key in self.instrument_groups:
# 			self.active_groups[key] = False
#
# 	def setAutonomies(self):
# 		get_user_rights = PPMSAPICalls.NewCall(calling_mode)
# 		user_rights = get_user_rights.get

SYSTEM_OPTIONS = Options.OptionReader('SystemOptions.txt')

#facility_id = SYSTEM_OPTIONS.getValue('PPMS_facilityid')
#system_id = SYSTEM_OPTIONS.getValue('PPMS_systemid')
calling_mode = SYSTEM_OPTIONS.getValue('calling_mode')
#
# get_active_users = PPMSAPICalls.NewCall(calling_mode)
# active_users = get_active_users.getAllUsers(True)
#
# user_list = []
#
# for user_login in active_users:
# 	user = BICUser(user_login)
# 	user.setAutonomies()


microscopes = Equipment()
microscopes.addMicroscopes()
for system in microscopes.microscope_list:
	print system.id, system.name, system.type