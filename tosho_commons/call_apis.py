# toshokan 
# Copyright (C) 2019 Aayush Agarwal
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General  Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# This program contains the API calls to the various online book databases
# Functions will call API and attempt to return a standardised set of data
# which will be the same across every program
# TODO

def get_information_from_database() -> tuple:
    # NOTE: Function arguments as yet undecided
    '''
    Attempt to grab the relevant information from different databases.
    If data is not found in one, call next database until a result is found.
    Then return the data and the database it was found in in a tuple, forthat any book can use for
    its __init__()
    '''
    # TODO
    pass

def _get_from_openlibrary(idtype="isbn", bookid: int) -> dict:
    api_call_result = requests.get(f'https://openlibrary.org/api/books?bibkeys'
                         '={idtype}:{bookid}&jscmd=data&format=json')
    return json.loads(api_call_result.content)

def __get_from_goodreads() -> dict:
    # NOTE: To be implemented later
    pass  # Do nothing for now

def __get_from_google() -> dict:
    # NOTE: To be implemented later
    pass  # Do nothing for now

def __get_from_amazon() -> dict:
    # NOTE: To be implemented later
    pass  # Do nothing for now

# Insert more databases below
