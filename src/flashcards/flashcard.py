#!/usr/bin/env python3

"""
Flashcard game
"""
import copy
import random
from flashcards.cards import GuessStatus, Guess
from flashcards.database import Db

def display_flash_card(card):
    """Print info about card"""
    print(f"{card['question']: ^80}")
    print("=" * 80)


def display_deck_info(deck):
    """Print info about deck"""
    print(f"Author: {deck['author']}")
    print(f"Card count: {len(deck['cards'])}")
    print("=" * 80)


def get_answer(guess: "Guess", max_retries: int = 5) -> bool:
    """Ask for answer

    Will retry as many times as ``max_tries``. By default it is 5
    """
    tries = 1
    display_flash_card(guess.card)
    while tries <= max_retries:
        answer = input("You answer: ")
        guess.tries.append(answer.strip())
        if answer.strip().lower() == guess.card["answer"].strip().lower():
            return True
        print(f"You gave: {answer}. This is not correct.", end=" ")
        print(f"You still have {tries} tries, out of {max_retries}")
        tries += 1
    print(f"The correct answer was: {guess.card['answer']}")
    return False


def play(db_handle: "Db", deck, max_cards: int = 3, max_guesses: int = 5):
    """Play single flashcard run

    cards - list of cards represented as dict with { question, answer }
    max_cards - maximum amount of cards to be selected for this run
    """
    all_cards = copy.deepcopy(deck.cards)
    random.shuffle(all_cards)
    card_lists = all_cards[:max_cards]
    guesses = []
    while card_lists:
        current = card_lists.pop()
        guess = Guess(card=current, tries=[], status=None)
        answer = get_answer(guess, max_retries=max_guesses)
        if answer:
            print("You got 1 point for this one")
            guess.status = GuessStatus.CORRECT
        else:
            print("You got 0 point for this one")
            guess.status = GuessStatus.FAILED
        guess.tries.append(answer)
        guesses.append(guess)
    print("=" * 80)

    all_card_count = len(guesses)
    correct_guesses = [g for g in guesses if g.status == GuessStatus.CORRECT]
    print(f"You correctly answered {len(correct_guesses)}/{all_card_count}.")
    db_handle.save_progress(guesses)
