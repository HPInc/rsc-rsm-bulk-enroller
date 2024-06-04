# Copyright 2024 HP Development Company, L.P.
# SPDX-License-Identifier: MIT
'''Functions for importing RSCs from CSV files or lists'''
import csv
from io import TextIOWrapper
from typing import List, Union

from rscbulkenrollment.rsc import rsc as rscpkg


def import_rscs(*, filename=None, rsc_list=None) -> List[rscpkg.RSC]:
    '''Reads RSCs from the csv file and command line options and returns a list of RSCs'''

    result = []

    if filename:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            result.extend(get_rscs_from_csv(csvfile))
    if rsc_list:
        result.extend(get_rscs_from_csv(rsc_list))
    return result

def get_rscs_from_csv(csv_object: Union[TextIOWrapper, list]) -> List[rscpkg.RSC]:
    '''Reads a csv object (text reader or list) and returns the list of RSCs contained there.'''
    rsc_list = []

    reader = csv.reader(csv_object)
    for line in reader:
        if len(line) < 2:
            raise ValueError(
                f"Error in line '{line}': need to have at least address and current password")
        rsc_list.append(rscpkg.RSC(
            line[0],
            line[1],
            line[2] if len(line) > 2 else ""
        ))
    return rsc_list
