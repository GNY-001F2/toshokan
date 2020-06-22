# Tentative table schema
# CREATE TABLE Books(BookID int primary key, Title, Publish_Date, Pages int);
# CREATE TABLE Authors(AuthorID int primary key, Name);
# CREATE TABLE Publishers(PublisherID int primary key, Name);
# CREATE TABLE ISBN_13(ISBN_13 int primary key, BookID, FOREIGN KEY(BookID) references Books(BookID));
# CREATE TABLE ISBN_10(ISBN_10 int primary key, BookID, FOREIGN KEY(BookID) references Books(BookID));
# CREATE TABLE ISSN(ISSN int primary key, BookID, FOREIGN KEY(BookID) references Books(BookID));
# CREATE TABLE OCLC(OCLC int primary key, BookID, FOREIGN KEY(BookID) references Books(BookID));
# CREATE TABLE LCCN(LCCN int primary key, BookID, FOREIGN KEY(BookID) references Books(BookID));
# CREATE TABLE publishers_books(PublisherID, BookID, Foreign Key(PublisherID) references Publishers(PublisherID), Foreign Key(BookID) references Books(BookID), UNIQUE(PublisherID, BookID));
# CREATE TABLE authors_books(AuthorID, BookID, Foreign Key(AuthorID) references Authors(AuthorID), Foreign Key(BookID) references Books(BookID), UNIQUE(AuthorID, BookID));

import sqlite3, logging
logger = logging.getLogger(__name__)

# definitions are temporary for testing purposes
def connect_to_database(db_path: str = "test/",
                        db_name: str = "sqlite_test.db") -> sqlite3.Connection:

    try:
        db_conn = sqlite3.connect(f"file:{db_path}{db_name}?mode=rw", uri=True)
    except sqlite3.OperationalError:
        logger.warning("WARNING: File not found! Creating new database!")
        db_conn = create_new_database(db_path, db_name)
    return db_conn

def create_new_database(db_path: str = "test/",
                        db_name: str = "sqlite_test.db") -> sqlite3.Connection:

    db_conn = sqlite3.connect(f"file:{db_path}{db_name}?mode=rwc", uri=True)
    db_cursor = db_conn.cursor()
    create_table_instructions = {
        'Books': "CREATE TABLE Books(BookID INTEGER PRIMARY KEY,"
                 "Title, Publish_Date, Pages int);",
        # SQLite has a quirk by which if I were to add AUTOINCREMENT to the
        # schema, I would still have to expand int to INTEGER. Which makes it
        # pointless because then I would not be able to reuse a deleted entry
        # because AFAIK AUTOINCREMENT guarantees that the table will use a
        # higher value.
        'Authors': "CREATE TABLE Authors(AuthorID int primary key, Name);",
        'Publishers': "CREATE TABLE Publishers(PublisherID int primary key,"
                      "Name);",
        'ISBN_13': "CREATE TABLE ISBN_13(ISBN_13 int primary key, BookID, "
                   "FOREIGN KEY(BookID) references Books(BookID));",
        'ISBN_10': "CREATE TABLE ISBN_10(ISBN_10 int primary key, BookID, "
                   "FOREIGN KEY(BookID) references Books(BookID));",
        'ISSN': "CREATE TABLE ISSN(ISSN int primary key, BookID, "
                "FOREIGN KEY(BookID) references Books(BookID));",
        'OCLC': "CREATE TABLE OCLC(OCLC int primary key, BookID, "
                "FOREIGN KEY(BookID) references Books(BookID));",
        'LCCN': "CREATE TABLE LCCN(LCCN int primary key, BookID, "
                "FOREIGN KEY(BookID) references Books(BookID));",
        'publishers_books': "CREATE TABLE publishers_books(PublisherID, "
                            "BookID, Foreign Key(PublisherID) references "
                            "Publishers(PublisherID), Foreign Key(BookID) "
                            "references Books(BookID), UNIQUE(PublisherID, "
                            "BookID));",
        'authors_books': "CREATE TABLE authors_books(AuthorID, BookID, "
                         "Foreign Key(AuthorID) references Authors(AuthorID), "
                         "Foreign Key(BookID) references Books(BookID), "
                         "UNIQUE(AuthorID, BookID));",
    }
    for table in create_table_instructions:
        db_cursor.execute(create_table_instructions[table])
    db_conn.commit()
    return db_conn

# Instructions to append stuff
# INSERT INTO Books(BookID, Title, Publish_Date, Pages) Values (1, "The Rise and Fall of Athens", "1960", 318);
# insert into Authors(AuthorID, Name) values (1, "Plutarch");
# insert into Publishers(PublisherID, Name) values (1, "Penguin Books");
# INSERT INTO LCCN(LCCN, BookID) VALUES (63005876, 1);
# and rest of the identifiers
# insert into publishers_books(publisherID, bookID) values (1,1);
# insert into authors_books(AuthorID, BookID) values (1,1);

def add_book_to_table(db_conn: sqlite3.Connection,
                         relevant_metadata: dict) -> sqlite3.Connection:
    db_cursor = db_conn.cursor()
    title = relevant_metadata['title']
    publish_date = relevant_metadata['publish_date']
    pages = relevant_metadata['pages']
    book_insertion_str = f'({title}, {publish_date}, {pages})'
    return db_conn

def add_publisher_to_table(db_conn: sqlite3.Connection,
                           relevant_metadata: dict) -> sqlite3.Connection:
    pass

def add_author_to_table(db_conn: sqlite3.Connection,
                        relevant_metadata: dict) -> sqlite3.Connection:
    pass

def create_publisher_book_relations(db_conn: sqlite3.Connection,
                                 relevant_metadata: dict) -> sqlite3.Connection:
    pass

def create_author_book_relations(db_conn: sqlite3.Connection,
                                 relevant_metadata: dict) -> sqlite3.Connection:
    pass

if __name__ == "__main__":
    # For testing only
    import "../book_lookup_apis"
    db_conn = connect_to_database()
    print(db_conn)
    db_conn.close()
