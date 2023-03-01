#!/usr/bin/env python3
"""
GUI entry point
"""

import enum
import logging
import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from typing import List

import flashcards.utils as utils
from flashcards.cards import Deck, Guess, GuessStatus
from flashcards.database import Db
from flashcards.ui_custom_dialogs import DeckListDialog

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

        self.max_card_count = MAX_CARDS
        self.max_tries_count = MAX_TRIES
        self.card = 1
        self.tries_count = 1

    def update_deck_name(self, deck: "Deck"):
        """Update statusbar deck info"""
        self._deck_name_text.set(deck.deck_name)
        self.card = 1
        self.tries_count = 1

    def update_play_info(self, card=None, tries=None):
        """Update status bar with current play info"""
        self.card = card or self.card
        self.tries_count = tries or self.tries_count
        self._card_info_text.set(f"{self.card} out of {self.max_card_count}")
        self._try_number_text.set(f"{self.tries_count}/{self.max_tries_count}")


class GuessView(tk.Frame):
    """Main guessing mode view"""

    def __init__(self, master):
        super().__init__(master)
        self.pack(side="top", fill="both", expand=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)
        self.card_label_txt = tk.StringVar()
        self.card_label = tk.Label(
            self, textvariable=self.card_label_txt, font=("Arial 30"), justify="center"
        )
        self.card_label.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.entry_box_val = tk.StringVar()
        self.entry_box = tk.Entry(
            self, font=("Arial 16"), textvariable=self.entry_box_val
        )
        self.entry_box.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.check_btn = tk.Button(
            self, text="Check Answer", command=self.check_answer, width=6, height=6
        )
        self.check_btn.grid(row=1, column=2, sticky="nsew")
        self.deck = None
        self.cards = []
        self.current_try = 1
        self.guesses = []
        self.current_guess = None

    def load_deck(self, deck: "Deck"):
        """Load deck into guess view"""
        self.deck = deck
        self.cards = utils.clone_cards(deck.cards, MAX_CARDS)
        if len(self.cards) == 0:
            showerror("Empty deck", "Empty deck: " + self.deck.deck_name)
            self.master.quit()
            return
        self.master.status_bar.max_card_count = len(self.cards)
        self.master.status_bar.update_play_info(1, 1)
        self.current_guess = Guess(self.cards.pop(), [], GuessStatus.FAILED)
        self.guesses = []
        self.check_btn.configure(text="Check", command=self.check_answer)
        self.card_label.configure(background="cyan")
        self.card_label_txt.set(self.current_guess.card.question)

    def check_answer(self):
        """Check answer command handler"""
        card = self.current_guess.card
        answer = self.entry_box_val.get()
        self.entry_box_val.set("")
        self.current_guess.tries.append(answer)
        if card.answer == answer:
            self.current_guess.status = GuessStatus.CORRECT
            self.guesses.append(self.current_guess)
            self.card_label_txt.set(card.answer)
            self.card_label.configure(background="green")
            if len(self.cards) == 0:
                self.check_btn.configure(
                    command=lambda: self.master.show_final_view(self.guesses), text="Show results"
                )
            else:
                self.check_btn.configure(command=self.load_next_card, text="Next card")
        else:
            if len(self.current_guess.tries) < MAX_TRIES:
                print(f"**** {self.current_guess.tries!r}")
                self.master.status_bar.update_play_info(
                    tries=len(self.current_guess.tries) + 1
                )
                self.blink_error()
                self.check_btn.configure(command=self.check_answer, text="Try again")
            else:
                self.current_guess.tries.append(answer)
                self.current_guess.status = GuessStatus.FAILED
                self.guesses.append(self.current_guess)
                self.card_label_txt.set(card.answer)
                self.card_label.configure(background="red")
                if len(self.cards) == 0:
                    self.check_btn.configure(
                        command=lambda: self.master.show_final_view(self.guesses),
                        text="Show results"
                    )
                else:
                    self.check_btn.configure(
                        command=self.load_next_card, text="Next card"
                    )

    def load_next_card(self):
        """Loading next card"""
        self.current_guess = Guess(self.cards.pop(), [], GuessStatus.FAILED)
        self.current_try = 1
        self.master.status_bar.update_play_info(card=len(self.guesses) + 1, tries=1)
        self.check_btn.configure(text="Check", command=self.check_answer)
        self.card_label.configure(background="cyan")
        self.card_label_txt.set(self.current_guess.card.question)

    def blink_error(self):
        """Blink card label red on incorrect answer"""

        def blink():
            self.card_label.configure(background="red")
            self.card_label.after(
                100, lambda: self.card_label.configure(background="cyan")
            )

        self.card_label.after(5, blink)

class FinalSummaryView(tk.Frame):
    """Tkinter widget with final summary view"""
    def __init__(self, master):
        super().__init__(master)
        self.guesses = None
        self._summary_label = tk.Label(self, text="You answered correctly to: ")
        self._summary_label.grid(row=0, column=0, sticky='w')
        self._correct_label_var = tk.StringVar(self, "")
        self._correct_label = tk.Label(self, textvariable=self._correct_label_var)
        self._correct_label.grid(row=0, column=1, sticky='e')
        self._btn = tk.Button(self,
            text="Next run",
            command=lambda: print("*** NOT IMPLEMENTED ***")
        )
        self._btn.grid(row=3, column=1, sticky="nsew")

    def update_view_state(self, guesses: List['Guess']):
        """Update state of FinalView"""
        self.guesses = guesses
        correct = len([g for g in self.guesses if g.status == GuessStatus.CORRECT])
        self._correct_label_var.set(f"{correct} / {len(self.guesses)}")


class App(tk.Tk):
    "Main UI App entry point"

    def __init__(self):
        super().__init__()
        self.geometry("480x300")
        self.status_bar = StatusBar(self)
        self.guess_view = GuessView(self)
        self.final_view = FinalSummaryView(self)
        self.menu_bar = tk.Menu(self)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        # file_menu.add_command(label="Load", command=self._load_saved_decks_cmd)
        # file_menu.add_command(label="Select Deck", command=self.select_deck)
        # file_menu.add_command(
        #    label="Import New Deck", command=self.import_new_deck_dialog
        # )
        # file_menu.add_command(label="Edit Deck", command=self._edit_deck_cmd)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=self.menu_bar)
        # check if there is saved db in standard location if not ask user for one

        self.data_store = None
        self.deck = None

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
            list_dialog = DeckListDialog(self, decks, on_change=self.prepare_deck)
            list_dialog.wait_window()

    def prepare_deck(self, deck: 'Deck'):
        """Load new deck"""
        self.deck = deck
        self.status_bar.max_card_count = min(len(self.deck.cards), MAX_CARDS)
        self.status_bar.update_deck_name(self.deck)
        self.guess_view.load_deck(self.deck)

    def show_final_view(self, guesses):
        """Toggle on final view"""
        self.toggle(self.guess_view)
        self.final_view.update_view_state(guesses)
        self.toggle(self.final_view)

    def is_view_active(self, view: "tk.Frame") -> bool:
        """Check if given view is active"""
        return view.winfo_manager() != ""

    def toggle(self, view: "tk.Frame"):
        """Show and hide view"""
        if not self.is_view_active(view):
            view.pack(side="top", fill="both")
        else:
            view.pack_forget()

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
