from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
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
SUITES_DICT = {
    "spades": 0,
    "hearts": 1,
    "clubs": 2,
    "diamonds": 3,
}

SERVER_KEY = b'6ry1SK4icjWBt5k1WhiD3BbTluMyVjtLxbzxxbfO3pg='
ENCRYPTION_TYPE = Fernet(SERVER_KEY)

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

    def is_Ace(self):
        return self.face == "A"

def create_card(s):
    """ create card from string """
    # for example, diamonds A
    card = s.split()
    if card[0] not in SUITES or card[1] not in FACES_LIST:
        raise ValueError("not a valid card")
    return Cards(card[1], SUITES_DICT[card[0]])

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
    def get_status(self):
        """ return a dict of info """
        ret = {}
        ret["suites"] = self.suites
        ret["next_index"] = self.next_index
        ret["number_of_sets"] = self.sets

class Player:
    def __init__(self, pid, cards=[], has_ended=0, dealer=False):
        self.cards = cards
        self.id = pid
        self.has_ended = has_ended # 0: False
        self.dealer = dealer
    def get_points(self):
        s = sum([x.get_value()) for x in self.cards])
        if any([x.is_Ace() for x in self.cards]) and s < 12:
            s += 10
        return s
    def is_blackjack(self):
        if len(self.cards) == 2:
            c = [x.get_value() for x in self.cards]
            return sorted(c) == [1, 10]
        return False
    def is_21():
        return self.get_points() == 21
    def add_card(self, card):
        if len(self.cards) < 5:
            self.cards.append(card)
        if self.is_burst() or self.is_21():
            self.has_ended = 1
    def is_burst(self):
        return self.get_points() > 21
    def get_cards(self):
        return [x.get_str() for x in self.cards]

class Game:
    def __init__(self, n_spots=3, n_sets=1):
        self.ps = PokerSets(n_sets)
        self.spots = n_spots
        self.players = [Player(i+1) for i in range(self.spots)]
        self.dealer = Player(0, dealer=True)
        # TODO deal with double down.
        self.ps.shuffle()

    def first_serve(self):
        for p in self.players:
            p.add_card(self.ps.get_next())
            p.add_card(self.ps.get_next())

    def get_public_status(self):
        """ get public status viewable to players """
        ret = {}
        ret["number_of_players"] = self.spots
        for i in range(len(self.players)):
            ret["players_cards_%d" % i] = self.players[i].get_cards()
            ret["players_ended_%d" % i] = self.players[i].has_ended
        ret["number_of_sets"] = self.ps.sets
        return ret

    def get_status(self):
        """ get the status of game and return a json """
        # structure of the dict
        # game
        #   number_of_players (int)
        #   players_cards_i (list)
        #   players_ended_i (int)
        #   ...
        #   dealer_cards (list)
        #   dealer_ended (int)
        #   suites (list)
        #   next_index (int)
        #   number_of_sets (int)
        ret = self.get_public_status()
        ret["dealer_cards"] = self.dealer.get_cards()
        ret["dealer_ended"] = self.dealer.has_ended
        ret["suites"] = self.ps.suites
        ret["next_index"] = self.ps.next_index
        
    def serve_one_card(self, player_id):
        # player id starting from 1
        if player_id > 0:
            c = self.ps.get_next()
            self.players[player_id-1].add_card(c)
        if player_id == 0:
            # dealer
            pass
        return c.get_str()

SEPARATOR = "_"
def encrypt_list(a_list):
    """ given a poker set, encrypt """
    enc_str = SEPARATOR.join([str(x) for x in a_list])
    # adding salt
    return encrypt_str(enc_str)

def decrypt_list(cipher):
    ret = decrypt_str(cipher)
    return ret.split(SEPARATOR)


def encrypt_str(s):
    salt = "".join([random.choice(string.ascii_letters) for _ in range(10)])
    return ENCRYPTION_TYPE.encrypt(s + SEPARATOR + salt)

def encrypt_number(a):
    """ given a number, encrypt """
    return encrypt_list([a, random.randint(0, 60)])

def decrypt_number(cipher):
    return decrypt_list(cipher)[1]


def encrypt_game(game):
    origin = game.get_status()
    ret = {}
    for k in origin.keys():
        v = origin[k]
        new_key = encrypt_str(k)
        if type(v) == int:
            new_value = encrypt_number(v)
        elif type(v) == list:
            new_value = encrypt_list(v)
        ret[new_key] = new_value
    return ret

def set_cookie(resp, game):
    """ set cookies for http response """
    cookies = encrypt_list(game)
    for k in cookies:
        resp.set_cookie(k, cookies[k])
    
def decrypt_game(cookie):
    ret = {}
    for k in cookie.keys():
        try:
            game_key = decrypt_str(k)
            # for all values, decrypt as a list, should check later
            game_value = decrypt_list(cookie[k])
            ret[game_key] = game_value
        except:
            # ignore all errors
            pass
    return ret


def load_game(info):
    """ given a decrypted dictionary, load a game """
    game = Game()
    game.players = []
    n_of_players = info["number_of_players"]
    if n_of_players < 0:
        raise ValueError("invalid number of players")

    prev_ended = False
    for i in range(n_of_players):
        cards_key = "players_cards_%d" % (i+1)
        ended_key = "players_ended_%d" % (i+1)
        if  cards_key not in info or ended_key not in info:
            raise ValueError("missing player info")
        a_list = []
        for c in info[cards_key]:
            a_list.append(create_card(c))
        p = Player(i+1, a_list, info[ended_key][0])
        if i == 0:
            prev_ended = p.has_ended
        else:
            if not prev_ended and p.has_ended:
                raise ValueError("player order messed up")
            prev_ended = p.has_ended
        game.players.append(p)
    # dealer
    dealer_cards = "dealer_cards"
    dealer_ended = "dealer_ended"
    if dealer_cards not in info or dealer_ended not in info:
        raise ValueError("missing dealer info")
    d_list = []
    for c in info[dealer_ended]:
        d_list.append(create_card(c))
    game.dealer = Player(0, d_list, info[dealer_ended][0])
    if not prev_ended and game.dealer.has_ended:
        raise ValueError("dealer ended before player done")
    # pokers
    if "suites" not in info or "next_index" not in info or "number_of_sets" not in info:
        raise ValueError("missing poker info")
    ps = PokerSets(info["number_of_sets"][0])
    ps.suites = info["suites"]
    check_shuffled(ps.suites)
    ps.next_index = info["next_index"][0]
    game.ps = ps

    # count total number of cards
    total_cards = sum([len(x.cards) for x in game.players])
    total_cards += len(game.dealer.cards)
    if total_cards != game.ps.next_index:
        raise ValueError("number of cards mismatched")
    

def decrypt_str(cipher):
    if type(cipher) == str:
        # the string starts like b'...=='xxx
        assert cipher[0] == 'b'
        index = cipher.index("\'", 2)
        cipher = cipher[2:index]
        cipher = cipher.encode()

    plain = ENCRYPTION_TYPE.decrypt(cipher).decode()
    ret = plain.split(SEPARATOR)
    return SEPARATOR.join([x for x in ret[:-1]])
    

def check_shuffled(a_list):
    if set(a_list) != set(range(len(a_list))):
        raise ValueError("the given list is not valid")


def serve_card(req):
    try:
        info = decrypt_game(req.COOKIES)
        game = load_game(info)
    except Exception as e:
        return HttpResponseServerError(e)
    resp = HttpResponse()
    player_n = int(req.GET.get("player", '-1'))
    if player_n == -1:
        # try to find the first player
        i = 1
        while i <= game.number_of_players:
            if not game.players[i-1].has_ended:
                player_n = i
                break
            i += 1
        if i == game.number_of_players + 1:
            # dealer's turn
            player_n = 0
    c = game.serve_one_card(player_n)
    resp.write(c)
    set_cookie(resp, game.get_status())
    return resp


def start_new_game(req):
    n_spots = int(req.GET.get("n_players", "3"))
    game = Game(n_spots, n_sets=1)
    game.first_serve()
    resp = JsonResponse(game.get_public_status())
    set_cookie(resp, game)
    return resp


def index(req):
    return render(req, 'blackjack/homepage.html')