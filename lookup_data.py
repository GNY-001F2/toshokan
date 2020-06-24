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


def lookup_data(idtype: str, bookid: int) -> dict:
    # NOTE: Function arguments as yet undecided
    '''
    Attempt to grab the relevant information from different databases.
    If data is not found in one, call next database until a result is found.
    Then return the data and the database it was found in in a dict, for that
    any book can use for its __init__()
    '''
    # NOTE: Open Library uses uppercase idtypes, while Google Books uses
    # lowercase.
    olib_metadata = olib(idtype.upper(), bookid)
    gbook_metadata = gbook(idtype.lower(), bookid)
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
        print("Merging results:")
        final_result = merge(gbook_metadata, olib_metadata)
    return final_result


def merge(gbook_metadata: dict, olib_metadata: dict) -> dict:
    # TODO: prh_metadata:
    '''
    Compares the metadata given by 
    '''
    attrs_to_be_examined = []  # Contains all the tags to be matched
    final_result = {}  # Contains the merged data
    for attr in olib_metadata:
        if olib_metadata[attr] == gbook_metadata[attr]:
            final_result[attr] = olib_metadata[attr]
        else:
            attrs_to_be_examined += [attr]
    print("The following tags have not matched in the compared results:\n")
    for attr in attrs_to_be_examined:
        print(f'{attr}')
    authorlist = []
    pick_authors = False
    print("Please select which data is to be kept.\n")
    if 'authors' in attrs_to_be_examined:
        attrs_to_be_examined.remove('authors')
        final_result['authors'] = _merge_authors(olib_metadata['authors'],
                                                 gbook_metadata['authors'])
    if 'identifiers' in attrs_to_be_examined:
        print("The following identifier types have not matched:")
        for id_type in mismatched_id_types:
            print(f'{id_type}')
        attrs_to_be_examined.remove('identifiers')
        final_result['identifiers'] = \
            _merge_identifiers(olib_metadata['identifiers'],
                               gbook_metadata['identifiers'])
    for attr in attrs_to_be_examined:
        print(f'Current item to be merged is {attr}')
        compared_values = {'1': olib_metadata[attr], '2': gbook_metadata[attr]}
        for index, value in compared_values.items():
            print(index, value, sep='. ')
        final_result[attr] = compared_values[input('Please choose which '
                                                   f'{attr} is to be kept: ')]
    return final_result


def _merge_authors(olib_authors: list, gbook_authors: list) -> list:
    # set() will merge all author names except when there is a case mismatch,
    # which we will have to do manually
    combined_authors = sorted(set(olib_authors,gbook_authors))
    combined_authors_deduped = _check_duplicate_authors(combined_authors)
    return combined_authors_deduped


def _check_duplicate_authors(combined_authors: list) -> list:
    combined_authors_len = len(combined_authors)
    deduped_authors_list = []
    c_a_l_range = range(combined_authors_len)
    for i in c_a_l_range:
        possible_duplicates = []
        for j in c_a_l_range:
            if combined_authors[i].lower() == \
                combined_authors[j].lower():
                possible_duplicates += [combined_authors[j]]
                combined_authors.pop(j)
        p_d_len = len(possible_duplicates)
        if p_d_len == 1:
            deduped_authors_list += possible_duplicates
        elif p_d_len > 1:
            p_d_l_range = range(p_d_len)
            print(f"Duplicates found for: {combined_authors[i]}")
            for i in p_d_l_range:
                # NOTE: More intuitive for a user to choose from 1 to x
                print(f'{i+1}. {possible_duplicates[i]}', end=" ")
            correct_name = \
                int(input("\nPlease choose the most correct version!"))-1
            # NOTE: We subtract 1 to get the index back
            deduped_authors_list += possible_duplicates[correct_name]
    return deduped_authors_list


def _merge_identifiers(olib_identifiers: dict,
                       gbook_identifiers: dict) -> dict:
    final_result_identifiers = {}
    # We know that LCCN and OCLC data is not available in the Google Books
    # database, so we get this part done first.
    final_result_identifiers['oclc'] = olib_identifiers['oclc']
    final_result_identifiers['lccn'] = olib_identifiers['lccn']
    identifiers_match = True
    mismatched_id_types = []
    for id_type in ['isbn_10', 'isbn_13', 'issn']:
        if olib_identifiers[id_type] == "N/A":
            final_result_identifiers[id_type] = gbook_identifiers[id_type]
        elif gbook_identifiers[id_type] == "N/A":
            final_result_identifiers[id_type] = olib_identifiers[id_type]
        elif olib_identifiers[id_type] == gbook_identifiers[id_type]:
            final_result_identifiers[id_type] = olib_identifiers[id_type]
        else:
            identifiers_match = False
            mismatched_id_types.append(id_type)


if __name__ == "__main__":
    #olib_dict = olib("ISBN", 9780980200447)
    #print(olib_dict)
    #gbook_dict = gbook("isbn", 9780980200447)
    #print(gbook_dict)
    #lookup_dict1 = lookup_data("isbn", 9780980200447)
    #print(lookup_dict1)
    #lookup_dict2 = lookup_data("isbn", 9781569702826)
    #print(lookup_dict2)
    combined_authors_cleaned = _check_duplicate_authors(["Jhon Mediema",
                                                         "Adam Smith",
                                                         "Frank Applebaum",
                                                         "ADAM SMITH",
                                                         "Michael Chrichton",
                                                         "Adam smith"])
