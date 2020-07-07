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
          library
        * Title: str, title of the book
        * Author(s): list, names of the authors who wrote this book
        * Pages: int, the number of pages in the book
        * Publisher: list, the list of publishers who published this edition
        * Date of Publishing: the date this edition was published
    '''

    def __init__(self,
                 title: str = "UNKNOWN",
                 authors: list = ["UNKNOWN"],
                 publisher: str = "UNKNOWN",
                 publish_date: str = "UNKNOWN",
                 identifiers: dict = {
                     'lccn': None,
                     'isbn_13': None,
                     'isbn_10': None,
                     'oclc': None,
                     'issn': None  # Magazines use this.
                 },
                 pages: int = 0,  # 0 represents unknown
                 book_id: int = 0):  # 0 represents book not extracted from db
        '''
        __init__() is used to create a book which contains the relevant
        information about it.
        '''
        # Let's add each id_type to the list of identifiers
        self.identifiers = {}
        for identifier in identifiers:
            self.identifiers[identifier] = identifiers[identifier]
        self._book_id = book_id
        self.title = title
        self.authors = []
        self.authors.extend(authors)
        self.pages = pages
        self.publisher = publisher
        self.publish_date = publish_date

    @property  # make this read-only; the database will assign an ID
    def book_id(self):
        return self._book_id

    def __str__(self):
        return str({
            'book_id': self.book_id,
            'title': self.title,
            'authors': self.authors,
            'publisher': self.publisher,
            'publish_date': self.publish_date,
            'identifiers': self.identifiers,
            'pages': self.pages
            })

if __name__ == '__main__':
    import lookup_data as ld
    #relevant_metadata = ld.lookup_data('isbn', 9780980200447)
    #b = book(relevant_metadata)
    #print(b.book_id, b.title, b.authors, b.publisher, b.identifiers,
          #b.publish_date, b.pages, sep=" ")
    c = book("Slow Reading",
             ['John Miedema'],
             'Litwin Books Llc',
             'March 2009',
             {
                 'oclc': 297222669,
                 'lccn': 2008054742,
                 'isbn_13': 9780980200447,
                 'issn': None,
                 'isbn_10': 1936117363
                     },
             92)
    print(c.book_id, c.title, c.authors, c.publisher, c.identifiers,
          c.publish_date, c.pages, sep=" ")
    print(c)
