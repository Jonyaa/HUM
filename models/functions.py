import string, random

LETTERS = string.digits + string.ascii_lowercase

def get_random_url():
    res = ''.join(random.choice(LETTERS) for i in range(12))
    return res