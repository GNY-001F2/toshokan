# toshokan 
# Copyright (C) 2019 Aayush Agarwal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This program contains the API calls to the various online book databases
# Functions will call API and attempt to return a standardised set of data
# which will be the same across every program

from openlibrary import openlibrary_results as olib
from googlebooks import googlebooks_results as gbook


def lookup_data(idtype: str="isbn", bookid: int) -> dict:
    # NOTE: Function arguments as yet undecided
    '''
    Attempt to grab the relevant information from different databases.
    If data is not found in one, call next database until a result is found.
    Then return the data and the database it was found in in a dict, for that
    any book can use for its __init__()
    '''
    # WIP
    olib_metadata = olib(idtype, bookid)
    gbook_metadata = gbook(idtype, bookid)
    # prh_results = prh(idtype, bookid)
    if olib_metadata == gbook_metadata:
        # If they are equivalent do nothing
        final_result = olib_metadata
    else:
        # If they are not equivalent, merge the data
        print("Merging results:")
        final_result = merge(gbook_metadata, olib_metadata)
    return final_result


def merge(gbook_metadata, olib_metadata):  # TODO: prh_metadata):
    '''
    Compares the metadata given by 
    '''
    attrs_to_be_examined = []
    for attr in olib_metadata:
        if olib_metadata[attr] == gbook_metadata[attr]:
            final_result[attr] = olib_metadata[attr]
        else:
            attrs_to_be_examined += [attr]
    if 'identifiers' in attrs_to_be_examined:
        attrs_to_be_examined.remove('identifiers')
        olib_identifiers = olib_metadata['identifiers']
        gbook_identifiers = gbook_metadata['identifiers']
        final_result_identifiers = {}
        # We know that LCCN and OCLC data is not available in the Google Books
        # database, so we get this part done first.
        final_result_identifiers['oclc'] = olib_identifiers['oclc']
        final_result_identifiers['lccn'] = olib_identifiers['lccn']
        identifiers_match = True
        mismatched_id_types = []
        for id_type in ['isbn_10', 'isbn_13', 'issn']:
            if olib_identifiers[id_type] == "N/A":
                final_result_identifiers[id_type] = gbook_identifiers[id_type]
            elif gbook_identifiers[id_type] == "N/A":
                final_result_identifiers[id_type] = olib_identifiers[id_type]
            elif olib_identifiers[id_type] == gbook_identifiers[id_type]:
                final_result_identifiers[id_type] = olib_identifiers[id_type]
            # NOTE: WIP: There is an edge case where Google Books and Open
            # Library will have different results. However that means an
            # upstream data entry mistake has happened. Correcting that is well
            # beyond the scope of this program.
            # A workaround would be to let the user decide which entry to
            # validate. However that should be done at a later stage when the
            # manual merge is called.
            else:
                identifiers_match = False
                mismatched_id_types.append(id_type)
    print("The following tags have not matched in the compared strings:\n")
    for attr in attrs_to_be_examined;
        print(f'{attr}')
    print("The following identifier types have also not matched:")
    for id_type in mismatched_id_types:
        print(f'{id_type}')
    print("Please select which data is to be kept.")
    for attr in attrs_to_be_examined:
        input()
    return final_result
