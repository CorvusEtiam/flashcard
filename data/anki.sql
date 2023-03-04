SELECT decks FROM col;
SELECT nid AS note_id FROM cards WHERE did=?deck_id?;

SELECT notes.id AS note_id, did AS deck_id, flds AS fields, tags 
FROM cards JOIN notes ON cards.nid=notes.id
WHERE did=? ORDER BY note_id ASC;



SELECT id, tags, flds FROM notes 
JOIN

WHERE
    did=:deck_id:
