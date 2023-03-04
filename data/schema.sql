CREATE TABLE IF NOT EXISTS decks 
            (
                deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_name TEXT NOT NULL,
                author TEXT NOT NULL
            );

CREATE TABLE IF not EXISTS cards(
            card_id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            card_level INTEGER NOT NULL,
            card_category TEXT NOT NULL,

            FOREIGN KEY (deck_id) 
                REFERENCES decks (deck_id)
);

CREATE TABLE IF NOT EXISTS progress(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    guess_list TEXT NOT NULL,
    status INTEGER NOT NULL,
    guess_ts TEXT NOT NULL,

    FOREIGN KEY (card_id) 
        REFERENCES cards (card_id)
);
            

