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

import requests, json

'''
Takes the book's ID type and sends it to the Open Libraries database. Supported
types are all that the Open Library API supports: ISBN, LCCN, OCLC and OLID
Receives data formatted in JSON with all the relevant info.
Converts the received JSON data into a python dictionary.
Returns the dictionary to the caller.
'''
def _get_openlibs_data(idtype: str, bookid: int) -> dict:
    # WIP
    return \      
        json.load(requester.(f'https://openlibrary.org/api/books?'
                             'bibkeys={idtype}:{isbn}&jscmd=data&format=json'))
   
if __name__=="__main__": #WIP
    import argparse    
    parser = \
        argparse.ArgumentParser(description = "Given an idenitifier, returns "
                                "information about a book as contained in the "
                                "Open Library database.")
    
    parser.add_argument("book_id", type = str, help = "The identifier of a " 
                        "book. Default assumption is that the ID is an ISBN.",
                        metavar = "ID")
    # TODO. Let's first get ISBN lookups working.
    # group = parser.add_mutually_exclusive_group()
    # group.add_argument("-l", "--lccn", action="store_const", const = 1,
    #                    default = 0, type = str,
    #                    help = "The ID is now an LCCN type.")
    # group.add_argument("-o", "--oclc", action="store_const", const = 1,
    #                    default = 0, type = str,
    #                    help = "The ID is now an OCLC type.")
    # group.add_argument("--olid", action="store_const", const = 1,
    #                    default = 0, type = str, 
    #                    help = "The ID is now an OCLC type.")
    # NOTE: ISBN is temporary, will be replaced by code from the parser later
    olib_results = _get_openlibs_data("ISBN", parser.parse_args().book_id)
