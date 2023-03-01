# Flashcard flow


1. Select new deck
2. Select MAX_CARDS cards from deck
3. Set new card, state=UiCardState.QUESTION
4. When answer is correct:
    turn card green
    push guess into table with state=CORRECT
   Else:
    turn card red
    if it was last try. 



# Views and UI States

* Need way to show on which try they are
* Need way to show on which card they are
* Display current deck info


1. Guess mode
    - flash card
    - entry box
    - single button
2. Check guess 
    If guess was correct:
        Turn screen green
        Display answer
        One button with: `Next` | `Result` message
    Else:
        Make screen red

```
guess_view.set_current_card(card)

check_answer: 
If answer is correct:
    self.show_answer()
    self.set_card_color("green")
    self.master.status_bar.update_status_bar()
Else:
    If try count < max_tries:
        guess_view -> blink card red
        increase try count
        update_status_bar
    Else:
        show answer
        turn card red
        update_status_bar    
```