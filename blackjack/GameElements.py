import random

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
    "hidden",
]
SUITES_DICT = {
    "spades": 0,
    "hearts": 1,
    "clubs": 2,
    "diamonds": 3,
    "hidden": -1,
}


class Cards:
    def __init__(self, face, suite):
        # face: str
        # suite: int
        self.face = face
        self.suite = suite
        self.hidden = suite == "hidden"

    def get_value(self):
        if self.hidden:
            return 0
        return FACES[self.face]

    def get_face(self):
        return self.face

    def get_suite(self):
        return self.suite

    def get_str(self):
        if self.hidden:
            return "hidden"
        return SUITES[self.suite] + " " + str(self.face)

    def is_Ace(self):
        return self.face == "A"

    def is_hidden(self):
        return self.hidden
        
def create_card(s):
    """ create card from string """
    # for example, diamonds A, hidden, 
    if s == "hidden":
        return Cards(0, s)
    else:
        card = s.split(" ")
        if len(card) != 2 or card[0] not in SUITES or card[1] not in FACES_LIST:
            raise ValueError("not a valid card " + s)
    return Cards(card[1], SUITES_DICT[card[0]])


def check_shuffled(a_list):
    if set([int(x) for x in a_list]) != set(range(len(a_list))):
        raise ValueError("the given list is not valid")


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


GAME_RESULTS = {
    -2: "PLAYER_BLACKJACK_WIN",
    -1: "PLAYER_WIN",
    0: "TIE",
    1: "DEALER_WIN",
}

class Player:
    def __init__(self, pid, cards=[], has_ended=False, dealer=False):
        self.cards = cards
        self.id = pid
        self.has_ended = has_ended
        self.dealer = dealer
        self.game_result = None
        self.game_ended = False
    
    def set_result(self, res):
        # set game results (int)
        self.game_ended = True
        self.game_result = res

    def get_points(self, show_private_card=False):
        if self.dealer and not self.game_ended and not show_private_card:
            s = sum([x.get_value() for x in self.cards[1:]])
            return s
        s = sum([x.get_value() for x in self.cards])
        if any([x.is_Ace() for x in self.cards]) and s < 12:
            s += 10
        return s
    
    def is_blackjack(self):
        if len(self.cards) == 2:
            c = [x.get_value() for x in self.cards]
            return sorted(c) == [1, 10]
        return False
    
    def is_21(self):
        return self.get_points() == 21
    
    def add_card(self, card):
        if len(self.cards) < 5:
            self.cards.append(card)
        else:
            self.has_ended = True
        if self.is_burst() or self.is_21():
            self.has_ended = True

    def is_burst(self):
        return self.get_points() > 21

    def get_cards(self):
        if self.dealer:
            return self.get_dealer_cards()
        return [x.get_str() for x in self.cards]

    def get_dealer_cards(self, show_private_card=False):
        # with the first card hidden
        if not self.game_ended and not show_private_card:
            return ["hidden"] + [x.get_str() for x in self.cards[1:]]
        else:
            return [x.get_str() for x in self.cards]

    def get_info(self, show_private_card=False):
        """ return a dict """
        ret = {}
        ret["id"] = self.id
        if self.dealer:
            ret["cards"] = self.get_dealer_cards(show_private_card)
            ret["total"] = self.get_points(show_private_card)
            ret["ended"] = self.game_ended
        else:
            ret["cards"] = self.get_cards()
            ret["ended"] = self.has_ended
            ret["total"] = self.get_points()
        ret["blackjack"] = self.is_blackjack()
        ret["burst"] = self.is_burst()
        if self.game_ended and not self.dealer:
            ret["result"] = GAME_RESULTS[self.game_result]
        return ret


class Game:
    def __init__(self, n_spots=3, n_sets=1):
        self.ps = PokerSets(n_sets)
        self.spots = n_spots
        self.players = [Player(i, dealer=i == 0) for i in range(self.spots+1)]
        self.dealer = self.players[0]
        self.ps.shuffle()

    def dealer_strategy(self):
        # define a simple dealer strategy
        # should be deprecated later

        # mark as game ended, such that get_points will calc all cards
        self.dealer.game_ended = True
        if self.next_player() == 0:
            while len(self.dealer.cards) < 5 and self.dealer.get_points() < 17:
                self.serve_one_card(0)

    def first_serve(self):
        self.ps.shuffle()
        for p in self.players:
            p.cards = []
            p.add_card(self.ps.get_next())
            p.add_card(self.ps.get_next())
        if self.game_ended():
            self.wrap_up()

    def get_public_status(self):
        """ get public status viewable to players """
        ret = {}
        ret["number_of_players"] = self.spots
        for i in range(self.spots):
            ret["players_%d" % (i+1)] = self.players[i+1].get_info()

        ret["number_of_sets"] = self.ps.sets
        # get_info: if game has ended, show dealer cards; otherwise hide first card.
        self.dealer.game_ended = self.game_ended()
        ret["dealer"] = self.dealer.get_info()
        ret["next_player"] = self.next_player()
        ret["game_ended"] = self.game_ended()
        return ret

    def get_status(self):
        """ get the status of game and return a json """
        # structure of the dict
        # game
        #   number_of_players (int)
        #   players_i = {
        #       id = int
        #       cards = ["diamond A", ...]
        #       ended = boolean
        #       total = int
        #       blackjack = int (0 or 1)
        #       burst = int (0 or 1)
        #   }
        #   dealer = {
        #       id = int
        #       cards = ["diamond A", ...]
        #       ended = boolean
        #       total = int
        #       blackjack = int (0 or 1)
        #       burst = int (0 or 1)
        #   }
        #   suites (list)
        #   next_index (int)
        #   number_of_sets (int)
        #   next_player (int)
        ret = self.get_public_status()
        ret["dealer"] = self.dealer.get_info(show_private_card=True)
        ret["suites"] = self.ps.suites
        ret["next_index"] = self.ps.next_index
        return ret
        
    def serve_one_card(self, player_id):
        # player id starting from 1
        if player_id != self.next_player():
            raise ValueError("Error: invalid player id.")
        if player_id > 0:
            if not self.players[player_id].has_ended:
                c = self.ps.get_next()
                self.players[player_id].add_card(c)
                if self.game_ended():
                    self.wrap_up()
            else:
                # TODO error handling
                pass
        elif player_id == 0:
            # dealer
            c = self.ps.get_next()
            self.dealer.add_card(c)
        return c.get_str()

    def game_ended(self):
        if self.dealer.is_blackjack() or self.dealer.is_burst():
            return True
        return self.next_player() == 0

    def next_player(self):
        """ get the next player to serve card """
        i = 1
        while i <= self.spots:
            if not self.players[i].has_ended:
                player_n = i
                break
            i += 1
        if i == self.spots + 1:
            # dealer's turn
            player_n = 0
        return player_n

    def pass_player(self, player_n):
        """ player choose to stand
            if all players ended, wrap up game
        """
        self.players[player_n].has_ended = True
        if self.next_player() == 0:
            # the game has ended
            self.wrap_up()

    def wrap_up(self):
        """ return a vector of results
            1: dealer wins
            0: tie
            -1: player wins
            -2: player blackjack
        """
        # first, dealer gets cards.
        self.dealer_strategy()

        # second, calculate results
        ret = []
        if self.dealer.is_blackjack():
            # dealer wins
            for p in self.players:
                if not p.is_blackjack():
                    ret.append(1)
                else:
                    ret.append(0)
        elif self.dealer.is_burst():
            # dealer loses unless player also bursts
            for p in self.players:
                if p.is_burst():
                    ret.append(1)
                elif p.is_blackjack():
                    ret.append(-2)
                else:
                    ret.append(-1)
        else:
            d = self.dealer.get_points()
            for p in self.players:
                if p.is_burst():
                    ret.append(1)
                elif p.is_blackjack():
                    ret.append(-2)
                else:
                    c = p.get_points()
                    if d > c:
                        ret.append(1)
                    elif d == c:
                        ret.append(0)
                    else:
                        ret.append(-1)

        i = 1
        while i < len(ret):
            self.players[i].set_result(ret[i])
            i += 1
        return ret


def load_game(info):
    """ given a decrypted dictionary, load a game """
    game = Game()
    game.players = []
    n_of_players = info["number_of_players"]
    if n_of_players < 0:
        raise ValueError("invalid number of players")
    game.spots = n_of_players

    # dealer
    dealer = "dealer"
    if dealer not in info:
        raise ValueError("missing dealer info")
    d_list = []
    for c in info[dealer]["cards"]:
        d_list.append(create_card(c))
    game.dealer = Player(0, d_list, info[dealer]["ended"], dealer=True)
    game.players.append(game.dealer)

    # other players
    for i in range(n_of_players):
        cards_key = "players_%d" % (i+1)
        if  cards_key not in info:
            raise ValueError("missing player %d info" % (i+1))
        a_list = []
        for c in info[cards_key]["cards"]:
            a_list.append(create_card(c))
        p = Player(i+1, a_list, info[cards_key]["ended"])
        game.players.append(p)
    
    # pokers
    if "suites" not in info or "next_index" not in info or "number_of_sets" not in info:
        raise ValueError("missing poker info")
    ps = PokerSets(info["number_of_sets"])
    ps.suites = info["suites"]
    check_shuffled(ps.suites)
    ps.next_index = info["next_index"]
    game.ps = ps

    # count total number of cards
    total_cards = sum([len(x.cards) for x in game.players])
    if total_cards != game.ps.next_index:
        raise ValueError("number of cards mismatched")

    # check if next player is correct
    if info["next_player"] != game.next_player():
        raise ValueError("incorrect next player")

    return game