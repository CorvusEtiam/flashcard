#!/usr/bin/env python3

"""
Flashcard game
"""
from argparse import ArgumentParser
import copy
import logging
import os
import random

from flashcard.cards import GuessStatus, Guess
from flashcard.database import Db


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


def main(arguments):
    """Main flashcard function"""
    database_handle = Db("result.db")
    database_handle.setup_database()

    if args.deck.endswith(".json"):
        if os.path.exists(args.deck):
            database_handle.load_flash_cards(args.deck)
    deck = database_handle.get_deck_from_database(args.deck)
    display_deck_info(deck)

    play(database_handle, deck, arguments.cards)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename="flashcard.log",
        filemode="w",
        format="[%(levelname)s] %(name)s -- %(message)s",
    )
    parser = ArgumentParser(description="Flashcard learning game")
    parser.add_argument(
        "deck", help="Path to deck of flashcards in json format or deck name"
    )
    parser.add_argument(
        "-c",
        "--cards",
        help="Max number of flashcards",
        type=int,
        default=3,
        required=False,
    )
    parser.add_argument(
        "-t",
        "--tries",
        help="Max number of retries",
        type=int,
        default=3,
        required=False,
    )
    args = parser.parse_args()
    main(args)

# USAGE:
#   flashcard.py deck.json --cards 5 --tries 3
#   flashcard.py deck.json -c 5 -t 3
#   flashcard.py help
