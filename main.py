# Merriam Webster Blossom Game Solver
# Briellyn B - 24 Nov 2023

from urllib.request import urlretrieve
import requests
import re
from datetime import date
import time

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
def getSolutions(dictionary: str, petals: str, center: str, bonus: str, display: int = 20) -> bool:

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
        return False

    print(f'-- Showing {display}/{len(valid_solutions)} solutions:')
    for word in valid_solutions[0:min(display, len(valid_solutions))]:
        print(f'{word} ({pointValue(word, petals, bonus)} pts) ', end='')
        best_turns = peakBonusLetter(word, center)
        if bonus not in best_turns:
            print(f'({best_turns.upper()}:{pointValue(word, petals, best_turns[0])}) ', end='')
        if isPanagram(word, petals):
            print('(Panagram)', end = '')
        print('')
    return True

def copyWeeklyDictToFile(fname:str):
    root = 'https://www.merriam-webster.com'
    game = '/games/blossom-word-game'
    page = requests.get(root + game).text
    link1 = re.compile(r'src="(/dist-cross.+?compiled.+?\.js)"', flags=re.I|re.M|re.X).search(page).group(1)
    distribution_root = link1.split('/js/')[0] + '/js/'
    page = requests.get(root + link1).text
    link2_version = re.compile(r'(vendors-node_modules_mw-semipublic_blossom_dist_blossom_js)[": ]{0,3}"([a-z0-9]+)"', flags=re.I|re.M|re.X).search(page)
    link2 = distribution_root + link2_version.group(1) + "." + link2_version.group(2) + ".js"
    page = requests.get(root + link2).text
    auth_code = re.compile(r'Authorization:.*"Bearer.*"\.concat\("(.*?)"\)', flags=re.I|re.M|re.X).search(page).group(1)

    headers =   {
                    "Authorization": "Bearer " + auth_code,
                    "Content-type": "application/json"
                }
    #payload = r'{"query":"\nquery {\nblossom (\nsort: [\"published_date\"]\nfilter: {\npublished_date: {\n_gte: \"' \
    #    + str(date.today()).replace('-', '/').strip() \
    #    + r'\"\n}\n}\n) {\npuzzle_id\npublished_date\ncenter\nletters\npangram \nwords\n}\n}"}'
    payload = r'{"query":"\nquery {\nblossom (\nsort: [\"published_date\"]\n'\
        + r'\n) {\npuzzle_id\npublished_date\ncenter\nletters\npangram \nwords\n}\n}"}'

    x = requests.post(url='https://prod-mw-cms.m-w.com/graphql', headers=headers, data=payload)

    with open(fname, 'wt+', encoding='utf-8') as OutFile:
        for puzzle in x.json()['data']['blossom']:
            for word in puzzle['words']:
                OutFile.write(word.strip().lower() + '\n')


def main():

    #disp = int(input('Display Limit? '))
    disp = 24
    petal_letters = (input('Outer letters? '))
    center_letter = (input('Center letter? '))[0]

    while True:
        bonus_letter = input('Bonus letter? ')[0]
        print('Searching...')
        dictionary = 'weekly.txt'
        try:
            open(dictionary, mode='r')
        except FileNotFoundError:
            print('Getting weekly database...')
            copyWeeklyDictToFile(dictionary)
            print('Done')
        solveSuccess = getSolutions(dictionary, petal_letters, center_letter, bonus_letter, display=disp)
        if not solveSuccess:
            print('Retrying weekly database...')
            copyWeeklyDictToFile(dictionary)
            print('Done')
            solveSuccess = getSolutions(dictionary, petal_letters, center_letter, bonus_letter, display=disp)
            if not solveSuccess:
                print('Falling back to built-in dictionary')
                dictionary = 'words_alpha.txt'
                try:
                    open(dictionary, mode='r')
                except FileNotFoundError:
                    print('No built-in dictionary found. Downloading...')
                    uri = 'https://github.com/dwyl/english-words/raw/master/words_alpha.txt'
                    urlretrieve(uri, dictionary)
                print('Dictionary downloaded')
                solveSuccess = getSolutions(dictionary, petal_letters, center_letter, bonus_letter, display=disp)

if __name__ == '__main__':
    main()
