from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import render
import random
import string
from cryptography.fernet import Fernet
import json

from .GameElements import Game, PokerSets, Cards, Player, load_game

SERVER_KEY = b'6ry1SK4icjWBt5k1WhiD3BbTluMyVjtLxbzxxbfO3pg='
ENCRYPTION_TYPE = Fernet(SERVER_KEY)



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
    plain = (s + SEPARATOR + salt).encode()
    return ENCRYPTION_TYPE.encrypt(plain)

def encrypt_number(a):
    """ given a number, encrypt """
    return encrypt_list([a, random.randint(0, 60)])

def decrypt_number(cipher):
    return decrypt_list(cipher)[1]


def encrypt_game(origin):
    ret = json.dumps(origin)
    return encrypt_str(ret)


def set_cookie(resp, game):
    """ set cookies for http response """
    cipher = encrypt_game(game.get_status())
    resp.set_cookie("data", cipher)


def decrypt_game(cookie):
    """
    ret = {}
    for k in cookie.keys():
        try:
            #game_key = decrypt_str(k)
            game_key = k
            # for all values, decrypt as a list, should check later
            game_value = decrypt_list(cookie[k])
            ret[game_key] = game_value
        except:
            # ignore all errors
            pass
    """
    return json.loads(decrypt_str(cookie))


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
    

def serve_card(req):
    #try:
    info = decrypt_game(req.COOKIES["data"])
    game = load_game(info)
    #except Exception as e:
    #    return HttpResponseServerError(e)
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
    ret = game.get_public_status()
    ret["last_served_card"] = c
    resp = JsonResponse(ret)
    set_cookie(resp, game)
    return resp


def start_new_game(req):
    """ API for shuffle """
    n_spots = int(req.GET.get("n_players", "3"))
    game = Game(n_spots, n_sets=1)
    game.first_serve()
    resp = JsonResponse(game.get_public_status())
    set_cookie(resp, game)
    return resp


def index(req):
    return render(req, 'blackjack/homepage.html')