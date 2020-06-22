# toshokan 
# Copyright (C) 2020 Aayush Agarwal
#
# Permission granted to use, modify, and/or distribute this program under the
# terms of the GNU Affero General Public License, including the network clause
# with the following exceptions:
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

def get_googlebooks_data(idtype: str, book_id: int) -> dict:
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

def process_googlebooks_data(googlebooks_data_json: dict) -> dict:
    """
    Process the result from Google Books and extract all relevant information.

    arguments:
        googlebooks_data_json -- 
    """
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
            print(googlebooks_data_json)
            print(googlebooks_data_json['totalItems'])
            raise ValueError
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
    try:
        relevant_metadata['title'] = googlebooks_data['title']
    except KeyError:
        logger.warning("WARNING: This book is untitled.")
        relevant_metadata['title'] = "Untitled"
    try:
        # Google Books stores author names in a really neat way.
        relevant_metadata['authors'] = googlebooks_data['authors']
    except KeyError:
        logger.warning("WARNING: This book has no known authors!")
        relevant_metadata['authors'] = ["unknown"]
    # Extract publisher names
    try:
        # Unlike the Open Library API, Google assumes that there is only
        # one publisher. However, to keep the data struture consistent we will
        # store it as a list.
        relevant_metadata['publishers'] = [googlebooks_data['publisher']]
    except KeyError:
        logger.warning("WARNING: The book has no known publishers.")
        relevant_metadata['publishers'] = ["UNKNOWN"]
    # Extract the date of publishing
    try:
        relevant_metadata['publish_date'] = googlebooks_data['publishedDate']
    except KeyError:
        logger.warning("WARNING: The publishing date is unknown.")
        relevant_metadata['publish_date'] = ["UNKNOWN"]
    try:
        identifiers = {'lccn':["N/A"],
                       'isbn_13':["N/A"], # WE ALREADY KNOW THAT LCCN and OCLC
                       'isbn_10':["N/A"], # ARE NOT PRESENT IN THE JSON DATA
                       'oclc':["N/A"],
                       'issn':["N/A"]}
        # A static version to check if the results were actually empty
        noidentifiers = identifiers.copy()
        logger.info("INFO: A Google JSON result does not contain LCCN or OCLC "
                    "data. Consequently those identifiers will remain "
                    "unpopulated")
        googlebooks_identifiers = googlebooks_data['industryIdentifiers']
        # NOTE: Google's reference also mentions an OTHER ID type, but at this
        # point, I don't want to play "Guess Who?" with that data. Probably
        # better to merge these with queries from other databases.
        for gidentifier in googlebooks_identifiers:
            if gidentifier['type'] == 'ISBN_13':
                identifiers['isbn_13'] = [gidentifier['identifier']]
            elif gidentifier['type'] == 'ISBN_10':
                identifiers['isbn_10'] = [gidentifier['identifier']]
            elif gidentifier['type'] == 'ISSN':
                identifiers['issn'] = [gidentifier['identifier']]
        # sanity check here
        if identifiers == noidentifiers:
            logger.warning("WARNING: This book has no industry-standard "
                           "identifiers!")
    except KeyError: # We do this because we're watching for a case where the
                     # industryIdentifiers tag itself is not declared.
                     # So even if it seems redundant, we're bound to do it
                     # twice.
        logger.warning("WARNING: This book has no industry-standard"
                       " identifiers!")
    relevant_metadata['identifiers'] = identifiers
    try:
        relevant_metadata['pages'] = googlebooks_data['pageCount']
    except KeyError:
        logger.warning("WARNING: The number of pages is unknown!")
        relevant_metadata['pages'] = -1
    return relevant_metadata

def googlebooks_results(idtype='ISBN', book_id=0) -> dict:
    """
    Recieves search query and passes it to _get_googlebooks_data() to get the data
    from The Google Books.

    Then calls _process_googlebooks_data to convert it into the format usable by
    toshokan\'s database and returns it to the caller.
    """
    gbooks_data = get_googlebooks_data(idtype, book_id)
    gbooks_data_processed = process_googlebooks_data()
    return gbooks_data_processed

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
    idtype = "isbn"
    # NOTE: 'parser' will be changed to group when I enable the flags for the
    #       ArgumentParser
    args = parser.parse_args()
    gbooks_results = get_googlebooks_data(idtype, args.book_id)
    relevant_metadata = process_googlebooks_data(gbooks_results)
    print(relevant_metadata)
