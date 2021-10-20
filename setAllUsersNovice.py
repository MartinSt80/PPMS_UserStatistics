#!/usr/bin/env python
# -*- coding: utf-8

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

	system_ids = [2, 3, 5, 7, 16, 17, 18, 58]

	def __init__(self):
		self.active_system_list = []
		self._get_bic_systems()

	def _get_bic_systems(self):

		def identify_active_systems(ppms_system_string):
			ppms_system_info = ppms_system_string.split(',')
			# check if a system is active, and needs to set to novice
			if 'True' == ppms_system_info[5] and int(ppms_system_info[1]) in Equipment.system_ids:
				new_system = Instrument(ppms_system_info[1],
											ppms_system_info[3].strip('"'),
											ppms_system_info[2].strip('"'),
											None,
											)
				return new_system

		ppms_system_call = PPMSAPICalls.NewCall(calling_mode)
		ppms_system_list = ppms_system_call.getSystems()

		for system in ppms_system_list:
			instrument = identify_active_systems(system)
			if instrument:
				self.active_system_list.append(instrument)


class Instrument:

	def __init__(self, id, name, type, status):
		self.id = id
		self.name = name
		self.type = type
		self.status = status
		self.unfiltered_login_list = self._get_active_user_rights()


	def _get_active_user_rights(self):

		user_rights_call = PPMSAPICalls.NewCall(calling_mode)
		user_rights = user_rights_call.getUserRights(system_id=self.id)

		login_list =[]
		for user_right in user_rights:
			user_right = user_right.split(',')
			if ('D' != user_right[0]) and ('.' in user_right[1]):
				login_list.append(user_right[1].strip('"'))
		return login_list


def print_microscope_users(microscope_list):
	print('Microscope statistics:')
	for m in microscope_list:
		print(f'{m.name} (id: {m.id}) is a {m.type}')
		print(f'All logins: {m.unfiltered_login_list}')
		print('--------------------')

def set_userright_novice(ppms_call, system_obj):
	with Timer(f'Setting users of {system_obj.name} to Novice...', 'Done!'):
		for user_login in system_obj.unfiltered_login_list:
			try:
				ppms_call.setUserRight(system_obj.id, user_login, 'N')
				print(f'{user_login} set to Novice on {system_obj.name}!')
			except Errors.APIError as e:
				print(f'Error: Setting{user_login} to Novice on {system_obj.name} failed!')
				print(f'Cause: {e.msg}')


SYSTEM_OPTIONS = Options.OptionReader('SystemOptions.txt')
calling_mode = SYSTEM_OPTIONS.getValue('calling_mode')

with Timer('Getting facility system info from PPMS...', 'Microscope list populated!'):
	equipment = Equipment()

# print_microscope_users(equipment.active_system_list)

set_novice_call = PPMSAPICalls.NewCall(calling_mode)
with Timer('Setting user_rights to novice...', 'All user rights set to novice!'):
	for system in equipment.active_system_list:
		set_userright_novice(set_novice_call, system)




