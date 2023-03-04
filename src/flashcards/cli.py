#!/usr/bin/env python3
"""
CLI entry point for flashcard app

USAGE:
  flashcard.py deck.json --cards 5 --tries 3
  flashcard.py deck.json -c 5 -t 3
  flashcard.py help
"""

from argparse import ArgumentParser
import logging
import os
import sys

from flashcards.fileloaders import load_from_json_file, DeckLoadingError
from flashcards.flashcard import display_deck_info, play
from flashcards.database import Db


def main(arguments):
    """Main flashcard function"""
    database_handle = Db("result.db")
    database_handle.setup_database()

    if args.deck.endswith(".json"):
        if os.path.exists(args.deck):
            try:
                load_from_json_file(args.deck, database_handle)
            except DeckLoadingError as err:
                print(f"[ERR] {err!s}")
                sys.exit(1) 

        deck = database_handle.get_deck_from_database(args.deck)
    display_deck_info(deck)

    play(database_handle, deck, arguments.cards)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename="flashcard.log",
        filemode="w",
        format="[%(levelname)s] %(name)s -- %(message)s",
    )
    parser = ArgumentParser(description="Flashcard learning game")
    parser.add_argument(
        "deck", help="Path to deck of flashcards in json format or deck name"
    )
    parser.add_argument(
        "-c",
        "--cards",
        help="Max number of flashcards",
        type=int,
        default=3,
        required=False,
    )
    parser.add_argument(
        "-t",
        "--tries",
        help="Max number of retries",
        type=int,
        default=3,
        required=False,
    )
    args = parser.parse_args()
    main(args)
