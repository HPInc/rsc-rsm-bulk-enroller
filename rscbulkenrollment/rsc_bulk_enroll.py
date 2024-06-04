# Copyright 2024 HP Development Company, L.P.
# SPDX-License-Identifier: MIT
'''Does bulk enrollment of RSCs'''

import logging
import argparse
import sys
import urllib3

from rscbulkenrollment.rsc import rsc as rscpkg
from rscbulkenrollment.discovery import rsc_finder, importer
from rscbulkenrollment import cloudenrollment, password

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning)  # type: ignore


EXAMPLES = '''
CSV Format
----------
Given RSC.csv as a file with the following contents:

192.168.240.172,CurrentPassword1,Newpassword1
192.168.240.46,CurrentPassword2,Newpassword2
192.168.240.42,CurrentPassword3
rsc-8DD123FFF,CurrentPassword4

The first two lines specify an address, current password and a new password. 
If a password change is required, that is, the RSC's password is still the 
default administrator password set at the factory, the script will change the
current password to the new password.
The third line only specifies the current password. If a password change is 
required the script will fail.
The fourth line specifies the RSC hostname instead of the IP address, which 
by default is "rsc-" with the serial number of the RSC, which can be scanned on 
the RSC QR code label. 
For example, the hostname for serial number 8DD123FFF would be, rsc-8DD123FFF.

Examples
--------
- Pass in a CSV of RSCs to enroll to cloud:
    python3 rsc_bulk_enroll -c RSC.csv
- Pass in RSCs as parameters:
    python3 rsc_bulk_enroll -i 192.168.240.172,CurrentPassword1 192.168.240.46,CurrentPassword2,Newpassword2
- Pass in a CSV of RSCs but only verify if the passwords are ok:
    python3 rsc_bulk_enroll -c RSC.csv -p
- Pass in a CSV of RSCs to enroll to cloud, informing proxy and NTP settings:
    python3 rsc_bulk_enroll -c RSC.csv --ntp myNTPserver.com --proxy http://myproxy.com:8080
'''

def main():
    '''main function'''
    args = parse_args()

    set_verbosity(args.verbose)

    if args.d:
        rscs = rsc_finder.discover_rscs()
        if len(rscs) == 0:
            print("No RSCs discovered. Is your firewall blocking UDP port 5353?")
            sys.exit(1)

        print("Discovered the following RSCs:")
        for rsc in rscs:
            print(rsc.address)
        sys.exit(0)

    if not args.i and not args.c:
        print("ERROR: Need either -c or -i to continue")
        sys.exit(1)

    try:
        rscs = importer.import_rscs(filename=args.c, rsc_list=args.i)
    except ValueError as exp:
        print(exp)
        sys.exit(1)

    if not password.validate_rsc_passwords(rscs):
        sys.exit(1)

    if args.p:
        sys.exit(0)

    if args.change_password:
        exit_code = 0 if password.change_rsc_passwords(rscs) else 1
        sys.exit(exit_code)

    rscs_to_monitor = cloudenrollment.bind_rscs_to_cloud(rscs, args.proxy, args.ntp)

    if len(rscs_to_monitor) > 0:
        cloudenrollment.print_verification_uri(rscs_to_monitor)
        if len([rsc for rsc in rscs_to_monitor if len(rsc.user_code) > 0 ]) > 0:
            print("**** Monitoring RSCs, enter CTRL+C to abort monitoring ****")
            cloudenrollment.monitor_rscs(rscs_to_monitor)

    print("Final state is:")
    for rsc in rscs:
        print_rsc_final_state(rsc)

def parse_args() -> argparse.Namespace:
    '''parses arguments'''

    parser = argparse.ArgumentParser(
        description="RSC Bulk Cloud Enroller")
    parser.add_argument("-c", help="CSV file path", metavar="CSVFilePath")
    parser.add_argument("-e", "--examples", help="Display help message with usage examples.",
                        action='store_true')
    parser.add_argument(
        "-p", help="Only validate passwords and exit.", action='store_true')
    parser.add_argument("-i",
                        help="Specify an RSC's IP, current password\
                            and new password (if necessary), separated by commas.",
                        nargs="*",
                        metavar="addr,curPass[,newPass]")
    parser.add_argument('--verbose', '-v', action='count',
                        default=0, help="Verbose logging. Can be used up to 2 times.")
    parser.add_argument('-d', action='store_true',
                        help=("Discover RSCs in the network and exit."
                              " Requires mDNS port (UDP 5353) to be open."))
    parser.add_argument('--proxy', help="Set this proxy for cloud access.")
    parser.add_argument('--ntp', help="Set this NTP server to correct RSC's times.")
    parser.add_argument('--change-password',
                        help="Only change passwords for the specified RSCs and exit.",
                        action='store_true', dest="change_password")

    args = parser.parse_args()
    if args.examples:
        parser.print_help()
        print(EXAMPLES)
        sys.exit(0)
    return args

def set_verbosity(verbose_level: int) -> None:
    '''Set verbosity level of the root logger'''
    if verbose_level == 1:
        logging.getLogger().setLevel(logging.INFO)
    if verbose_level > 1:
        logging.getLogger().setLevel(logging.DEBUG)

def print_rsc_final_state(rsc: rscpkg.RSC) -> None:
    '''Prints the final state of the RSC'''
    if rsc.monitor_state == rscpkg.TaskState.SUCCESS:
        print("\t", rsc.address, ":", "Enrolled to cloud")
    elif rsc.monitor_state == rscpkg.TaskState.IN_PROGRESS:
        print("\t", rsc.address, ":", "enroll to cloud IN PROGRESS")
    elif rsc.monitor_state == rscpkg.TaskState.CANCELLED:
        print("\t", rsc.address, ":", "enroll to cloud CANCELLED")
    elif rsc.monitor_state == rscpkg.TaskState.ERROR:
        print("\t", rsc.address, ":", "enroll to cloud ERROR")
    elif rsc.monitor_state == rscpkg.TaskState.ALREADY_ENROLLED:
        print("\t", rsc.address, ":", "ALREADY ENROLLED")
    else:
        print("\t", rsc.address, ":", "UNKNOWN STATE")
