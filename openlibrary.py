# CK2 Culture Namelist Generator
# Copyright (C) 2016 Gundam Astraea Type F2
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General  Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Requests is needed to get the data from libraries
# json is needed to convert the requested data into useable dicts

import requests, json
# access the openlibs database and grab the information from there
def get_openlibs_data(isbn: str)->dict:
    return requester.(isbn) #TODO
   

'''
Runs 
'''    
def if __name__=="__main__": #TODO
    
    parser = \
        argparse.ArgumentParser(description = "Given an idenitifier, returns "
                                "information about a book as contained in the "
                                "Open Library database")
    
    parser.addargument("ISBN", type = str, help = "The ISBN-13 " 
                       "identifier of a book.")
    # parser.addargument("-i", "--isbn10", type = str, help = "The ISBN-10 " 
                       "identifier of a book.")
    # parser.addargument("--isbn9", type = str, help = "The ISBN-9 " 
                       "identifier of a book.")
    # parser.addargument("-l", "--lccn", type = str, help = "The LCCN " 
                       "identifier of a book.") TBD
   
