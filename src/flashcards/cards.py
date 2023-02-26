"""
Basic dataclasses for the project
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass
class Card:
    """Class represant single card"""

    card_id: int
    question: str
    answer: str
    level: int
    category: List[str]

    @classmethod
    def from_dict(cls, dct):
        """Constructor from dictionary"""
        return Card(
            card_id=dct["id"],
            question=dct["question"],
            answer=dct["answer"],
            level=int(dct["level"]),
            category=dct["category"],
        )

    @classmethod
    def from_row(cls, row):
        """Constructor from table row"""
        return cls(
            card_id=row["card_id"],
            question=row["question"],
            answer=row["answer"],
            level=row["card_level"],
            category=row["card_category"].split(";"),
        )


@dataclass
class Deck:
    """Class represent single deck of cards"""

    deck_id: int
    deck_name: str
    author: str
    cards: List["Card"]

    def __str__(self):
        return (
            f"Deck(id={self.deck_id}, name={self.deck_name!r}, "
            f"author={self.author!r}, cards=[...{len(self.cards)}])"
        )

    @classmethod
    def from_dict(cls, dct):
        """Constructor from dictionary"""
        return Deck(
            deck_id=dct.get("id", 0),
            deck_name=dct["name"],
            author=dct["author"],
            cards=[Card.from_dict(d) for d in dct["cards"]],
        )

    @classmethod
    def from_row(cls, row, cards):
        """Constructor from list"""
        return cls(
            deck_id=row["deck_id"],
            deck_name=row["deck_name"],
            author=row["author"],
            cards=[Card.from_row(r) for r in cards],
        )


@dataclass
class Guess:
    """Type respresent single guess"""

    card: "Card"
    tries: List[str]
    status: str


class GuessStatus(Enum):
    """Enum for guess status"""

    FAILED = 0
    CORRECT = 1
