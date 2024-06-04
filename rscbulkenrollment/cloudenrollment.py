# Copyright 2024 HP Development Company, L.P.
# SPDX-License-Identifier: MIT
'''Functions for enrollment rscs to the cloud'''
import logging
import time
from typing import List
from rscbulkenrollment.rsc import rsc as rscpkg

VERIFICATION_URI = "https://rsm.anyware.hp.com/console/binding/device/activate?user_codes="

def bind_rscs_to_cloud(rscs: List[rscpkg.RSC],
                          proxy: str,
                          ntp: str) -> List[rscpkg.RSC]:
    '''Initiates the enrollment process for all RSCs passed in.
    Returns the list of RSCs that have successfully started the process.'''
    rscs_to_monitor: List[rscpkg.RSC] = []

    for rsc in rscs:
        try:
            logging.info("Logging in '%s'", rsc.address)
            rsc.login()

            needs_password_change = rsc.check_needs_change_password()
            if needs_password_change:
                logging.info("Changing password for '%s'", rsc.address)
                rsc.change_password()
                print(f"Changed password for rscpkg.RSC '{rsc.address}'")
                logging.info("Logging in to '%s' with new password",
                             rsc.address)
                rsc.login()
            if proxy or ntp:
                logging.info(
                    "Changing proxy/NTP settings to rscpkg.RSC %s", rsc.address)
                rsc.set_proxy_ntp_settings(proxy, ntp)
                time.sleep(2)

            if rsc.is_enrolled_to_cloud():
                logging.info("RSC '%s' is already enrolled to cloud",
                             rsc.address)
                continue
            logging.info("Enrolling to cloud '%s'", rsc.address)
            rsc.enroll_to_cloud()
            rscs_to_monitor.append(rsc)
        except rscpkg.RSCException as exp:
            logging.error(exp)
    return rscs_to_monitor


def print_verification_uri(rscs_to_monitor: List[rscpkg.RSC]) -> None:
    '''Prints the verification URI'''
    user_codes = [rsc.user_code for rsc in rscs_to_monitor if len(rsc.user_code) > 0 ]
    if len(user_codes) > 0:
        print("Verification URI is ready! Paste this link in a web browser:",
              VERIFICATION_URI + ",".join(user_codes), sep='\n')
    else:
        print("No user codes received!")
        for rsc in rscs_to_monitor:
            if rsc.monitor_state != rscpkg.TaskState.ALREADY_ENROLLED:
                rsc.monitor_state = rscpkg.TaskState.ERROR

def monitor_rscs(rscs_to_monitor: List[rscpkg.RSC]) -> None:
    '''Monitors the cloud enrollment process'''
    in_prog_for_monitor = [rsc for rsc in rscs_to_monitor if rsc.monitor_state ==
                           rscpkg.TaskState.IN_PROGRESS and len(rsc.bind_monitor) > 0]
    if len(in_prog_for_monitor) != len(rscs_to_monitor):
        raise ValueError(
            ("There are RSCs to monitor that do not have a monitor"
             " location or are not in a running state!")
            )

    running = len(rscs_to_monitor)
    try:
        while running > 0:
            for rsc in rscs_to_monitor:
                if rsc.monitor_state != rscpkg.TaskState.IN_PROGRESS:
                    continue
                try:
                    if enrollment_complete(rsc):
                        running -= 1
                except rscpkg.RSCException as exp:
                    logging.error(exp)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Interrupted! Canceling enrollment...")
        for rsc in rscs_to_monitor:
            if rsc.monitor_state == rscpkg.TaskState.IN_PROGRESS:
                cancel_enrollment(rsc)
                print(f"Enrollment canceled for RSC '{rsc.address}'")
                rsc.monitor_state = rscpkg.TaskState.CANCELLED

def enrollment_complete(rsc: rscpkg.RSC) -> bool:
    '''Handles the enrollment task state of an RSC.
    Returns True if the enrollment for the RSC is complete, successful or not.
    False if enrollment is still running.'''
    task_state = rsc.get_bind_status()
    if task_state == rscpkg.TaskState.IN_PROGRESS:
        logging.info(
            "RSC '%s' enrollment in progress...", rsc.address)
        return False

    if task_state == rscpkg.TaskState.SUCCESS:
        logging.info(
            "RSC '%s' was enrolled successfully!", rsc.address)
    else:
        logging.info(
            "RSC '%s' was NOT enrolled successfully!", rsc.address)
    return True

def cancel_enrollment(rsc) -> None:
    '''Cancels the enrollment process for an RSC'''
    if rsc.monitor_state == rscpkg.TaskState.IN_PROGRESS:
        rsc.cancel_enrollment()
        logging.info("RSC '%s' enrollment canceled", rsc.address)
    else:
        logging.info("RSC '%s' enrollment not in progress", rsc.address)
