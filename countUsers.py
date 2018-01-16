#!/usr/bin/env python
# -*- coding: utf-8

from lib import Options, PPMSAPICalls

SYSTEM_OPTIONS = Options.OptionReader('SystemOptions.txt')

facility_id = SYSTEM_OPTIONS.getValue('PPMS_facilityid')
system_id = SYSTEM_OPTIONS.getValue('PPMS_systemid')
calling_mode = SYSTEM_OPTIONS.getValue('calling_mode')

get_all_users = PPMSAPICalls.NewCall(calling_mode)
all_users = get_all_users.getAllUsers(True)


#aaa