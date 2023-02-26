#!/usr/bin/env python3
"""
GUI entry point
"""
import copy
import enum
import logging
import os
import random

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror

from typing import List

from flashcards.cards import Deck, Card, Guess, GuessStatus
from flashcards.database import Db
from flashcards.ui_custom_dialogs import deck_list_dialog

MAX_TRIES = 5
MAX_CARDS = 5
DEFAULT_SAVE_FILE_NAME = "test.db"


class NotLoadedError(Exception):
    """Deck not loaded yet"""


class DeckNotSelected(Exception):
    """No deck selected"""


class UiCardState(enum.Enum):
    "Represent state of card label"
    QUESTION = 1
    CORRECT_ANSWER = 2
    FAILED_ANSWER = 3


class StatusBar(tk.Frame):
    """Statusbar widget"""

    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="x", side="bottom")
        self._deck_name_text = tk.StringVar()
        self._deck_name_lbl = tk.Label(self, textvariable=self._deck_name_text)
        self._deck_name_lbl.pack(side="left")

        self._card_info_text = tk.StringVar()
        self._card_info_lbl = tk.Label(self, textvariable=self._card_info_text)
        self._card_info_lbl.pack(side="bottom")

        self._try_number_text = tk.StringVar()
        self._try_number_lbl = tk.Label(self, textvariable=self._try_number_text)
        self._try_number_lbl.pack(side="right")

    def update_deck_info(self, deck: "Deck"):
        """Update statusbar deck info"""
        self._deck_name_text.set(deck.deck_name)

    def update_card_info(self, current_card_index: int = 1, max_cards: int = MAX_CARDS):
        """Update statusbar card info"""
        self._card_info_text.set(f"{current_card_index} out of {max_cards}")

    def update_try_info(self, current_try: int = 1, max_tries: int = MAX_TRIES):
        """Update statusbar try count"""
        self._try_number_text.set(f"{current_try}/{max_tries}")

class GuessView(tk.Frame):
    """Main guessing mode view"""

    def __init__(self, master, on_answer):
        super().__init__(master)
        self.on_answer_cb = on_answer
        self.pack(side='top', fill='both', expand=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)
        self.card_label_txt = tk.StringVar()
        self.card_label = tk.Label(self,
            textvariable=self.card_label_txt,
            font=("Arial 30"),
            justify="center"
        )
        self.card_label.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.entry_box_val = tk.StringVar()
        self.entry_box = tk.Entry(self, font=("Arial 16"), textvariable=self.entry_box_val)
        self.entry_box.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.check_btn = tk.Button(self,
            text="Check Answer",
            command=lambda: self.check_answer() , width=6, height=6)
        self.check_btn.grid(row=1, column=2, sticky="nsew")
    @property
    def current_card(self) -> 'Card':
        '''Return card from parent main widget'''
        return self.master.current_card

    def check_answer(self):
        print("**** ", self.entry_box_val.get())
        self.on_answer_cb(self.entry_box_val.get())

    def update_card(self):
        self.card_label.configure(bg='cyan')
        self.card_label_txt.set(self.current_card.question)

class App(tk.Tk):
    "Main UI App entry point"
    def __init__(self):
        super().__init__()
        self.geometry("480x300")
        self.status_bar = StatusBar(self)
        self.guess_view = GuessView(self, on_answer=self.on_answer_handler)
        self.menu_bar = tk.Menu(self)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        #file_menu.add_command(label="Load", command=self._load_saved_decks_cmd)
        #file_menu.add_command(label="Select Deck", command=self.select_deck)
        #file_menu.add_command(
        #    label="Import New Deck", command=self.import_new_deck_dialog
        #)
        # file_menu.add_command(label="Edit Deck", command=self._edit_deck_cmd)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=self.menu_bar)
        # check if there is saved db in standard location if not ask user for one

        self.data_store = None
        self.deck = None
        self.current_try = 1
        self.guesses = []
        self.answers = []
        self.card_count = 0
        self.current_card = None

        if os.path.exists(DEFAULT_SAVE_FILE_NAME):
            self.data_store = Db(DEFAULT_SAVE_FILE_NAME)
        else:
            self.load_user_data_store_dialog()

        # views should only be responsible for displaying stuff and handling user-input
        # all logic should go into main app
        # select deck
        decks = self.data_store.get_all_decks()
        if not decks:
            self.import_new_deck_dialog()
            decks = self.data_store.get_all_decks()
        if len(decks) == 1:
            self.prepare_deck(decks[0])
        else:
            selected_deck = deck_list_dialog(decks)
            self.prepare_deck(selected_deck)

    def import_new_deck_dialog(self):
        """Load new deck"""
        json_file = askopenfilename(
            initialdir=".",
            title="Pick deck JSON file",
            filetypes=(
                (
                    "JSON file",
                    "*.json*",
                ),
            ),
        )
        try:
            self.data_store.load_flash_cards(json_file)
        except Exception as ex:  # pylint: disable=broad-except
            # anything wrong happen - log it
            logging.error(str(ex))
            print(f"[ERROR] {ex!r}")
            showerror("Error occured while import new deck")

    def prepare_deck(self, deck: "Deck"):
        """Prepare deck for play"""
        self.deck = deck
        cards = copy.deepcopy(self.deck.cards)
        random.shuffle(cards)
        self.cards = cards[:MAX_CARDS]
        self.current_try = 1
        self.guesses = []
        self.answers = []
        self.card_count = len(self.cards)
        self.current_card = self.cards.pop()
        print(f"Current card is: {self.current_card}")

        self.status_bar.update_deck_info(self.deck)
        self.status_bar.update_card_info(1, len(self.cards))
        self.status_bar.update_try_info(1, MAX_TRIES)
        self.guess_view.update_card()

    def load_user_data_store_dialog(self):
        """Command resposible for loading saved decks"""
        db_file = askopenfilename(
            initialdir=".",
            title="Pick data file",
            filetypes=(
                (
                    "DB file",
                    "*.db*",
                ),
            ),
        )
        try:
            self.data_store = Db(db_path=db_file)
        except Exception as ex:  # pylint: disable=broad-except
            # anything wrong happen - log it
            logging.error(str(ex))
            print(f"[ERROR] {ex!r}")
            showerror("Error occured while loading datastore")

    def pop_card(self):
        """Set state with new card"""
        self.current_card = self.cards.pop()
        self.answers = []
        self.current_try = 1
        self.guess_view.update_card()
        self.status_bar.update_card_info(len(self.guesses)+1)
    
    def on_answer_handler(self, raw_answer: str):
        """Callback for new answer"""
        self.answers.append(raw_answer)
        if self.current_card.answer == raw_answer:
            self.guesses.append(Guess(self.current_card, self.answers, GuessStatus.CORRECT))
            if not self.cards:
                # show_final_screen()
                return
            self.pop_card()
            self.status_bar.update_try_info(self.current_try)
        else:
            if self.current_try >= MAX_TRIES:
                self.guesses.append(Guess(self.current_card, self.answers, GuessStatus.FAILED))
                if not self._cards:
                    # show_final_screen()
                    return
                self.pop_card()
            else:
                self.current_try += 1
                self.status_bar.update_try_info(self.current_try)

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
    logging.basicConfig(
        level=logging.INFO,
        filename="flashcard.log",
        filemode="w",
        format="[%(levelname)s] %(name)s -- %(message)s",
    )

    root = App()
    root.mainloop()
