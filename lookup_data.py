# toshokan
# Copyright (C) 2019 Aayush Agarwal
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

# This program contains the API calls to the various online book databases
# Functions will call API and attempt to return a standardised set of data
# which will be the same across every program

from openlibrary import openlibrary_results as olib
from googlebooks import googlebooks_results as gbook
from book import book

def lookup_data(idtype: str, bookid: int) -> book:
    # NOTE: Function arguments as yet undecided
    '''
    Attempt to grab the relevant information from different databases.
    Currently only Open Library and Google Books are implemented.
    Compare the data and attempt to fill in the blanks for a more complete
    record. Return the data in a dictionary.
    '''
    # NOTE: Open Library uses uppercase idtypes, while Google Books uses
    # lowercase.
    olib_metadata = olib(idtype, bookid)
    gbook_metadata = gbook(idtype, bookid)
    # prh_results = prh(idtype, bookid)
    if olib_metadata == gbook_metadata:
        # If they are equivalent do nothing
        final_result = olib_metadata
    elif gbook_metadata == {}:
        final_result = olib_metadata
    elif olib_metadata == {}:
        final_result = gbook_metadata
    else:
        # If they are not equivalent, merge the data
        print("Non-identical data found. Merging results:")
        final_result = merge_data(gbook_metadata, olib_metadata)
    if final_result == {}:
        final_book = book(book_id=-1)
    else:
        final_book = book(final_result['title'],
                          final_result['authors'],
                          final_result['publisher'],
                          final_result['publish_date'],
                          final_result['identifiers'],
                          final_result['pages'])
    return final_book


def merge_data(gbook_metadata: dict, olib_metadata: dict) -> dict:
    # TODO: prh_metadata:
    '''
    Compares the metadata given by Google Books and Open Library and merges
    them. In case of conflicts, the user is asked to select the correct item.

    gbook_metadata --
    olib_metadata --
    '''
    attrs_to_be_examined = []  # Contains all the tags to be matched
    final_result = {}  # Contains the merged data
    # IF a tag (attr) from the Open Library data matches the corresponding
    # tag from Google Books, we directly add it to final_result
    # Otherwise we add the tag to the list of tags that need to be matched.
    for attr in olib_metadata:
        if olib_metadata[attr] == gbook_metadata[attr]:
            final_result[attr] = olib_metadata[attr]
        else:
            attrs_to_be_examined.append(attr)
    print("The following tags have not matched in the compared results:\n")
    for attr in attrs_to_be_examined:
        print(f'{attr}')
    authorlist = []
    print("Please select which data is to be kept.\n")
    if 'authors' in attrs_to_be_examined:
        attrs_to_be_examined.remove('authors')
        final_result['authors'] = _merge_authors(olib_metadata['authors'],
                                                 gbook_metadata['authors'])
    if 'identifiers' in attrs_to_be_examined:
        attrs_to_be_examined.remove('identifiers')
        final_result['identifiers'] = \
            _merge_identifiers(olib_metadata['identifiers'],
                               gbook_metadata['identifiers'])
    for attr in attrs_to_be_examined:
        print(f'Current item to be merged is {attr}')
        compared_values = {'1': olib_metadata[attr], '2': gbook_metadata[attr]}
        for index, value in compared_values.items():
            print(index, value, sep='. ', end=" ")
        print("")
        while True:
            chosen_value = input(f'Please choose which {attr} is to be kept: ')
            if chosen_value not in ['1', '2']:
                print("Invalid entry. Please choose from the options shown!")
                continue
            final_result[attr] = compared_values[chosen_value]
            break
    return final_result


def _merge_authors(olib_authors: list, gbook_authors: list) -> list:
    # set() will merge all author names except when there is a case mismatch,
    # which we will have to do manually
    combined_authors = sorted(set(olib_authors, gbook_authors))
    combined_authors_deduped = _check_duplicate_authors(combined_authors)
    return combined_authors_deduped


def _check_duplicate_authors(combined_authors: list) -> list:
    combined_authors_len = len(combined_authors)
    deduped_authors_list = []
    while combined_authors_len > 0:
        # First consume the item at the first index. We want to check all
        # other values against this item and flag duplicates.
        possible_duplicates = [combined_authors[0]]
        combined_authors.remove(combined_authors[0])
        combined_authors_len = len(combined_authors)
        # Next, we make sure that the list is not empty.
        if combined_authors_len == 0:
            # At this point it should not be possible for possible_duplicates
            # to have more than one value, so we can just add it and break out
            # of this loop if all names in combined_authors have been exhausted
            deduped_authors_list.extend(possible_duplicates)
            break
        # If the list is not empty, then we compare the value in
        # possible_duplicates with the remaining values in the list using a
        # loop
        i = 0
        while i < combined_authors_len:
            # If the value matches, then we add it to possible_duplicates and
            # remove it from the list.
            # Otherwise we iterate to the next item in the list.
            if possible_duplicates[0].lower() == combined_authors[i].lower():
                # While we _can_ check if an identical same name is already
                # present in possible_duplicates, _check_duplicate_authors()
                # works under the assumption that the data passed to it is
                # already sorted and naively deduplicated.
                possible_duplicates.append(combined_authors[i])
                combined_authors.remove(combined_authors[i])
                combined_authors_len = len(combined_authors)
            else:
                i += 1
        p_d_len = len(possible_duplicates)
        if p_d_len == 1:
            deduped_authors_list.extend(possible_duplicates)
        elif p_d_len > 1:
            print(f"Duplicates found for: {possible_duplicates[0]}")
            j = 0
            while j < p_d_len:
                # NOTE: More intuitive for a user to choose from 1 to x
                print(f'{(j+1)}. {possible_duplicates[j]}', end=" ")
                j += 1
            print("")
            while True:
                correct_name = \
                    int(input("Please choose the most correct "
                              "version! ")) - 1
                # NOTE: We subtract 1 to get the index back
                # If the user gives an invalid input, we inform him of the
                # invalid input and ask him to re-enter. Don't wan the program
                # crashing because of an out_of_range error.
                if correct_name < 0 or correct_name >= p_d_len:
                    print("Invalid entry. Please choose from the options "
                          "shown!")
                    continue
                deduped_authors_list.append(possible_duplicates[correct_name])
                break
    return deduped_authors_list


def _merge_identifiers(olib_identifiers: dict,
                       gbook_identifiers: dict) -> dict:
    print("Merging identifiers.")
    final_result_identifiers = {}
    # We know that LCCN and OCLC data is not available in the Google Books
    # database, so we get this part done first.
    final_result_identifiers['oclc'] = olib_identifiers['oclc']
    final_result_identifiers['lccn'] = olib_identifiers['lccn']
    identifiers_match = True
    mismatched_id_types = []
    for id_type in ['isbn_10', 'isbn_13', 'issn']:
        if olib_identifiers[id_type] == None:
            final_result_identifiers[id_type] = gbook_identifiers[id_type]
        elif gbook_identifiers[id_type] == None:
            final_result_identifiers[id_type] = olib_identifiers[id_type]
        elif olib_identifiers[id_type] == gbook_identifiers[id_type]:
            final_result_identifiers[id_type] = olib_identifiers[id_type]
        else:
            identifiers_match = False
            mismatched_id_types.append(id_type)
    if not identifiers_match:
        print("The following identifiers have not matched: ")
        for id_type in mismatched_id_types:
            print(id_type, end=' ')
        print("")
        for id_type in mismatched_id_types:
            print(f"Showing found values for the idenifier \'{id_type}\'")
            id_type_options = {'1': olib_identifiers[id_type],
                               '2': gbook_identifiers[id_type]}
            for index, identifier in id_type_options.items():
                print(index, identifier, sep='. ', end=" ")
            print("")
            while True:
                chosen_value = input(f"Please choose the correct value: ")
                if chosen_value not in ['1', '2']:
                    print("Invalid entry. Please choose from the "
                          "options shown!")
                    continue
                final_result_identifiers[id_type] = \
                    id_type_options[str(chosen_value)]
                break
    return final_result_identifiers


if __name__ == "__main__":
    isbn_13s = [
        9780980200447,  # Slow Reading by John Miedema
        9781569702826,  # Barbara by Osamu Tezuka
        9780007934393,  # The Aeneid by Virgil
        9780752858586,  # The Chancellor Manuscript by Robert Ludlum
        9788175993679,  # The Count of Monte Cristo by Alexandre Dumas
        9780718154189,  # Devil May Care by Sebastian Faulks
        9780008241902,  # Dragon Teeth by Michael Crichton
        9780857525956,  # The Bridge of Clay by Marcus Zusak
        9780099544319
    ]
    for isbn in isbn_13s:
        lookup_dict = lookup_data("isbn", isbn)
        print(lookup_dict)
