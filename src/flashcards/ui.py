#!/usr/bin/env python3
"""
GUI entry point
"""
import copy
import enum
import logging
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
DEFAULT_SAVE_FILE_NAME="test.db"

class NotLoadedError(Exception):
    '''Deck not loaded yet'''

class DeckNotSelected(Exception):
    '''No deck selected'''

class UiCardState(enum.Enum):
    "Represent state of card label"
    QUESTION = 1
    CORRECT_ANSWER   = 2
    FAILED_ANSWER = 3

class App(tk.Frame):
    "Main window"
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.data_store = Db(DEFAULT_SAVE_FILE_NAME)
        self.data_store.setup_database()
        self._cards = []
        self._current_deck = None
        self._guesses: List['Guess'] = []
        self._card_lbl_state = UiCardState.QUESTION    
        self._setup_menu(master)
        self._setup_widgets()

    @property
    def current_guess(self) -> 'Guess':
        '''Return current guess. Raise error if deck is not loaded yet'''
        if self._current_deck is None:
            raise NotLoadedError("Deck is not loaded yet")
        return self._guesses[-1]

    @property
    def current_card(self):
        '''Returns current active card'''
        return self._guesses[-1].card
    
    def _setup_menu(self, master_wnd):
        self._menubar = tk.Menu(master_wnd)
        file_menu = tk.Menu(self._menubar, tearoff=0)
        file_menu.add_command(label="Load Saved Decks", command=self._load_saved_decks_cmd)
        file_menu.add_command(label="Select Deck", command=self.select_deck)
        file_menu.add_command(
            label="Import New Deck", command=self._import_new_deck_cmd
        )
        file_menu.add_command(label="Edit Deck", command=self._edit_deck_cmd)
        self._menubar.add_cascade(label="File", menu=file_menu)
        master_wnd.config(menu=self._menubar)

    def _setup_widgets(self):
        self._card_text = tk.StringVar()
        self._card_text.set("")
        self._card_lbl = tk.Label(self, textvariable=self._card_text, font=("Arial 24"), bg="cyan")
        self._card_lbl.grid(row=0, column=0, columnspan=2, ipadx=2, ipady=2, sticky="nsew")
        self._card_lbl.bind("<Button-1>", lambda _ev: self._on_click_label)
        self._entry_var = tk.StringVar(self)
        self._entry_box = ttk.Entry(
            self, font=("Arial 24"), textvariable=self._entry_var
        )
        self._entry_box.grid(row=1, column=0, sticky="nsew")
        self._btn = tk.Button(self, text="Check", width=12, command=self._check_answer)
        self._btn.grid(row=1, column=1, sticky="nsew")
        self._message_text_var = tk.StringVar()
        self._message_lbl = tk.Label(self, textvariable=self._message_text_var, font=("Arial 24"))
        self._btn.configure(text="Next card", command=self._next_card)
        self._message_lbl.bind("<Button-1>", self._next_card)

    def _on_click_label(self):
        if self._card_lbl_state == UiCardState.CORRECT_ANSWER:
            self.play_top_card()
        elif self._card_lbl_state == UiCardState.FAILED_ANSWER:
            self._card_lbl_state = UiCardState.QUESTION
            self._card_lbl.configure(bg='cyan')
            self._entry_var.set("")
        
    
    def _next_card(self, _ev):
        self._message_lbl.grid_forget()
        self._card_lbl.grid(row=0, column=0, columnspan=2, ipadx=2, ipady=2, sticky="nsew")
        self._btn.configure(command=self._check_answer, text="Check")
        self.play_top_card()

    def load_deck(self, deck: 'Deck'):
        """Setup new flashcard deck and pick a set of cards"""
        print("Loading new deck")
        self._current_deck = deck
        self._cards = copy.deepcopy(deck.cards)
        random.shuffle(self._cards)
        self._cards = self._cards[:MAX_CARDS]

    def select_deck(self):
        '''Select and setup new deck'''
        all_decks = self.data_store.get_all_decks()
        if not all_decks:
            self._import_new_deck_cmd()
            return
        if len(all_decks) == 1:
            self.load_deck(all_decks[0])
        else:
            try:
                selected_deck = deck_list_dialog(all_decks)
                self.load_deck(selected_deck)
            except DeckNotSelected:
                showerror("Deck Selection", "No deck selected")
        self.play_top_card()
        
    def play_top_card(self):
        '''Set new card ui'''
        card = self._cards.pop()
        print("Top card is: ", card)
        self._guesses.append(Guess(card=card, tries=[], status=None))
        self._card_lbl.configure(bg='cyan')
        self._card_text.set(self.current_card.question)
        self._entry_var.set("")

    def _load_saved_decks_cmd(self):
        '''Menu command resposible for loading saved decks'''
        db_file = askopenfilename(
            initialdir="/", 
            title="Pick db file",
            filetypes=(("DB file", "*.db*",),)
        )
        self.data_store = Db(db_path=db_file)
        self.select_deck()
        if not self._cards:
            showerror(f"Deck {self._current_deck.deck_name!r} doesn't have any cards")
            return    
        self.play_top_card()
    
    def _import_new_deck_cmd(self):
        json_file_path = askopenfilename(
            initialdir='/',
            title='Pick json file with flashcards',
            filetypes=(("JSON file", "*.json*"),)
        )
        self.data_store.load_flash_cards(json_file_path)
        self.select_deck()
        if not self._cards:
            showerror(f"Deck {self._current_deck.deck_name!r} doesn't have any cards")
            return
        self.play_top_card()

    def show_final_screen(self):
        t = tk.Toplevel()
        correct = len(card for card in self._guesses if card.status == GuessStatus.CORRECT)
        lbl_text = f"You correctly answered to {len(correct)} cards out of {len(self._guesses)}"
        lbl_widget = tk.Label(t, text=lbl_text)
        lbl_widget.bind("<Button-1>", self._new_game)
    
    def _new_game(self):
        # save progress
        # remove all guesses
        # remove all cards
        # get all cards from current deck
        pass


    def correct_card_msg(self):
        pass
    def failure_card_msg(self):
        pass


    def _check_answer(self):
        given_answer = self._entry_var.get()
        if given_answer.strip() == self.current_card.answer:
            self._guesses[-1].status = GuessStatus.CORRECT
            self._guesses[-1].tries.append(given_answer)
            if len(self._guesses) >= MAX_CARDS:
                self.show_final_screen()
            else:
                self._card_lbl.grid_forget()
                self._correct_card_var.set("Correct: :\n"+self.current_card.answer+"\nPress to get next card")
                self._correct_card_lbl.grid(row=0, column=0, columnspan=2, ipadx=2, ipady=2, sticky="nsew")
                self._card_lbl_state = UiCardState.CORRECT_ANSWER
        else:
            if len(self._guesses[-1].tries) < MAX_TRIES:
                self._guesses[-1].tries.append(given_answer)
                self._card_lbl.configure(bg='red')
                self._card_lbl_state = UiCardState.FAILED_ANSWER
            else:
                self._guesses[-1].tries.append(given_answer)
                self._card_lbl.grid_forget()
                self._failure_card_var.set("Correct answer was:\n"+self.current_card.answer)
                self._failure_card_lbl.grid(row=0, column=0, columnspan=2, ipadx=2, ipady=2, sticky="nsew")
                

    def _edit_deck_cmd(self):
        window = DeckEditor(self._current_deck)
        window.grab_set()




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
    root = tk.Tk()
    root.geometry("480x300")
    app = App(root)
    app.mainloop()
