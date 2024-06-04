# Copyright 2024 HP Development Company, L.P.
# SPDX-License-Identifier: MIT
'''Functions that handle RSC password changes and validation'''

import logging
from typing import List
from rscbulkenrollment.rsc import rsc as rscpkg

def change_rsc_passwords(rscs: List[rscpkg.RSC]) -> bool:
    '''Changes the password for the RSCs passed in. Returns True if all RSCs'
    passwords were successfully changed. False otherwise.'''
    changed_all = True

    for rsc in rscs:
        try:
            logging.info("Logging in '%s'", rsc.address)
            rsc.login()
            logging.info("Changing password for '%s'", rsc.address)
            rsc.change_password()
            print(f"Changed password for RSC '{rsc.address}'")
        except rscpkg.RSCException as exp:
            print(exp)
            changed_all = False
    return changed_all

def validate_rsc_passwords(rscs: List[rscpkg.RSC]) -> bool:
    '''Validates if RSCs' current passwords work and whether they need to be changed.
    If that's the case, checks if a new password was specified.
    Returns True if all RSCs pass the checks.'''
    result = True
    for rsc in rscs:
        logging.info("Logging in '%s'", rsc.address)

        try:
            rsc.login()
            logging.info("Current password ok for '%s'", rsc.address)
            needs_password_change = rsc.check_needs_change_password()
            if needs_password_change:
                logging.info("RSC '%s' needs password change.",
                             rsc.address)
                if not rsc.new_password:
                    logging.error("RSC '%s' needs password change,\
                                but no new password was specified for it", rsc.address)
                    result = False
        except rscpkg.RSCException as exp:
            logging.error(exp)
            result = False
    return result
