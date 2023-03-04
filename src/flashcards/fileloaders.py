"""Classes for loading ANKI flash cards"""

import json
import os
import sqlite3
import tempfile
import zipfile

from flashcards.database import Db
from flashcards.cards import Deck, Card


class DeckLoadingError(Exception):
    """Error on deck load"""

def load_anki2_file(file_path: str, data_store: Db):
    """Load ANKI2 file"""
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    result_decks = cursor.execute("SELECT ver, decks FROM col;")
    version, deck_json = result_decks.fetchone()
    if int(version) > 11:
        print(f"[WARN] Your deck collection is newer version ({version}) than fully supported one (11)")
    deck_list = []
    if deck_json is not None:
        deck_obj = json.loads(deck_json)
        deck_list = [ (int(k), v['name']) for k,v in deck_obj.items() ]
        print(f"Found: {len(deck_list)} decks.\n{deck_list!r}")
    decks = []
    for deck_id, deck_name in deck_list:
        deck = Deck(deck_id=deck_id, deck_name=deck_name, author="Imported from ANKI2", cards=[])
        result = cursor.execute("""
        SELECT notes.id AS note_id, did AS deck_id, flds AS fields, tags 
        FROM cards JOIN notes ON cards.nid=notes.id
        WHERE did=? ORDER BY note_id ASC;
        """, (deck_id, ))
        card_rows = result.fetchall()
        for (note_id, deck_id, fields, tags) in card_rows:
            question, answer = fields.split("\v")
            card = Card(card_id=int(note_id), question=question, answer=answer, level=-1, category=[ tags ])
            deck.cards.append(card)
        decks.append(deck)
    for deck in decks:
        data_store.put_deck_into_database(deck)

def load_apkg_file(anki_file: str, data_store: "Db"):
    """Load apkg file into database"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(anki_file, mode="r") as z_file:
            z_file.extractall(path=tmp_dir, members="collection.anki2")
            collection_file = os.path.join(tmp_dir, "collection.anki2")
            if os.path.exists(collection_file):
                load_anki2_file(collection_file, data_store)

def load_from_json_file(file_path: str, data_store: Db):
    """Load deck from json file"""
    if os.path.exists(file_path):
        deck = None
        with open(file_path, "r", encoding="utf-8") as file_handle:
            deck_dict = json.load(file_handle)
            deck = Deck.from_dict(deck_dict)
        data_store.put_deck_into_database(deck)
