# toshokan
# Copyright (C) 2020 Aayush Agarwal
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

import logging
logger = logging.getLogger(__name__)


def get_openlib_data(idtype: str, book_id: int) -> dict:
    """
    Looks for information on a book from the Open Library database.

    Sends a GET request using the Open Library book lookup JSON API. Returns
    a dictionary created from the result, which is a JSON object containing
    all the metadata about the book.

    arguments:
        idtype  -- The type of ID being looked up. Supported values are ISBN,
                   OCLC, LCCN and OLID.
        book_id -- The value of the idtype being looked up. Any integer value
                   is safe for input.
    return value:
        openlib_data_json -- the dictionary containing the parsed JSON metadata
                             about the book
    """
    from requests import get
    from json import loads
    openlib_request_url = 'https://openlibrary.org/api/books'
    openlib_request_result = get('https://openlibrary.org/api/books?bibkeys'
                                 f'={idtype}:{book_id}&jscmd=data&format=json')
    # NOTE: I looked into using the params argument, but apparently params get
    # converted into the % encoding format, which the Open Library API does not
    # know how to work with.
    openlib_data_json = loads(openlib_request_result.content)
    return openlib_data_json


def process_openlib_data(openlib_data_json: dict) -> dict:
    """
    Process the result from Open Library and extract all relevant information.

    arguments:
        openlib_data_json --
    """
    from re import findall
    current_id_types = ['lccn', 'isbn_13', 'isbn_10', 'oclc', 'issn']
    try:
        openlib_data = openlib_data_json.popitem()[1]
        # We can do this because the json data given by the Open
        # Library API call only has one key with a second level
        # dictionary placed inside it in the format
        # {"search_key":{...actual_data...}}
        #
        # When we call dict.popitem(), we get a tuple with
        # ("search_key", {...actual_data...}) and we only
        # need actual_data. Since search_key can change based on
        # the request, it is not a reliable value to work with.
    except KeyError:
        # If this fails, it means either some catastrophic failure
        # happened or the search result was empty.
        logger.warning("WARNING: The search results are empty! Book not found"
                       " on Open Library.")
        return {}
    relevant_metadata = {}
    try:
        relevant_metadata['title'] = openlib_data['title']
    except KeyError:
        logger.warning("WARNING: This book is untitled.")
        relevant_metadata['title'] = "Untitled"
    try:
        # Because the API is really inconsistent, we may need this if the key
        # 'authors' does not exist.
        check_by_statement = False
        openlib_authors = openlib_data['authors']
        relevant_metadata['authors'] = [author['name'] for author in
                                        openlib_authors]
    except KeyError:
        logger.warning("WARNING: Key 'authors' not found! Checking the data "
                       "for a 'by_statement' key.")
        check_by_statement = True
    if(check_by_statement):
        # The JSON data is extremely inconsistent and poorly documented, so
        # data checks will be error-prone. It is recommended to use other
        # sources as well and merge with the Open Library result to fill in the
        # blanks
        try:
            relevant_metadata['authors'] = [openlib_data['by_statement']]
        except KeyError:
            logger.warning("WARNING: This book has no known authors!")
            relevant_metadata['authors'] = ["UNKNOWN"]
    # Extract publisher names
    try:
        openlib_publishers = openlib_data['publishers']
        publishers = [publisher['name'] for publisher in openlib_publishers]
        relevant_metadata['publishers'] = sorted(publishers)
    except KeyError:
        logger.warning("WARNING: The book has no known publishers.")
        relevant_metadata['publishers'] = ["UNKNOWN"]
    # Extract the date of publishing
    try:
        relevant_metadata['publish_date'] = openlib_data['publish_date']
    except KeyError:
        logger.warning("WARNING: The publishing date is unknown.")
        relevant_metadata['publish_date'] = ["UNKNOWN"]
    openlib_identifiers = openlib_data['identifiers']  # dictionary
    identifiers = {}
    for id_type in current_id_types:
        try:
            # The data is presented as a list, but we will store it as a string
            identifiers[id_type] = openlib_identifiers[id_type][0]
        except KeyError:
            logger.warning(f"WARNING: There is no {id_type} for this book.")
            identifiers[id_type] = ["N/A"]
            # If openlib_data[identifiers] does not contain data for a type of
            # ID we are supporting, then we append it with ["N/A"]
            # NOTE: There are some books in the Open Library database that
            # actually contain multiple ISBNs for the exact same book for some
            # reason. It is not in the scope of this program to sanity-check
            # the upstream database.
    relevant_metadata['identifiers'] = identifiers
    try:
        check_pagination = False
        relevant_metadata['pages'] = openlib_data['number_of_pages']
    except KeyError:
        logger.warning("WARNING: The key \'number_of_pages\' not found in the "
                       "request.\nTrying key \'pagination\'")
        check_pagination = True
    if(check_pagination):
        try:
            page_data = openlib_data['pagination']
            # only doing this because the data is stored inconsistently and I
            # don't want the stupid situation where pagination stores multiple
            # sets of digits and I grab the wrong set
            relevant_metadata['pages'] = max(list(map(int,
                                                      findall(r'\d+',
                                                              page_data))))
            # quick and dirty; should work for 99.9% of books in existence
            # credit:
            # https://www.geeksforgeeks.org/python-extract-numbers-from-string/
        except KeyError:
            logger.warning("WARNING: The key \'pagination\' was also not"
                           "found!\nPage count unknown!")
            relevant_metadata['pages'] = -1
    return relevant_metadata


def openlibrary_results(idtype='ISBN', book_id=0) -> dict:
    """
    Recieves search query and passes it to _get_openlib_data() to get the data
    from The Open Library.

    Then calls process_openlib_data to convert it into the format usable by
    toshokan\'s database and returns it to the caller.
    """
    olib_data = get_openlib_data(idtype, book_id)
    olib_data_processed = process_openlib_data(olib_data)
    return olib_data_processed


if __name__ == "__main__":  # NOTE:WIP
    import argparse
    parser = \
        argparse.ArgumentParser(description="Given an identifier, returns "
                                "information about a book as contained in the "
                                "Open Library database.")
    parser.add_argument("book_id", type=str, help="The identifier of a "
                        "book. Default assumption is that the ID is an ISBN.",
                        metavar="ID")
    # TODO. Let's first get ISBN lookups working.
    # group = parser.add_mutually_exclusive_group()
    parser.add_argument("-i", "--isbn", action="store_const", const=1,
                        default=1,  # type=str,
                        help="The ID is processed as an ISBN. Enabled"
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
    args = parser.parse_args()
    olib_results = get_openlib_data(idtype, args.book_id)
    relevant_metadata = process_openlib_data(olib_results)
    print(relevant_metadata)
    relevant_metadata2 = openlibrary_results(idtype, args.book_id)
    assert relevant_metadata == relevant_metadata2
    print(relevant_metadata)
