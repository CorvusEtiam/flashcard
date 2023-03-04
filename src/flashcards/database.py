"""
Database handler
"""

import json
import logging
import os
import sqlite3
from typing import List

from flashcards.cards import Deck, Guess


class Db:
    """Db handler class"""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def rebuild_database(self):
        """Reset database for access"""
        self.conn.close()
        os.remove(self._db_path)
        self.conn = sqlite3.connect(self._db_path)
        self.setup_database()

        logging.info("Rebuilding database at path=%s", self._db_path)

    def setup_database(self):
        "Setup db from scratch"
        cursor = self.conn.cursor()
        # check if tables exist
        cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS decks 
        (
            deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_name TEXT NOT NULL,
            author TEXT NOT NULL
        );
        """
        )
        logging.info("Table decks created")
        cursor.executescript(
        """
        CREATE TABLE IF not EXISTS cards(
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            card_level INTEGER NOT NULL,
            card_category TEXT NOT NULL,

            FOREIGN KEY (deck_id) 
                REFERENCES decks (deck_id)
        );
        """
        )
        logging.info("Table cards created")
        cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS progress(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            guess_list TEXT NOT NULL,
            status INTEGER NOT NULL,
            guess_ts TEXT NOT NULL,
            
            FOREIGN KEY (card_id) 
                REFERENCES cards (card_id)
            );
        """
        )
        self.conn.commit()

    def put_deck_into_database(self, deck: "Deck"):
        """Load deck into database"""

        cursor = self.conn.cursor()
        result = cursor.execute(
            "SELECT deck_id FROM decks WHERE deck_name=? AND author=?",
            (
                deck.deck_name,
                deck.author,
            ),
        )
        if result.fetchone() is not None:
            return

        cursor.execute(
            "INSERT INTO decks(deck_name, author) VALUES(?, ?)",
            (deck.deck_name, deck.author),
        )
        self.conn.commit()
        result = cursor.execute(
            "SELECT deck_id FROM decks WHERE deck_name=?", (deck.deck_name,)
        )
        deck_id = result.fetchone()["deck_id"]
        cards = [
            (
                deck_id,
                card.question,
                card.answer,
                card.level,
                ";".join(card.category),
            )
            for card in deck.cards
        ]
        print(cards)
        cursor.executemany(
            """
            INSERT INTO cards(deck_id, question, answer, card_level, card_category) 
            VALUES (?, ?, ?, ?, ?)
            """,
            cards,
        )
        self.conn.commit()

    def get_deck_from_database(self, deck_id):
        """Get single deck from db"""
        cursor = self.conn.cursor()
        deck_ = cursor.execute("SELECT * FROM decks WHERE deck_id=?", (deck_id,))
        deck_result = deck_.fetchone()
        cards_ = cursor.execute("SELECT * FROM cards WHERE deck_id=?", (deck_id,))
        cards_result = cards_.fetchall()
        return Deck.from_row(deck_result, cards=cards_result)

    def get_all_decks(self):
        """Get all decks from database"""
        cursor = self.conn.cursor()
        deck_result_ = cursor.execute("SELECT * FROM decks ORDER BY deck_id ASC")
        deck_result = deck_result_.fetchall()
        result = []
        for deck in deck_result:
            result.append(self.get_deck_from_database(deck["deck_id"]))
        return result

    def put_guesses_into_database(self, guesses: List[Guess]):
        """Save game progress"""
        guesses_rows = [ (g.card.card_id, ";".join(g.tries), g.status.value) for g in guesses ]
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT INTO progress(card_id, guess_list, status)
            VALUES (?, ?, ?)
            """, guesses_rows
        )
        cursor.commit()

    def get_guesses_from_database(self):
        pass