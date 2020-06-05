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
