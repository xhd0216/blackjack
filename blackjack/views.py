from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
import random
import string
from cryptography.fernet import Fernet

NUM_OF_CARDS = 52
FACES = {
    "A": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
}
FACES_LIST = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITES = [
    "spades",
    "hearts",
    "clubs",
    "diamonds",
]


SERVER_KEY = b'6ry1SK4icjWBt5k1WhiD3BbTluMyVjtLxbzxxbfO3pg='
class Cards:
    def __init__(self, face, suite):
        # face: str
        # suite: int
        assert face in FACES
        self.face = face
        self.suite = suite

    def get_value(self):
        return FACES[self.face]

    def get_face(self):
        return self.face

    def get_suite(self):
        return self.suite

    def get_str(self):
        return SUITES[self.suite] + " " + self.face

class PokerSets:
    def __init__(self, num_set=1):
        assert num_set > 0
        self.suites = [x for x in range(num_set * NUM_OF_CARDS)]
        self.next_index = 0
        self.sets = num_set
    def shuffle(self):
        random.shuffle(self.suites)
        self.next_index = 0
        return self.shuffle
    def get_next(self):
        if self.next_index >= len(self.suites):
            raise ValueError("running out of cards")
        n = self.suites[self.next_index]
        self.next_index += 1
        c = n % NUM_OF_CARDS
        return Cards(FACES_LIST[c % 13], int(c/13))
    def load_suite(self, a_list, a_index):
        check_shuffled(a_list)
        if len(a_list) != self.sets * NUM_OF_CARDS:
            raise ValueError("Invalid number of cards")
        if a_index > self.sets * NUM_OF_CARDS:
            raise ValueError("Invalid index")
        self.next_index = a_index
        self.suites = a_list

SEPARATOR = "_"
def encrypt_list(a_list):
    """ given a poker set, encrypt """
    enc_str = SEPARATOR.join([str(x) for x in a_list])
    # adding salt
    enc_str += SEPARATOR + "".join([random.choice(string.ascii_letters) for _ in range(10)])
    et = Fernet(SERVER_KEY)
    return et.encrypt(str.encode(enc_str))

def decrypt_list(cipher):
    if type(cipher) == str:
        # the string starts like b'...=='xxx
        assert cipher[0] == 'b'
        index = cipher.index("\'", 2)
        cipher = cipher[2:index]
        cipher = cipher.encode()

    et = Fernet(SERVER_KEY)
    plain = et.decrypt(cipher).decode()
    ret = plain.split(SEPARATOR)
    return [int(x) for x in ret[:-1]]


def check_shuffled(a_list):
    if set(a_list) != set(range(len(a_list))):
        raise ValueError("the given list is not valid")


KEY_OF_RANDOM_SUITE = "x3842r"
KEY_OF_SUITE_INDEX = "j2984t"

def serve_card(req):
    ps = PokerSets(1)
    if KEY_OF_RANDOM_SUITE not in req.COOKIES:
        # no cookies? 
        return HttpResponseServerError("cookie not enabled")
    else:
        cipher_suite = req.COOKIES.get(KEY_OF_RANDOM_SUITE)
        plain_suite = decrypt_list(cipher_suite)
        resp = HttpResponse()
        ps.load_suite(plain_suite, int(req.COOKIES.get(KEY_OF_SUITE_INDEX)))
        resp.write(ps.get_next().get_str())
        resp.set_cookie(KEY_OF_SUITE_INDEX, ps.next_index)
        return resp


def index(req):
    ps = PokerSets(1)
    resp = render(req, 'blackjack/homepage.html')

    if KEY_OF_RANDOM_SUITE not in req.COOKIES:
        # TODO: set new game
        # visit for the first time
        ps.shuffle()
        resp.set_cookie(KEY_OF_RANDOM_SUITE, encrypt_list(ps.suites))
        resp.set_cookie(KEY_OF_SUITE_INDEX, str(ps.next_index))
    else:
        # game already started
        pass
    
    return resp


if __name__ == "__main__":
    ps = PokerSets(1)
    a = encrypt_list(ps.suites)
    b = decrypt_list(a)
    print(b)
    assert len(b) == len(ps.suites)
    for i in range(len(b)):
        assert b[i] == ps.suites[i]