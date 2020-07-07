import logging
logger = logging.getLogger(__name__)
from book import book

def manual_entry() -> book:
    '''
    The user manually creates a new entry to be stored in the database.
    '''
    title = input("Please enter the title of the book (leave blank if not "
                  "known): ")
    title = title if len(title) > 0 else "UNKNOWN"
    authors = []
    i = 1
    while True:
        author_name = input(f"Please enter the name of the {i}{_i_suffix(i)} "
                            "author (leave blank to end): ")
        if author_name != '':
            authors.append(author_name)
        else:
            break
        i += 1
    authors = authors if len(authors) != 0 else ["UNKNOWN"]
    publisher = input("Please enter the name of the publisher (leave blank if "
                      "not known): ")
    publisher = publisher if len(publisher) > 0 else "UNKNOWN"
    publish_date = input("Please enter the date of publishing (leave blank if "
                         "not known): ")
    publish_date = publish_date if len(publish_date) > 0 else "UNKNOWN"
    identifiers = {
        'isbn_10': None,
        'isbn_13': None,
        'issn': None,
        'oclc': None,
        'lccn': None
    }
    for identifier in identifiers:
        while True:
            identifier_value = input(f"Please enter the {identifier.upper()} "
                                     "of the book (leave blank if not known)"
                                     ": ")
            if identifier_value == '':
                break
            try:
                identifiers[identifier] = int(identifier_value)
            except ValueError as e:
                logger.error("Invalid value provided for "
                             f"{identifier.upper()}.")
                logger.error(e)
                logger.error("Please enter a valid value!")
                continue
            break
    pages = 0
    while True:
        try:
            pages_str = input("Please enter the number of pages of this book "
                              "(leave blank if not known): ")
            pages = pages if len(pages_str) == 0 else int(pages_str)
        except ValueError as e:
            logger.error("Invalid input!")
            logger.error(e)
            logger.error("Please re-enter the number of pages!")
            continue
        break
    book_manual = book(title, authors, publisher, publish_date, identifiers,
                       pages)
    return book_manual

def _i_suffix(i: int) -> str:
    '''
    Checks the number and returns the appropriate suffix for it.
    '''
    i_str = str(i)
    suff_123 = {1: 'st', 2: 'nd', 3: 'rd'}
    suff_th = 'th'
    i_last_num = int(i_str[-1])
    return suff_123[i_last_num] if i_last_num in suff_123 else suff_th


if __name__ == "__main__":
    c = manual_entry()
    print(c)
