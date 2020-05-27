# toshokan 
# Copyright (C) 2020 Aayush Agarwal
#
# Permission granted to use, modify, and/or distribute this program under terms
# similar to the GNU Affero General Public License, including the network
# clause, with the following exceptions:
#
# In compliance with Google's Terms of Service, you are expressly forbidden
# from monetising or commercialising this program in any state, whether a
# a verbatim or derived copy is used. You must also comply with any other terms
# that are stated in Google's terms of service.
# 
# Google's terms of service can be found at:
#
# <https://developers.google.com/books/terms>
#
# Should you wish to use the the overall work (Toshokan) in a commercial 
# version, you must exclude this program from that version. Permission from
# Google to monetise their services does not grant you permission to use this
# program to use this program in a commercial capacity.

import logging
logger = logging.getLogger(__name__)

def _get_googlebooks_data(idtype: str, book_id: int) -> dict:
    """
    Looks for information on a book from the Google Books database.

    Sends a GET request using the Google Books lookup JSON API. Returns
    a dictionary created from the result, which is a JSON object containing
    all the metadata about the book.

    arguments:
        idtype  -- The type of ID being looked up. Supported values are ISBN,
                   OCLC, LCCN.
        book_id -- The value of the idtype being looked up. Any integer value
                   is safe for input.
    return value:
        googlebooks_data_json -- the dictionary containing the parsed JSON metadata
                             about the book
    """
    from requests import get
    from json import loads
    googlebooks_request_result = get('https://www.googleapis.com/books/v1/'
                                     f'volumes?q={idtype}:{book_id}')
    googlebooks_data_json = loads(googlebooks_request_result.content)
    return googlebooks_data_json

def _process_googlebooks_data(googlebooks_data_json: dict) -> dict:
    """
    Process the result from Google Books and extract all relevant information.

    arguments:
        googlebooks_data_json -- 
    """
    from re import findall
    current_id_types = ['lccn', 'isbn_13', 'isbn_10', 'oclc']
    # NOTE: Based on preliminary searches, Google Books does not appear to
    # catalogue LCCN values in the JSON reference for each volume. This is
    # highly unusual as their API reference explicitly mentions lccn as a valid
    # search query.
    # Yet the JSON data structure does not store an LCCN-type
    # industryIdentifiers key based on their JSON reference.
    # Querying a valid LCCN from the Library of Congress catalogue did not
    # return any results, with totalItems = 0, but the ISBN of that same book
    # returned a valid result.
    # The OCLC-type is also not present in the JSON reference, but I have not
    # yet attempted to search for results using it.
    # The experimental status of the v1 API might be the reason for
    # this. Further investigation is needed.
    try:
        if(googlebooks_data_json['totalItems'] > 1):
            raise ValueError
        #elif(googlebooks_data_json['totalItems'] < 1):
            #raise KeyError
    except ValueError:
        logger.warning("WARNING: More than one result found for requested "
                       "search. This means someone has tried to pass a more "
                       "general search result to this scraper. Continuing "
                       "with first search result.")
        # NOTE: Possible avenue for future feature creep and bloatism :^)
    except KeyError:
        # If this fails, it means either some catastrophic failure
        # happened or the search result was empty.
        logger.warning("WARNING: The search results are empty! Book not found"
                       " on Google Books!")
    try:
        googlebooks_data = googlebooks_data_json['items'][0]['volumeInfo']
        # We can do this because the json data given by the Google Books
        # API call is neatly broken into three keys: kind, totalItems and items.
        #
        # The data we care about is an individual volume, specifically the
        # first result present in the key items. The Python JSON module neatly
        # indexes the values in items as a sorted list. The actual Google JSON
        # reference also indexes the results as numbers starting from zero.
        #
        # Within the node, we only need the key volumeInfo which contains the
        # subset of data we are interested in, apart from other bits and pieces
        # we will strip out.
    except KeyError:
        # If this fails, it means either some catastrophic failure
        # happened or the search result was empty.
        logger.warning("WARNING: The search results are empty! Book not found"
                       " on Google Books!")
        return {}
    relevant_metadata = {}
    # Extract publisher names
    try:
        googlebooks_publishers = googlebooks_data['publishers']
        publishers = [publisher['name'] for publisher in googlebooks_publishers]
        relevant_metadata['publishers'] = sorted(publishers)
    except KeyError:
        logger.warning("WARNING: The book has no known publishers.")
        relevant_metadata['publishers'] = ["UNKNOWN"]
    # Extract the date of publishing
    try:
        relevant_metadata['publish_date'] = googlebooks_data['publish_date']
    except KeyError:
        logger.warning("WARNING: The publishing date is unknown.")
        relevant_metadata['publish_date'] = ["UNKNOWN"]
    googlebooks_identifiers = googlebooks_data['identifiers']  # dictionary
    identifiers = {}
    for id_type in current_id_types:
        try:
            identifiers[id_type] = googlebooks_identifiers[id_type]
            # Stored as a list, in case a single book has more than one
            # value for one ID type
        except KeyError:
            logger.warning(f"WARNING: There is no {id_type} for this book.")
            identifiers[id_type] = ["N/A"]
            # If googlebooks_data[identifiers] does not contain data for a type of
            # ID we are supporting, then we append it with ["N/A"]
    relevant_metadata['identifiers'] = identifiers
    try:
        check_pagination = False
        relevant_metadata['pages'] = googlebooks_data['number_of_pages']
    except KeyError:
        logger.warning("WARNING: The key \'number_of_pages\' not found in the "
                       "request.\nTrying key \'pagination\'")
        check_pagination = True
    if(check_pagination):
        try:
            page_data = googlebooks_data['pagination']
            # only doing this because the data is stored inconsistently and I
            # don't want the stupid situation where pagination stores multiple
            # sets of digits and I grab the wrong set
            relevant_metadata['pages'] = max(list(map(int,
                                                      findall(r'\d+',
                                                              page_data))))
            # quick and dirty; should work for 99.9% of books in existence
            # credit:
            # https://www.geeksforgeeks.org/python-extract-numbers-from-string/
        except:
            logger.warning("WARNING: The key \'pagination\' was also not found!"
                           "\nPage count unknown!")
            relevant_metadata['pages'] = -1
    try:
        relevant_metadata['title'] = googlebooks_data['title']
    except KeyError:
        logger.warning("WARNING: This book is untitled.")
        relevant_metadata['title'] = "Untitled"
    try:
        googlebooks_authors = googlebooks_data['authors']
        relevant_metadata['authors'] = [author['name'] for author in
                                        googlebooks_authors]
    except KeyError:
        logger.warning("WARNING: This book has no known authors!")
        relevant_metadata['authors'] = ["unknown"]
    #try:
    #    googlebooks_authors = googlebooks_data['authors']
    #    relevant_metadata['authors'] = [author['name'] for author in
    #                                    googlebooks_authors]
    return relevant_metadata

def googlebooks_results(idtype='ISBN', book_id=0) -> dict:
    """
    Recieves search query and passes it to _get_googlebooks_data() to get the data
    from The Google Books.

    Then calls _process_googlebooks_data to convert it into the format usable by
    toshokan\'s database and returns it to the caller.
    """
    olib_data = _get_googlebooks_data(idtype, book_id)
    olib_data_processed = _process_googlebooks_data()
    return olib_data_processed

if __name__=="__main__":  #NOTE:WIP
    import argparse
    parser = \
        argparse.ArgumentParser(description = "Given an identifier, returns "
                                "information about a book as contained in the "
                                "Google Books database.")
    parser.add_argument("book_id", type = str, help = "The identifier of a "
                        "book. Default assumption is that the ID is an ISBN.",
                        metavar = "ID")
    # TODO. Let's first get ISBN lookups working.
    #group = parser.add_mutually_exclusive_group()
    parser.add_argument("-i", "--isbn", action="store_const", const=1,
                       default=1, #type=str,
                       help="The ID is processed as an ISBN. Enabled default.")
    # group.add_argument("-l", "--lccn", action="store_const", const = 1,
    #                    default = 0, type = str,
    #                    help = "The ID is processed as an LCCN.")
    # group.add_argument("-o", "--oclc", action="store_const", const = 1,
    #                    default = 0, type = str,
    #                    help = "The ID is processed as an OCLC identifier.")
    # group.add_argument("--olid", action="store_const", const = 1,
    #                    default = 0, type = str, 
    #                    help = "The ID is processed as Google Books's "
    #                    "internal identifier the book.")
    # NOTE: ISBN is temporary, will be replaced by code from the parser later
    idtype = "ISBN"
    # NOTE: 'parser' will be changed to group when I enable the flags for the
    #       ArgumentParser
    args = parser.parse_args()
    olib_results = _get_googlebooks_data(idtype, args.book_id)
    print(olib_results)
    relevant_metadata = _process_googlebooks_data(olib_results)
    print(relevant_metadata)
