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
                 book_id: int = -1,
                 title: str = "_unknown",
                 authors: list = ["Anonymous"],
                 publishers: list = ["_unknown/Self-published"],
                 publish_date: list = "_unknown",
                 identifiers: dict = {
                     'lccn': "N/A",
                     'isbn_13': "N/A",
                     'isbn_10': "N/A",
                     'oclc': "N/A",
                     'issn': "N/A"  # Magazines use this.
                 },
                 pages: int = 0):
        '''
        __init__() is used to create a book which contains the relevant
        information about it.
        '''
        # Let's add each id_type to the list of identifiers
        self.identifiers = {}
        for id_type in ['lccn', 'isbn_13', 'isbn_10', 'oclc', 'issn']:
            try:
                self.identifiers[id_type] = identifiers[id_type]
            except KeyError:
                self.identifiers[id_type] = ["N/A"]
            # Any other error is beyond the scope of this at the moment
        # NOTE:this will be updated by whatever process adds the book to the
        # collection (TODO)
        self.__book_id = book_id
        self.title = title
        self.authors = []
        for author in authors:
            self.authors.append(author)
        self.pages = pages
        self.publishers = publishers
        self.publish_date = publish_date

    @property  # make this read-only; the database will assign an ID
    def book_id(self):
        return self.__book_id


if __name__ == '__main__':
    a = book()
    print(a.book_id)
