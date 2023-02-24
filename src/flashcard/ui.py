#!/usr/bin/env python3
"""
GUI entry point
"""
import copy
import logging
import random
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import ttk

from flashcard.cards import Deck, Card
from flashcard.database import Db

MAX_TRIES = 5
MAX_CARDS = 5
DEFAULT_SAVE_FILE_NAME="test.db"

class App(tk.Frame):
    "Main window"

    def __init__(self, master):
        super().__init__(master)
        self._setup_menu(master)
        self.pack(fill="both", expand=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.data_store = Db(DEFAULT_SAVE_FILE_NAME)
        self._current_deck = None
        self._cards = []
        self._current_card = None
        self._guesses = []
        self._tries = 0

        self._setup_widgets()

    def _setup_widgets(self):
        self._card_text = tk.StringVar()
        self._card_text.set("Apple")
        self._label = tk.Label(self, text="Apple", font=("Arial 24"), bg="cyan")
        self._label.grid(row=0, column=0, columnspan=2, ipadx=2, ipady=2, sticky="nsew")
        self._entry_var = tk.StringVar(self)
        self._entry_box = ttk.Entry(
            self, font=("Arial 24"), textvariable=self._entry_var
        )
        self._entry_box.grid(row=1, column=0, sticky="nsew")
        self._btn = tk.Button(self, text="Check", width=12)
        self._btn.grid(row=1, column=1, sticky="nsew")

    def _load_saved_cmd(self):
        db_file = askopenfilename(initialdir="/", title="Pick db file", filetypes=(("DB file", "*.db*", ),))
        self.data_store = Db(db_path=db_file)
        self._select_deck_cmd()

    def _pick_new_card(self) -> "Card":
        if self._cards is None:
            self._cards = copy.deepcopy(self._current_deck.cards)
            random.shuffle(self._cards)
        if len(self._guesses) < MAX_CARDS:
            if self._cards:
                return self._cards.pop()
        else:
            return None

    def _select_deck_cmd(self):
        decks = self.data_store.get_all_decks()
        if len(decks) == 1:
            self._current_deck = decks[0]
            return
        self._current_deck = deck_list_dialog(decks)

    def _import_new_deck_cmd(self):
        # filedialog -> get json file
        # check if Db is open
        # push deck into db
        pass

    def _check_answer(self):
        if self._current_card is None:
            if self._current_deck is None:
                self._select_deck_cmd()
            self._current_card = self._pick_new_card()

        if self._current_deck is None or self._current_card is None:
            logging.debug("Deck and card are both None")
            return False

        if self._entry_var.get().strip().lower() == self._current_card.answer:
            self._show_answer()
            self._tries = 0
        else:
            self._tries += 1
            self._wrong_answer()

    def _wrong_answer(self):
        # blink flash card
        # if self._tries >= MAX_TRIES:
        #    switch_card; push card into failed group
        pass

    def _show_answer(self):
        # clear entryvar
        # set label var to answer
        # push guess into guesses as correct
        pass

    def _change_card(self):
        # change card when correct or tries used up
        pass

    def _edit_deck_cmd(self):
        window = DeckEditor(self._current_deck)
        window.grab_set()

    def _setup_menu(self, master_wnd):
        self._menubar = tk.Menu(master_wnd)
        file_menu = tk.Menu(self._menubar, tearoff=0)
        file_menu.add_command(label="Load Deck", command=self._load_saved_cmd)
        file_menu.add_command(label="Select Deck", command=self._select_deck_cmd)
        file_menu.add_command(
            label="Import New Deck", command=self._import_new_deck_cmd
        )
        file_menu.add_command(label="Edit Deck", command=self._edit_deck_cmd)
        self._menubar.add_cascade(label="File", menu=file_menu)
        master_wnd.config(menu=self._menubar)


def deck_list_dialog(decks):
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



class DeckEditor(tk.Toplevel):
    """Deck editor class"""

    def __init__(self, master, deck: "Deck" = None):
        super().__init__(master)
        self._deck = deck
        self._deck_name = deck or "Unknown Deck"
        self.geometry("600x480")
        self.title(f"Deck Editor -- {self._deck_name}")
        self.__columns = ("Lp.", "Question", "Answer", "Level", "Category")
        self._tree = ttk.Treeview(
            self, columns=self.__columns, show="headings", height=5
        )
        self._setup_widgets()

    def _setup_widgets(self):
        # treeview with
        # | index | cb | question | answer | level | category |
        # Add 4 buttons
        # Add Card, Remove card, Update Card
        for index, name in enumerate(self.__columns, 1):
            self._tree.column(f"# {index}", anchor=tk.CENTER)
            self._tree.heading(f"# {index}", text=name)
        self._add_card_btn = tk.Button(self)
        self._rem_card_btn = tk.Button(self)
        self._update_card_btn = tk.Button(self)
    

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("480x300")
    app = App(root)
    app.mainloop()
