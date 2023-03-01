"""
Custom TK dialogs
"""

from typing import List
import tkinter as tk

from flashcards.cards import Card, Deck


class DeckListDialog(tk.Toplevel):
    """Deck selection dialogue"""

    def __init__(self, master, decks, on_change):
        super().__init__(master)
        self.geometry("300x160")
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self._label = tk.Label(self, text="Select deck: ")
        self._label.grid(row=0, column=0, sticky="nsew")
        self._decks: List["Deck"] = decks
        self._deck_options = (d.deck_name for d in decks)
        self._option_var = tk.StringVar(self)
        self._options = tk.OptionMenu(
            self,
            variable=self._option_var,
            value=self._deck_options[0],
            *self._deck_options,
            command=self.on_selection_changed_cmd
        )
        self._options.grid(row=0, column=1, sticky="nsew")
        self._confirm_btn = tk.Button(
            self, text="Confirm", command=self.on_confirm_command
        )
        self._options.grid(row=1, column=1, sticky="e")
        self._selected_deck = None
        self._on_deck_changed_cb = on_change

    def on_selection_changed_cmd(self):
        """selection handler for option menu"""
        self._selected_deck = None
        for deck in self._decks:
            if deck.deck_name == self._option_var.get():
                self._selected_deck = deck
                break

    def on_confirm_command(self):
        "Confirmation button handler"
        if self._selected_deck is not None:
            self._on_deck_changed_cb(self._selected_deck)
            self.destroy()
            self.update()


def deck_list_dialog(decks: List["Deck"]) -> "Deck":
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


def card_edit_dialog(card: "Card" = None):
    """Dialogue for card editing"""
    win = tk.Toplevel()
    win.title("Card Edit")
    win.wait_window()
    return card
