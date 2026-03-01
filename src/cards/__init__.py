from cards.base import Card, CardBackSep
from cards.basic import CardBasic
from cards.choices import CardChoices
from cards.input import CardBasicInput, Redline


def create_card(data: dict) -> Card:
    card_type = data["type"]
    if card_type == "basic":
        return CardBasic(data["front"], data["back"])
    elif card_type == "input":
        return CardBasicInput(data["front"], data["answer"], data.get("back"))
    elif card_type == "choices":
        return CardChoices(data["front"], data["options"], data.get("back"))
    else:
        raise ValueError(f"Unknown card type: {card_type!r}")
