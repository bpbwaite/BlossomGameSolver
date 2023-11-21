# Merriam Webster Blossom Game Solver
# Briellyn B - 20 Nov 2023

import time
from urllib.request import urlretrieve

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        ts = time.time()
        ret = func(*args, **kwargs)
        tf = time.time()
        print(f'-- Returned in {1000*(tf-ts):.1f} ms')
        return ret
    return wrapper

def isPanagram(word: str, allLetters: str):
    return sorted(list(set(word))) == sorted(list(set(allLetters)))

def pointValue(word: str, allLetters: str, bonus: str):
    value = 0
    if len(word) == 4:
        value += 2
    if len(word) == 5:
        value += 4
    if len(word) == 6:
        value += 6
    if len(word) >= 7:
        value += 12
        value += 3 * (len(word) - 7)
    value += 5 * word.count(bonus) # yellow letter
    if isPanagram(word, allLetters):
        value += 7
    return value

def peakBonusLetter(word: str, centerLetter: str):
    # return letters with most occurences
    most = ('.', 0) # may break on strings that are all one letter
    for char in word:
        if char != centerLetter:
            num = word.count(char)
            if num > most[1]:
                most = (char, num)
            elif num == most[1]:
                most = (most[0] + char, num) # multiple candidates
    return ''.join(sorted(list(set(most[0]))))

@timing_decorator
def getSolutions(dictionary: str, petals: str, center: str, bonus: str, display: int = 20):

    petals = (petals + center[0] + bonus[0]).replace(' ', '').lower()

    valid_solutions = []
    with open(dictionary, mode='rt', encoding='utf-8') as dictFile:
        for line in dictFile:

            word = line.strip().lower()

            if center not in word:
                continue
            if (len(word) not in range(4, 34)): # range accepted by the game
                continue

            flag = True
            for char in word: # faster to iterate all than cast to set
                if char not in petals:
                    flag = False
                    break

            if flag and word not in valid_solutions:
                valid_solutions.append(word)

    valid_solutions.sort(key=lambda X: pointValue(X, petals, bonus), reverse=True)

    if display >= len(valid_solutions):
        display = len(valid_solutions)
    if display == 0:
        print('No Solutions')
        exit()

    print(f'-- Showing {display}/{len(valid_solutions)} solutions:')
    for word in valid_solutions[0:display]:
        print(f'{word} ({pointValue(word, petals, bonus)} pts) ', end='')
        best_turns = peakBonusLetter(word, center)
        if bonus not in best_turns:
            print(f'({best_turns.upper()}:{pointValue(word, petals, best_turns[0])}) ', end='')
        if isPanagram(word, petals):
            print('(Panagram)', end = '')
        print('')
    return

def main():
    dictionary = 'words_alpha.txt'
    try:
        open(dictionary, mode='r')
    except FileNotFoundError:
        uri = 'https://github.com/dwyl/english-words/raw/master/words_alpha.txt'
        print('No dictionary found. Downloading...')
        urlretrieve(uri, dictionary)

    print('Dictionary downloaded!')

    disp = int(input('Display Limit? '))
    petal_letters = input('Outer letters? ')[0]
    center_letter = input('Center letter? ')[0]
    while True:
        bonus_letter = input('Bonus letter? ')
        print('Searching...')

        getSolutions(dictionary, petal_letters, center_letter, bonus_letter, display=disp)

if __name__ == '__main__':
    main()
