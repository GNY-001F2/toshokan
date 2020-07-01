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


import sqlite3
import logging
from book import book
logger = logging.getLogger(__name__)


def connect_to_database(db_path: str,
                        db_name: str) -> sqlite3.Connection:
    '''
    Given a path and file name, connect to a SQLite v3 database. If the file
    does not exist, then it is created by calling create_new_database().
    '''
    try:
        db_conn = sqlite3.connect(f"file:{db_path}{db_name}?mode=rw", uri=True)
    except sqlite3.OperationalError:
        logger.warning("WARNING: File not found! Creating new database!")
        db_conn = create_new_database(db_path, db_name)
        db_conn.close()
        db_conn = connect_to_database(db_path, db_name)
    return db_conn


def create_new_database(db_path: str,
                        db_name: str) -> sqlite3.Connection:
    '''
    Given a path and file name, create an SQLite v3 database and create the
    table schema for the newly created database.
    '''
    db_conn = sqlite3.connect(f"file:{db_path}{db_name}?mode=rwc", uri=True)
    db_cursor = db_conn.cursor()
    create_table_instructions = {
        'Books': "CREATE TABLE Books(BookID INTEGER PRIMARY KEY, Title, "
                 "PublishDate, Pages INT, ISBN_10 INT UNIQUE, ISBN_13 INT "
                 "UNIQUE, ISSN INT UNIQUE, OCLC INT UNIQUE, LCCN INT UNIQUE);",
        'Authors': "CREATE TABLE Authors(AuthorID INTEGER PRIMARY KEY, "
                   "Name UNIQUE);",
        'Publishers': "CREATE TABLE Publishers(PublisherID INTEGER PRIMARY "
                      "KEY, Name UNIQUE);",
        'Authors_Books': "CREATE TABLE Authors_Books(AuthorID, BookID, "
                         "FOREIGN KEY(AuthorID) REFERENCES Authors(AuthorID) "
                         "ON DELETE CASCADE, FOREIGN KEY(BookID) REFERENCES "
                         "Books(BookID) ON DELETE CASCADE, UNIQUE(AuthorID, "
                         "BookID));",
        'Publishers_Books': "CREATE TABLE Publishers_Books(PublisherID, "
                            "BookID, FOREIGN KEY(PublisherID) REFERENCES "
                            "Publishers(PublisherID) ON DELETE CASCADE, "
                            "FOREIGN KEY(BookID) REFERENCES Books(BookID) ON "
                            "DELETE CASCADE, UNIQUE(PublisherID, BookID));"
    }
    #db_cursor.execute("BEGIN;")
    for table in create_table_instructions:
        #print(create_table_instructions[table])
        db_cursor.execute(create_table_instructions[table])
    #db_cursor.execute("END;")
    db_conn.commit()
    return db_conn


def add_book_to_database(db_cursor: sqlite3.Cursor,
                         relevant_book: book) -> sqlite3.Cursor:
    '''
    Given a book object, add its details to the database.
    '''
    publisher_id = add_publisher_to_table(db_cursor,
                                          relevant_book.publisher)
    author_ids = add_authors_to_table(db_cursor, relevant_book.authors)
    book_id = add_book_to_table(db_cursor, relevant_book.title,
                                relevant_book.publish_date,
                                relevant_book.pages,
                                relevant_book.identifiers)
    db_cursor = add_authors_book_relations(db_cursor, author_ids, book_id)
    db_cursor = add_publisher_book_relations(db_cursor, publisher_id, book_id)
    return db_cursor


def add_book_to_table(db_cursor: sqlite3.Cursor, title: str, publish_date: str,
                      pages: int, identifiers: dict) -> int:
    '''
    Add information about the book to the table "Books".
    '''
    isbn_10 = identifiers['isbn_10']
    isbn_13 = identifiers['isbn_13']
    issn = identifiers['issn']
    oclc = identifiers['oclc']
    lccn = identifiers['lccn']
    db_cursor = db_cursor.execute("INSERT INTO Books(Title, PublishDate, "
                                  "Pages, ISBN_10, ISBN_13, ISSN, OCLC, LCCN) "
                                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                  [title, publish_date, pages, isbn_10,
                                   isbn_13, issn, oclc, lccn])
    db_cursor.connection.commit()
    db_cursor = db_cursor.execute("SELECT BookID FROM Books WHERE Title=? AND "
                                  "PublishDate=? AND Pages=? AND (ISBN_10=? "
                                  "OR ISBN_10 IS NULL) AND (ISBN_13=? OR "
                                  "ISBN_13 IS NULL) AND (ISSN=? OR ISSN IS "
                                  "NULL) AND (OCLC=? OR OCLC IS NULL) AND "
                                  "(LCCN=? OR LCCN IS NULL)",
                                  [title, publish_date, pages, isbn_10,
                                   isbn_13, issn, oclc, lccn])
    book_row = db_cursor.fetchone()
    book_id = book_row[0]
    print(f"bookid: {type(book_id)}")
    return book_id


def add_publisher_to_table(db_cursor: sqlite3.Cursor, publisher: str) -> int:
    '''
    Add the name of the Publisher to the table "Publishers".
    '''
    db_cursor.execute("INSERT INTO Publishers(Name) VALUES (?)", [publisher])
    db_cursor.connection.commit()
    db_cursor.execute("SELECT PublisherID FROM Publishers WHERE Name=?",
                      [publisher])
    publisher_row = db_cursor.fetchone()
    publisher_id = int(publisher_row[0])
    return publisher_id


def add_authors_to_table(db_cursor: sqlite3.Cursor, authors: list) -> list:
    '''
    Add the name of the Author to the table "Authors".
    '''
    db_cursor = db_conn.cursor()
    author_ids = []
    for author in authors:
        db_cursor.execute("INSERT INTO Authors(Name) VALUES (?)", [author])
        db_cursor.connection.commit()
        db_cursor.execute("SELECT AuthorID FROM Authors WHERE Name=?",
                          [author])
        author_row = db_cursor.fetchone()
        author_id = int(author_row[0])
        author_ids.append(author_id)
    return author_ids


def _add_identifiers_to_table(db_cursor: sqlite3.Cursor, identifiers: dict,
                              book_id: int) -> sqlite3.Cursor:
    '''
    Internal function used to add the various identification tags such as ISBNs
    for the book.
    '''
    print(f"_add_identifiers_to_table(): book_id type: {type(book_id)}")
    db_cursor = _add_isbn_10(db_cursor, identifiers['isbn_10'], book_id)
    db_cursor = _add_isbn_13(db_cursor, identifiers['isbn_13'], book_id)
    db_cursor = _add_issn(db_cursor, identifiers['issn'], book_id)
    db_cursor = _add_oclc(db_cursor, identifiers['oclc'], book_id)
    db_cursor = _add_lccn(db_cursor, identifiers['lccn'], book_id)
    return db_cursor


def _add_isbn_10(db_cursor: sqlite3.Cursor, identifier: int,
                 book_id: int) -> sqlite3.Cursor:
    '''
    Internal function that adds the ISBN-10 record.
    '''
    assert type(identifier) is int
    print(f"book_id type: {type(book_id)}")
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an ISBN-10 and so "
                       "an entry for its ISBN-10 value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET ISBN_10=? WHERE BookID=?", [identifier,
                                                                    book_id])
    return db_cursor


def _add_isbn_13(db_cursor: sqlite3.Cursor, identifier: int,
                 book_id: int) -> sqlite3.Cursor:
    '''
    Internal function that adds the ISBN-13 record.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an ISBN-13 and so "
                       "an entry for its ISBN-13 value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET ISBN_13=? WHERE BookID=?", [identifier,
                                                                    book_id])
    return db_cursor


def _add_issn(db_cursor: sqlite3.Cursor, identifier: int,
              book_id: int) -> sqlite3.Cursor:
    '''
    Internal function that adds the ISSN record.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an ISSN and so "
                       "an entry for its ISSN value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET ISSN=? WHERE BookID=?", [identifier,
                                                                 book_id])
    return db_cursor


def _add_oclc(db_cursor: sqlite3.Cursor, identifier: int,
              book_id: int) -> sqlite3.Cursor:
    '''
    Internal function that adds the OCLC record.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an OCLC and so "
                       "an entry for its OCLC value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET OCLC=? WHERE BookID=?", [identifier,
                                                                 book_id])
    return db_cursor


def _add_lccn(db_cursor: sqlite3.Cursor, identifier: int,
              book_id: int) -> sqlite3.Cursor:
    '''
    Internal function that adds the LCCN record.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an LCCN and so "
                       "an entry for its LCCN value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET LCCN=? WHERE BookID=?", [identifier,
                                                                 book_id])
    return db_cursor


def add_authors_book_relations(db_cursor: sqlite3.Cursor, author_ids: list,
                               book_id: int) -> sqlite3.Cursor:
    '''
    Create a many to many mapping between authors and books.
    '''
    for author_id in author_ids:
        db_cursor.execute("INSERT INTO Authors_Books(AuthorID, BookID) "
                          "VALUES (?, ?)", [author_id, book_id])
    db_cursor.connection.commit()
    return db_cursor


def add_publisher_book_relations(db_cursor: sqlite3.Cursor, publisher_id: int,
                                 book_id: int) -> sqlite3.Cursor:
    '''
    Create a one to many mapping between publishers and books.
    '''
    db_cursor.execute("INSERT INTO Publishers_Books(PublisherID, BookID) "
                      "VALUES (?, ?)", [publisher_id, book_id])
    db_cursor.connection.commit()
    return db_cursor


if __name__ == "__main__":
    # For testing only
    db_path = "test/"
    db_name = "sqlite_test.db"
    db_conn = connect_to_database(db_path, db_name)
    print(f"db_conn: {db_conn}")
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
    db_cursor = db_conn.cursor()
    db_cursor = add_book_to_database(db_cursor, c)
    db_conn.commit()
    # db_cursor.execute("SELECT ")
    db_conn.commit()
    db_conn.close()
