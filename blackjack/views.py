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
def encrypt_str(s):
    salt = "".join([random.choice(string.ascii_letters) for _ in range(10)])
    plain = (s + SEPARATOR + salt).encode()
    return ENCRYPTION_TYPE.encrypt(plain)


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

def encrypt_game(origin):
    ret = json.dumps(origin)
    return encrypt_str(ret)


def decrypt_game(cookie):
    return json.loads(decrypt_str(cookie))


def set_cookie(resp, game):
    """ set cookies for http response """
    cipher = encrypt_game(game.get_status())
    resp.set_cookie("data", cipher)


def check_and_load_game(req):
    """ load game and check if the game is valid """
    info = decrypt_game(req.COOKIES["data"])
    game = load_game(info)
    return game


def pass_player(req):
    """ API player choose to pass """
    try:
        game = check_and_load_game(req)
    except Exception as e:
        return HttpResponseServerError(e)

    player_n = int(req.GET.get("player", "-1"))
    if player_n == -1:
        return HttpResponseServerError("missing player number")
    if game.next_player() != player_n:
        return HttpResponseServerError("invalid player to pass")
    game.pass_player(player_n)
    ret = game.get_public_status()
    resp = JsonResponse(ret)
    set_cookie(resp, game)
    return resp


def serve_card(req):
    """ API serve card """
    #try:
    game = check_and_load_game(req)
    #except Exception as e:
    #    return HttpResponseServerError(e)
    
    player_n = int(req.GET.get("player", "-1"))
    if player_n == -1:
        return HttpResponseServerError("missing player number")
    if game.next_player() != player_n:
        return HttpResponseServerError("invalid player to serve %d, %d" % (game.next_player(), player_n))
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