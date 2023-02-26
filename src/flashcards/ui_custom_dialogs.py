"""
Custom TK dialogs
"""

from typing import List
import tkinter as tk

from flashcards.cards import Card, Deck

def deck_list_dialog(decks: List['Deck']) -> 'Deck':
    """Dialogue returning one of the decks"""
    win = tk.Toplevel()
    win.title("Deck List")

    decks_names = [deck.deck_name for deck in decks]
    deck_list = tk.Variable(value=decks_names)
    deck_listbox = tk.Listbox(win, listvariable=deck_list, height=6)

    selected_element = None

    def store(_event):
        nonlocal selected_element
        selected_index = deck_listbox.curselection()
        deck_name = deck_listbox.get(selected_index)
        selected_element = decks[deck_name]

    deck_listbox.bind("<Double-1>", store)
    deck_listbox.pack(fill="both")
    win.wait_window()
    return selected_element

def card_edit_dialog(card: 'Card'=None):
    """Dialogue for card editing"""
    win = tk.Toplevel()
    win.title("Card Edit")
    win.wait_window()
    return card

def config_dialog():
    pass

