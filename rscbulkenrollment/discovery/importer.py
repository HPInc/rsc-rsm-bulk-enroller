# Copyright 2024 HP Development Company, L.P.
# SPDX-License-Identifier: MIT
'''Functions for importing RSCs from CSV files or lists'''
import csv
import logging
from io import TextIOWrapper
from typing import List, Union

from rscbulkenrollment.rsc import rsc as rscpkg


def import_rscs(*, filename=None, rsc_list=None) -> List[rscpkg.RSC]:
    '''Reads RSCs from the csv file and command line options and returns a list of RSCs'''
    logging.debug("Importing RSCs from file '%s' and list '%s'", filename, rsc_list)
    result = []

    if filename:
        with open(filename, 'r', newline='', encoding='utf-8-sig') as csvfile:
            result.extend(get_rscs_from_csv(csvfile, guess_dialect(csvfile)))
    if rsc_list:
        result.extend(get_rscs_from_csv(rsc_list))
    return result

def guess_dialect(csv_object: Union[TextIOWrapper, list]) -> csv.Dialect:
    '''Guesses the dialect of a csv object'''
    if isinstance(csv_object, TextIOWrapper):
        csv_object.seek(0)
        dialect = csv.Sniffer().sniff(csv_object.read(1024))
        csv_object.seek(0)
        logging.debug("Guessed dialect. Separator: '%s', quotechar: '%s', escapechar: '%s', doublequote: '%s', lineterminator: '%s', quoting: '%s'",
            dialect.delimiter, dialect.quotechar, dialect.escapechar, dialect.doublequote, dialect.lineterminator, dialect.quoting)
        return dialect
    else:
        logging.debug("No file to guess dialect from, using default excel dialect.")
        return csv.excel

def get_rscs_from_csv(csv_object: Union[TextIOWrapper, list], dialect: csv.Dialect=csv.excel) -> List[rscpkg.RSC]:
    '''Reads a csv object (text reader or list) and returns the list of RSCs contained there.'''
    rsc_list = []

    reader = csv.reader(csv_object, dialect=dialect)
    line_no = 1
    for line in reader:
        if len(line) < 2:
            raise ValueError(
                f"Error in line '{line}': need to have at least address and current password")
        new_rsc = rscpkg.RSC(
            line[0],
            line[1],
            line[2] if len(line) > 2 else ""
        )
        if new_rsc not in rsc_list:
            rsc_list.append(new_rsc)
        else:
            logging.warning("Duplicate RSC found in CSV file line %d: %s", line_no, new_rsc)
        line_no += 1
    return rsc_list
