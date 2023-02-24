import enum
import unicodedata


def remove_accents(input_text: str) -> str:
    '''Remove accents from unicode string'''
    nkfd_form = unicodedata.normalize('NFKD', input_text)
    return ''.join(char for char in nkfd_form if not unicodedata.combining(char))

class Closeness(enum.Enum):
    EXACT = 0
    COMBINING_DISMATCH = 1 # differ by combining marks
    CLOSE = 1 # differ by less then 2 steps by Levenstein distance, closeness can be configured
    NOT_MATCHING = 2

def compare_normalized(left_raw: str, right_raw: str) -> Closeness:
    left_stripped = left_raw.strip()
    right_stripped = right_raw.strip()

    if left_stripped == right_stripped:
        return Closeness.EXACT()

    left_ = remove_accents(left_stripped)
    right_ = remove_accents(right_stripped)

    if left_ == right_:
        return Closeness.COMBINING_DISMATCH()

    distance = iterative_levenshtein(left_, right_)
    if distance > 2:
        return Closeness.NOT_MATCHING
    else:
        return Closeness.CLOSE


# Implementation from: https://python-course.eu/applications-python/levenshtein-distance.php
def iterative_levenshtein(s, t):
    """ 
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings 
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein 
        distance between the first i characters of s and the 
        first j characters of t
    """

    rows = len(s)+1
    cols = len(t)+1
    dist = [[0 for x in range(cols)] for x in range(rows)]

    # source prefixes can be transformed into empty strings 
    # by deletions:
    for i in range(1, rows):
        dist[i][0] = i

    # target prefixes can be created from an empty source string
    # by inserting the characters
    for i in range(1, cols):
        dist[0][i] = i
        
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row-1][col] + 1,      # deletion
                                 dist[row][col-1] + 1,      # insertion
                                 dist[row-1][col-1] + cost) # substitution

    for r in range(rows):
        print(dist[r])
    
 
    return dist[row][col]
