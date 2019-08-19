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

# Requests is needed to get the data from libraries
# json is needed to convert the requested data into useable dicts

current_id_types = ['lccn', 'isbn_13', 'isbn_10', 'oclc']
import requests, json
from re import findall

'''
Takes the book's ID type and sends it to the Open Libraries database. Supported
types are all that the Open Library API supports: ISBN, LCCN, OCLC and OLID
Receives data formatted in JSON with all the relevant info.
Converts the received JSON data into a python dictionary.
Returns the dictionary to the caller.
'''
def get_openlibs_data(idtype: str, bookid: int) -> dict:
    # WIP
    return \      
        json.loads(\
            requests.get(f'https://openlibrary.org/api/books?bibkeys'
                         '={idtype}:{isbn}&jscmd=data&format=json').content)

def process_openlibs_data(openlib_data_json: dict) -> dict:
    '''
    We have the relevant json data, so let's do this
    '''
    try:
        openlib_data = openlib_data_json.popitem()[1]
        # We can do this because the json data given by the Open
        # Library API call only has one key with a second level dictionary
        # placed inside it.
        # When we call popitem(), we get a tuple with
        # ("search_key", actual_data) and we only need actual_data
    except KeyError:
        # NOTE: I don't yet know how to correctly handle this
        # exception so I am returning an empty dictionary currently
        # This should not crash the program, and instead the user
        # should be able to call another database for the correct date.
        return {}
    # relevant_metadata = {}
    try:
        publishers = openlib_data['publishers']
        nonlocal relevant_metadata['publishers'] = \
            [publisher['name'] for publisher in publishers]
    except KeyError:
        relevant_metadata['publishers'] = ["Unknown/Self-Published"]
    # NOTE: WIP
            # Let's add each id_type to the list of identifiers
    for id_type in current_id_types:
        try:
            nonlocal identifiers[id_type] = identifiers[id_type]
        except KeyError:
            nonlocal identifiers[id_type] = ["N/A"]
    relevant_metadata['identifiers'] = identifiers
    page_data = openlib_data['pagination']
    # only doing this because the data is stored inconsistently and I don't
    # want the stupid situation where pagination stores multiple sets of digits
    # and I grab the wrong set
    relevant_metadata['pages'] = max(list(map(int, re.findall(r'\d+',
                                                              page_data))))
    # quick and dirty; should work for 99.9% of books in existence
    # credit: https://www.geeksforgeeks.org/python-extract-numbers-from-string/

if __name__=="__main__": #WIP
    import argparse
    parser = \
        argparse.ArgumentParser(description = "Given an identifier, returns "
                                "information about a book as contained in the "
                                "Open Library database.")
    parser.add_argument("book_id", type = str, help = "The identifier of a "
                        "book. Default assumption is that the ID is an ISBN.",
                        metavar = "ID")
    # TODO. Let's first get ISBN lookups working.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", "--isbn", action="store_const", const = 1,
                       default = 1, type = str,
                       help = "The ID is processed as an ISBN. Enabled by "
                       "default.")
    # group.add_argument("-l", "--lccn", action="store_const", const = 1,
    #                    default = 0, type = str,
    #                    help = "The ID is processed as an LCCN.")
    # group.add_argument("-o", "--oclc", action="store_const", const = 1,
    #                    default = 0, type = str,
    #                    help = "The ID is processed as an OCLC identifier.")
    # group.add_argument("--olid", action="store_const", const = 1,
    #                    default = 0, type = str, 
    #                    help = "The ID is processed as Open Library's "
    #                    "internal identifier the book.")
    # NOTE: ISBN is temporary, will be replaced by code from the parser later
    idtype = "ISBN"
    # NOTE: 'parser' will be changed to group when I enable the flags for the
    #       ArgumentParser
    olib_results = _get_openlibs_data(idtype, parser.parse_args().book_id)
