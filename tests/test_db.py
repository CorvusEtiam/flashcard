#!/usr/bin/env python3
"""
Basic test of the flashcard db loader
"""

import os

from flashcard.database import Db

DB_PATH = "test.db"


def main():
    """Main test function"""

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db_handle = Db(DB_PATH)
    db_handle.setup_database()
    print(f"Setup database finished db_file_path={DB_PATH!s}")
    db_handle.load_flash_cards("./tests/flashcard_example.json")
    for deck in db_handle.get_all_decks():
        print(deck)


if __name__ == "__main__":
    main()
