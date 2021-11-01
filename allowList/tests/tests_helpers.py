import string
import random

def gen_random_strings(n):
    toReturn = []
    for _ in range(n):
        toReturn.append(  ''.join(random.choice(string.ascii_letters) for i in range(15)) )
    return toReturn