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

'''
A set of backend functions to handle the interactions between the sqlite
database and the user.
'''

# WARNING: All functions here should be at the moment treated as unsafe until
# the sequence of which calls are to be clubbed together for the user are
# decided.

import sqlite3
import logging
from book import book
logger = logging.getLogger(__name__)

# NOTE: Database Connection, Creation and Initialisation code here.


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
        'Volumes': "CREATE TABLE Volumes(VolumeID INTEGER PRIMARY KEY, BookID,"
                   " FOREIGN KEY(BookID) REFERENCES Books(BookID) ON DELETE "
                   "CASCADE);",
        'Libraries': "CREATE TABLE Libraries(LibraryID INTEGER PRIMARY KEY, "
                     "Name UNIQUE);",
        'Borrowers': "CREATE TABLE Borrowers(BorrowerID INTEGER PRIMARY KEY, "
                     "Name, ContactNumber INT UNIQUE);",
        'Authors_Books': "CREATE TABLE Authors_Books(AuthorID, BookID, "
                         "FOREIGN KEY(AuthorID) REFERENCES Authors(AuthorID) "
                         "ON DELETE CASCADE, FOREIGN KEY(BookID) REFERENCES "
                         "Books(BookID) ON DELETE CASCADE, UNIQUE(AuthorID, "
                         "BookID));",
        'Publishers_Books': "CREATE TABLE Publishers_Books(PublisherID, "
                            "BookID UNIQUE, FOREIGN KEY(PublisherID) "
                            "REFERENCES Publishers(PublisherID) ON DELETE "
                            "CASCADE, FOREIGN KEY(BookID) REFERENCES "
                            "Books(BookID) ON DELETE CASCADE);",
        'Collections': "CREATE TABLE Collections(LibraryID, VolumeID UNIQUE, "
                       "FOREIGN KEY(LibraryID) REFERENCES Libraries(LibraryID)"
                       " ON DELETE CASCADE, FOREIGN KEY(VolumeID) REFERENCES "
                       "Volumes(VolumeID) ON DELETE CASCADE);",
        'Borrowings': "CREATE TABLE Borrowings(BorrowerID, VolumeID, UNIQUE("
                      "BorrowerID, VolumeID), FOREIGN KEY(BorrowerID) "
                      "REFERENCES Borrowers(BorrowerID) ON DELETE CASCADE, "
                      "FOREIGN KEY(VolumeID) REFERENCES Volumes(VolumeID) ON "
                      "DELETE CASCADE);"
    }
    db_cursor.execute("BEGIN;")
    for table in create_table_instructions:
        db_cursor.execute(create_table_instructions[table])
    db_cursor.execute("END;")
    library_id = add_library_to_table(db_cursor)  # Create the Local library
    db_conn.commit()
    return db_conn

# NOTE: Functions to insert new rows into tables here.


def add_record_to_database(db_cursor: sqlite3.Cursor,
                           relevant_book: book,
                           library_id: int = 1) -> sqlite3.Cursor:
    '''
    Given a book object, add its details to the database.
    '''
    # First, add the details of the publisher
    publisher_id = add_publisher_to_table(db_cursor,
                                          relevant_book.publisher)
    # Then add the author(s)
    author_ids = add_authors_to_table(db_cursor, relevant_book.authors)
    # Then add the details of the book
    book_id = add_book_to_database(db_cursor, relevant_book.title,
                                   relevant_book.publish_date,
                                   relevant_book.pages,
                                   relevant_book.identifiers, publisher_id,
                                   author_ids)
    # Then create a volume for this book
    volume_id = add_volume_to_table(db_cursor, book_id)
    # Then add it to the library
    add_volume_library_relation = (db_cursor, volume_id, library_id)
    return db_cursor


def add_book_to_database(db_cursor: sqlite3.Cursor, title: str,
                         publish_date: str, pages: int, identifiers: dict,
                         publisher_id: int, author_ids: int) -> int:
    book_id = add_book_to_table(db_cursor, title, publish_date, pages,
                                identifiers)
    db_cursor = add_authors_book_relation(db_cursor, author_ids, book_id)
    db_cursor = add_publisher_book_relation(db_cursor, publisher_id, book_id)
    return book_id


def add_publisher_to_table(db_cursor: sqlite3.Cursor, name: str) -> int:
    '''
    Add the name of the Publisher to the table "Publishers". Return the
    PublisherID of the added Publisher.
    '''
    try:
        db_cursor.execute("INSERT INTO Publishers(Name) VALUES (?)",
                          [name])
        db_cursor.connection.commit()
    except sqlite3.IntegrityError:
        logger.info(f"The publisher {name} already exists in the database.")
    db_cursor.execute("SELECT PublisherID FROM Publishers WHERE Name=?",
                      [name])
    publisher_row = db_cursor.fetchone()
    publisher_id = int(publisher_row[0])
    return publisher_id


def add_authors_to_table(db_cursor: sqlite3.Cursor, authors: list) -> list:
    '''
    Add a list of authors to the table "Authors". Return the AuthorIDs
    of the authors added to the table.
    '''
    db_cursor = db_conn.cursor()
    author_ids = []
    for author_name in authors:
        author_id = add_author_to_table(db_cursor, author_name)
        author_ids.append(author_id)
    return author_ids


def add_author_to_table(db_cursor: sqlite3.Cursor, name: str) -> int:
    '''
    Add the name of an author to a table and return his author_id.
    '''
    try:
        db_cursor.execute("INSERT INTO Authors(Name) VALUES (?)", [name])
        db_cursor.connection.commit()
    except sqlite3.IntegrityError:
        logger.info(f"The author {name} already exists in the database.")
    db_cursor.execute("SELECT AuthorID FROM Authors WHERE Name=?", [name])
    author_row = db_cursor.fetchone()
    author_id = int(author_row[0])
    return author_id


def add_volume_to_table(db_cursor: sqlite3.Cursor, book_id: int) -> int:
    '''
    Given the book_id of a book, create a volume that is stored in the
    database. Return the volume_id of the newly created volume.
    '''
    db_cursor.execute("INSERT INTO Volumes(BookID) VALUES (?)", [book_id])
    db_cursor.connection.commit()
    # Grab all copies of the book from the Table Volumes
    db_cursor.execute("SELECT VolumeID FROM Volumes WHERE BookID=?", [book_id])
    # We can use SELECT last_inserted_row() to do it quickly but where's the
    # fun in that? I wrote an algorithm to do it to better understand the
    # language
    v_rows: list = db_cursor.fetchall()
    v_rows_index = 0
    v_rows_len = len(v_rows)
    while v_rows_index >= 0 and v_rows_index < v_rows_len:
        v_row = v_rows[v_rows_index]
        volume_id = v_row[0]
        # Check if the book is already mapped to Collections
        db_cursor.execute("SELECT VolumeID FROM Collections WHERE VolumeID=?",
                          [volume_id])
        # NOTE: In schema, Collections(VolumeID) is unique so we can just take
        # the first result
        c_row = db_cursor.fetchone()
        if c_row is None:
            # This means given Volume is not in Collections and is the newly
            # created volume. So we do not need to iterate over the remaining
            break
        else:
            # This book has been found Collections and we need to check the
            # remaining rows.
            v_rows_index += 1
    if v_rows_index >= v_rows_len:
        # Something catastrophic happened
        raise ValueError
    return volume_id


def add_borrower_to_table(db_cursor: sqlite3.Cursor, name: str,
                          contact_number: int) -> int:
    '''
    Add the name and contact_number of a borrower to the table.
    Return the borrower_id of the borrower.
    '''
    try:
        db_cursor.execute("INSERT INTO Borrowers(Name, ContactNumber) VALUES "
                          "(?, ?)", [name, contact_number])
        db_cursor.connection.commit()
    except sqlite3.IntegrityError:
        logger.error("Error: This Contact Number already exists in "
                     "the database!\nReturning the BorrowerID of the existing "
                     "Borrower!")
        db_cursor.execute("SELECT BorrowerID FROM Borrowers WHERE "
                          "ContactNumber=?", [contact_number])
    else:
        db_cursor.execute("SELECT BorrowerID FROM Borrowers WHERE Name=? AND "
                          "ContactNumber=?", [name, contact_number])
    row = db_cursor.fetchone()
    borrower_id = row[0]
    return borrower_id


def add_library_to_table(db_cursor: sqlite3.Cursor,
                         name: str = "Local") -> int:
    '''
    Create the Library entry which contains the name of a library. Return the
    LibraryID of the created library.
    '''
    try:
        db_cursor.execute("INSERT INTO Libraries(Name) VALUES (?)", [name])
        db_cursor.connection.commit()
    except sqlite3.IntegrityError:
        logger.info(f"{name} already exists in the database.")
    library_id = db_cursor.execute("SELECT LibraryID from Libraries WHERE "
                                   "Name=?", [name])
    return library_id


def add_book_to_table(db_cursor: sqlite3.Cursor, title: str, publish_date: str,
                      pages: int, identifiers: dict) -> int:
    '''
    Add information about the book to the table "Books". Return the BookID of
    the added book.
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

# NOTE: Functions to create mappings between two tables here


def add_authors_book_relation(db_cursor: sqlite3.Cursor, author_ids: list,
                              book_id: int) -> sqlite3.Cursor:
    '''
    Create a many to many mapping between authors and books.
    '''
    for author_id in author_ids:
        db_cursor = add_author_book_relation(db_cursor, author_id, book_id)
    return db_cursor


def add_author_book_relation(db_cursor, author_id: str,
                             book_id: int):
    try:
        db_cursor.execute("INSERT INTO Authors_Books(AuthorID, BookID) "
                          "VALUES (?, ?)", [author_id, book_id])
        db_cursor.connection.commit()
    except sqlite3.IntegrityError:
        logger.error("This AuthorID and BookID relation already exists! "
                     "Skipping!")
    return db_cursor


def add_publisher_book_relation(db_cursor: sqlite3.Cursor, publisher_id: int,
                                book_id: int) -> sqlite3.Cursor:
    '''
    Create a one to many mapping between publishers and books.
    '''
    try:
        db_cursor.execute("INSERT INTO Publishers_Books(PublisherID, BookID) "
                          "VALUES (?, ?)", [publisher_id, book_id])
        db_cursor.connection.commit()
    except sqlite3.IntegrityError:
        logger.error("This PublisherID and BookID relation already exists! "
                     "Skipping!")
    return db_cursor


def add_borrower_volume_relation(db_cursor: sqlite3.Cursor, borrower_id: int,
                                 volume_id: int) -> sqlite3.Cursor:
    '''
    Lend a volume with ID volume_id to a borrower with borrower_id.
    '''
    try:
        db_cursor.execute("INSERT INTO Borrowings(BorrowerID, VolumeID) "
                          "VALUES (?, ?)", [borrower_id, volume_id])
        db_cursor.connection.commit()
    except sqlite3.IntegrityError:
        logger.error("This volume is already borrowed! Cannot borrow a volume"
                     " which is already borrowed by you or another person!\n"
                     "If you intended to change the borrower, then return the "
                     "volume to the library first!")
    return db_cursor


def add_volume_library_relation(db_cursor: sqlite3.Cursor, volume_id: int,
                                library_id: int = 1) -> sqlite3.Cursor:
    '''
    Given the volume_id of a Volume, and the library_id of the Library it is
    in, create a database relation between the volume and the library.
    '''
    try:
        db_cursor.execute("INSERT INTO Collections(LibraryID, VolumeID) VALUES"
                          " (?, ?)", [library_id, volume_id])
        db_cursor.connection.commit()
    except sqlite3.IntegrityError:
        logger.error("This volume is already stocked in a library! Cannot add "
                     "it to another library.\nIf you wish to move the book to "
                     "a different library, then remove it from the current "
                     "library first!")
    return db_cursor

# NOTE: Update row entries here!


def update_identifiers(db_cursor: sqlite3.Cursor, identifiers: dict,
                       book_id: int) -> sqlite3.Cursor:
    '''
    Given a list of identifiers, add all of them to the table.
    '''
    db_cursor = update_isbn_10(db_cursor, identifiers['isbn_10'], book_id)
    db_cursor = update_isbn_13(db_cursor, identifiers['isbn_13'], book_id)
    db_cursor = update_issn(db_cursor, identifiers['issn'], book_id)
    db_cursor = update_oclc(db_cursor, identifiers['oclc'], book_id)
    db_cursor = update_lccn(db_cursor, identifiers['lccn'], book_id)
    return db_cursor


def update_isbn_10(db_cursor: sqlite3.Cursor, identifier: int,
                   book_id: int) -> sqlite3.Cursor:
    '''
    Update the ISBN-10 record of a given book_id.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an ISBN-10 and so "
                       "an entry for its ISBN-10 value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET ISBN_10=? WHERE BookID=?", [identifier,
                                                                    book_id])
    return db_cursor


def update_isbn_13(db_cursor: sqlite3.Cursor, identifier: int,
                   book_id: int) -> sqlite3.Cursor:
    '''
    Update the ISBN-13 record of a given book_id.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an ISBN-13 and so "
                       "an entry for its ISBN-13 value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET ISBN_13=? WHERE BookID=?", [identifier,
                                                                    book_id])
    return db_cursor


def update_issn(db_cursor: sqlite3.Cursor, identifier: int,
                book_id: int) -> sqlite3.Cursor:
    '''
    Update the ISSN record of a given book_id.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an ISSN and so "
                       "an entry for its ISSN value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET ISSN=? WHERE BookID=?", [identifier,
                                                                 book_id])
    return db_cursor


def update_oclc(db_cursor: sqlite3.Cursor, identifier: int,
                book_id: int) -> sqlite3.Cursor:
    '''
    Update the OCLC record of a given book_id.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an OCLC and so "
                       "an entry for its OCLC value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET OCLC=? WHERE BookID=?", [identifier,
                                                                 book_id])
    return db_cursor


def update_lccn(db_cursor: sqlite3.Cursor, identifier: int,
                book_id: int) -> sqlite3.Cursor:
    '''
    Update the LCCN record of a given book_id.
    '''
    if identifier <= 0:
        identifier = None
        logger.warning("WARNING: This Book does not have an LCCN and so "
                       "an entry for its LCCN value has not been added to "
                       "the database!")
    db_cursor.execute("UPDATE Books SET LCCN=? WHERE BookID=?", [identifier,
                                                                 book_id])
    return db_cursor

# NOTE: Functions that return rows from tables here

# TODO


if __name__ == "__main__":
    # For testing only
    db_path = "test/"
    db_name = "sqlite_test.db"
    db_conn = connect_to_database(db_path, db_name)
    print(f"db_conn: {db_conn}")
    local_borrowers = {}
    isbn_13s = [
        9780980200447,  # Slow Reading by John Miedema
        9781569702826,  # Barbara by Osamu Tezuka
        9780007934393,  # The Aeneid by Virgil
        9780752858586,  # The Chancellor Manuscript by Robert Ludlum
        9788175993679,  # The Count of Monte Cristo by Alexandre Dumas
        9780718154189,  # Devil May Care by Sebastian Faulks
        9780008241902,  # Dragon Teeth by Michael Crichton
        9780857525956,  # The Bridge of Clay by Marcus Zusak
        # Some other books by authors mentioned earlier
        9780099544319,  # Congo by Michael Crichton
        9781569703533,  # Under The Air by Osamu Tezuka
        9781934287729,  # MW by Osamu Tezuka
        9780312990701,  # The Bancroft Strategy by Robert Ludlum
    ]
    from lookup_data import lookup_data
    from manual_entry import manual_entry
    for isbn_13 in isbn_13s:
        print(isbn_13)
        c = lookup_data("ISBN", isbn_13)
        db_cursor = db_conn.cursor()
        if c.book_id < 0:
            c = manual_entry()
        db_cursor = add_record_to_database(db_cursor, c)
        db_conn.commit()
        # db_cursor.execute("SELECT ")
    db_conn.commit()
    db_conn.close()
