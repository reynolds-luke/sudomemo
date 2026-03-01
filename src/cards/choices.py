import random

from textual.containers import Container, HorizontalGroup
from textual.widgets import Label, Markdown, RadioButton, RadioSet

from cards.base import Card


class CardChoices(Card):
    DEFAULT_CSS = """
    CardChoices #answer_cont {
        width: 1fr;
        align-horizontal: center;
    }

    CardChoices HorizontalGroup {
        width: auto;
    }

    CardChoices .incorrect {
        color: $error;
        background: $error 20%;
    }

    CardChoices .correct {
        color: $success;
        background: $success 20%;
    }
    """

    BINDINGS = [("j", "next_button", "Next option"),
            ("k", "previous_button", "Previous option")]

    def __init__(self, card_front, options, card_back=None):
        super().__init__()
        self.card_front = card_front
        self.correct = options[0] # assume correct answer always provided as correct answer.
        self.options = options
        random.shuffle(self.options)

        self.card_back = card_back
        if self.card_back:
            if len(self.card_back) == 0:
                self.card_back = None

    def mount_front(self, c):
        c.mount(Markdown(self.card_front))

        radioset = RadioSet(id="card_radio")
        c.mount(radioset)

        for n, option in enumerate(self.options):
            radioset.mount(RadioButton(option, id=f"radio_opt_{n}"))

        radioset.focus()

    def mount_back(self, c):
        pressed_id = self.query_one("#card_radio").pressed_index
        if pressed_id >= 0:
            selected_answer = self.options[pressed_id]
        else:
            selected_answer = "None"

        answer_cont = Container(id="answer_cont")
        c.mount(answer_cont)

        if selected_answer == self.correct:
            answer_cont.mount(Label(f"✓  {self.correct}  ✓"))
        else:
            answer_cont.mount(HorizontalGroup(  Label("You chose: "),
                                Label(selected_answer, classes="incorrect")
                              ))
            answer_cont.mount(HorizontalGroup(  Label("Correct  : "),
                                    Label(self.correct, classes="correct")
                            ))

        if self.card_back:
            c.mount(Markdown(self.card_back))

        self.query_one("#card_radio").disabled = True

    def action_next_button(self) -> None:
        radioset = self.query_one("#card_radio")
        radioset.action_next_button()

    def action_previous_button(self) -> None:
        radioset = self.query_one("#card_radio")
        radioset.action_previous_button()

    def action_choose(self, index: int) -> None:
        radioset = self.query_one("#card_radio")
        buttons = radioset.query(RadioButton)

        if 0 <= index < len(buttons):
            buttons[index].value = True

    def on_radio_set_changed(self, event: RadioButton.Changed) -> None:
        self.force_flip()
