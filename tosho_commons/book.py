current_id_types = ['lccn', 'isbn_13', 'isbn_10', 'oclc']


class book:
    '''
    A book contains some information about itself. This book class does the
    same.
    The following information is currently present:
        * Identifier(s): dict, a dictionary containing various book identifiers
            * ISBN-13: a list of ISBNs assigned
            * ISBN-10: a list of ISBNs assigned
            * LCCN: list, but ideally there should only be one LCCN. stored as
                * stored as a list for ease of programming algorithmically
            * OCLC: list, but I don't know anything about it currently.
                * may or may not be unique, but stored as a list for ease of
                programming
        * Unique ID: dict, This is the ID that is used by the API which is
          called.
        * For example, if the Open Library API is used, then the  data stored
          is {'openlibrary':'OLID'}
        * For a book manually added to the database, this will be {'N/A':'N/A'}
        * Title: str, title of the book
        * Author(s): list, names of the authors who wrote this book
        * Pages: int, the number of pages in the book
        * Publisher: list, the list of publishers who published this edition
        * Date of Publishing: the date this edition was published
    '''

    def __init__(self,
                 identifiers={
                     'lccn': ["N/A"],
                     'isbn_13': ["N/A"],
                     'isbn_10': ["N/A"],
                     'oclc': ["N/A"]
                     # Any other IDs added to current_id_types will
                     # automatically receive N/A
                 },
                 unique_id={
                     'N/A': "N/A"
                 },
                 title="_unknown", authors=["Anonymous"],
                 pages=0,
                 publishers=["_unknown/Self-published"],
                 publish_date="_unknown"):
        '''
        __init__() is used to create a book which contains the relevant 
        information about it.
        '''
        # Let's add each id_type to the list of identifiers
        for id_type in current_id_types:
            try:
                self.identifiers[id_type] = identifiers[id_type]
            except KeyError:
                self.identifiers[id_type] = ["N/A"]
            # Any other error is beyond the scope of this at the moment
        self.unique_id = unique_id
        self.title = title
        for author in authors:
            self.authors.append(author)
        self.pages = pages
        self.publishers = publishers
        self.publish_date = publish_date

    def __init__(self, id_type: str, id_str: str):
        '''
        This __init__() will use api calls to acquire the correct information
        and call __init__(self,ARGS) responsible for value assignment
        '''
        # NOTE: To be implemented at a much later date
        __init__(self)  # for now just call defaults to prevent funky behaviour
        pass