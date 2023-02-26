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
