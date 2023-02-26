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



Failure