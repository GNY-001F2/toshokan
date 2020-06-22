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
    Then return the data and the database it was found in in a tuple, forthat any book can use for
    its __init__()
    '''
    # TODO
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

def merge(gbook_metadata, olib_metadata):
    attrs_to_be_examined = []
    for attr in olib_metadata:
        if olib_metadata[attr] == gbook_metadata[attr]:
            final_result[attr] = olib_metadata[attr]
        else:
            attrs_to_be_examined += [attr]
    print("The following tags have not matched in the compared strings:\n")
    for attr in attrs_to_be_examined;
        print(f'{attr}\n')
    print("Please select which data is to be kept.")
    return final_result
