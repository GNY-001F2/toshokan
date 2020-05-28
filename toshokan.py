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

def main(args) -> None:
    pass

if __name__="__main__":
    import argparse
    parser = \
        argparse.ArgumentParser(description = "Given an identifier, returns "
                                "information about a book as contained in the "
                                "Open Library database.")
    parser.add_argument("book_id", type = str, help = "The identifier of a "
                        "book. Default assumption is that the ID is an ISBN.",
                        metavar = "ID")
    # TODO. Let's first get ISBN lookups working.
    #group = parser.add_mutually_exclusive_group()
    parser.add_argument("-i", "--isbn", action="store_const", const=1,
                       default=1, #type=str,
                       help="The ID is processed as an ISBN. Enabled default.")
    # group.add_argument("-l", "--lccn", action="store_const", const = 1,
    #                    default = 0, type = str,
    #                    help = "The ID is processed as an LCCN.")
    # group.add_argument("-o", "--oclc", action="store_const", const = 1,
    #                    default = 0, type = str,
    #                    help = "The ID is processed as an OCLC identifier.")
    # group.add_argument("--olid", action="store_const", const = 1,
    #                    default = 0, type = str, 
    #                    help = "The ID is processed as Open Library's "
    #                    "internal identifier the book.")
    # NOTE: ISBN is temporary, will be replaced by code from the parser later
    idtype = "ISBN"
    # NOTE: 'parser' will be changed to group when I enable the flags for the
    #       ArgumentParser
    args = parser.parse_args()
    main(args)
