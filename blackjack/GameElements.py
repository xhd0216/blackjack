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
]
SUITES_DICT = {
    "spades": 0,
    "hearts": 1,
    "clubs": 2,
    "diamonds": 3,
}


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
    card = s.split(" ")
    if card[0] not in SUITES or card[1] not in FACES_LIST:
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


def load_game(info):
    """ given a decrypted dictionary, load a game """
    game = Game()
    game.players = []
    n_of_players = info["number_of_players"]
    if n_of_players < 0:
        raise ValueError("invalid number of players")

    # dealer
    dealer_cards = "dealer_cards"
    dealer_ended = "dealer_ended"
    if dealer_cards not in info or dealer_ended not in info:
        raise ValueError("missing dealer info")
    d_list = []
    for c in info[dealer_cards]:
        d_list.append(create_card(c))
    game.dealer = Player(0, d_list, info[dealer_ended])
    game.players.append(game.dealer)

    # other players
    for i in range(n_of_players):
        cards_key = "players_cards_%d" % (i+1)
        ended_key = "players_ended_%d" % (i+1)
        if  cards_key not in info or ended_key not in info:
            raise ValueError("missing player info")
        a_list = []
        for c in info[cards_key]:
            a_list.append(create_card(c))
        p = Player(i+1, a_list, info[ended_key])
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

    return game

class Player:
    def __init__(self, pid, cards=[], has_ended=0, dealer=False):
        self.cards = cards
        self.id = pid
        self.has_ended = has_ended # 0: False
        self.dealer = dealer
    def get_points(self):
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
            self.has_ended = 1
        if self.is_burst() or self.is_21():
            self.has_ended = 1
    def is_burst(self):
        return self.get_points() > 21
    def get_cards(self, hide_dealer_card=True):
        if self.dealer and hide_dealer_card:
            return self.get_dealer_cards()
        return [x.get_str() for x in self.cards]
    def get_dealer_cards(self):
        # with the first card hidden
        return ["hidden"] + [x.get_str() for x in self.cards[1:]]

class Game:
    def __init__(self, n_spots=3, n_sets=1):
        self.ps = PokerSets(n_sets)
        self.spots = n_spots
        self.players = [Player(i, dealer=i == 0) for i in range(self.spots+1)]
        self.dealer = self.players[0]
        self.ps.shuffle()

    def first_serve(self):
        self.ps.shuffle()
        for p in self.players:
            p.cards = []
            p.add_card(self.ps.get_next())
            p.add_card(self.ps.get_next())

    def get_public_status(self):
        """ get public status viewable to players """
        ret = {}
        ret["number_of_players"] = self.spots
        for i in range(self.spots):
            ret["players_cards_%d" % (i+1)] = self.players[i+1].get_cards()
            ret["players_ended_%d" % (i+1)] = self.players[i+1].has_ended
        ret["number_of_sets"] = self.ps.sets
        ret["dealer_cards"] = self.dealer.get_cards(True) # hidden
        ret["dealer_ended"] = self.dealer.has_ended
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
        #   suites (list)0
        #   next_index (int)
        #   number_of_sets (int)
        ret = self.get_public_status()
        ret["dealer_cards"] = self.dealer.get_cards(False) # dealer's cards not hidden
        ret["suites"] = self.ps.suites
        ret["next_index"] = self.ps.next_index
        return ret
        
    def serve_one_card(self, player_id):
        # player id starting from 1
        if player_id > 0:
            if not self.players[player_id].has_ended:
                c = self.ps.get_next()
                self.players[player_id].add_card(c)
            else:
                # TODO error handling
                pass
        if player_id == 0:
            # dealer
            pass
        return c.get_str()

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
        self.players[player_n].has_ended = 1